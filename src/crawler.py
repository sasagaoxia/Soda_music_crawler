# =============================================================================
# 文件: src/crawler.py
# 功能: 核心爬虫功能
# =============================================================================

import json
import os
import re
import shutil
import tempfile
import time
from pathlib import Path
from typing import Optional

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .config import Config
from .converter import AudioConverter
from .parser import PageParser
from .api_fetcher import APIFetcher

class QiShuiMusicCrawler:
    """汽水音乐爬虫"""
    
    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.session = requests.Session()
        self.session.headers.update(self.config.get_headers())

        self.parser = PageParser()
        self.api_fetcher = APIFetcher(self.config)
        self.converter = AudioConverter() if self.config.AUTO_CONVERT else None

        # Selenium 用的隔离 profile 目录，避免与日常 Chrome 冲突
        self._chrome_user_dir: Optional[str] = None
        self.driver = None

        if self.config.USE_SELENIUM:
            self.setup_selenium()
    
    def setup_selenium(self):
        """设置Selenium WebDriver (依赖 Selenium 4.6+ 内置的 Selenium Manager 自动管理驱动)"""
        try:
            chrome_options = Options()
            if self.config.HEADLESS:
                chrome_options.add_argument('--headless=new')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument(f'--window-size={self.config.WINDOW_SIZE}')
            chrome_options.add_argument(f'--user-agent={self.config.USER_AGENT}')

            # 反检测：移除 webdriver 标记。注意 `useAutomationExtension`
            # 和 `excludeSwitches=enable-automation` 在 Chrome 132+ 已被弃用，
            # 传入会导致子进程立刻退出 (session not created)，故只保留下面这一项。
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')

            # 用临时 profile 隔离，避免与用户日常运行的 Chrome 共享 user-data-dir
            # 导致 "Chrome instance exited" 启动失败
            self._chrome_user_dir = tempfile.mkdtemp(prefix="qishui_chrome_")
            chrome_options.add_argument(f'--user-data-dir={self._chrome_user_dir}')

            # 优化性能：禁用图片与通知
            prefs = {
                "profile.managed_default_content_settings.images": 2,
                "profile.default_content_setting_values.notifications": 2,
            }
            chrome_options.add_experimental_option("prefs", prefs)

            self.driver = webdriver.Chrome(options=chrome_options)
            # 进一步隐藏 webdriver 属性
            self.driver.execute_cdp_cmd(
                "Page.addScriptToEvaluateOnNewDocument",
                {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"},
            )
            print("✓ Selenium WebDriver 初始化成功")
        except Exception as e:
            print(f"⚠️ Selenium初始化失败: {e}")
            print("   汽水音乐是 SPA 站点，必须经由 Selenium 抓取动态渲染后的页面，无法降级。")
            print("   排查思路：")
            print("   1) Chrome 浏览器已安装且可正常启动；")
            print("   2) selenium 已升级到 4.6+，让 Selenium Manager 自动匹配 ChromeDriver；")
            print("   3) 关闭所有正在运行的 Chrome 后重试。")
            self.config.USE_SELENIUM = False
            self.driver = None
    
    def get_real_url(self, share_url: str) -> str:
        """获取分享链接的真实URL"""
        try:
            response = self.session.get(share_url, allow_redirects=True)
            return response.url
        except Exception as e:
            print(f"获取真实URL时出错: {e}")
            return share_url
    
    def get_page_content(self, url: str) -> Optional[str]:
        """获取页面内容"""
        if self.config.USE_SELENIUM and hasattr(self, 'driver') and self.driver:
            return self._get_content_with_selenium(url)
        else:
            return self._get_content_with_requests(url)
    
    def _get_content_with_selenium(self, url: str) -> Optional[str]:
        """使用Selenium获取页面内容"""
        try:
            print(f"使用Selenium请求: {url}")
            self.driver.get(url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(3)
            html_content = self.driver.page_source
            print(f"✓ 页面内容获取成功，长度: {len(html_content)}")
            return html_content
        except Exception as e:
            print(f"Selenium获取页面失败: {e}")
            return None
    
    def _get_content_with_requests(self, url: str) -> Optional[str]:
        """使用requests获取页面内容"""
        try:
            response = self.session.get(url)
            return response.text
        except Exception as e:
            print(f"requests获取页面失败: {e}")
            return None
    
    def download_audio(self, audio_url: str, filename: str, download_dir: str = None) -> Optional[str]:
        """下载音频文件"""
        download_dir = download_dir or self.config.DOWNLOAD_DIR
        
        try:
            Path(download_dir).mkdir(exist_ok=True)
            
            print(f"开始下载: {filename}")
            
            # 添加下载专用请求头
            headers = self.config.get_headers()
            headers.update({
                'Referer': 'https://music.douyin.com/',
                'Range': 'bytes=0-',
            })
            
            response = self.session.get(audio_url, headers=headers, stream=True)
            response.raise_for_status()
            
            file_path = os.path.join(download_dir, filename)
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        
                        if total_size > 0:
                            progress = (downloaded_size / total_size) * 100
                            print(f"\r下载进度: {progress:.1f}%", end='', flush=True)
            
            print(f"\n✓ 下载完成: {file_path}")
            return file_path
            
        except Exception as e:
            print(f"❌ 下载音频时出错: {e}")
            return None
    
    def crawl_and_download(self, share_url: str, download_dir: str = None) -> bool:
        """完整的爬取和下载流程 - 多策略智能获取"""
        print(f"=== 开始处理: {share_url} ===")

        # 汽水音乐是 SPA，Selenium 不可用时 requests 拿到的只是空壳 HTML，
        # 解析必然失败，提前结束并给出明确提示
        if self.config.USE_SELENIUM and not self.driver:
            print("❌ Selenium 未就绪，无法继续抓取动态页面。")
            return False

        try:
            # 1. 获取真实URL
            if 'qishui.douyin.com/s/' in share_url:
                url = self.get_real_url(share_url)
            else:
                url = share_url

            print(f"目标URL: {url}")

            # 策略1: 尝试通过API获取（更稳定）
            track_id = self.api_fetcher.extract_track_id(url)
            track_info = None

            if track_id:
                print(f"✓ 提取到track_id: {track_id}")
                print("策略1: 尝试通过API获取...")
                track_info = self.api_fetcher.fetch_track_info_by_api(track_id)

            # 策略2: 解析HTML页面（备用方案）
            if not track_info:
                print("策略2: 解析HTML页面...")
                html_content = self.get_page_content(url)
                if not html_content:
                    print("❌ 无法获取页面内容")
                    return False

                track_info = self.parser.extract_track_info(html_content)

            # 检查结果
            if not track_info:
                print("❌ 获取音乐信息失败")
                print("   可能原因：")
                print("   1. 该歌曲没有版权或已下架")
                print("   2. 网站结构发生变化")
                print("   3. 链接已失效")
                print("   建议：尝试其他歌曲链接")
                return False

            if not track_info.get('audio_url'):
                print("❌ 未找到音频下载链接")
                print("   该歌曲可能没有播放权限或已下架")
                return False

            print(f"✓ 找到音乐: {track_info['track_name']} - {track_info['artist_name']}")

            # 4. 生成安全的文件名
            safe_track_name = self._safe_filename(track_info.get('track_name', 'unknown'))
            safe_artist_name = self._safe_filename(track_info.get('artist_name', 'unknown'))
            filename = f"{safe_artist_name} - {safe_track_name}.mp4"

            # 5. 下载音频
            downloaded_file = self.download_audio(
                track_info['audio_url'],
                filename,
                download_dir
            )

            if not downloaded_file:
                return False

            print(f"✅ 成功下载: {os.path.basename(downloaded_file)}")

            # 6. 保存音乐信息
            self._save_track_info(track_info, downloaded_file)

            # 7. 自动转换格式
            final_file = downloaded_file
            if self.converter:
                converted_file = self.converter.convert_audio(downloaded_file)
                if converted_file:
                    final_file = converted_file

            print(f"🎉 处理完成: {os.path.basename(final_file)}")
            return True

        except Exception as e:
            print(f"❌ 处理失败: {e}")
            return False
    
    def _safe_filename(self, filename: str) -> str:
        """生成安全的文件名"""
        if not filename:
            return "unknown"
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        filename = filename.strip()
        return filename[:100]
    
    def _save_track_info(self, track_info: dict, file_path: str):
        """保存音乐信息到JSON文件"""
        try:
            info_file = Path(file_path).with_suffix('.info.json')
            with open(info_file, 'w', encoding='utf-8') as f:
                json.dump(track_info, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存音乐信息失败: {e}")
    
    def close(self):
        """关闭资源"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
        if self._chrome_user_dir:
            shutil.rmtree(self._chrome_user_dir, ignore_errors=True)
