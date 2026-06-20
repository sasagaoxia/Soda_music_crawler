# 汽水音乐分享链接下载工具 - 无 API 多线程剪贴板版

当前版本重点：

- 不调用 API 下载，只解析分享页面和页面内嵌音频地址。
- 多线程监听剪贴板，复制新的汽水音乐分享链接后自动加入下载队列。
- 下载时继续监听剪贴板，不用等上一首完成。
- Chrome/Selenium 默认无头模式运行，不弹白色空白页面。
- 下载完成后自动检测时长，60 秒以内疑似试听片段会自动删除。
- 支持完整分享文本，例如：`《歌曲名》@汽水音乐 https://qishui.douyin.com/s/xxxx/`。
- 支持自动 MP4 转 MP3。

> 仅用于下载你有权保存的音频内容。请尊重版权和平台规则。

## 快速运行

### 第一次使用

双击：

```text
01_安装依赖.bat
```

如果你喜欢命令行，也可以在项目目录执行：

```bat
py -m pip install -r requirements.txt
```

如果 `py` 不能用：

```bat
python -m pip install -r requirements.txt
```

### 推荐启动方式

双击：

```text
02_启动剪贴板监听.bat
```

然后在汽水音乐里复制分享链接，程序会自动识别并下载。

### 菜单启动

双击：

```text
03_启动菜单.bat
```

或命令行：

```bat
py main.py
```

## 菜单说明

```text
1. 手动输入链接，连续下载
2. 多线程监听剪贴板，复制/分享链接后自动下载
3. 只转换现有的MP4文件
0. 退出
```

推荐选择 `2`。

## 直接命令模式

```bat
py main.py --clipboard
py main.py --manual
py main.py --convert
```

## 配置位置

打开：

```text
src/config.py
```

常用配置：

```python
MAX_DOWNLOAD_WORKERS = 2
SHORT_AUDIO_THRESHOLD_SECONDS = 60
DELETE_SHORT_AUDIO = True
HEADLESS = True
HIDE_BROWSER_WINDOW = True
```

建议线程数先保持 2。线程太大可能同时启动多个 Chrome，电脑会卡。

## 常见问题

### pip 不是内部或外部命令

不要直接用 `pip install`，用：

```bat
py -m pip install -r requirements.txt
```

或双击 `01_安装依赖.bat`。

### 仍然弹白色页面

确认 `src/config.py` 里：

```python
HEADLESS = True
HIDE_BROWSER_WINDOW = True
```

### 下载到 60 秒就没了

这是当前设置：60 秒以内疑似试听片段会自动删除。要保留短音频，把：

```python
DELETE_SHORT_AUDIO = False
```

### 转换 MP3 失败

需要 Python 的 `moviepy`，并且本机 ffmpeg 可用。先执行：

```bat
py -m pip install -r requirements.txt
```

## 文件说明

```text
main.py                    程序入口
src/crawler.py             页面解析和下载核心
src/parser.py              页面内嵌数据和音频URL解析
src/url_extractor.py       分享文本/链接提取
src/audio_checker.py       音频时长检测和短音频删除
src/converter.py           MP4转MP3
downloads/                 下载目录
```
