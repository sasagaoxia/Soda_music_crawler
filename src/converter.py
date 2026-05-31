# =============================================================================
# 文件: src/converter.py
# 功能: 音频格式转换
# =============================================================================

import os
import shutil
from pathlib import Path
from typing import Optional

from moviepy import AudioFileClip

from .config import Config


class AudioConverter:
    """音频转换器"""

    def __init__(self, output_format: str = None, bitrate: str = None):
        self.output_format = output_format or Config.OUTPUT_FORMAT
        self.bitrate = bitrate or Config.BITRATE

    def _build_output_path(self, input_file: str) -> Path:
        return Path(input_file).with_suffix(f'.{self.output_format}')

    def convert_audio(self, input_file: str, keep_original: bool = None) -> Optional[str]:
        """转换音频格式"""
        if keep_original is None:
            keep_original = Config.KEEP_ORIGINAL

        input_path = Path(input_file)
        output_path = self._build_output_path(input_file)

        try:
            print(f"🔄 开始转换音频格式: {input_path.name} -> {self.output_format.upper()}")

            audio_clip = AudioFileClip(str(input_path))
            try:
                audio_clip.write_audiofile(str(output_path), bitrate=self.bitrate, logger=None)
            except TypeError:
                # 兼容更老的 moviepy 接口
                audio_clip.write_audiofile(str(output_path))
            finally:
                audio_clip.close()

            print(f"✅ 音频转换完成: {output_path.name}")

            if not keep_original:
                os.remove(input_path)
                print(f"🗑️ 已删除原文件: {input_path.name}")

            return str(output_path)

        except Exception as e:
            print(f"❌ 音频转换失败: {e}")
            return self._fallback_rename(input_file, keep_original)

    def _fallback_rename(self, input_file: str, keep_original: bool) -> Optional[str]:
        """备用方案：直接复制并改后缀（非真正转码）"""
        input_path = Path(input_file)
        output_path = self._build_output_path(input_file)
        try:
            print("🔄 使用备用方案：重命名文件")
            shutil.copy2(input_path, output_path)

            if not keep_original:
                os.remove(input_path)
                print(f"🗑️ 已删除原文件: {input_path.name}")

            print(f"✅ 文件已重命名: {output_path.name}")
            print("⚠️ 注意：这只是重命名，不是真正的格式转换")
            return str(output_path)

        except Exception as e:
            print(f"❌ 备用方案失败: {e}")
            return None
    
    def batch_convert(self, input_dir: str) -> int:
        """批量转换目录中的MP4文件"""
        input_path = Path(input_dir)
        
        if not input_path.exists():
            print(f"❌ 目录不存在: {input_dir}")
            return 0
        
        # 查找所有MP4文件
        mp4_files = list(input_path.glob("*.mp4"))
        
        if not mp4_files:
            print(f"❌ 在 {input_dir} 中未找到MP4文件")
            return 0
        
        print(f"📁 找到 {len(mp4_files)} 个MP4文件")
        
        success_count = 0
        for i, mp4_file in enumerate(mp4_files, 1):
            print(f"\n--- 转换文件 {i}/{len(mp4_files)} ---")
            if self.convert_audio(str(mp4_file)):
                success_count += 1
        
        print(f"\n🎉 批量转换完成！成功: {success_count}/{len(mp4_files)}")
        return success_count