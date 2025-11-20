import os
import sys
import ctypes
from ctypes import wintypes
import win32api
import win32con
import win32process
import win32security
import win32gui
import win32event
from win32com.shell import shell
from win32com.shell import shellcon
import win32com.client
import psutil
import platform
import subprocess
import tempfile
import time
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Any, Optional, Union
import threading

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Windows:
    """
    Windows系统操作工具类
    提供常用的Windows系统功能接口
    """

    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """获取系统基本信息"""
        try:
            # 获取更详细的系统信息
            sys_info = {
                'computer_name': os.environ.get('COMPUTERNAME', 'N/A'),
                'username': os.environ.get('USERNAME', 'N/A'),
                'user_domain': os.environ.get('USERDOMAIN', 'N/A'),
                'system_drive': os.environ.get('SYSTEMDRIVE', 'N/A'),
                'windows_dir': os.environ.get('WINDIR', 'N/A'),
                'temp_dir': os.environ.get('TEMP', 'N/A'),
                'platform': platform.platform(),
                'processor': platform.processor(),
                'architecture': platform.architecture()[0],
                'windows_version': platform.version(),
                'windows_edition': platform.win32_edition() if hasattr(platform, 'win32_edition') else 'N/A',
                'cpu_cores': os.cpu_count(),
                'python_version': platform.python_version()
            }
            
            # 尝试获取更多系统信息
            try:
                memory = psutil.virtual_memory()
                sys_info.update({
                    'total_ram': f"{round(memory.total / (1024**3), 2)} GB",
                    'available_ram': f"{round(memory.available / (1024**3), 2)} GB",
                    'ram_usage_percent': memory.percent,
                    'ram_used': f"{round(memory.used / (1024**3), 2)} GB"
                })
            except Exception as e:
                logger.warning(f"获取内存信息失败: {e}")
                sys_info.update({
                    'total_ram': 'N/A',
                    'available_ram': 'N/A',
                    'ram_usage_percent': 'N/A'
                })
                
            return sys_info
        except Exception as e:
            logger.error(f"获取系统信息失败: {e}")
            return {'error': f'获取系统信息失败: {str(e)}'}

    @staticmethod
    def get_process_list(sort_by_memory: bool = True) -> List[Dict[str, Any]]:
        """获取当前运行的进程列表"""
        processes = []
        try:
            for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent', 'create_time', 'username']):
                try:
                    process_info = proc.info
                    processes.append({
                        'pid': process_info['pid'],
                        'name': process_info['name'],
                        'memory_mb': round(process_info['memory_info'].rss / (1024 * 1024), 2),
                        'cpu_percent': round(process_info['cpu_percent'], 2) if process_info['cpu_percent'] else 0.0,
                        'create_time': datetime.fromtimestamp(process_info['create_time']).strftime('%Y-%m-%d %H:%M:%S') if process_info['create_time'] else 'N/A',
                        'username': process_info.get('username', 'N/A')
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    continue
            
            # 排序
            if sort_by_memory:
                processes.sort(key=lambda x: x['memory_mb'], reverse=True)
            else:
                processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
                
        except Exception as e:
            logger.error(f"获取进程列表时出错: {e}")
            
        return processes

    @staticmethod
    def get_process_by_name(process_name: str) -> List[Dict[str, Any]]:
        """根据进程名查找进程"""
        try:
            matching_processes = []
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if process_name.lower() in proc.info['name'].lower():
                        matching_processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return matching_processes
        except Exception as e:
            logger.error(f"查找进程失败: {e}")
            return []

    @staticmethod
    def show_notification(title: str, message: str, style: int = win32con.MB_OK | win32con.MB_ICONINFORMATION) -> bool:
        """显示系统通知/消息框"""
        try:
            win32gui.MessageBox(0, message, title, style)
            return True
        except Exception as e:
            logger.error(f"无法显示通知: {e}")
            return False

    @staticmethod
    def show_toast_notification(title: str, message: str, duration: int = 5, icon_path: str = None) -> bool:
        """显示Windows Toast通知（改进版本）"""
        try:
            # 使用线程避免阻塞
            def show_toast():
                try:
                    import winsound
                    
                    # 创建临时窗口用于Toast
                    wc = win32gui.WNDCLASS()
                    wc.hInstance = win32api.GetModuleHandle(None)
                    wc.lpszClassName = "ToastWindow"
                    wc.lpfnWndProc = lambda hwnd, msg, wparam, lparam: win32gui.DefWindowProc(hwnd, msg, wparam, lparam)
                    class_atom = win32gui.RegisterClass(wc)
                    
                    hwnd = win32gui.CreateWindow(class_atom, "Toast", 0, 0, 0, 0, 0, 0, 0, wc.hInstance, None)
                    
                    # 使用Shell_NotifyIconW显示通知
                    shell32 = ctypes.windll.shell32
                    
                    class NOTIFYICONDATA(ctypes.Structure):
                        _fields_ = [
                            ("cbSize", wintypes.DWORD),
                            ("hWnd", wintypes.HWND),
                            ("uID", wintypes.UINT),
                            ("uFlags", wintypes.UINT),
                            ("uCallbackMessage", wintypes.UINT),
                            ("hIcon", wintypes.HICON),
                            ("szTip", wintypes.WCHAR * 128),
                            ("dwState", wintypes.DWORD),
                            ("dwStateMask", wintypes.DWORD),
                            ("szInfo", wintypes.WCHAR * 256),
                            ("uTimeout", wintypes.UINT),
                            ("szInfoTitle", wintypes.WCHAR * 64),
                            ("dwInfoFlags", wintypes.DWORD),
                            ("guidItem", wintypes.DWORD * 4)
                        ]
                    
                    nid = NOTIFYICONDATA()
                    nid.cbSize = ctypes.sizeof(NOTIFYICONDATA)
                    nid.hWnd = hwnd
                    nid.uID = 0
                    nid.uFlags = 0x00000001 | 0x00000002 | 0x00000004 | 0x00000010  # NIF_ICON|NIF_MESSAGE|NIF_TIP|NIF_INFO
                    nid.uCallbackMessage = win32con.WM_USER + 20
                    nid.hIcon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)
                    nid.szTip = title[:127]
                    nid.szInfo = message[:255]
                    nid.uTimeout = duration * 1000
                    nid.szInfoTitle = title[:63]
                    nid.dwInfoFlags = 0x00000001  # NIIF_INFO
                    
                    # 显示通知
                    shell32.Shell_NotifyIconW(0, ctypes.byref(nid))  # NIM_ADD
                    
                    # 播放提示音
                    winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
                    
                    time.sleep(duration)
                    
                    # 移除通知
                    shell32.Shell_NotifyIconW(2, ctypes.byref(nid))  # NIM_DELETE
                    win32gui.DestroyWindow(hwnd)
                    
                except Exception as e:
                    logger.error(f"Toast通知线程错误: {e}")
                    # 回退到消息框
                    Windows.show_notification(title, message)
            
            # 在新线程中显示Toast
            thread = threading.Thread(target=show_toast, daemon=True)
            thread.start()
            return True
            
        except Exception as e:
            logger.error(f"显示Toast通知失败: {e}")
            return Windows.show_notification(title, message)

    @staticmethod
    def is_admin() -> bool:
        """检查当前程序是否以管理员权限运行"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except Exception as e:
            logger.error(f"检查管理员权限失败: {e}")
            return False

    @staticmethod
    def run_as_admin() -> bool:
        """以管理员权限重新运行程序"""
        if Windows.is_admin():
            return True
        
        try:
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
            return True
        except Exception as e:
            logger.error(f"请求管理员权限失败: {e}")
            return False

    @staticmethod
    def get_file_properties(filepath: str) -> Dict[str, Any]:
        """获取文件属性"""
        try:
            if not os.path.exists(filepath):
                return {'error': '文件不存在'}
            
            stat = os.stat(filepath)
            props = {
                'size': stat.st_size,
                'size_formatted': Windows._format_file_size(stat.st_size),
                'created': stat.st_ctime,
                'created_formatted': datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                'modified': stat.st_mtime,
                'modified_formatted': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                'accessed': stat.st_atime,
                'accessed_formatted': datetime.fromtimestamp(stat.st_atime).strftime('%Y-%m-%d %H:%M:%S'),
                'is_file': os.path.isfile(filepath),
                'is_dir': os.path.isdir(filepath),
                'absolute_path': os.path.abspath(filepath)
            }
            
            # 尝试获取文件版本信息（仅适用于可执行文件）
            try:
                if props['is_file'] and filepath.lower().endswith(('.exe', '.dll')):
                    info = win32api.GetFileVersionInfo(filepath, "\\")
                    props['file_version'] = "%d.%d.%d.%d" % (
                        info['FileVersionMS'] / 65536,
                        info['FileVersionMS'] % 65536,
                        info['FileVersionLS'] / 65536,
                        info['FileVersionLS'] % 65536
                    )
            except:
                props['file_version'] = 'N/A'
                
            return props
        except Exception as e:
            logger.error(f"获取文件属性失败: {e}")
            return {'error': f'获取文件属性失败: {str(e)}'}

    @staticmethod
    def _format_file_size(size_bytes: int) -> str:
        """格式化文件大小"""
        if size_bytes == 0:
            return "0 B"
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        return f"{size_bytes:.2f} {size_names[i]}"

    @staticmethod
    def create_shortcut(target: str, shortcut_path: str, description: str = "", 
                       arguments: str = "", work_dir: str = "", icon_path: str = "") -> bool:
        """创建快捷方式"""
        try:
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = target
            shortcut.WorkingDirectory = work_dir if work_dir else os.path.dirname(target)
            shortcut.Arguments = arguments
            shortcut.Description = description
            if icon_path:
                shortcut.IconLocation = icon_path
            shortcut.save()
            logger.info(f"快捷方式创建成功: {shortcut_path}")
            return True
        except Exception as e:
            logger.error(f"创建快捷方式失败: {e}")
            return False

    @staticmethod
    def get_registry_value(key: str, subkey: str, value_name: str) -> Any:
        """读取注册表值"""
        try:
            key_const = getattr(win32con, key)
            handle = win32api.RegOpenKeyEx(key_const, subkey, 0, win32con.KEY_READ)
            value, value_type = win32api.RegQueryValueEx(handle, value_name)
            win32api.RegCloseKey(handle)
            
            # 根据类型转换值
            if value_type == win32con.REG_DWORD:
                return int(value)
            elif value_type == win32con.REG_QWORD:
                return int(value)
            elif value_type == win32con.REG_BINARY:
                return value.hex() if value else ""
            else:
                return str(value) if value else ""
        except Exception as e:
            logger.error(f"读取注册表失败: {e}")
            return None

    @staticmethod
    def set_registry_value(key: str, subkey: str, value_name: str, 
                          value_type: str, value: Any) -> bool:
        """设置注册表值"""
        try:
            key_const = getattr(win32con, key)
            handle = win32api.RegCreateKeyEx(key_const, subkey, 0, None, 
                                           win32con.REG_OPTION_NON_VOLATILE, 
                                           win32con.KEY_WRITE, None)
            
            # 根据类型转换值
            if value_type == "REG_DWORD":
                value = int(value)
                reg_type = win32con.REG_DWORD
            elif value_type == "REG_QWORD":
                value = int(value)
                reg_type = win32con.REG_QWORD
            elif value_type == "REG_SZ":
                reg_type = win32con.REG_SZ
            elif value_type == "REG_BINARY":
                if isinstance(value, str):
                    value = bytes.fromhex(value)
                reg_type = win32con.REG_BINARY
            else:
                reg_type = win32con.REG_SZ
                
            win32api.RegSetValueEx(handle, value_name, 0, reg_type, value)
            win32api.RegCloseKey(handle)
            logger.info(f"注册表值设置成功: {key}\\{subkey}\\{value_name}")
            return True
        except Exception as e:
            logger.error(f"设置注册表失败: {e}")
            return False

    @staticmethod
    def get_system_uptime() -> Dict[str, Any]:
        """获取系统运行时间"""
        try:
            boot_time = psutil.boot_time()
            uptime_seconds = time.time() - boot_time
            uptime_str = str(timedelta(seconds=int(uptime_seconds)))
            
            return {
                'boot_time': datetime.fromtimestamp(boot_time).strftime('%Y-%m-%d %H:%M:%S'),
                'uptime_seconds': uptime_seconds,
                'uptime_formatted': uptime_str,
                'boot_timestamp': boot_time
            }
        except Exception as e:
            logger.error(f"获取系统运行时间失败: {e}")
            return {'error': f'获取系统运行时间失败: {str(e)}'}

    @staticmethod
    def get_disk_usage() -> List[Dict[str, Any]]:
        """获取磁盘使用情况"""
        try:
            disk_info = []
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_info.append({
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'total_gb': round(usage.total / (1024**3), 2),
                        'used_gb': round(usage.used / (1024**3), 2),
                        'free_gb': round(usage.free / (1024**3), 2),
                        'percent': round(usage.percent, 2),
                        'free_percent': round(100 - usage.percent, 2)
                    })
                except (PermissionError, OSError) as e:
                    logger.warning(f"无法访问磁盘 {partition.device}: {e}")
                    continue
            return disk_info
        except Exception as e:
            logger.error(f"获取磁盘信息失败: {e}")
            return [{'error': f'获取磁盘信息失败: {str(e)}'}]

    @staticmethod
    def terminate_process(pid: int, force: bool = False) -> bool:
        """终止指定PID的进程"""
        try:
            process = psutil.Process(pid)
            if force:
                process.kill()
                logger.info(f"强制终止进程: {pid}")
            else:
                process.terminate()
                logger.info(f"终止进程: {pid}")
            return True
        except psutil.NoSuchProcess:
            logger.warning(f"进程 {pid} 不存在")
            return False
        except psutil.AccessDenied:
            logger.error(f"无权限终止进程 {pid}")
            return False
        except Exception as e:
            logger.error(f"终止进程失败: {e}")
            return False

    @staticmethod
    def run_command(command: str, timeout: int = 30, capture_output: bool = True) -> Dict[str, Any]:
        """运行命令并返回结果"""
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=capture_output, 
                text=True, 
                timeout=timeout,
                encoding='utf-8',
                errors='ignore'
            )
            return {
                'returncode': result.returncode,
                'stdout': result.stdout if capture_output else '',
                'stderr': result.stderr if capture_output else '',
                'success': result.returncode == 0,
                'command': command
            }
        except subprocess.TimeoutExpired:
            logger.error(f"命令执行超时: {command}")
            return {'error': '命令执行超时', 'command': command}
        except Exception as e:
            logger.error(f"执行命令失败: {e}")
            return {'error': f'执行命令失败: {str(e)}', 'command': command}

    @staticmethod
    def lock_workstation() -> bool:
        """锁定工作站"""
        try:
            ctypes.windll.user32.LockWorkStation()
            logger.info("工作站已锁定")
            return True
        except Exception as e:
            logger.error(f"锁定工作站失败: {e}")
            return False

    @staticmethod
    def set_wallpaper(image_path: str) -> bool:
        """设置桌面壁纸"""
        try:
            if not os.path.isabs(image_path):
                image_path = os.path.abspath(image_path)
                
            if not os.path.exists(image_path):
                logger.error(f"壁纸文件不存在: {image_path}")
                return False
                
            # 设置壁纸
            result = ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 3)
            if result:
                logger.info(f"壁纸设置成功: {image_path}")
                return True
            else:
                logger.error("壁纸设置失败")
                return False
        except Exception as e:
            logger.error(f"设置壁纸失败: {e}")
            return False

    @staticmethod
    def get_active_window() -> Dict[str, Any]:
        """获取当前活动窗口信息"""
        try:
            hwnd = win32gui.GetForegroundWindow()
            window_title = win32gui.GetWindowText(hwnd)
            window_class = win32gui.GetClassName(hwnd)
            
            # 获取窗口位置和大小
            rect = win32gui.GetWindowRect(hwnd)
            
            # 获取进程ID
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            
            return {
                'hwnd': hwnd,
                'title': window_title,
                'class': window_class,
                'pid': pid,
                'position': {
                    'x': rect[0],
                    'y': rect[1],
                    'width': rect[2] - rect[0],
                    'height': rect[3] - rect[1]
                }
            }
        except Exception as e:
            logger.error(f"获取活动窗口失败: {e}")
            return {'error': f'获取活动窗口失败: {str(e)}'}

    @staticmethod
    def system_shutdown(force: bool = False, reboot: bool = False, timer: int = 0, reason: str = "") -> bool:
        """关机或重启系统"""
        try:
            if timer > 0:
                # 使用shutdown命令设置定时
                command = f"shutdown {'/r' if reboot else '/s'} /t {timer}"
                if force:
                    command += " /f"
                if reason:
                    command += f" /c \"{reason}\""
                subprocess.run(command, shell=True, check=False)
                logger.info(f"系统将在 {timer} 秒后{'重启' if reboot else '关机'}")
            else:
                # 立即执行
                flags = win32con.EWX_SHUTDOWN
                if force:
                    flags |= win32con.EWX_FORCE
                if reboot:
                    flags |= win32con.EWX_REBOOT
                
                win32api.InitiateSystemShutdown(None, reason, 0, force, reboot)
                logger.info(f"系统立即{'重启' if reboot else '关机'}")
            
            return True
        except Exception as e:
            logger.error(f"系统关机/重启操作失败: {e}")
            return False

    @staticmethod
    def cancel_shutdown() -> bool:
        """取消系统关机/重启"""
        try:
            subprocess.run("shutdown /a", shell=True, check=False)
            logger.info("已取消系统关机/重启")
            return True
        except Exception as e:
            logger.error(f"取消关机失败: {e}")
            return False

    @staticmethod
    def get_network_info() -> Dict[str, Any]:
        """获取网络信息"""
        try:
            import socket
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            
            # 获取网络接口信息
            net_io = psutil.net_io_counters()
            net_info = {
                'hostname': hostname,
                'local_ip': local_ip,
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv
            }
            
            return net_info
        except Exception as e:
            logger.error(f"获取网络信息失败: {e}")
            return {'error': f'获取网络信息失败: {str(e)}'}

    @staticmethod
    def create_temp_file(content: str = "", prefix: str = "temp_", suffix: str = ".txt") -> str:
        """创建临时文件"""
        try:
            with tempfile.NamedTemporaryFile(mode='w', delete=False, prefix=prefix, suffix=suffix) as f:
                if content:
                    f.write(content)
                return f.name
        except Exception as e:
            logger.error(f"创建临时文件失败: {e}")
            return ""

# 使用示例和测试
if __name__ == "__main__":
    # 获取系统信息
    print("=== 系统信息 ===")
    sys_info = Windows.get_system_info()
    for key, value in sys_info.items():
        print(f"{key}: {value}")
    
    print("\n=== 管理员权限检查 ===")
    print("是否管理员:", Windows.is_admin())
    
    print("\n=== 进程列表 (前5个) ===")
    processes = Windows.get_process_list()
    for proc in processes[:5]:
        print(f"PID: {proc['pid']}, 名称: {proc['name']}, 内存: {proc['memory_mb']}MB, CPU: {proc['cpu_percent']}%")
    
    print("\n=== 磁盘信息 ===")
    disks = Windows.get_disk_usage()
    for disk in disks:
        print(f"磁盘: {disk['device']}, 使用率: {disk['percent']}%, 可用: {disk['free_gb']}GB")
    
    print("\n=== 系统运行时间 ===")
    uptime = Windows.get_system_uptime()
    print(f"启动时间: {uptime['boot_time']}")
    print(f"运行时间: {uptime['uptime_formatted']}")
    
    print("\n=== 网络信息 ===")
    net_info = Windows.get_network_info()
    for key, value in net_info.items():
        print(f"{key}: {value}")
    
    # 显示通知
    Windows.show_notification("系统信息", "系统信息获取完成！")
    
    # 显示Toast通知
    Windows.show_toast_notification("测试", "这是一个Toast通知测试", duration=3)