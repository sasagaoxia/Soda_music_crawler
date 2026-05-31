# =============================================================================
# 文件: src/parser.py
# 功能: 页面解析和数据提取 - 通用智能版本
# =============================================================================

import re
import json
from typing import Optional, Dict, Any

class PageParser:
    """页面解析器 - 使用多种策略智能提取音频信息"""

    def __init__(self):
        # 多种数据源模式
        self.data_patterns = [
            # 模式1: _ROUTER_DATA 对象
            r'_ROUTER_DATA\s*=\s*(\{[\s\S]*?\});(?=\s*function|\s*</script>|\s*var|\s*window|\s*$)',
            # 模式2: window.__INITIAL_STATE__
            r'window\.__INITIAL_STATE__\s*=\s*(\{[\s\S]*?\});',
            # 模式3: audioWithLyricsOption 直接匹配
            r'"audioWithLyricsOption":\s*(\{[\s\S]*?\})(?=,\s*"[a-zA-Z]|\})',
            # 模式4: SSR_DATA
            r'window\._SSR_DATA\s*=\s*(\{[\s\S]*?\});',
        ]

        # 音频URL的特征模式
        self.audio_url_patterns = [
            r'douyinvod\.com',
            r'\.mp4',
            r'\.mp3',
            r'bytecdn\.cn',
            r'tosv\.byted\.org',
        ]

    def extract_track_info(self, html_content: str) -> Optional[Dict[str, Any]]:
        """从HTML内容中提取音乐信息 - 智能多策略"""
        print("=== 开始智能解析页面 ===")

        # 策略1: 尝试从各种数据源提取
        for i, pattern in enumerate(self.data_patterns):
            print(f"尝试数据源模式 {i+1}...")
            matches = re.findall(pattern, html_content, re.DOTALL)

            if matches:
                print(f"✓ 模式 {i+1} 找到 {len(matches)} 个匹配")

                for j, match in enumerate(matches):
                    try:
                        data = json.loads(match)
                        audio_info = self._extract_from_data(data)
                        if audio_info:
                            print(f"✓ 从数据源 {i+1}.{j+1} 成功提取音频信息")
                            return audio_info
                    except json.JSONDecodeError as e:
                        print(f"  JSON解析失败: {str(e)[:100]}")
                        continue

        # 策略2: 直接搜索音频URL
        print("尝试直接搜索音频URL...")
        audio_info = self._search_audio_urls(html_content)
        if audio_info:
            print("✓ 通过URL搜索找到音频信息")
            return audio_info

        print("❌ 所有策略均未找到有效音频信息")
        return None

    def _extract_from_data(self, data: Any, path: str = "root") -> Optional[Dict[str, Any]]:
        """从JSON数据中智能提取音频信息"""
        if isinstance(data, dict):
            # 检查版权状态
            has_copyright = data.get('hasCopyright')
            if has_copyright is False:
                print(f"  ⚠️ 检测到无版权标记 (hasCopyright=false)")
                return None

            # 检查状态码
            status_code = data.get('status_code')
            if status_code and status_code != 0:
                print(f"  ⚠️ 检测到错误状态码: {status_code}")
                # 继续尝试，可能其他地方有数据

            # 查找包含音频URL的对象
            url = data.get('url', '')
            if url and self._is_audio_url(url):
                # 找到了音频URL，提取完整信息
                track_name = (
                    data.get('trackName') or
                    data.get('track_name') or
                    data.get('name') or
                    data.get('title') or
                    '未知歌曲'
                )

                artist_name = (
                    data.get('artistName') or
                    data.get('artist_name') or
                    data.get('artist') or
                    data.get('singer') or
                    '未知艺术家'
                )

                # 过滤掉占位符
                if track_name in ['-', '', 'null', 'undefined']:
                    track_name = '未知歌曲'
                if artist_name in ['-', '', 'null', 'undefined']:
                    artist_name = '未知艺术家'

                return {
                    'track_name': track_name,
                    'artist_name': artist_name,
                    'audio_url': url,
                    'track_id': data.get('track_id') or data.get('trackId'),
                    'duration': data.get('duration', 0),
                    'cover_url': data.get('cover_url') or data.get('coverURL') or data.get('cover')
                }

            # 递归搜索所有字段
            for key, value in data.items():
                result = self._extract_from_data(value, f"{path}.{key}")
                if result:
                    return result

        elif isinstance(data, list):
            for i, item in enumerate(data):
                result = self._extract_from_data(item, f"{path}[{i}]")
                if result:
                    return result

        return None

    def _is_audio_url(self, url: str) -> bool:
        """判断是否为有效的音频URL"""
        if not url or len(url) < 10:
            return False

        # 检查是否匹配任何音频URL特征
        for pattern in self.audio_url_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return True

        return False

    def _search_audio_urls(self, html_content: str) -> Optional[Dict[str, Any]]:
        """直接在HTML中搜索音频URL"""
        # 搜索所有可能的URL
        url_pattern = r'https?://[^\s"\'<>]+?\.(?:mp4|mp3)[^\s"\'<>]*'
        urls = re.findall(url_pattern, html_content, re.IGNORECASE)

        # 过滤出音频URL
        audio_urls = [url for url in urls if self._is_audio_url(url)]

        if audio_urls:
            print(f"  找到 {len(audio_urls)} 个可能的音频URL")
            # 使用第一个找到的URL
            audio_url = audio_urls[0]

            # 尝试在附近查找歌曲信息
            track_name = '未知歌曲'
            artist_name = '未知艺术家'

            # 在URL附近搜索标题和艺术家
            url_pos = html_content.find(audio_url)
            if url_pos > 0:
                context = html_content[max(0, url_pos-1000):min(len(html_content), url_pos+1000)]

                # 搜索标题
                title_match = re.search(r'"(?:trackName|track_name|title|name)"\s*:\s*"([^"]+)"', context)
                if title_match and title_match.group(1) not in ['-', '', 'null']:
                    track_name = title_match.group(1)

                # 搜索艺术家
                artist_match = re.search(r'"(?:artistName|artist_name|artist|singer)"\s*:\s*"([^"]+)"', context)
                if artist_match and artist_match.group(1) not in ['-', '', 'null']:
                    artist_name = artist_match.group(1)

            return {
                'track_name': track_name,
                'artist_name': artist_name,
                'audio_url': audio_url,
                'track_id': None,
                'duration': 0,
                'cover_url': None
            }

        return None
