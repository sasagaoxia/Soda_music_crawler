# =============================================================================
# 文件: src/audio_checker.py
# 功能: 音频时长检测，识别并自动删除 60 秒以内短音频/试听片段
# =============================================================================

import os
from pathlib import Path
from typing import Optional, Tuple

try:
    from moviepy import AudioFileClip
except Exception:  # moviepy/ffmpeg 不可用时不影响主程序下载
    AudioFileClip = None


class AudioChecker:
    """检测音频时长；发现疑似 60 秒以内短音频/试听片段时可自动删除。"""

    def __init__(self, short_threshold_seconds: float = 60.0, delete_short_audio: bool = True):
        # 60 秒以内短音频/试听片段经常会有 60 秒以内，阈值给一点余量
        self.short_threshold_seconds = short_threshold_seconds
        self.delete_short_audio = delete_short_audio

    def get_duration_seconds(self, file_path: str) -> Optional[float]:
        """返回音频时长，读取失败返回 None。"""
        if not file_path:
            return None

        path = Path(file_path)
        if not path.exists() or path.stat().st_size <= 0:
            return None

        if AudioFileClip is None:
            return None

        clip = None
        try:
            clip = AudioFileClip(str(path))
            duration = getattr(clip, "duration", None)
            if duration is None:
                return None
            return float(duration)
        except Exception:
            return None
        finally:
            try:
                if clip is not None:
                    clip.close()
            except Exception:
                pass

    def is_short_preview(self, file_path: str) -> Tuple[bool, Optional[float]]:
        """判断是否为疑似 60 秒以内短音频/试听片段。"""
        duration = self.get_duration_seconds(file_path)
        if duration is None:
            return False, None
        return duration <= self.short_threshold_seconds, duration

    def print_duration_warning(self, file_path: str, label: str = "音频") -> Optional[float]:
        """打印时长；如果疑似 60 秒以内短音频/试听片段，给出醒目提示。"""
        duration = self.get_duration_seconds(file_path)
        if duration is None:
            print("⚠️ 未能检测音频时长，可能是 moviepy/ffmpeg 不完整；文件已保留。")
            return None

        print(f"⏱️ {label}时长: {duration:.1f} 秒")

        if duration <= self.short_threshold_seconds:
            print("⚠️ 检测到音频时长小于等于 60 秒，可能只是试听片段/预览音频。")

        return duration

    def delete_file_and_info(self, file_path: str) -> bool:
        """删除音频文件和同名 .info.json 文件。"""
        deleted_any = False
        if not file_path:
            return False

        path = Path(file_path)
        related_files = [path, path.with_suffix('.info.json')]

        for item in related_files:
            try:
                if item.exists():
                    item.unlink()
                    print(f"🗑️ 已删除: {item.name}")
                    deleted_any = True
            except Exception as e:
                print(f"⚠️ 删除失败 {item}: {e}")

        return deleted_any

    def check_and_delete_if_short(self, file_path: str, label: str = "音频") -> Tuple[bool, Optional[float]]:
        """
        检测音频时长。
        返回: (是否已删除/应跳过, 时长)
        """
        duration = self.get_duration_seconds(file_path)
        if duration is None:
            print("⚠️ 未能检测音频时长，可能是 moviepy/ffmpeg 不完整；文件已保留。")
            return False, None

        print(f"⏱️ {label}时长: {duration:.1f} 秒")

        if duration <= self.short_threshold_seconds:
            print("⚠️ 检测到音频时长小于等于 60 秒，可能只是试听片段/预览音频。")
            if self.delete_short_audio:
                self.delete_file_and_info(file_path)
                print("✅ 已自动删除 60 秒以内短音频，继续下一首。")
                return True, duration
            print("⚠️ 当前配置为不删除短音频，文件已保留。")

        return False, duration
