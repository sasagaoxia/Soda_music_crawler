# =============================================================================
# 文件: src/url_extractor.py
# 功能: 智能提取和清理URL
# =============================================================================

import re
from typing import Optional

class URLExtractor:
    """智能URL提取器 - 从混杂文本中提取有效链接"""

    def __init__(self):
        # 汽水音乐的URL模式
        self.url_patterns = [
            # 分享短链接
            r'https?://qishui\.douyin\.com/s/[a-zA-Z0-9]+/?',
            # 直接页面链接
            r'https?://music\.douyin\.com/[^\s一-鿿]+',
            # 抖音音乐链接
            r'https?://www\.douyin\.com/qishui/[^\s一-鿿]+',
            # 通用抖音链接
            r'https?://[a-zA-Z0-9.-]*douyin\.com[^\s一-鿿]*',
        ]

    def extract_url(self, text: str) -> Optional[str]:
        """从文本中智能提取URL"""
        if not text:
            return None

        # 去除首尾空白
        text = text.strip()

        # 如果已经是纯URL，直接返回
        if self._is_pure_url(text):
            return self._clean_url(text)

        # 从混杂文本中提取URL
        for pattern in self.url_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # 返回第一个匹配的URL
                url = matches[0]
                return self._clean_url(url)

        # 如果没有匹配到，尝试查找任何http/https链接
        generic_pattern = r'https?://[^\s一-鿿]+'
        matches = re.findall(generic_pattern, text, re.IGNORECASE)
        if matches:
            # 过滤出包含douyin的链接
            for url in matches:
                if 'douyin' in url.lower():
                    return self._clean_url(url)

        return None

    def _is_pure_url(self, text: str) -> bool:
        """判断是否为纯URL（不包含其他文字）"""
        # 检查是否以http开头且不包含中文
        if text.startswith(('http://', 'https://')):
            # 检查是否包含中文或其他明显的非URL字符
            if not re.search(r'[一-鿿《》@]', text):
                return True
        return False

    def _clean_url(self, url: str) -> str:
        """清理URL，去除尾部的无关字符"""
        # 去除尾部的标点符号和空白
        url = url.rstrip('.,;!?。，；！？、\'"\'\"')

        # 去除URL中的中文字符（如果有的话）
        url = re.sub(r'[一-鿿]+', '', url)

        # 去除特殊符号
        url = re.sub(r'[《》@]', '', url)

        return url.strip()

    def extract_and_validate(self, text: str) -> tuple[Optional[str], str]:
        """提取URL并返回验证信息"""
        url = self.extract_url(text)

        if not url:
            return None, "❌ 未找到有效的汽水音乐链接"

        # 验证是否为汽水音乐链接
        if 'douyin' not in url.lower():
            return None, "❌ 这不是汽水音乐的链接"

        # 提取歌曲信息（如果文本中包含）
        song_info = self._extract_song_info(text)
        if song_info:
            message = f"✓ 识别到链接: {url}\n  歌曲: {song_info}"
        else:
            message = f"✓ 识别到链接: {url}"

        return url, message

    def _extract_song_info(self, text: str) -> Optional[str]:
        """从文本中提取歌曲信息"""
        # 匹配《歌曲名》格式
        match = re.search(r'《([^》]+)》', text)
        if match:
            return match.group(1)

        # 匹配引号中的内容
        match = re.search(r'["""]([^"""]+)["""]', text)
        if match:
            return match.group(1)

        return None
