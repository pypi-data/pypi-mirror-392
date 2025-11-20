import ctypes.util
import platform
import socket
import wave
from pathlib import Path

import xiaozhi_sdk

sdk_dir = Path(xiaozhi_sdk.__file__).parent


def get_ip():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]


def get_wav_info(file_path):
    with wave.open(file_path, "rb") as wav_file:
        return wav_file.getframerate(), wav_file.getnchannels()


def read_audio_file(file_path, sample_rate, frame_duration):
    """
    读取音频文件并通过yield返回PCM流

    Args:
        file_path (str): 音频文件路径

    Yields:
        bytes: PCM音频数据块
    """
    frame_size = sample_rate * frame_duration // 1000
    with wave.open(file_path, "rb") as wav_file:
        while True:
            pcm = wav_file.readframes(frame_size)
            if not pcm:
                break
            yield pcm


def get_opus_path():
    system = platform.system().lower()
    machine = platform.machine().lower()

    # 检测架构
    if machine in ["x86_64", "amd64", "x64"]:
        arch = "x64"
    elif machine in ["arm64", "aarch64"]:
        arch = "arm64"
    else:
        # 默认使用x64作为回退
        arch = "x64"

    if system == "darwin":  # macOS
        return f"{sdk_dir}/file/opus/macos-{arch}-libopus.dylib"
    elif system == "windows":  # Windows
        return f"{sdk_dir}/file/opus/windows-opus.dll"
    elif system == "linux":  # Linux
        return f"{sdk_dir}/file/opus/linux-{arch}-libopus.so"


def setup_opus():
    def fake_find_library(name):
        if name == "opus":
            return get_opus_path()

    ctypes.util.find_library = fake_find_library
