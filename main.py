# =============================================================================
# 文件: main.py
# 功能: 主程序入口
# =============================================================================

import os
import sys
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
    - PyInstaller 打包后：exe 所在目录（**不是** _MEIPASS 解压目录，那是只读临时目录）
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent



# 切换到应用目录，保证相对路径如 "downloads" 始终落在 exe 旁边
os.chdir(_app_dir())

from src.crawler import QiShuiMusicCrawler
from src.converter import AudioConverter
from src.config import Config

def main():
    print("=== 汽水音乐爬虫 ===")
    print()
    print("选择操作模式:")
    print("1. 爬取新音乐并自动转换")
    print("2. 只转换现有的MP4文件")
    
    try:
        choice = input("请选择 (1/2): ").strip()
        
        if choice == "1":
            # 爬取新音乐
            crawler = QiShuiMusicCrawler()
            
            try:
                share_url = input("请输入汽水音乐分享链接: ").strip()
                if not share_url:
                    share_url = "https://qishui.douyin.com/s/iaVudjjq/"  # 默认测试链接
                
                success = crawler.crawl_and_download(share_url)
                
                if success:
                    print("\n🎉 处理完成！")
                else:
                    print("\n💥 处理失败！")
                    
            finally:
                crawler.close()
        
        elif choice == "2":
            # 转换现有文件
            converter = AudioConverter()
            success_count = converter.batch_convert(Config.DOWNLOAD_DIR)
            
            if success_count > 0:
                print(f"\n🎉 成功转换 {success_count} 个文件！")
            else:
                print("\n💥 没有文件被转换！")
        
        else:
            print("❌ 无效选择")
            
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