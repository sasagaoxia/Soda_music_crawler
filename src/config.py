# =============================================================================
# 文件: src/config.py
# 功能: 配置管理
# =============================================================================

class Config:
    """配置类"""
    
    # 下载设置
    DOWNLOAD_DIR = "downloads"
    OUTPUT_FORMAT = "mp3"
    KEEP_ORIGINAL = False
    AUTO_CONVERT = True
    # 小于/等于这个时长会判定为短音频/试听片段
    SHORT_AUDIO_THRESHOLD_SECONDS = 60
    # 检测到 60 秒以内短音频/试听片段后自动删除
    DELETE_SHORT_AUDIO = True
    
    # 音频质量设置
    BITRATE = "320k"
    SAMPLE_RATE = 44100
    CHANNELS = 2
    
    # Selenium设置
    USE_SELENIUM = True
    # True = 后台无窗口运行，不弹出白色 Chrome 页面
    HEADLESS = True
    # 即使手动关闭 HEADLESS，也尽量把 Chrome 窗口移到屏幕外
    HIDE_BROWSER_WINDOW = True
    WINDOW_SIZE = "1920,1080"
    

    # 剪贴板多线程下载设置
    # 线程数不要太大；每个线程会单独打开一个 Selenium 浏览器实例。
    MAX_DOWNLOAD_WORKERS = 2
    CLIPBOARD_POLL_INTERVAL_SECONDS = 0.8

    # 请求设置
    MAX_RETRIES = 3
    TIMEOUT = 30
    DELAY_SECONDS = 2
    
    # 用户代理
    USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
    
    @classmethod
    def get_headers(cls):
        """获取请求头"""
        return {
            'User-Agent': cls.USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }