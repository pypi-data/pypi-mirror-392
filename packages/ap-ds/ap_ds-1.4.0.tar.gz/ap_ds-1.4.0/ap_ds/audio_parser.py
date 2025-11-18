# audio_parser.py
import os
import ctypes
from ctypes import *

class AudioParser:
    def __init__(self, dll_path=None):
        """
        初始化音频解析器
        
        Args:
            dll_path: audio_parser.dll 路径，如果为None则在当前目录查找
        """
        # 获取当前脚本所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        if dll_path is None:
            # 首先尝试当前目录
            dll_path = os.path.join(current_dir, "audio_parser.dll")
        
        # 如果指定路径不存在，尝试在当前目录查找
        if not os.path.exists(dll_path):
            # 尝试当前目录
            alt_path = os.path.join(current_dir, "audio_parser.dll")
            if os.path.exists(alt_path):
                dll_path = alt_path
            else:
                # 最后尝试直接文件名（系统路径）
                dll_path = "audio_parser.dll"
        
        # 添加当前目录到DLL搜索路径
        if hasattr(os, 'add_dll_directory'):
            os.add_dll_directory(current_dir)
        
        # 设置DLL搜索路径
        os.environ['PATH'] = current_dir + os.pathsep + os.environ.get('PATH', '')
        
        try:
            self._dll = CDLL(dll_path)
            self._setup_prototypes()
        except Exception as e:
            raise RuntimeError(f"Failed to load audio parser DLL '{dll_path}': {str(e)}")
    
    def _setup_prototypes(self):
        """设置DLL函数原型"""
        # 通用音频时长获取
        self._dll.GetAudioDuration.argtypes = [c_char_p]
        self._dll.GetAudioDuration.restype = c_int
        
        # 各格式专用函数
        self._dll.GetOggDuration.argtypes = [c_char_p]
        self._dll.GetOggDuration.restype = c_int
        
        self._dll.GetFlacDuration.argtypes = [c_char_p]
        self._dll.GetFlacDuration.restype = c_int
        
        self._dll.GetMp3Duration.argtypes = [c_char_p]
        self._dll.GetMp3Duration.restype = c_int
        
        self._dll.GetWavDuration.argtypes = [c_char_p]
        self._dll.GetWavDuration.restype = c_int
        
    
    def get_audio_duration(self, file_path: str) -> int:
        """
        获取音频文件时长（秒）
        
        Args:
            file_path: 音频文件路径
            
        Returns:
            int: 时长（秒），失败返回0
        """
        if not os.path.exists(file_path):
            return 0
        
        try:
            file_path_bytes = file_path.encode('utf-8')
            duration = self._dll.GetAudioDuration(file_path_bytes)
            return max(0, duration)  # 确保非负
        except Exception:
            return 0
    
    def get_ogg_duration(self, file_path: str) -> int:
        """获取OGG文件时长"""
        if not os.path.exists(file_path):
            return 0
        
        try:
            file_path_bytes = file_path.encode('utf-8')
            duration = self._dll.GetOggDuration(file_path_bytes)
            return max(0, duration)
        except Exception:
            return 0
    
    def get_flac_duration(self, file_path: str) -> int:
        """获取FLAC文件时长"""
        if not os.path.exists(file_path):
            return 0
        
        try:
            file_path_bytes = file_path.encode('utf-8')
            duration = self._dll.GetFlacDuration(file_path_bytes)
            return max(0, duration)
        except Exception:
            return 0
    
    def get_mp3_duration(self, file_path: str) -> int:
        """获取MP3文件时长"""
        if not os.path.exists(file_path):
            return 0
        
        try:
            file_path_bytes = file_path.encode('utf-8')
            duration = self._dll.GetMp3Duration(file_path_bytes)
            return max(0, duration)
        except Exception:
            return 0
    
    def get_wav_duration(self, file_path: str) -> int:
        """获取WAV文件时长"""
        if not os.path.exists(file_path):
            return 0
        
        try:
            file_path_bytes = file_path.encode('utf-8')
            duration = self._dll.GetWavDuration(file_path_bytes)
            return max(0, duration)
        except Exception:
            return 0

    
    def get_duration_by_extension(self, file_path: str) -> int:
        """
        根据文件扩展名调用相应的专用函数
        
        Args:
            file_path: 音频文件路径
            
        Returns:
            int: 时长（秒），失败返回0
        """
        if not os.path.exists(file_path):
            return 0
        
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.mp3':
            return self.get_mp3_duration(file_path)
        elif ext == '.flac':
            return self.get_flac_duration(file_path)
        elif ext == '.ogg':
            return self.get_ogg_duration(file_path)
        elif ext == '.wav':
            return self.get_wav_duration(file_path)
        else:
            # 对于未知格式，使用通用函数
            return self.get_audio_duration(file_path)

# 全局实例
_audio_parser = None

def get_audio_parser():
    """获取全局音频解析器实例"""
    global _audio_parser
    if _audio_parser is None:
        _audio_parser = AudioParser()
    return _audio_parser
