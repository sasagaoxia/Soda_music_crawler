# =============================================================================
# 文件: src/api_fetcher.py
# 功能: API接口获取 - 更稳定的数据获取方式
# =============================================================================

import re
import requests
from typing import Optional, Dict, Any
from .config import Config

class APIFetcher:
    """通过API接口获取音乐信息 - 比解析HTML更稳定"""

    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.session = requests.Session()
        self.session.headers.update(self.config.get_headers())

    def extract_track_id(self, url: str) -> Optional[str]:
        """从URL中提取track_id"""
        patterns = [
            r'track_id=(\d+)',
            r'/track/(\d+)',
            r'/song/(\d+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return None

    def fetch_track_info_by_api(self, track_id: str) -> Optional[Dict[str, Any]]:
        """通过API获取歌曲信息"""
        # 尝试多个可能的API端点
        api_endpoints = [
            f"https://music.douyin.com/api/song/detail?id={track_id}",
            f"https://www.douyin.com/aweme/v1/web/music/detail/?music_id={track_id}",
        ]

        for api_url in api_endpoints:
            try:
                print(f"尝试API: {api_url}")
                response = self.session.get(api_url, timeout=10)

                if response.status_code == 200:
                    data = response.json()

                    # 尝试从响应中提取信息
                    track_info = self._parse_api_response(data)
                    if track_info:
                        print(f"✓ API获取成功")
                        return track_info

            except Exception as e:
                print(f"  API请求失败: {e}")
                continue

        return None

    def _parse_api_response(self, data: Dict) -> Optional[Dict[str, Any]]:
        """解析API响应"""
        # 这里需要根据实际API响应结构调整
        # 目前作为框架预留

        if isinstance(data, dict):
            # 递归查找音频信息
            return self._find_audio_recursive(data)

        return None

    def _find_audio_recursive(self, data: Any) -> Optional[Dict[str, Any]]:
        """递归查找音频信息"""
        if isinstance(data, dict):
            # 查找包含URL的对象
            url = data.get('url') or data.get('play_url') or data.get('playUrl')

            if url and ('douyinvod.com' in url or '.mp4' in url or '.mp3' in url):
                return {
                    'track_name': data.get('title') or data.get('name') or '未知歌曲',
                    'artist_name': data.get('author') or data.get('artist') or '未知艺术家',
                    'audio_url': url,
                    'track_id': data.get('id') or data.get('music_id'),
                    'duration': data.get('duration', 0),
                    'cover_url': data.get('cover') or data.get('cover_url')
                }

            # 递归搜索
            for value in data.values():
                result = self._find_audio_recursive(value)
                if result:
                    return result

        elif isinstance(data, list):
            for item in data:
                result = self._find_audio_recursive(item)
                if result:
                    return result

        return None
