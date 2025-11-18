import os
import sys
import time
import ctypes
import urllib.request  # Use Python's built-in library instead of external requests
from ctypes import *
from collections import defaultdict
import struct
from typing import *
try:
    try:
        from audio_parser import get_audio_parser
        AUDIO_PARSER_AVAILABLE = True
    except:
        from .audio_parser import get_audio_parser
        AUDIO_PARSER_AVAILABLE = True
except ImportError:
    AUDIO_PARSER_AVAILABLE = False
    print("Warning: audio_parser module not available, using fallback duration methods")

def download_sdl_libraries():
    """Download SDL2.dll and SDL2_mixer.dll to package directory"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Package directory: {current_dir}")
    
    files = [
        {
            "url": "https://dvsyun.top/ap_ds/download/SDL2",
            "expected_name": "SDL2.dll",
        },
        {
            "url": "https://dvsyun.top/ap_ds/download/SDL2_M", 
            "expected_name": "SDL2_mixer.dll",
        },
        {
            "url": "https://dvsyun.top/ap_ds/download/AParser_DLL",
            "expected_name": "audio_parser.dll",
        }
    ]
    
    for file_info in files:
        file_path = os.path.join(current_dir, file_info["expected_name"])
        if os.path.exists(file_path):
            print(f"{file_info['expected_name']} already exists")
            continue
            
        print(f"Downloading {file_info['expected_name']} to package directory...")
        try:
            with urllib.request.urlopen(file_info["url"], timeout=30) as response:
                content = response.read()
                print(f"Downloaded {len(content)} bytes")
                with open(file_path, 'wb') as f:
                    f.write(content)
                
                print(f"Successfully downloaded {file_info['expected_name']} to package directory")
                
        except Exception as e:
            print(f"Download failed: {str(e)}")
            continue

    print(f"Files in package directory after download: {os.listdir(current_dir)}")
# SDL2 and SDL2_mixer constants and structures

# SDL base type definitions
SDL_bool = c_int
SDL_TRUE = 1
SDL_FALSE = 0

# SDL initialization flags
SDL_INIT_TIMER = 0x00000001
SDL_INIT_AUDIO = 0x00000010
SDL_INIT_VIDEO = 0x00000020
SDL_INIT_JOYSTICK = 0x00000200
SDL_INIT_HAPTIC = 0x00001000
SDL_INIT_GAMECONTROLLER = 0x00002000
SDL_INIT_EVENTS = 0x00004000
SDL_INIT_EVERYTHING = (SDL_INIT_TIMER | SDL_INIT_AUDIO | SDL_INIT_VIDEO |
                      SDL_INIT_JOYSTICK | SDL_INIT_HAPTIC |
                      SDL_INIT_GAMECONTROLLER | SDL_INIT_EVENTS)

# SDL audio format constants
AUDIO_U8 = 0x0008
AUDIO_S8 = 0x8008
AUDIO_U16LSB = 0x0010
AUDIO_S16LSB = 0x8010
AUDIO_U16MSB = 0x1010
AUDIO_S16MSB = 0x9010
AUDIO_U16 = AUDIO_U16LSB
AUDIO_S16 = AUDIO_S16LSB
AUDIO_S32LSB = 0x8020
AUDIO_S32MSB = 0x9020
AUDIO_S32 = AUDIO_S32LSB
AUDIO_F32LSB = 0x8120
AUDIO_F32MSB = 0x9120
AUDIO_F32 = AUDIO_F32LSB

if sys.byteorder == 'little':
    AUDIO_U16SYS = AUDIO_U16LSB
    AUDIO_S16SYS = AUDIO_S16LSB
    AUDIO_S32SYS = AUDIO_S32LSB
    AUDIO_F32SYS = AUDIO_F32LSB
else:
    AUDIO_U16SYS = AUDIO_U16MSB
    AUDIO_S16SYS = AUDIO_S16MSB
    AUDIO_S32SYS = AUDIO_S32MSB
    AUDIO_F32SYS = AUDIO_F32MSB

MIX_DEFAULT_FORMAT = AUDIO_S16SYS

# SDL_mixer constants
MIX_INIT_FLAC = 0x00000001
MIX_INIT_MOD = 0x00000002
MIX_INIT_MP3 = 0x00000008
MIX_INIT_OGG = 0x00000010
MIX_INIT_MID = 0x00000020
MIX_INIT_OPUS = 0x00000040

# Channel control constants
MIX_CHANNEL_POST = -2
MIX_DEFAULT_CHANNELS = 2

# Music type constants
MUS_NONE = 0
MUS_CMD = 1
MUS_WAV = 2
MUS_MOD = 3
MUS_MID = 4
MUS_OGG = 5
MUS_MP3 = 6
MUS_FLAC = 7
MUS_OPUS = 8

# SDL structure definitions
class SDL_AudioSpec(ctypes.Structure):
    _fields_ = [
        ("freq", c_int),
        ("format", c_uint16),
        ("channels", c_uint8),
        ("silence", c_uint8),
        ("samples", c_uint16),
        ("padding", c_uint16),
        ("size", c_uint32),
        ("callback", c_void_p),
        ("userdata", c_void_p)
    ]

class Mix_Chunk(ctypes.Structure):
    _fields_ = [
        ("allocated", c_int),
        ("abuf", ctypes.POINTER(c_uint8)),
        ("alen", c_uint32),
        ("volume", c_uint8)
    ]
def check_sdl_libraries_exist(directory):
    """Check if SDL2 library files exist in the specified directory"""
    sdl2_path = os.path.join(directory, "SDL2.dll")
    sdl2_mixer_path = os.path.join(directory, "SDL2_mixer.dll")
    return os.path.exists(sdl2_path) and os.path.exists(sdl2_mixer_path)

def load_sdl2_from_directory(directory):
    """Load SDL2 libraries from the specified directory"""
    # Add DLL search path
    if hasattr(os, 'add_dll_directory'):
        os.add_dll_directory(directory)
    
    # Set DLL search path
    os.environ['PATH'] = directory + os.pathsep + os.environ.get('PATH', '')
    
    # Build full DLL paths
    sdl2_path = os.path.join(directory, "SDL2.dll")
    sdl2_mixer_path = os.path.join(directory, "SDL2_mixer.dll")
    
    if os.path.exists(sdl2_path) and os.path.exists(sdl2_mixer_path):
        _sdl_lib = CDLL(sdl2_path)
        _mix_lib = CDLL(sdl2_mixer_path)
        return _sdl_lib, _mix_lib
    else:
        raise FileNotFoundError(f"SDL2 libraries not found in {directory}")
def import_sdl2():
    """Main function: Import SDL2 libraries"""
    global _sdl_lib, _mix_lib  # 添加全局声明
    
    # Get current script directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    try:
        # First try to load from current directory
        if check_sdl_libraries_exist(current_dir):
            return load_sdl2_from_directory(current_dir)
        
        # If not found in current directory, try system path
        _sdl_lib = CDLL("SDL2.dll")
        _mix_lib = CDLL("SDL2_mixer.dll")
        return _sdl_lib, _mix_lib
        
    except Exception as e:
        # If loading fails, download library files
        print("SDL2 libraries not found, downloading...")
        download_sdl_libraries()
        
        # After download, try to load from current directory again
        if check_sdl_libraries_exist(current_dir):
            return load_sdl2_from_directory(current_dir)
        else:
            print(f"Files in current directory: {os.listdir(current_dir)}")
            raise ImportError(
                f"Failed to load SDL libraries after download!\n"
                f"Current directory: {current_dir}\n"
                f"DLL search path: {os.environ.get('PATH', '')}\n"
                f"Error details: {str(e)}"
            )
# Usage example
try:
    _sdl_lib, _mix_lib = import_sdl2()
except ImportError as e:
    print(f"Failed to load SDL2: {e}")    
# SDL function definitions
def SDL_Init(flags):
    return _sdl_lib.SDL_Init(flags)

def SDL_InitSubSystem(flags):
    return _sdl_lib.SDL_InitSubSystem(flags)

def SDL_Quit():
    _sdl_lib.SDL_Quit()

def SDL_QuitSubSystem(flags):
    _sdl_lib.SDL_QuitSubSystem(flags)

def SDL_WasInit(flags):
    return _sdl_lib.SDL_WasInit(flags)

def SDL_GetError():
    return _sdl_lib.SDL_GetError()

# SDL_mixer function definitions
def Mix_OpenAudio(frequency, format, channels, chunksize):
    return _mix_lib.Mix_OpenAudio(frequency, format, channels, chunksize)

def Mix_CloseAudio():
    _mix_lib.Mix_CloseAudio()

def Mix_QuerySpec(frequency, format, channels):
    return _mix_lib.Mix_QuerySpec(ctypes.byref(frequency),
                                ctypes.byref(format),
                                ctypes.byref(channels))

def Mix_LoadWAV(file):
    if isinstance(file, str):
        file = file.encode('utf-8')
    elif isinstance(file, bytes):
        pass
    else:
        file = str(file).encode('utf-8')
    
    return _mix_lib.Mix_LoadWAV_RW(_sdl_lib.SDL_RWFromFile(file, b"rb"), 1)

def Mix_LoadMUS(file: Union[str, bytes]) -> Any:
    if isinstance(file, str):
        file = file.encode('utf-8')
    elif isinstance(file, bytes):
        pass
    else:
        file = str(file).encode('utf-8')
    
    return _mix_lib.Mix_LoadMUS_RW(_sdl_lib.SDL_RWFromFile(file, b"rb"), 1)

def Mix_FreeChunk(chunk):
    _mix_lib.Mix_FreeChunk(chunk)

def Mix_FreeMusic(music):
    _mix_lib.Mix_FreeMusic(music)

def Mix_PlayChannel(channel, chunk, loops):
    return _mix_lib.Mix_PlayChannel(channel, chunk, loops)

def Mix_PlayMusic(music, loops):
    return _mix_lib.Mix_PlayMusic(music, loops)

def Mix_Pause(channel):
    _mix_lib.Mix_Pause(channel)

def Mix_PauseMusic():
    _mix_lib.Mix_PauseMusic()

def Mix_Resume(channel):
    _mix_lib.Mix_Resume(channel)

def Mix_ResumeMusic():
    _mix_lib.Mix_ResumeMusic()

def Mix_HaltChannel(channel):
    return _mix_lib.Mix_HaltChannel(channel)

def Mix_HaltMusic():
    return _mix_lib.Mix_HaltMusic()

def Mix_SetMusicPosition(position):
    return _mix_lib.Mix_SetMusicPosition(position)

def Mix_MusicDuration(music):
    return _mix_lib.Mix_MusicDuration(music)

def Mix_Volume(channel, volume):
    return _mix_lib.Mix_Volume(channel, volume)

def Mix_VolumeMusic(volume):
    return _mix_lib.Mix_VolumeMusic(volume)

def Mix_AllocateChannels(numchans):
    return _mix_lib.Mix_AllocateChannels(numchans)

def Mix_GetMusicType(music):
    return _mix_lib.Mix_GetMusicType(music)

def Mix_FadingMusic():
    return _mix_lib.Mix_FadingMusic()

def Mix_FadeInMusic(music, loops, ms):
    return _mix_lib.Mix_FadeInMusic(music, loops, ms)

def Mix_FadeOutMusic(ms):
    return _mix_lib.Mix_FadeOutMusic(ms)

def Mix_FadeInChannel(channel, chunk, loops, ms):
    return _mix_lib.Mix_FadeInChannel(channel, chunk, loops, ms)

def Mix_FadeOutChannel(channel, ms):
    return _mix_lib.Mix_FadeOutChannel(channel, ms)

def Mix_Playing(channel):
    return _mix_lib.Mix_Playing(channel)

def Mix_PlayingMusic():
    return _mix_lib.Mix_PlayingMusic()

def Mix_Paused(channel):
    return _mix_lib.Mix_Paused(channel)

def Mix_PausedMusic():
    return _mix_lib.Mix_PausedMusic()

def Mix_SetPanning(channel, left, right):
    return _mix_lib.Mix_SetPanning(channel, left, right)

def Mix_SetDistance(channel, distance):
    return _mix_lib.Mix_SetDistance(channel, distance)

def Mix_SetPosition(channel, angle, distance):
    return _mix_lib.Mix_SetPosition(channel, angle, distance)

def Mix_SetReverseStereo(channel, flip):
    return _mix_lib.Mix_SetReverseStereo(channel, flip)

# Set up function prototypes for Windows
if sys.platform.startswith('win32'):
    # SDL function prototypes
    _sdl_lib.SDL_Init.argtypes = [c_uint32]
    _sdl_lib.SDL_Init.restype = c_int
    
    _sdl_lib.SDL_InitSubSystem.argtypes = [c_uint32]
    _sdl_lib.SDL_InitSubSystem.restype = c_int
    
    _sdl_lib.SDL_Quit.argtypes = []
    _sdl_lib.SDL_Quit.restype = None
    
    _sdl_lib.SDL_QuitSubSystem.argtypes = [c_uint32]
    _sdl_lib.SDL_QuitSubSystem.restype = None
    
    _sdl_lib.SDL_WasInit.argtypes = [c_uint32]
    _sdl_lib.SDL_WasInit.restype = c_uint32
    
    _sdl_lib.SDL_GetError.argtypes = []
    _sdl_lib.SDL_GetError.restype = c_char_p
    
    _sdl_lib.SDL_RWFromFile.argtypes = [c_char_p, c_char_p]
    _sdl_lib.SDL_RWFromFile.restype = c_void_p
    
    _sdl_lib.SDL_Delay.argtypes = [c_uint32]
    _sdl_lib.SDL_Delay.restype = None

    # SDL_mixer function prototypes
    _mix_lib.Mix_OpenAudio.argtypes = [c_int, c_uint16, c_int, c_int]
    _mix_lib.Mix_OpenAudio.restype = c_int
    
    _mix_lib.Mix_CloseAudio.argtypes = []
    _mix_lib.Mix_CloseAudio.restype = None
    
    _mix_lib.Mix_QuerySpec.argtypes = [ctypes.POINTER(c_int),
                                     ctypes.POINTER(c_uint16),
                                     ctypes.POINTER(c_int)]
    _mix_lib.Mix_QuerySpec.restype = c_int
    
    _mix_lib.Mix_LoadWAV_RW.argtypes = [c_void_p, c_int]
    _mix_lib.Mix_LoadWAV_RW.restype = ctypes.POINTER(Mix_Chunk)
    
    _mix_lib.Mix_LoadMUS_RW.argtypes = [c_void_p, c_int]
    _mix_lib.Mix_LoadMUS_RW.restype = c_void_p
    
    _mix_lib.Mix_FreeChunk.argtypes = [ctypes.POINTER(Mix_Chunk)]
    _mix_lib.Mix_FreeChunk.restype = None
    
    _mix_lib.Mix_FreeMusic.argtypes = [c_void_p]
    _mix_lib.Mix_FreeMusic.restype = None
    
    _mix_lib.Mix_PlayChannel.argtypes = [c_int, ctypes.POINTER(Mix_Chunk), c_int]
    _mix_lib.Mix_PlayChannel.restype = c_int
    
    _mix_lib.Mix_PlayMusic.argtypes = [c_void_p, c_int]
    _mix_lib.Mix_PlayMusic.restype = c_int
    
    _mix_lib.Mix_Pause.argtypes = [c_int]
    _mix_lib.Mix_Pause.restype = None
    
    _mix_lib.Mix_PauseMusic.argtypes = []
    _mix_lib.Mix_PauseMusic.restype = None
    
    _mix_lib.Mix_Resume.argtypes = [c_int]
    _mix_lib.Mix_Resume.restype = None
    
    _mix_lib.Mix_ResumeMusic.argtypes = []
    _mix_lib.Mix_ResumeMusic.restype = None
    
    _mix_lib.Mix_HaltChannel.argtypes = [c_int]
    _mix_lib.Mix_HaltChannel.restype = c_int
    
    _mix_lib.Mix_HaltMusic.argtypes = []
    _mix_lib.Mix_HaltMusic.restype = c_int
    
    _mix_lib.Mix_SetMusicPosition.argtypes = [c_double]
    _mix_lib.Mix_SetMusicPosition.restype = c_int
    
    if hasattr(_mix_lib, 'Mix_MusicDuration'):
        _mix_lib.Mix_MusicDuration.argtypes = [c_void_p]
        _mix_lib.Mix_MusicDuration.restype = c_float
    
    _mix_lib.Mix_Volume.argtypes = [c_int, c_int]
    _mix_lib.Mix_Volume.restype = c_int
    
    _mix_lib.Mix_VolumeMusic.argtypes = [c_int]
    _mix_lib.Mix_VolumeMusic.restype = c_int
    
    _mix_lib.Mix_AllocateChannels.argtypes = [c_int]
    _mix_lib.Mix_AllocateChannels.restype = c_int
    
    _mix_lib.Mix_GetMusicType.argtypes = [c_void_p]
    _mix_lib.Mix_GetMusicType.restype = c_int
    
    _mix_lib.Mix_FadingMusic.argtypes = []
    _mix_lib.Mix_FadingMusic.restype = c_int
    
    _mix_lib.Mix_FadeInMusic.argtypes = [c_void_p, c_int, c_int]
    _mix_lib.Mix_FadeInMusic.restype = c_int
    
    _mix_lib.Mix_FadeOutMusic.argtypes = [c_int]
    _mix_lib.Mix_FadeOutMusic.restype = c_int
    
    _mix_lib.Mix_FadeInChannel.argtypes = [c_int, ctypes.POINTER(Mix_Chunk), c_int, c_int]
    _mix_lib.Mix_FadeInChannel.restype = c_int
    
    _mix_lib.Mix_FadeOutChannel.argtypes = [c_int, c_int]
    _mix_lib.Mix_FadeOutChannel.restype = c_int
    
    _mix_lib.Mix_Playing.argtypes = [c_int]
    _mix_lib.Mix_Playing.restype = c_int
    
    _mix_lib.Mix_PlayingMusic.argtypes = []
    _mix_lib.Mix_PlayingMusic.restype = c_int
    
    _mix_lib.Mix_Paused.argtypes = [c_int]
    _mix_lib.Mix_Paused.restype = c_int
    
    _mix_lib.Mix_PausedMusic.argtypes = []
    _mix_lib.Mix_PausedMusic.restype = c_int
    
    _mix_lib.Mix_SetPanning.argtypes = [c_int, c_uint8, c_uint8]
    _mix_lib.Mix_SetPanning.restype = c_int
    
    _mix_lib.Mix_SetDistance.argtypes = [c_int, c_uint8]
    _mix_lib.Mix_SetDistance.restype = c_int
    
    _mix_lib.Mix_SetPosition.argtypes = [c_int, c_uint16, c_uint8]
    _mix_lib.Mix_SetPosition.restype = c_int
    
    _mix_lib.Mix_SetReverseStereo.argtypes = [c_int, c_int]
    _mix_lib.Mix_SetReverseStereo.restype = c_int

# Set up SDL_Delay parameters and return type
_sdl_lib.SDL_Delay.argtypes = [ctypes.c_uint32]
_sdl_lib.SDL_Delay.restype = None

class AudioLibrary:
    def __init__(self, frequency: int = 44100, format: int = MIX_DEFAULT_FORMAT,
                 channels: int = 2, chunksize: int = 2048):
        """Initialize the audio library"""
        if SDL_Init(SDL_INIT_AUDIO) != 0:
            raise RuntimeError(f"SDL initialization failed: {SDL_GetError().decode()}")
        
        if Mix_OpenAudio(frequency, format, channels, chunksize) != 0:
            raise RuntimeError(f"Mixer initialization failed: {SDL_GetError().decode()}")
        
        # Audio state tracking
        self._audio_cache = {}  # File path -> Mix_Chunk
        self._music_cache = {}  # File path -> Mix_Music
        self._channel_info = {}  # Channel ID -> Playback info
        self._aid_to_filepath = {}  # Store AID to file mapping
        self._aid_counter = 0
        self._sample_rate = frequency
        self._format = format
        self._channels = channels

    def Delay(self, ms):
        _sdl_lib.SDL_Delay(ms)

    # Core playback functionality ======================================================
    def play_audio(self, aid: int) -> None:
        """Play/resume audio with specified AID"""
        channel = self._find_channel_by_aid(aid)
        if channel is None:
            raise ValueError("Invalid AID")
        
        info = self._channel_info[channel]
        if info['paused']:
            if info['is_music']:
                Mix_ResumeMusic()
            else:
                Mix_Resume(channel)
            info['paused'] = False
            info['start_time'] = time.time() - info['paused_position']

    def play_from_memory(self, file_path: str, loops: int = 0, start_pos: float = 0.0) -> int:
        """Play audio from memory cache, return AID"""
        self._aid_counter += 1
        aid = self._aid_counter
        
        # Music file handling
        if file_path in self._music_cache:
            if Mix_PlayMusic(self._music_cache[file_path], loops) != 0:
                raise RuntimeError(f"Failed to play music: {SDL_GetError().decode()}")
            channel = -1
        # Sound effect handling
        elif file_path in self._audio_cache:
            channel = Mix_PlayChannel(-1, self._audio_cache[file_path], loops)
            if channel == -1:
                raise RuntimeError(f"Failed to play audio: {SDL_GetError().decode()}")
        else:
            raise ValueError("Audio not loaded in memory")
        
        # Record playback information
        self._channel_info[channel] = {
            'aid': aid,
            'start_time': time.time() - start_pos,
            'paused': False,
            'file_path': file_path,
            'is_music': channel == -1,
            'loops': loops
        }
        
        # Seek to specified position
        if start_pos > 0:
            self._seek_audio(channel, start_pos)
        self._aid_to_filepath[aid] = file_path  # Save mapping
        return aid

    def play_from_file(self, file_path: str, loops: int = 0, start_pos: float = 0.0) -> int:
        """Play audio directly from file, return AID"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Audio file not found: {file_path}")
        
        self._aid_counter += 1
        aid = self._aid_counter
        
        # Music file handling
        if file_path.lower().endswith(('.mp3', '.ogg', '.flac')):
            music = Mix_LoadMUS(file_path.encode())
            if not music:
                raise RuntimeError(f"Failed to load music file: {SDL_GetError().decode()}")
            
            if Mix_PlayMusic(music, loops) != 0:
                Mix_FreeMusic(music)
                raise RuntimeError(f"Failed to play music: {SDL_GetError().decode()}")
            
            channel = -1
            self._music_cache[file_path] = music  # Cache music object
        # Sound effect handling
        else:
            audio = Mix_LoadWAV(file_path.encode())
            if not audio:
                raise RuntimeError(f"Failed to load audio file: {SDL_GetError().decode()}")
            
            channel = Mix_PlayChannel(-1, audio, loops)
            if channel == -1:
                Mix_FreeChunk(audio)
                raise RuntimeError(f"Failed to play audio: {SDL_GetError().decode()}")
            
            self._audio_cache[file_path] = audio  # Cache audio object
        
        # Record playback information
        self._channel_info[channel] = {
            'aid': aid,
            'start_time': time.time() - start_pos,
            'paused': False,
            'file_path': file_path,
            'is_music': channel == -1,
            'loops': loops
        }
        
        # Seek to specified position
        if start_pos > 0:
            self._seek_audio(channel, start_pos)
        self._aid_to_filepath[aid] = file_path  # Save mapping
        return aid

    def new_aid(self, file_path: str) -> int:
        """Load file into memory and return AID without playing
    
        Args:
            file_path: Path to audio file
        
        Returns:
            int: Audio ID (AID)
        
        Raises:
            FileNotFoundError: If file doesn't exist
            RuntimeError: If loading fails
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Audio file not found: {file_path}")
    
        self._aid_counter += 1
        aid = self._aid_counter
    
        # Music file handling
        if file_path.lower().endswith(('.mp3', '.ogg', '.flac')):
            if file_path not in self._music_cache:
                music = Mix_LoadMUS(file_path.encode())
                if not music:
                    raise RuntimeError(f"Failed to load music file: {SDL_GetError().decode()}")
                self._music_cache[file_path] = music
    
        # Sound effect handling
        else:
            if file_path not in self._audio_cache:
                audio = Mix_LoadWAV(file_path.encode())
                if not audio:
                    raise RuntimeError(f"Failed to load audio file: {SDL_GetError().decode()}")
                self._audio_cache[file_path] = audio
    
        # Save AID to file path mapping
        self._aid_to_filepath[aid] = file_path
    
        return aid

    # Control functionality ======================================================
    
    def pause_audio(self, aid: int) -> None:
        """Pause audio with specified AID"""
        channel = self._find_channel_by_aid(aid)
        if channel is None:
            raise ValueError("Invalid AID")
        
        info = self._channel_info[channel]
        if not info['paused']:
            if info['is_music']:
                Mix_PauseMusic()
            else:
                Mix_Pause(channel)
            info['paused'] = True
            info['paused_position'] = time.time() - info['start_time']

    def stop_audio(self, aid: int) -> float:
        """Stop playback and return played duration"""
        channel = self._find_channel_by_aid(aid)
        if channel is None:
            return 0.0
        
        info = self._channel_info[channel]
        played_time = time.time() - info['start_time'] if not info['paused'] else info['paused_position']
        
        if info['is_music']:
            Mix_HaltMusic()
        else:
            Mix_HaltChannel(channel)
        
        del self._channel_info[channel]
        return played_time

    def seek_audio(self, aid: int, position: float) -> None:
        """Seek to specified position (seconds)"""
        channel = self._find_channel_by_aid(aid)
        if channel is not None:
            self._seek_audio(channel, position)

    def _seek_audio(self, channel: int, position: float) -> None:
        """Internal method: seek audio"""
        info = self._channel_info.get(channel)
        if not info:
            return
        
        # Music seeking
        if info['is_music']:
            Mix_HaltMusic()
            music = Mix_LoadMUS(info['file_path'].encode())
            if Mix_PlayMusic(music, info['loops']) != 0:
                Mix_FreeMusic(music)
                return
            
            if hasattr(Mix_SetMusicPosition, '__call__'):
                Mix_SetMusicPosition(position)
            
            self._music_cache[info['file_path']] = music
            self._channel_info[channel] = {
                **info,
                'start_time': time.time() - position,
                'paused': False
            }
        # Sound effect seeking
        else:
            Mix_HaltChannel(channel)
            audio = self._audio_cache.get(info['file_path'])
            new_channel = Mix_PlayChannel(-1, audio, info['loops'])
            
            self._channel_info[new_channel] = {
                **info,
                'start_time': time.time() - position,
                'paused': False
            }
            del self._channel_info[channel]


    def set_volume(self, aid: int, volume: int) -> bool:
        """Set audio volume
    
        Args:
            aid: Audio ID
            volume: Volume value (0-128)
    
        Returns:
            bool: Whether the setting was successful
        """
        channel = self._find_channel_by_aid(aid)
        if channel is None:
            return False
    
        info = self._channel_info[channel]
        volume = max(0, min(128, volume))  # Ensure volume is within 0-128 range
    
        if info['is_music']:
            return Mix_VolumeMusic(volume) == volume
        else:
            return Mix_Volume(channel, volume) == volume

    def get_volume(self, aid: int) -> int:
        """Get current audio volume
    
        Args:
            aid: Audio ID
    
        Returns:
            int: Current volume value (0-128)
        """
        channel = self._find_channel_by_aid(aid)
        if channel is None:
            return 0
    
        info = self._channel_info[channel]
        if info['is_music']:
            return Mix_VolumeMusic(-1)  # -1 means get without setting
        else:
            return Mix_Volume(channel, -1)  # -1 means get without setting


    # Helper methods ======================================================
    
    def _find_channel_by_aid(self, aid: int) -> Optional[int]:
        """Find channel by AID"""
        for channel, info in self._channel_info.items():
            if info['aid'] == aid:
                return channel
        return None

    
    def _get_file_path_by_aid(self, aid: int) -> Optional[str]:
        """Get file path by AID"""
        for info in self._channel_info.values():
            if info['aid'] == aid:
                return info['file_path']
        return None
    

    def get_audio_duration(self, source: Union[str, int], is_file: bool = False) -> Union[int, Tuple[int, str]]:
        """
        Get the duration of an audio file in seconds
        
        This method supports both file paths and AID (Audio ID) as input sources.
        It automatically detects the file format and uses the appropriate parser
        to calculate the duration accurately.
        
        Args:
            source: Either a file path string or an integer AID
            is_file: If True, treats source as file path; if False, as AID
            
        Returns:
            Union[int, Tuple[int, str]]: 
                - On success: Integer duration in seconds (rounded)
                - On failure: Tuple (0, error_message_string)
                
        Examples:
            >>> # Get duration by file path
            >>> duration = lib.get_audio_duration("audio/song.mp3", is_file=True)
            >>> # Get duration by AID
            >>> duration = lib.get_audio_duration(123, is_file=False)
        """
        try:
            # Case 1: Get duration by AID (Audio ID)
            if not is_file and isinstance(source, int):
                if source not in self._aid_to_filepath:
                    return (0, f"Invalid AID: {source}")
                
                file_path = self._aid_to_filepath[source]
                return self._get_duration_by_filepath(file_path)
            
            # Case 2: Get duration by file path
            file_path = str(source)
            return self._get_duration_by_filepath(file_path)
            
        except Exception as e:
            return (0, f"Error getting audio duration: {str(e)}")

    def _get_duration_by_filepath(self, file_path: str) -> Union[int, Tuple[int, str]]:
        try:
            if not os.path.exists(file_path):
                return (0, f"File not found: {file_path}")
        
            if AUDIO_PARSER_AVAILABLE:
                try:
                    parser = get_audio_parser()
                    duration = parser.get_audio_duration(file_path)
                    if duration > 0:
                        return duration
                    file_ext = os.path.splitext(file_path)[1].lower()
                    if file_ext == '.mp3':
                        duration = parser.get_mp3_duration(file_path)
                    elif file_ext == '.ogg':
                        duration = parser.get_ogg_duration(file_path)
                    elif file_ext == '.flac':
                        duration = parser.get_flac_duration(file_path)
                    elif file_ext == '.wav':
                        duration = parser.get_wav_duration(file_path)
                    
                    if duration > 0:
                        return duration
                except Exception as e:
                    print(f"Audio parser DLL error: {e}")
            
        except Exception as e:
            return (0, f"Error calculating audio duration: {str(e)}")
    
    def simple_mp3_duration_estimation(self, filename: str) -> float:
        """
        Estimate MP3 duration based on file size and common bitrates
        
        This provides a fallback when frame-by-frame parsing fails.
        
        Args:
            filename: Path to the MP3 file
            
        Returns:
            float: Estimated duration in seconds, 0 on error
        """
        try:
            file_size = os.path.getsize(filename)
            
            # Estimate audio data size (subtract possible ID3 tag)
            audio_data_size = max(file_size - 2048, file_size * 0.98)
            
            # Estimate bitrate based on file size
            if file_size < 2 * 1024 * 1024:  # < 2MB
                bitrate = 128
            elif file_size < 5 * 1024 * 1024:  # < 5MB
                bitrate = 192
            elif file_size < 10 * 1024 * 1024:  # < 10MB
                bitrate = 256
            else:
                bitrate = 320
            
            # Calculate duration: (file_size_bytes * 8) / (bitrate_bps)
            duration = (audio_data_size * 8) / (bitrate * 1000)
            return duration
            
        except Exception as e:
            print(f"MP3 duration estimation error: {e}")
            return 0
    def _get_sample_rate(self) -> int:
        """Get actual sample rate (default 44100)"""
        return 44100  # Can be adjusted based on actual configuration

    def _get_channels(self) -> int:
        """Get actual channel count (default 2)"""
        return 2  # Can be adjusted based on actual configuration

    def _get_aid_for_audio(self, file_path: str) -> Optional[int]:
        """Find corresponding AID by file path"""
        for channel, info in self._channel_info.items():
            if info.get('file_path') == file_path and not info.get('is_music', True):
                return info.get('aid')
        return None

    def _get_aid_for_music(self, file_path: str) -> Optional[int]:
        """Find corresponding AID by music file path"""
        for channel, info in self._channel_info.items():
            if info.get('file_path') == file_path and info.get('is_music', False):
                return info.get('aid')
        return None
    
    def _get_playing_duration(self, aid: int) -> float:
        """Get total duration of playing audio"""
        file_path = self._get_file_path_by_aid(aid)
        return self._get_file_duration(file_path) if file_path else 0.0
    def _get_file_duration(self, file_path: str) -> float:
        result = self._get_duration_by_filepath(file_path)
        if isinstance(result, tuple):
            return 0.0  
        return float(result)

    # Resource management ======================================================
    
    def clear_memory_cache(self) -> None:
        """Clear memory cache"""
        for audio in self._audio_cache.values():
            if audio:
                Mix_FreeChunk(audio)
        for music in self._music_cache.values():
            if music:
                Mix_FreeMusic(music)
        self._audio_cache.clear()
        self._music_cache.clear()

    def __del__(self):
        """Clean up resources"""
        self.clear_memory_cache()
        Mix_CloseAudio()
        SDL_Quit()
