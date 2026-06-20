# =============================================================================
# 文件: main.py
# 功能: 主程序入口
# =============================================================================

import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

# Windows 控制台默认 cp936/GBK，无法直接输出 emoji，会触发 UnicodeEncodeError。
# Python 3.7+ 起可在运行时把 stdout/stderr 重编码为 UTF-8。
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass


def _app_dir() -> Path:
    """获取应用所在目录。

    - 普通 Python 运行：项目根目录（main.py 所在）
    - PyInstaller 打包后：exe 所在目录（不是 _MEIPASS 解压目录）
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent


# 切换到应用目录，保证相对路径如 "downloads" 始终落在 exe 旁边
os.chdir(_app_dir())

from src.config import Config
from src.converter import AudioConverter
from src.crawler import QiShuiMusicCrawler
from src.url_extractor import URLExtractor


def _print_menu():
    print("\n=== 汽水音乐爬虫 ===")
    print("1. 手动输入链接，连续下载")
    print("2. 多线程监听剪贴板，复制/分享链接后自动下载")
    print("3. 只转换现有的MP4文件")
    print("0. 退出")


def _manual_download_loop():
    """手动连续下载：每次下载完成后直接提示输入下一个地址。"""
    crawler = QiShuiMusicCrawler()
    url_extractor = URLExtractor()

    try:
        while True:
            user_input = input("\n请输入汽水音乐分享链接/完整分享文本（输入 q 返回菜单）: ").strip()

            if user_input.lower() in ("q", "quit", "exit", "0"):
                print("已返回主菜单。")
                break

            if not user_input:
                print("❌ 没有输入链接，请重新输入。")
                continue

            share_url, message = url_extractor.extract_and_validate(user_input)
            print(message)

            if not share_url:
                print("💥 无法识别有效链接，请重新输入。")
                continue

            success = crawler.crawl_and_download(share_url)
            if success:
                print("\n🎉 下载完成，可以直接输入下一条地址。")
            else:
                print("\n💥 本条处理失败，可以直接输入下一条地址。")

    finally:
        crawler.close()


def _get_clipboard_text() -> str:
    """读取剪贴板文本。

    优先使用 tkinter，不额外安装依赖；如果 tkinter 不可用，Windows 下尝试 PowerShell Get-Clipboard。
    """
    try:
        import tkinter as tk

        root = tk.Tk()
        root.withdraw()
        try:
            text = root.clipboard_get()
        finally:
            root.destroy()
        return text or ""
    except Exception:
        pass

    if sys.platform == "win32":
        try:
            import subprocess

            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command", "Get-Clipboard -Raw"],
                capture_output=True,
                text=True,
                timeout=3,
                encoding="utf-8",
                errors="replace",
            )
            if result.returncode == 0:
                return result.stdout or ""
        except Exception:
            pass

    return ""


def _download_worker(share_url: str) -> bool:
    """在线程里单独创建爬虫实例，避免多个任务共用同一个 Selenium 浏览器。"""
    crawler = QiShuiMusicCrawler()
    try:
        return crawler.crawl_and_download(share_url)
    finally:
        crawler.close()


def _clipboard_watch_loop():
    """连续监听剪贴板：检测到新分享链接后提交到线程池下载。"""
    url_extractor = URLExtractor()
    max_workers = max(1, int(getattr(Config, "MAX_DOWNLOAD_WORKERS", 2)))
    poll_interval = float(getattr(Config, "CLIPBOARD_POLL_INTERVAL_SECONDS", 0.8))

    submitted_urls = set()
    last_raw_text = None
    futures = {}

    print("\n=== 多线程剪贴板自动下载模式 ===")
    print("用法：在汽水音乐里点 分享/复制链接，或复制包含 qishui.douyin.com 的分享文本。")
    print(f"当前线程数: {max_workers}；复制新链接后会自动加入下载队列。")
    print("下载时仍会继续监听剪贴板，检测到下一条会自动排队。")
    print("按 Ctrl+C 返回主菜单。")

    def collect_finished():
        for future, url in list(futures.items()):
            if not future.done():
                continue
            futures.pop(future, None)
            try:
                success = future.result()
            except Exception as e:
                print(f"\n💥 任务异常: {url}\n   {e}")
                continue
            if success:
                print(f"\n🎉 任务完成，继续监听剪贴板: {url}")
            else:
                print(f"\n💥 任务失败或已删除60秒以内短音频，继续监听剪贴板: {url}")

    executor = ThreadPoolExecutor(max_workers=max_workers)
    try:
        while True:
            collect_finished()
            text = _get_clipboard_text().strip()

            if text and text != last_raw_text:
                last_raw_text = text
                share_url, message = url_extractor.extract_and_validate(text)

                if share_url:
                    if share_url in submitted_urls:
                        print("\n检测到重复链接，已跳过。")
                    else:
                        submitted_urls.add(share_url)
                        print("\n检测到新的汽水音乐链接，已加入下载队列：")
                        print(message)
                        future = executor.submit(_download_worker, share_url)
                        futures[future] = share_url
                # 剪贴板里不是汽水链接时静默忽略，避免复制其他文字时刷屏

            time.sleep(poll_interval)

    except KeyboardInterrupt:
        print("\n已停止监听剪贴板。")
    finally:
        # 已提交的任务会让它正常收尾；未开始的任务尽量取消。
        executor.shutdown(wait=False, cancel_futures=True)


def _convert_existing_files():
    converter = AudioConverter()
    success_count = converter.batch_convert(Config.DOWNLOAD_DIR)

    if success_count > 0:
        print(f"\n🎉 成功转换 {success_count} 个文件！")
    else:
        print("\n💥 没有文件被转换！")


def main():
    try:
        while True:
            _print_menu()
            choice = input("请选择 (1/2/3/0): ").strip()

            if choice == "1":
                _manual_download_loop()
            elif choice == "2":
                _clipboard_watch_loop()
            elif choice == "3":
                _convert_existing_files()
            elif choice in ("0", "q", "quit", "exit"):
                print("👋 已退出")
                break
            else:
                print("❌ 无效选择，请重新输入。")

    except KeyboardInterrupt:
        print("\n\n👋 程序已取消")
    except Exception as e:
        print(f"\n❌ 程序错误: {e}")


if __name__ == "__main__":
    main()
    # 打包成 exe 后，双击启动时控制台会随程序退出关闭。等用户按键再退。
    if getattr(sys, "frozen", False):
        try:
            input("\n按 Enter 键退出...")
        except EOFError:
            pass
