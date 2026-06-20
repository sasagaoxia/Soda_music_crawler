# =============================================================================
# 文件: src/parser.py
# 功能: 页面解析和数据提取 - 只解析分享页面，不调用API
# =============================================================================

import html
import json
import re
from typing import Any, Dict, Iterable, List, Optional
from urllib.parse import unquote

from .audio_info_extractor import AudioInfoExtractor


class PageParser:
    """页面解析器 - 从分享页面和页面内嵌数据中提取音频信息"""

    def __init__(self):
        self.audio_info_extractor = AudioInfoExtractor()
        self.state_markers = [
            "_ROUTER_DATA",
            "__INITIAL_STATE__",
            "_SSR_DATA",
            "__SSR_DATA__",
            "__UNIVERSAL_DATA_FOR_REHYDRATION__",
            "SIGI_STATE",
            "RENDER_DATA",
        ]
        self.audio_url_patterns = [
            r"douyinvod\.com",
            r"bytevod",
            r"tos-cn-ve-",
            r"tosv\.",
            r"\.mp4",
            r"\.mp3",
            r"\.m4a",
            r"\.aac",
        ]

    def extract_track_info(self, html_content: str) -> Optional[Dict[str, Any]]:
        """从HTML内容中提取音乐信息 - 智能多策略"""
        print("=== 开始智能解析页面 ===")
        if not html_content:
            return None

        # 策略1：从页面内嵌 JSON / SSR 状态里提取
        json_blocks = self._extract_json_blocks(html_content)
        if json_blocks:
            print(f"找到 {len(json_blocks)} 个页面JSON数据块，开始解析...")
            for i, data in enumerate(json_blocks, start=1):
                try:
                    audio_info = self.audio_info_extractor.extract_from_data(data)
                    if audio_info and audio_info.get("audio_url"):
                        audio_info["source"] = "html_json"
                        print(f"✓ 从页面JSON数据块 {i} 提取成功")
                        return audio_info
                except Exception as e:
                    print(f"  页面JSON数据块 {i} 解析失败: {str(e)[:80]}")
        else:
            print("未找到可解析的页面JSON数据块")

        # 策略2：直接搜索页面中的音频 URL
        print("尝试直接搜索音频URL...")
        audio_info = self._search_audio_urls(html_content)
        if audio_info:
            print("✓ 通过URL搜索找到音频信息")
            return audio_info

        print("❌ 所有策略均未找到有效音频信息")
        return None

    def _extract_json_blocks(self, html_content: str) -> List[Any]:
        """提取页面中的 JSON 块，兼容普通赋值、script JSON、URL编码 RENDER_DATA。"""
        candidates: List[str] = []

        # 1) window.xxx = {...}; 这类数据，使用括号平衡提取，避免正则截断
        for marker in self.state_markers:
            for raw in self._extract_balanced_after_marker(html_content, marker):
                candidates.append(raw)

        # 2) <script type="application/json">...</script>
        for match in re.findall(r"<script[^>]+type=[\"']application/json[\"'][^>]*>([\s\S]*?)</script>", html_content, re.I):
            candidates.append(html.unescape(match.strip()))

        # 3) Next/Nuxt/React 常见 hydration 数据
        for script_id in ("__NEXT_DATA__", "__NUXT_DATA__"):
            pattern = rf"<script[^>]+id=[\"']{re.escape(script_id)}[\"'][^>]*>([\s\S]*?)</script>"
            for match in re.findall(pattern, html_content, re.I):
                candidates.append(html.unescape(match.strip()))

        parsed: List[Any] = []
        seen = set()
        for raw in candidates:
            raw = self._clean_json_candidate(raw)
            if not raw or raw in seen:
                continue
            seen.add(raw)
            data = self._loads_maybe_encoded_json(raw)
            if data is not None:
                parsed.append(data)
        return parsed

    def _extract_balanced_after_marker(self, text: str, marker: str) -> Iterable[str]:
        """找到 marker 后第一个 { 或 [，按括号平衡提取完整 JSON。"""
        start = 0
        while True:
            idx = text.find(marker, start)
            if idx == -1:
                break
            eq_idx = text.find("=", idx)
            # 允许 JSON 被放在 script 标签属性附近，没有 = 时从 marker 后面找
            search_from = eq_idx + 1 if eq_idx != -1 and eq_idx - idx < 200 else idx + len(marker)
            brace_positions = [pos for pos in (text.find("{", search_from), text.find("[", search_from)) if pos != -1]
            if not brace_positions:
                start = idx + len(marker)
                continue
            brace_idx = min(brace_positions)
            raw = self._balanced_slice(text, brace_idx)
            if raw:
                yield raw
            start = brace_idx + 1

    def _balanced_slice(self, text: str, start: int) -> Optional[str]:
        opener = text[start]
        closer = "}" if opener == "{" else "]"
        depth = 0
        in_string = False
        quote_char = ""
        escape = False

        for i in range(start, len(text)):
            ch = text[i]
            if in_string:
                if escape:
                    escape = False
                elif ch == "\\":
                    escape = True
                elif ch == quote_char:
                    in_string = False
                continue

            if ch in ('"', "'"):
                in_string = True
                quote_char = ch
            elif ch == opener:
                depth += 1
            elif ch == closer:
                depth -= 1
                if depth == 0:
                    return text[start:i + 1]
        return None

    def _clean_json_candidate(self, raw: str) -> str:
        raw = html.unescape(raw or "").strip().lstrip("\ufeff")
        raw = re.sub(r"^\)\]\}',?\s*", "", raw)
        raw = raw.strip().rstrip(";")
        return raw

    def _loads_maybe_encoded_json(self, raw: str) -> Optional[Any]:
        """尝试普通JSON、URL编码JSON、JS字符串包裹JSON。"""
        tries = [raw]
        try:
            decoded = unquote(raw)
            if decoded != raw:
                tries.append(decoded)
        except Exception:
            pass

        for candidate in tries:
            if not candidate:
                continue
            if candidate[0] in ('"', "'") and candidate[-1:] == candidate[0]:
                candidate = candidate[1:-1]
                candidate = candidate.encode("utf-8").decode("unicode_escape", errors="ignore")
            if not candidate.startswith(("{", "[")):
                continue
            try:
                return json.loads(candidate)
            except Exception:
                continue
        return None

    def _is_audio_url(self, url: str) -> bool:
        if not url or len(url) < 10:
            return False
        lower = url.lower()
        if any(img in lower for img in (".jpg", ".jpeg", ".png", ".webp", ".gif")):
            return False
        return any(re.search(pattern, lower, re.I) for pattern in self.audio_url_patterns)

    def _search_audio_urls(self, html_content: str) -> Optional[Dict[str, Any]]:
        """直接在HTML中搜索音频URL。"""
        text = html.unescape(html_content)
        text = text.replace("\\u0026", "&").replace("\\/", "/")
        text = unquote(text)

        url_patterns = [
            r"https?://[^\s\"'<>]+?(?:\.mp4|\.mp3|\.m4a|\.aac)[^\s\"'<>]*",
            r"https?://[^\s\"'<>]*(?:douyinvod\.com|bytevod|tos-cn-ve-|tosv\.)[^\s\"'<>]*",
        ]

        urls: List[str] = []
        for pattern in url_patterns:
            urls.extend(re.findall(pattern, text, re.IGNORECASE))

        cleaned_urls: List[str] = []
        seen = set()
        for url in urls:
            url = url.strip().strip('"\'').rstrip(",;\\")
            if url.startswith("//"):
                url = "https:" + url
            if self._is_audio_url(url) and url not in seen:
                seen.add(url)
                cleaned_urls.append(url)

        if not cleaned_urls:
            return None

        print(f"  找到 {len(cleaned_urls)} 个可能的音频URL")
        audio_url = cleaned_urls[0]
        track_name, artist_name = self._find_title_near_url(text, audio_url)

        return {
            "track_name": track_name or "未知歌曲",
            "artist_name": artist_name or "未知艺术家",
            "audio_url": audio_url,
            "track_id": None,
            "duration": 0,
            "cover_url": None,
            "source": "html_url",
        }

    def _find_title_near_url(self, text: str, audio_url: str) -> tuple[str, str]:
        track_name = "未知歌曲"
        artist_name = "未知艺术家"
        url_pos = text.find(audio_url)
        if url_pos <= 0:
            return track_name, artist_name

        context = text[max(0, url_pos - 3000):min(len(text), url_pos + 3000)]
        title_match = re.search(r'"(?:trackName|track_name|musicTitle|title|name|song_name)"\s*:\s*"([^"]+)"', context)
        if title_match and title_match.group(1) not in ["-", "", "null", "undefined"]:
            track_name = title_match.group(1)

        artist_match = re.search(r'"(?:artistName|artist_name|authorName|author_name|artist|singer|nickname)"\s*:\s*"([^"]+)"', context)
        if artist_match and artist_match.group(1) not in ["-", "", "null", "undefined"]:
            artist_name = artist_match.group(1)

        return track_name, artist_name
