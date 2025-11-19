import win32api
import win32con
import win32gui
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import time
import win32com.client
import psutil
import re
from typing import Optional, Dict, Any

class MediaController:
    def __init__(self):
        self.shell = win32com.client.Dispatch("WScript.Shell")
        self.supported_players = {
            'Spotify': self._get_spotify_info,
            'MusicBee': self._get_musicbee_info,
            'AIMP': self._get_aimp_info,
            'foobar2000': self._get_foobar2000_info,
            'VLC': self._get_vlc_info,
            'Windows Media Player': self._get_wmp_info,
            'iTunes': self._get_itunes_info
        }

    def volume_up(self):
        """增加系统音量"""
        win32api.keybd_event(win32con.VK_VOLUME_UP, 0)
        time.sleep(0.1)

    def volume_down(self):
        """降低系统音量"""
        win32api.keybd_event(win32con.VK_VOLUME_DOWN, 0)
        time.sleep(0.1)

    def volume_mute(self):
        """静音/取消静音"""
        win32api.keybd_event(win32con.VK_VOLUME_MUTE, 0)
        time.sleep(0.1)

    def get_volume(self):
        """获取当前系统音量（0-100）"""
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        return int(volume.GetMasterVolumeLevelScalar() * 100)

    def set_volume(self, volume_level):
        """设置系统音量（0-100）"""
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMasterVolumeLevelScalar(volume_level / 100, None)

    def play_pause(self):
        """播放/暂停"""
        self.shell.SendKeys("{MEDIA_PLAY_PAUSE}")

    def next_track(self):
        """下一首"""
        self.shell.SendKeys("{MEDIA_NEXT_TRACK}")

    def previous_track(self):
        """上一首"""
        self.shell.SendKeys("{MEDIA_PREV_TRACK}")

    def get_active_player(self) -> Optional[str]:
        """获取当前活动的媒体播放器"""
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] in self.supported_players:
                    return proc.info['name']
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return None

    def get_current_track_info(self) -> Optional[Dict[str, Any]]:
        """获取当前播放的音轨信息"""
        player = self.get_active_player()
        if player and player in self.supported_players:
            return self.supported_players[player]()
        return None

    def _format_time(self, seconds: float) -> str:
        """将秒数格式化为 MM:SS 或 HH:MM:SS"""
        minutes, seconds = divmod(int(seconds), 60)
        hours, minutes = divmod(minutes, 60)
        if hours:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return f"{minutes:02d}:{seconds:02d}"

    def _get_spotify_info(self) -> Optional[Dict[str, Any]]:
        """获取Spotify当前播放信息"""
        try:
            spotify = win32com.client.Dispatch("Spotify.Application")
            if spotify.PlayerState == 1:  # 正在播放
                current_time = spotify.GetPosition()
                duration = spotify.CurrentTrack.Duration
                return {
                    'artist': spotify.CurrentTrack.Artist,
                    'title': spotify.CurrentTrack.Name,
                    'album': spotify.CurrentTrack.Album,
                    'duration': duration,
                    'duration_str': self._format_time(duration),
                    'current_time': current_time,
                    'current_time_str': self._format_time(current_time),
                    'progress': (current_time / duration * 100) if duration > 0 else 0,
                    'player': 'Spotify'
                }
        except:
            return None

    def _get_musicbee_info(self) -> Optional[Dict[str, Any]]:
        """获取MusicBee当前播放信息"""
        try:
            hwnd = win32gui.FindWindow("MusicBeeWindowClass", None)
            if hwnd:
                win32gui.SetForegroundWindow(hwnd)
                title = win32gui.GetWindowText(hwnd)
                # 解析窗口标题获取歌曲信息
                match = re.match(r'(.+?) - (.+?) - MusicBee', title)
                if match:
                    # 获取播放进度信息
                    progress_hwnd = win32gui.FindWindowEx(hwnd, 0, "msctls_progress32", None)
                    progress = 0
                    current_time = 0
                    duration = 0
                    if progress_hwnd:
                        progress = win32gui.SendMessage(progress_hwnd, win32con.PBM_GETPOS, 0, 0)
                        # 获取时间信息
                        time_hwnd = win32gui.FindWindowEx(hwnd, 0, "Static", None)
                        if time_hwnd:
                            time_text = win32gui.GetWindowText(time_hwnd)
                            time_match = re.match(r'(\d+:\d+|\d+:\d+:\d+) / (\d+:\d+|\d+:\d+:\d+)', time_text)
                            if time_match:
                                current_time = self._parse_time(time_match.group(1))
                                duration = self._parse_time(time_match.group(2))
                    return {
                        'artist': match.group(1),
                        'title': match.group(2),
                        'duration': duration,
                        'duration_str': self._format_time(duration),
                        'current_time': current_time,
                        'current_time_str': self._format_time(current_time),
                        'progress': progress,
                        'player': 'MusicBee'
                    }
        except:
            return None

    def _get_aimp_info(self) -> Optional[Dict[str, Any]]:
        """获取AIMP当前播放信息"""
        try:
            hwnd = win32gui.FindWindow("AIMP2_RemoteInfo", None)
            if hwnd:
                text = win32gui.GetWindowText(hwnd)
                # 解析窗口标题获取歌曲信息
                match = re.match(r'(.+?) - (.+?) - AIMP', text)
                if match:
                    # 获取播放进度信息
                    progress_hwnd = win32gui.FindWindowEx(hwnd, 0, "AIMP2_RemoteProgressBar", None)
                    progress = 0
                    current_time = 0
                    duration = 0
                    if progress_hwnd:
                        progress = win32gui.SendMessage(progress_hwnd, win32con.PBM_GETPOS, 0, 0)
                        # 获取时间信息
                        time_hwnd = win32gui.FindWindowEx(hwnd, 0, "AIMP2_RemoteTime", None)
                        if time_hwnd:
                            time_text = win32gui.GetWindowText(time_hwnd)
                            time_match = re.match(r'(\d+:\d+|\d+:\d+:\d+) / (\d+:\d+|\d+:\d+:\d+)', time_text)
                            if time_match:
                                current_time = self._parse_time(time_match.group(1))
                                duration = self._parse_time(time_match.group(2))
                    return {
                        'artist': match.group(1),
                        'title': match.group(2),
                        'duration': duration,
                        'duration_str': self._format_time(duration),
                        'current_time': current_time,
                        'current_time_str': self._format_time(current_time),
                        'progress': progress,
                        'player': 'AIMP'
                    }
        except:
            return None

    def _get_foobar2000_info(self) -> Optional[Dict[str, Any]]:
        """获取foobar2000当前播放信息"""
        try:
            hwnd = win32gui.FindWindow("{DA7CD0DE-5202-40E2-85D2-E48F387046C3}", None)
            if hwnd:
                title = win32gui.GetWindowText(hwnd)
                # 解析窗口标题获取歌曲信息
                match = re.match(r'(.+?) - (.+?) - foobar2000', title)
                if match:
                    # 获取播放进度信息
                    progress_hwnd = win32gui.FindWindowEx(hwnd, 0, "msctls_progress32", None)
                    progress = 0
                    current_time = 0
                    duration = 0
                    if progress_hwnd:
                        progress = win32gui.SendMessage(progress_hwnd, win32con.PBM_GETPOS, 0, 0)
                        # 获取时间信息
                        time_hwnd = win32gui.FindWindowEx(hwnd, 0, "Static", None)
                        if time_hwnd:
                            time_text = win32gui.GetWindowText(time_hwnd)
                            time_match = re.match(r'(\d+:\d+|\d+:\d+:\d+) / (\d+:\d+|\d+:\d+:\d+)', time_text)
                            if time_match:
                                current_time = self._parse_time(time_match.group(1))
                                duration = self._parse_time(time_match.group(2))
                    return {
                        'artist': match.group(1),
                        'title': match.group(2),
                        'duration': duration,
                        'duration_str': self._format_time(duration),
                        'current_time': current_time,
                        'current_time_str': self._format_time(current_time),
                        'progress': progress,
                        'player': 'foobar2000'
                    }
        except:
            return None

    def _get_vlc_info(self) -> Optional[Dict[str, Any]]:
        """获取VLC当前播放信息"""
        try:
            hwnd = win32gui.FindWindow("VLC", None)
            if hwnd:
                title = win32gui.GetWindowText(hwnd)
                # 解析窗口标题获取歌曲信息
                match = re.match(r'(.+?) - VLC', title)
                if match:
                    # 获取播放进度信息
                    progress_hwnd = win32gui.FindWindowEx(hwnd, 0, "msctls_progress32", None)
                    progress = 0
                    current_time = 0
                    duration = 0
                    if progress_hwnd:
                        progress = win32gui.SendMessage(progress_hwnd, win32con.PBM_GETPOS, 0, 0)
                        # 获取时间信息
                        time_hwnd = win32gui.FindWindowEx(hwnd, 0, "Static", None)
                        if time_hwnd:
                            time_text = win32gui.GetWindowText(time_hwnd)
                            time_match = re.match(r'(\d+:\d+|\d+:\d+:\d+) / (\d+:\d+|\d+:\d+:\d+)', time_text)
                            if time_match:
                                current_time = self._parse_time(time_match.group(1))
                                duration = self._parse_time(time_match.group(2))
                    return {
                        'title': match.group(1),
                        'duration': duration,
                        'duration_str': self._format_time(duration),
                        'current_time': current_time,
                        'current_time_str': self._format_time(current_time),
                        'progress': progress,
                        'player': 'VLC'
                    }
        except:
            return None

    def _get_wmp_info(self) -> Optional[Dict[str, Any]]:
        """获取Windows Media Player当前播放信息"""
        try:
            wmp = win32com.client.Dispatch("WMPlayer.OCX")
            if wmp.playState == 3:  # 正在播放
                current_time = wmp.controls.currentPosition
                duration = wmp.currentMedia.duration
                return {
                    'artist': wmp.currentMedia.getItemInfo("Author"),
                    'title': wmp.currentMedia.getItemInfo("Title"),
                    'album': wmp.currentMedia.getItemInfo("Album"),
                    'duration': duration,
                    'duration_str': self._format_time(duration),
                    'current_time': current_time,
                    'current_time_str': self._format_time(current_time),
                    'progress': (current_time / duration * 100) if duration > 0 else 0,
                    'player': 'Windows Media Player'
                }
        except:
            return None

    def _get_itunes_info(self) -> Optional[Dict[str, Any]]:
        """获取iTunes当前播放信息"""
        try:
            itunes = win32com.client.Dispatch("iTunes.Application")
            if itunes.PlayerState == 1:  # 正在播放
                track = itunes.CurrentTrack
                current_time = itunes.PlayerPosition
                duration = track.Duration
                return {
                    'artist': track.Artist,
                    'title': track.Name,
                    'album': track.Album,
                    'duration': duration,
                    'duration_str': self._format_time(duration),
                    'current_time': current_time,
                    'current_time_str': self._format_time(current_time),
                    'progress': (current_time / duration * 100) if duration > 0 else 0,
                    'player': 'iTunes'
                }
        except:
            return None

    def _parse_time(self, time_str: str) -> int:
        """将时间字符串转换为秒数"""
        parts = time_str.split(':')
        if len(parts) == 3:  # HH:MM:SS
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        elif len(parts) == 2:  # MM:SS
            return int(parts[0]) * 60 + int(parts[1])
        return 0
