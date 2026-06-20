"""
汽水音乐爬虫 - 简单系统测试脚本
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
    print("=" * 50)
    print("测试1: 模块导入")
    print("=" * 50)

    try:
        from src.config import Config
        print("✓ Config 导入成功")

        from src.parser import PageParser
        print("✓ PageParser 导入成功")

        from src.audio_info_extractor import AudioInfoExtractor
        print("✓ AudioInfoExtractor 导入成功")

        from src.crawler import QiShuiMusicCrawler
        print("✓ QiShuiMusicCrawler 导入成功")

        from src.converter import AudioConverter
        print("✓ AudioConverter 导入成功")

        print("\n✅ 所有模块导入成功！\n")
        return True
    except Exception as e:
        print(f"\n❌ 模块导入失败: {e}\n")
        return False


def test_audio_info_extraction():
    print("=" * 50)
    print("测试2: 页面内嵌数据音频地址提取")
    print("=" * 50)

    from src.audio_info_extractor import AudioInfoExtractor

    extractor = AudioInfoExtractor()
    data = {
        "title": "测试歌曲",
        "author": "测试歌手",
        "play_url": {"url_list": ["https://tos-cn-ve-0000.example.com/test.mp3"]},
    }
    info = extractor.extract_from_data(data)
    if info and info.get("audio_url"):
        print("✓ 音频信息提取正常")
        print(f"  歌曲: {info.get('track_name')} - {info.get('artist_name')}")
        print(f"  地址: {info.get('audio_url')}")
        return True
    print("✗ 音频信息提取失败")
    return False


def test_selenium_setup():
    print("=" * 50)
    print("测试3: Selenium WebDriver")
    print("=" * 50)

    from src.crawler import QiShuiMusicCrawler

    try:
        crawler = QiShuiMusicCrawler()
        if crawler.driver:
            print("✓ Selenium WebDriver 初始化成功")
            print("  浏览器: Chrome")
            print(f"  无头模式: {crawler.config.HEADLESS}")
            crawler.close()
            print("\n✅ Selenium测试通过！\n")
            return True
        print("✗ Selenium WebDriver 初始化失败")
        print("\n⚠️ Selenium测试失败，分享页面解析可能无法运行\n")
        return False
    except Exception as e:
        print(f"✗ Selenium测试出错: {e}")
        print("\n⚠️ Selenium测试失败，分享页面解析可能无法运行\n")
        return False


def test_url_extraction():
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
        url, _msg = extractor.extract_and_validate(text)
        if url:
            print(f"✓ 测试 {i}: 成功提取 -> {url}")
        else:
            print(f"✗ 测试 {i}: 提取失败")

    print()


def show_usage_tips():
    print("=" * 50)
    print("使用提示")
    print("=" * 50)
    print()
    print("1. 运行程序：")
    print("   python main.py")
    print()
    print("2. 推荐模式：")
    print("   选择 2，多线程监听剪贴板自动下载")
    print()
    print("3. 输入示例：")
    print("   ✓ 纯链接: https://qishui.douyin.com/s/abc123/")
    print("   ✓ 完整文本: 《歌曲名》@汽水音乐 https://qishui.douyin.com/s/abc123/")
    print()
    print("4. 本版不调用 API 下载，只解析分享页面。")
    print()


def main():
    print("\n")
    print("╔" + "═" * 48 + "╗")
    print("║" + " " * 12 + "汽水音乐爬虫 - 系统测试" + " " * 13 + "║")
    print("╚" + "═" * 48 + "╝")
    print()

    if not test_imports():
        print("❌ 基础模块测试失败，请检查依赖安装")
        return

    test_audio_info_extraction()
    test_selenium_setup()
    test_url_extraction()
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
