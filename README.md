# 汽水音乐爬虫 🎵

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Selenium](https://img.shields.io/badge/Selenium-4.20+-orange.svg)](https://selenium-python.readthedocs.io/)
[![MoviePy](https://img.shields.io/badge/MoviePy-2.0+-red.svg)](https://zulko.github.io/moviepy/)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()

一个用于从汽水音乐下载歌曲并自动转换音频格式的Python爬虫工具。

## ✨ 功能特性

- 🔗 支持汽水音乐分享链接解析
- 🎵 自动提取音频下载链接
- 📱 智能处理重定向和动态页面
- 🎧 自动转换MP4到MP3格式
- 📊 实时下载进度显示
- 📁 批量转换现有文件
- 🛡️ 完善的错误处理机制

## 📁 项目结构

```
qishui-music-crawler/
├── main.py                    # 程序入口，提供交互式界面
├── requirements.txt           # 项目依赖清单
├── README.md                  # 项目说明文档
├── downloads/                 # 音频下载目录 (自动创建)
├── debug_page_fixed.html     # 调试文件 (运行时生成)
└── src/
    ├── config.py              # 配置管理模块
    ├── crawler.py             # 爬虫核心功能
    ├── parser.py              # 页面解析和数据提取
    └── converter.py           # 音频格式转换
```

## 🚀 快速开始

### 环境要求

![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square&logo=python&logoColor=white)
![Chrome](https://img.shields.io/badge/Chrome-Latest-green?style=flat-square&logo=googlechrome&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=flat-square)

### 安装依赖

```bash
pip install -r requirements.txt
```

### 依赖说明

项目使用以下核心库：

![Requests](https://img.shields.io/badge/requests-2.32.0+-blue?style=flat-square&logo=python&logoColor=white)
![Selenium](https://img.shields.io/badge/selenium-4.20.0+-orange?style=flat-square&logo=selenium&logoColor=white)
![MoviePy](https://img.shields.io/badge/moviepy-2.0.0+-red?style=flat-square&logo=python&logoColor=white)
![WebDriver Manager](https://img.shields.io/badge/webdriver--manager-4.0.0+-green?style=flat-square&logo=python&logoColor=white)

```
requests>=2.32.0         # HTTP请求处理
selenium>=4.20.0         # 动态页面抓取 (4.6+ 内置 Selenium Manager 自动下载驱动)
moviepy>=2.0.0           # 音频格式转换 (2.0 起取消了 moviepy.editor 命名空间)
webdriver-manager>=4.0.0 # Chrome驱动管理 (可选，Selenium 4.6+ 已不再必需)
```

### 运行程序

```bash
python main.py
```

![Run](https://img.shields.io/badge/Run-python%20main.py-green?style=flat-square&logo=python&logoColor=white)

## 🎯 使用指南

### 基本使用

1. **启动程序**
   ```bash
   python main.py
   ```

2. **选择操作模式**
   - `1` - 爬取新音乐并自动转换
   - `2` - 只转换现有的MP4文件

3. **输入分享链接**（模式1）
   ```
   请输入汽水音乐分享链接: https://qishui.douyin.com/s/iaVudjjq/
   ```

### 支持的链接格式

- `https://qishui.douyin.com/s/xxxxxx/` - 分享短链接
- `https://music.douyin.com/xxxxx` - 直接页面链接

### 输出文件

下载的文件将保存在 `downloads/` 目录中：

- `{艺术家} - {歌曲名}.mp4` - 原始音频文件
- `{艺术家} - {歌曲名}.mp3` - 转换后的音频文件
- `{艺术家} - {歌曲名}_info.json` - 歌曲信息文件

## ⚙️ 配置选项

### 主要配置 (`src/config.py`)

```python
class Config:
    # 下载设置
    DOWNLOAD_DIR = "downloads"      # 下载目录
    OUTPUT_FORMAT = "mp3"           # 输出格式
    KEEP_ORIGINAL = False           # 是否保留原文件
    AUTO_CONVERT = True             # 自动转换格式
    
    # 音频质量
    BITRATE = "320k"                # 音频比特率
    SAMPLE_RATE = 44100             # 采样率
    CHANNELS = 2                    # 声道数
    
    # 浏览器设置
    USE_SELENIUM = True             # 使用Selenium
    HEADLESS = True                 # 无头模式
    WINDOW_SIZE = "1920,1080"       # 窗口大小
```

### 自定义配置

您可以修改 `src/config.py` 中的配置来调整程序行为：

- **下载目录**: 修改 `DOWNLOAD_DIR`
- **音频格式**: 修改 `OUTPUT_FORMAT` (支持 mp3, wav, flac 等)
- **音频质量**: 修改 `BITRATE` (如 "128k", "192k", "320k")
- **浏览器模式**: 设置 `HEADLESS = False` 查看浏览器操作

## 🔧 核心模块

### 1. 爬虫模块 (`crawler.py`)

```python
from src.crawler import QiShuiMusicCrawler

crawler = QiShuiMusicCrawler()
success = crawler.crawl_and_download(share_url)
crawler.close()
```

**功能：**
- 处理分享链接重定向
- 使用Selenium获取动态内容
- 下载音频文件
- 生成安全文件名

### 2. 解析模块 (`parser.py`)

```python
from src.parser import PageParser

parser = PageParser()
track_info = parser.extract_track_info(html_content)
```

**功能：**
- 多模式正则表达式匹配
- 递归搜索音频信息
- JSON数据解析

### 3. 转换模块 (`converter.py`)

```python
from src.converter import AudioConverter

converter = AudioConverter()
output_file = converter.convert_audio(input_file)
```

**功能：**
- MP4到MP3转换
- 批量文件处理
- 备用重命名方案

### 4. 配置模块 (`config.py`)

统一管理所有配置参数，包括：
- 下载设置
- 音频质量参数
- 浏览器配置
- 请求头设置

## 🐛 常见问题

### 1. Chrome驱动问题

**错误**: `selenium.common.exceptions.WebDriverException`

**解决方案**:
```bash
# 推荐：升级到 Selenium 4.6+，内置 Selenium Manager 会自动下载并管理 ChromeDriver
pip install -U selenium

# 备选：使用 webdriver-manager（已在 requirements.txt 中，作为可选项）
pip install webdriver-manager

# 或手动下载 Chrome 驱动并加入 PATH
```

### 2. 音频转换失败

**现象**: 显示 "使用备用方案：重命名文件"

**解决方案**:
```bash
# 安装ffmpeg
# Windows: 下载ffmpeg并添加到PATH
# macOS: brew install ffmpeg
# Ubuntu: sudo apt install ffmpeg
```

### 3. 页面解析失败

**错误**: "未找到音频信息"

**可能原因**:
- 网页结构已更新
- 网络连接问题
- 反爬虫机制

**解决方案**:
- 检查网络连接
- 更新User-Agent
- 查看生成的debug文件

### 4. 下载速度慢

**优化方案**:
- 检查网络连接
- 修改 `TIMEOUT` 和 `DELAY_SECONDS` 配置
- 使用代理（需自行配置）

## 📝 开发说明

### 添加新的解析模式

在 `src/parser.py` 中添加新的正则表达式模式：

```python
self.patterns = [
    r'现有模式1',
    r'现有模式2',
    r'新的模式',  # 添加新模式
]
```

### 支持新的音频格式

在 `src/converter.py` 中扩展转换功能：

```python
def convert_audio(self, input_file: str, output_format: str = "mp3"):
    # 支持更多格式
    if output_format in ["mp3", "wav", "flac", "aac"]:
        # 转换逻辑
```

### 自定义请求头

修改 `src/config.py` 中的 `get_headers()` 方法：

```python
@classmethod
def get_headers(cls):
    return {
        'User-Agent': '自定义User-Agent',
        # 其他请求头
    }
```

## 📄 许可证

本项目仅供学习和研究使用。请遵守相关网站的服务条款和版权法律。

## 🤝 贡献

欢迎提交Issues和Pull Requests来改进项目！

## ⚠️ 免责声明

- 本工具仅供个人学习和研究使用
- 请尊重音乐版权，不要用于商业用途
- 使用本工具下载的内容请遵守相关法律法规
- 开发者不承担任何法律责任

---

![Made with Love](https://img.shields.io/badge/Made%20with-❤️-red?style=flat-square)
![Python](https://img.shields.io/badge/Made%20with-Python-blue?style=flat-square&logo=python&logoColor=white)

**注意**: 如果遇到任何问题，请先查看 `downloads/debug_page_fixed.html` 文件来诊断页面解析问题。
