"""
汽水音乐爬虫 - 完整测试脚本
测试所有功能模块
"""
import sys
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """测试模块导入"""
    print("=" * 50)
    print("测试1: 模块导入")
    print("=" * 50)

    try:
        from src.config import Config
        print("✓ Config 导入成功")

        from src.parser import PageParser
        print("✓ PageParser 导入成功")

        from src.api_fetcher import APIFetcher
        print("✓ APIFetcher 导入成功")

        from src.crawler import QiShuiMusicCrawler
        print("✓ QiShuiMusicCrawler 导入成功")

        from src.converter import AudioConverter
        print("✓ AudioConverter 导入成功")

        print("\n✅ 所有模块导入成功！\n")
        return True
    except Exception as e:
        print(f"\n❌ 模块导入失败: {e}\n")
        return False

def test_track_id_extraction():
    """测试track_id提取"""
    print("=" * 50)
    print("测试2: Track ID 提取")
    print("=" * 50)

    from src.api_fetcher import APIFetcher

    fetcher = APIFetcher()

    test_urls = [
        "https://music.douyin.com/qishui/share/track?track_id=7436454427404765196",
        "https://music.douyin.com/track/7436454427404765196",
        "https://www.douyin.com/qishui/song/7436454427404765196",
    ]

    for url in test_urls:
        track_id = fetcher.extract_track_id(url)
        if track_id:
            print(f"✓ {url[:50]}... -> {track_id}")
        else:
            print(f"✗ {url[:50]}... -> 未提取到")

    print()

def test_selenium_setup():
    """测试Selenium设置"""
    print("=" * 50)
    print("测试3: Selenium WebDriver")
    print("=" * 50)

    from src.crawler import QiShuiMusicCrawler

    try:
        crawler = QiShuiMusicCrawler()
        if crawler.driver:
            print("✓ Selenium WebDriver 初始化成功")
            print(f"  浏览器: Chrome")
            print(f"  无头模式: {crawler.config.HEADLESS}")
            crawler.close()
            print("\n✅ Selenium测试通过！\n")
            return True
        else:
            print("✗ Selenium WebDriver 初始化失败")
            print("\n⚠️ Selenium测试失败，但程序仍可运行\n")
            return False
    except Exception as e:
        print(f"✗ Selenium测试出错: {e}")
        print("\n⚠️ Selenium测试失败，但程序仍可运行\n")
        return False

def test_url_extraction():
    """测试URL提取功能"""
    print("=" * 50)
    print("测试4: URL智能提取")
    print("=" * 50)

    from src.url_extractor import URLExtractor

    extractor = URLExtractor()

    test_cases = [
        '《One Of The Girls》@汽水音乐 https://qishui.douyin.com/s/iQfNnBfJ/',
        'https://qishui.douyin.com/s/iaVudjjq/',
        '听这首歌 https://music.douyin.com/track/123456',
    ]

    for i, text in enumerate(test_cases, 1):
        url, msg = extractor.extract_and_validate(text)
        if url:
            print(f"✓ 测试 {i}: 成功提取")
            print(f"  输入: {text[:40]}...")
            print(f"  提取: {url}")
        else:
            print(f"✗ 测试 {i}: 提取失败")

    print()

def show_usage_tips():
    """显示使用提示"""
    print("=" * 50)
    print("使用提示")
    print("=" * 50)
    print()
    print("1. 获取有效链接：")
    print("   - 打开汽水音乐APP")
    print("   - 找到一首可以正常播放的歌曲")
    print("   - 点击分享 -> 复制链接")
    print("   - 可以直接粘贴完整分享文本，程序会自动提取链接")
    print()
    print("2. 运行程序：")
    print("   python main.py")
    print()
    print("3. 输入示例：")
    print("   ✓ 纯链接: https://qishui.douyin.com/s/abc123/")
    print("   ✓ 完整文本: 《歌曲名》@汽水音乐 https://qishui.douyin.com/s/abc123/")
    print("   程序会自动识别并提取链接")
    print()
    print("4. 常见问题：")
    print("   - 如果提示'没有版权'，换一首歌试试")
    print("   - 确保歌曲在APP中可以正常播放")
    print("   - 检查网络连接")
    print()
    print("4. 查看详细文档：")
    print("   使用说明.md")
    print()

def main():
    print("\n")
    print("╔" + "═" * 48 + "╗")
    print("║" + " " * 12 + "汽水音乐爬虫 - 系统测试" + " " * 13 + "║")
    print("╚" + "═" * 48 + "╝")
    print()

    # 测试1: 模块导入
    if not test_imports():
        print("❌ 基础模块测试失败，请检查依赖安装")
        return

    # 测试2: Track ID提取
    test_track_id_extraction()

    # 测试3: Selenium
    test_selenium_setup()

    # 测试4: URL提取
    test_url_extraction()

    # 显示使用提示
    show_usage_tips()

    print("=" * 50)
    print("测试完成！")
    print("=" * 50)
    print()
    print("现在可以运行: python main.py")
    print()

if __name__ == "__main__":
    main()

    if getattr(sys, "frozen", False):
        try:
            input("\n按 Enter 键退出...")
        except EOFError:
            pass
