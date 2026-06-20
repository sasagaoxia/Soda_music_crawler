# =============================================================================
# 文件: src/audio_info_extractor.py
# 功能: 页面内嵌数据中的音频信息提取；不请求任何 API
# =============================================================================

import html
from typing import Any, Dict, Iterable, Optional


class AudioInfoExtractor:
    """从页面 JSON / HTML 内嵌数据里递归查找音频地址。"""

    AUDIO_HOST_KEYWORDS = (
        "douyinvod.com",
        "bytevod",
        "tos-cn-ve-",
        "tosv.",
        "muscdn.",
        "music-cdn",
    )
    AUDIO_EXTENSIONS = (".mp3", ".m4a", ".mp4", ".aac", ".wav", ".flac")

    TITLE_KEYS = (
        "trackName", "track_name", "musicTitle", "music_title", "title", "name",
        "song_name", "songName", "desc", "caption",
    )
    ARTIST_KEYS = (
        "artistName", "artist_name", "authorName", "author_name", "author", "artist",
        "singer", "user_name", "nickname", "owner_nickname",
    )
    ID_KEYS = ("track_id", "trackId", "music_id", "musicId", "id", "mid")
    DURATION_KEYS = ("duration", "duration_ms", "play_duration", "durationMs")
    COVER_KEYS = (
        "cover_url", "coverURL", "cover", "cover_hd", "cover_large", "cover_medium",
        "cover_thumb", "avatar_thumb",
    )
    AUDIO_URL_KEYS = (
        "audio_url", "audioUrl", "play_url", "playUrl", "play_addr", "playAddr",
        "url", "uri", "main_url", "music_url", "download_url", "downloadUrl", "src",
    )

    def extract_from_data(self, data: Any) -> Optional[Dict[str, Any]]:
        return self._find_audio_recursive(data, context={})

    def _normalise_url(self, value: Any) -> Optional[str]:
        """兼容 URL 字符串、url_list 列表、{'url_list': [...]} 等结构。"""
        if value is None:
            return None

        if isinstance(value, str):
            url = value.strip().strip('"\'')
            if not url:
                return None
            url = html.unescape(url)
            url = url.replace("\\u0026", "&").replace("\\/", "/")
            if url.startswith("//"):
                url = "https:" + url
            if url.startswith("http") and self._is_audio_url(url):
                return url
            return None

        if isinstance(value, list):
            for item in value:
                result = self._normalise_url(item)
                if result:
                    return result
            return None

        if isinstance(value, dict):
            for key in ("url_list", "urls", "url", "main_url", "play_url", "playUrl", "src", "download_url"):
                result = self._normalise_url(value.get(key))
                if result:
                    return result
            return None

        return None

    def _is_audio_url(self, url: str) -> bool:
        if not url or not isinstance(url, str):
            return False
        lower = url.lower()
        if lower.startswith("data:"):
            return False
        if any(ext in lower for ext in self.AUDIO_EXTENSIONS):
            return True
        if any(keyword in lower for keyword in self.AUDIO_HOST_KEYWORDS):
            if any(img_ext in lower for img_ext in (".jpg", ".jpeg", ".png", ".webp", ".gif")):
                return False
            return True
        return False

    def _find_audio_recursive(self, data: Any, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """递归查找音频信息，并继承父级的歌名/歌手。"""
        if isinstance(data, dict):
            current_context = self._merge_context(context, data)

            for key in self.AUDIO_URL_KEYS:
                if key in data:
                    url = self._normalise_url(data.get(key))
                    if url:
                        return self._build_track_info(current_context, url)

            for key in ("play_url", "playUrl", "play_addr", "playAddr", "audio", "music", "music_info", "musicInfo"):
                if key in data:
                    result = self._find_audio_recursive(data.get(key), current_context)
                    if result:
                        return result

            for value in data.values():
                result = self._find_audio_recursive(value, current_context)
                if result:
                    return result

        elif isinstance(data, list):
            for item in data:
                result = self._find_audio_recursive(item, context)
                if result:
                    return result

        return None

    def _merge_context(self, context: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        new_context = dict(context)

        for out_key, keys in (
            ("track_name", self.TITLE_KEYS),
            ("artist_name", self.ARTIST_KEYS),
            ("track_id", self.ID_KEYS),
            ("duration", self.DURATION_KEYS),
            ("cover_url", self.COVER_KEYS),
        ):
            if not new_context.get(out_key):
                value = self._first_value(data, keys)
                if value not in (None, "", "-", "null", "undefined"):
                    if out_key == "cover_url":
                        value = self._normalise_any_url(value)
                    new_context[out_key] = value

        for nested_key in ("author", "artist", "user", "owner"):
            nested = data.get(nested_key)
            if isinstance(nested, dict) and not new_context.get("artist_name"):
                value = self._first_value(nested, self.ARTIST_KEYS)
                if value not in (None, "", "-", "null", "undefined"):
                    new_context["artist_name"] = value

        return new_context

    def _first_value(self, data: Dict[str, Any], keys: Iterable[str]) -> Any:
        for key in keys:
            if key in data:
                value = data.get(key)
                if isinstance(value, (str, int, float)) and str(value).strip():
                    return value
                if isinstance(value, dict):
                    url = self._normalise_any_url(value)
                    if url:
                        return url
        return None

    def _normalise_any_url(self, value: Any) -> Optional[str]:
        """普通URL归一化，cover也可用，不要求音频特征。"""
        if isinstance(value, str):
            url = html.unescape(value.strip().strip('"\''))
            url = url.replace("\\u0026", "&").replace("\\/", "/")
            if url.startswith("//"):
                url = "https:" + url
            if url.startswith("http"):
                return url
        if isinstance(value, list):
            for item in value:
                url = self._normalise_any_url(item)
                if url:
                    return url
        if isinstance(value, dict):
            for key in ("url_list", "urls", "url", "uri", "main_url", "cover", "cover_url"):
                url = self._normalise_any_url(value.get(key))
                if url:
                    return url
        return None

    def _build_track_info(self, context: Dict[str, Any], audio_url: str) -> Dict[str, Any]:
        track_name = str(context.get("track_name") or "未知歌曲").strip()
        artist_name = str(context.get("artist_name") or "未知艺术家").strip()
        if track_name in ("-", "null", "undefined", ""):
            track_name = "未知歌曲"
        if artist_name in ("-", "null", "undefined", ""):
            artist_name = "未知艺术家"

        duration = context.get("duration", 0) or 0
        return {
            "track_name": track_name,
            "artist_name": artist_name,
            "audio_url": audio_url,
            "track_id": context.get("track_id"),
            "duration": duration,
            "cover_url": context.get("cover_url"),
            "source": "html_embedded_data",
        }
