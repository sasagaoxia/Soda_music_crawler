# 汽水音乐爬虫 🎵

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Selenium](https://img.shields.io/badge/Selenium-4.20+-orange.svg)](https://selenium-python.readthedocs.io/)
[![MoviePy](https://img.shields.io/badge/MoviePy-2.0+-red.svg)](https://zulko.github.io/moviepy/)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()

一个用于从汽水音乐下载歌曲并自动转换音频格式的Python爬虫工具。

## ⚡ 最新更新 (v2.0)

- ✅ **多策略智能获取** - API接口 + HTML解析 + URL搜索三重保障
- ✅ **智能URL提取** - 支持直接粘贴完整分享文本，自动识别链接
- ✅ **版权智能检测** - 自动识别无版权歌曲并给出提示
- ✅ **更稳定的解析** - 不再依赖单一数据结构，适应网站变化
- ✅ **详细错误提示** - 清晰的失败原因和解决建议
- ✅ **完整测试套件** - 一键测试所有功能模块

## ✨ 功能特性

- 🔗 支持汽水音乐分享链接解析
- 🎵 多策略智能提取音频链接（API + HTML + 直接搜索）
- 📱 智能处理重定向和动态页面
- 🎧 自动转换MP4到MP3格式
- 📊 实时下载进度显示
- 📁 批量转换现有文件
- 🛡️ 完善的错误处理和版权检测
- 🔄 自动降级备用方案

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

### 测试系统

运行测试脚本检查所有模块是否正常：

```bash
python test_system.py
```

### 运行程序

```bash
python main.py
```

## 🎯 使用指南

### ⚠️ 重要提示

**版权限制：** 汽水音乐的歌曲有版权保护。如果遇到以下提示，说明该歌曲无法下载：
- "该歌曲没有版权或已下架"
- "未找到音频下载链接"

**解决方法：** 换一首在APP中可以正常播放的歌曲。

### 获取有效链接

1. 打开汽水音乐APP
2. 找到一首**可以正常播放**的歌曲
3. 点击分享按钮
4. 复制分享链接
5. 粘贴到本程序中

### 基本使用

1. **启动程序**
   ```bash
   python main.py
   ```

2. **选择操作模式**
   - `1` - 爬取新音乐并自动转换
   - `2` - 只转换现有的MP4文件

3. **输入分享链接**（模式1）
   
   **支持两种输入方式：**
   
   ✅ **方式1: 直接粘贴完整分享文本（推荐）**
   ```
   《One Of The Girls x After Hours》@汽水音乐 https://qishui.douyin.com/s/iQfNnBfJ/
   ```
   程序会自动识别并提取链接，无需手动删除其他文字！
   
   ✅ **方式2: 只粘贴链接**
   ```
   https://qishui.douyin.com/s/iQfNnBfJ/
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

### 工作原理 - 多策略智能获取

程序使用三重策略确保最大成功率：

#### 策略1: API接口获取（最稳定）
```python
from src.api_fetcher import APIFetcher

fetcher = APIFetcher()
track_id = fetcher.extract_track_id(url)
track_info = fetcher.fetch_track_info_by_api(track_id)
```

**优势：**
- 直接从API获取，不依赖HTML结构
- 速度快，成功率高
- 不易受网站改版影响

#### 策略2: HTML智能解析（备用）
```python
from src.parser import PageParser

parser = PageParser()
track_info = parser.extract_track_info(html_content)
```

**功能：**
- 多种数据源模式匹配
- 递归搜索音频信息
- 自动版权检测

#### 策略3: 直接URL搜索（兜底）
- 在页面源码中直接搜索音频链接
- 正则匹配所有可能的音频URL
- 最后的保障方案

### 1. 爬虫模块 (`crawler.py`)

```python
from src.crawler import QiShuiMusicCrawler

crawler = QiShuiMusicCrawler()
success = crawler.crawl_and_download(share_url)
crawler.close()
```

**功能：**
- 多策略智能获取音频信息
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
- 版权状态检测

### 3. API模块 (`api_fetcher.py`)

```python
from src.api_fetcher import APIFetcher

fetcher = APIFetcher()
track_info = fetcher.fetch_track_info_by_api(track_id)
```

**功能：**
- 从URL提取track_id
- 通过API获取歌曲信息
- 多端点自动尝试

### 4. 转换模块 (`converter.py`)

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

### 1. 为什么有些歌曲下载不了？

**原因：** 该歌曲可能：
- 没有版权授权
- 仅限APP内播放
- 已经下架

**解决：** 换一首在汽水音乐APP中可以正常播放的歌曲。

### 2. 如何判断歌曲是否可下载？

在汽水音乐APP中：
- ✅ 能正常播放 = 可能可以下载
- ❌ 显示"暂不支持播放" = 无法下载

### 3. Chrome驱动问题

**错误**: `selenium.common.exceptions.WebDriverException`

**解决方案**:
```bash
# 推荐：升级到 Selenium 4.6+，内置 Selenium Manager 会自动下载并管理 ChromeDriver
pip install -U selenium

# 或手动下载 Chrome 驱动并加入 PATH
```

### 4. 音频转换失败

**现象**: 显示 "使用备用方案：重命名文件"

**解决方案**:
```bash
# 安装ffmpeg
# Windows: 下载ffmpeg并添加到PATH
# macOS: brew install ffmpeg
# Ubuntu: sudo apt install ffmpeg
```

### 5. 页面解析失败

**错误**: "未找到音频信息"

**可能原因**:
- 歌曲没有版权
- 网络连接问题
- 链接已失效

**解决方案**:
- 检查歌曲是否能在APP中播放
- 检查网络连接
- 尝试其他歌曲链接
- 运行 `python test_system.py` 检查系统状态

### 6. 程序运行很慢

**优化方案**:
- 检查网络连接
- 关闭其他占用网络的程序
- 耐心等待（首次运行需要初始化浏览器）

## 📝 开发说明

### 项目结构

```
Soda_music_crawler/
├── main.py                    # 程序入口
├── test_system.py             # 系统测试脚本
├── requirements.txt           # 项目依赖
├── README.md                  # 项目文档
├── 使用说明.md                # 详细使用指南
├── downloads/                 # 下载目录 (自动创建)
├── debug_page_fixed.html     # 调试文件 (运行时生成)
└── src/
    ├── config.py              # 配置管理
    ├── crawler.py             # 爬虫核心 (多策略)
    ├── parser.py              # HTML解析 (智能搜索)
    ├── api_fetcher.py         # API接口获取
    └── converter.py           # 音频格式转换
```

### 技术特性

#### 多策略架构
- **策略1**: API接口 - 最稳定，不依赖HTML结构
- **策略2**: HTML解析 - 智能搜索，多模式匹配
- **策略3**: URL搜索 - 兜底方案，直接匹配

#### 智能解析
- 多种数据源模式匹配
- 自动检测版权状态
- 递归搜索音频信息
- 过滤占位符数据

#### 反爬虫对策
- 使用真实浏览器User-Agent
- 隐藏WebDriver特征
- 临时profile隔离
- 自动处理重定向

#### 错误处理
- 详细的错误提示
- 多策略自动降级
- 完善的异常捕获
- 版权状态检测

### 添加新的解析模式

在 `src/parser.py` 中添加新的正则表达式模式：

```python
self.data_patterns = [
    r'现有模式1',
    r'现有模式2',
    r'新的模式',  # 添加新模式
]
```

### 支持新的API端点

在 `src/api_fetcher.py` 中扩展API端点：

```python
api_endpoints = [
    f"现有端点1",
    f"现有端点2",
    f"新的端点",  # 添加新端点
]
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

## 📊 更新日志
### v3.0 (2026-06-20)
- ✅ 删除API接口支持
- ✅ 实现多策略智能获取
- ✅ 改进版权检测机制
- ✅ 删除30-60秒试听片段
- ✅ 自动监测剪切板自动下载
- ✅ 更稳定的解析逻辑
- ✅ 添加完整测试套件
- ✅ 优化代码结构
### v2.0 (2024-05-31)
- ✅ 添加API接口支持
- ✅ 实现多策略智能获取
- ✅ 改进版权检测机制
- ✅ 更详细的错误提示
- ✅ 更稳定的解析逻辑
- ✅ 添加完整测试套件
- ✅ 优化代码结构

### v1.0
- 基础HTML解析功能
- Selenium动态渲染
- MP4转MP3转换

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
