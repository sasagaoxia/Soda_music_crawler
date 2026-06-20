# 汽水音乐爬虫 - 页面解析 + 多线程剪贴板版

本版按要求修改：

- 删除 API 下载流程：主程序不再调用 `music.douyin.com/api/...`、`douyin.com/aweme/v1/web/music/detail` 这类 API 接口下载。
- 保留分享页面解析：通过 Selenium 打开分享页，从页面内嵌数据和页面源码里查找音频地址。
- 多线程剪贴板监听：菜单 2 会持续监听剪贴板，复制新的汽水音乐分享链接后自动加入下载队列。
- 60 秒以内短音频自动删除：检测到小于等于 60 秒的音频会自动删除。
- 下载完成后继续监听：不需要再按 Enter 继续。

## 安装依赖

在项目目录打开 CMD：

```bat
py -m pip install -r requirements.txt
```

如果 `py` 不可用：

```bat
python -m pip install -r requirements.txt
```

## 运行

```bat
py main.py
```

或：

```bat
python main.py
```

## 推荐使用方式

选择菜单：

```text
2. 多线程监听剪贴板，复制/分享链接后自动下载
```

然后在汽水音乐里复制分享链接，程序会自动检测并加入下载队列。

## 修改线程数

打开：

```text
src/config.py
```

修改：

```python
MAX_DOWNLOAD_WORKERS = 2
```

建议 2 就够了。线程数越大，Chrome/Selenium 实例越多，电脑会更卡。

## 说明

本工具不包含登录绕过、签名破解、加密缓存破解。请只下载你有权保存的内容。
