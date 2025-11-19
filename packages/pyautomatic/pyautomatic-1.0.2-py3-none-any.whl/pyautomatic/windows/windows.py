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
from platform import platform
import subprocess
import tempfile
import time
from datetime import datetime, timedelta  

class Windows:
    """
    Windows系统操作工具类
    提供常用的Windows系统功能接口
    """

    @staticmethod
    def get_system_info():
        """获取系统基本信息"""
        try:
            # 获取更详细的系统信息
            sys_info = {
                'computer_name': os.environ.get('COMPUTERNAME', 'N/A'),
                'username': os.environ.get('USERNAME', 'N/A'),
                'system_drive': os.environ.get('SYSTEMDRIVE', 'N/A'),
                'windows_dir': os.environ.get('WINDIR', 'N/A'),
                'temp_dir': os.environ.get('TEMP', 'N/A'),
                'platform': platform.platform(),
                'processor': platform.processor(),
                'architecture': platform.architecture()[0],
                'windows_version': platform.version(),
                'windows_edition': platform.win32_edition() if hasattr(platform, 'win32_edition') else 'N/A'
            }
            
            # 尝试获取更多系统信息
            try:
                sys_info['total_ram'] = f"{round(psutil.virtual_memory().total / (1024**3), 2)} GB"
                sys_info['available_ram'] = f"{round(psutil.virtual_memory().available / (1024**3), 2)} GB"
            except:
                sys_info['total_ram'] = 'N/A'
                sys_info['available_ram'] = 'N/A'
                
            return sys_info
        except Exception as e:
            return {'error': f'获取系统信息失败: {str(e)}'}

    @staticmethod
    def get_process_list():
        """获取当前运行的进程列表"""
        processes = []
        try:
            for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent', 'create_time']):
                try:
                    process_info = proc.info
                    processes.append({
                        'pid': process_info['pid'],
                        'name': process_info['name'],
                        'memory_mb': round(process_info['memory_info'].rss / (1024 * 1024), 2),
                        'cpu_percent': process_info['cpu_percent'],
                        'create_time': datetime.fromtimestamp(process_info['create_time']).strftime('%Y-%m-%d %H:%M:%S') if process_info['create_time'] else 'N/A'
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            print(f"获取进程列表时出错: {str(e)}")
            
        return processes

    @staticmethod
    def show_notification(title, message, duration=5, style=win32con.MB_OK | win32con.MB_ICONINFORMATION):
        """显示系统通知/消息框"""
        try:
            win32gui.MessageBox(0, message, title, style)
        except Exception as e:
            print(f"无法显示通知: {str(e)}")
            return False
        return True

    @staticmethod
    def show_toast_notification(title, message, duration=5):
        """显示Windows Toast通知"""
        try:
            import ctypes
            from ctypes import wintypes  # 移除GUID导入，改为手动定义
            # 补充必要的win32模块导入
            import win32gui
            import win32api
            import win32con
            
            # 手动定义GUID结构（解决ctypes无GUID的问题）
            class GUID(ctypes.Structure):
                _fields_ = [
                    ("data1", wintypes.DWORD),
                    ("data2", wintypes.WORD),
                    ("data3", wintypes.WORD),
                    ("data4", wintypes.BYTE * 8)
                ]
            
            # 正确的API库：Shell_NotifyIconW位于shell32.dll
            shell32 = ctypes.windll.shell32
            user32 = ctypes.windll.user32
            
            # 修正NOTIFYICONDATA结构，使用手动定义的GUID
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
                    ("uTimeoutOrVersion", wintypes.UINT),  # 修正超时字段名
                    ("szInfoTitle", wintypes.WCHAR * 64),
                    ("dwInfoFlags", wintypes.DWORD),
                    ("guidItem", GUID),  # 使用手动定义的GUID
                ]
            
            # 常量定义
            NIM_ADD = 0x00000000
            NIM_MODIFY = 0x00000001
            NIM_DELETE = 0x00000002
            NIF_MESSAGE = 0x00000001
            NIF_ICON = 0x00000002
            NIF_TIP = 0x00000004
            NIF_INFO = 0x00000010
            NIIF_INFO = 0x00000001
            NOTIFYICON_VERSION_4 = 4
            
            # 创建隐藏窗口
            class_name = "NotificationWindow"
            wc = win32gui.WNDCLASS()
            wc.hInstance = win32api.GetModuleHandle(None)
            wc.lpszClassName = class_name
            wc.lpfnWndProc = lambda hwnd, msg, wparam, lparam: win32gui.DefWindowProc(hwnd, msg, wparam, lparam)
            class_atom = win32gui.RegisterClass(wc)
            
            hwnd = win32gui.CreateWindow(
                class_atom, class_name, 0, 0, 0, 0, 0,
                0, 0, wc.hInstance, None
            )
            
            # 初始化通知数据
            nid = NOTIFYICONDATA()
            nid.cbSize = ctypes.sizeof(NOTIFYICONDATA)
            nid.hWnd = hwnd
            nid.uID = 0
            nid.uFlags = NIF_ICON | NIF_MESSAGE | NIF_TIP | NIF_INFO
            nid.uCallbackMessage = win32con.WM_USER + 20
            nid.hIcon = user32.LoadIconW(0, win32con.IDI_APPLICATION)
            nid.szTip = title
            nid.szInfo = message
            nid.uTimeoutOrVersion = duration * 1000
            nid.szInfoTitle = title
            nid.dwInfoFlags = NIIF_INFO
            nid.guidItem = GUID()  # 初始化手动定义的GUID
            
            # 显示通知
            shell32.Shell_NotifyIconW(NIM_ADD, ctypes.byref(nid))
            # 设置通知版本
            nid.uTimeoutOrVersion = NOTIFYICON_VERSION_4
            shell32.Shell_NotifyIconW(NIM_MODIFY, ctypes.byref(nid))
            
            # 等待后删除通知
            import time
            time.sleep(duration)
            shell32.Shell_NotifyIconW(NIM_DELETE, ctypes.byref(nid))
            
            return True
            
        except ImportError as e:
            print(f"Toast通知不可用（缺少模块：{e}），使用消息框替代")
            return Windows.show_notification(title, message, duration)
        except Exception as e:
            print(f"显示Toast通知失败: {str(e)}")
            return Windows.show_notification(title, message, duration)


    @staticmethod
    def is_admin():
        """检查当前程序是否以管理员权限运行"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    @staticmethod
    def run_as_admin():
        """以管理员权限重新运行程序"""
        if Windows.is_admin():
            return True
        
        try:
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
            sys.exit(0)  # 退出当前非管理员进程
        except Exception as e:
            print(f"请求管理员权限失败: {str(e)}")
            return False

    @staticmethod
    def get_file_properties(filepath):
        """获取文件属性"""
        try:
            if not os.path.exists(filepath):
                return {'error': '文件不存在'}
                
            props = {
                'size': os.path.getsize(filepath),
                'size_formatted': Windows._format_file_size(os.path.getsize(filepath)),
                'created': os.path.getctime(filepath),
                'created_formatted': datetime.fromtimestamp(os.path.getctime(filepath)).strftime('%Y-%m-%d %H:%M:%S'),
                'modified': os.path.getmtime(filepath),
                'modified_formatted': datetime.fromtimestamp(os.path.getmtime(filepath)).strftime('%Y-%m-%d %H:%M:%S'),
                'accessed': os.path.getatime(filepath),
                'accessed_formatted': datetime.fromtimestamp(os.path.getatime(filepath)).strftime('%Y-%m-%d %H:%M:%S'),
                'is_file': os.path.isfile(filepath),
                'is_dir': os.path.isdir(filepath)
            }
            return props
        except Exception as e:
            return {'error': f'获取文件属性失败: {str(e)}'}

    @staticmethod
    def _format_file_size(size_bytes):
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
    def create_shortcut(target, shortcut_path, description="", arguments="", work_dir="", icon_path=""):
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
            return True
        except Exception as e:
            print(f"创建快捷方式失败: {str(e)}")
            return False

    @staticmethod
    def get_registry_value(key, subkey, value_name):
        """读取注册表值"""
        try:
            key = getattr(win32con, key)
            handle = win32api.RegOpenKeyEx(key, subkey, 0, win32con.KEY_READ)
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
            print(f"读取注册表失败: {str(e)}")
            return None

    @staticmethod
    def set_registry_value(key, subkey, value_name, value_type, value):
        """设置注册表值"""
        try:
            key = getattr(win32con, key)
            handle = win32api.RegCreateKeyEx(key, subkey, 0, None, win32con.REG_OPTION_NON_VOLATILE, win32con.KEY_WRITE, None)
            
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
            return True
        except Exception as e:
            print(f"设置注册表失败: {str(e)}")
            return False

    @staticmethod
    def get_system_uptime():
        """获取系统运行时间"""
        try:
            boot_time = psutil.boot_time()  # 获取系统启动时间戳
            uptime_seconds = time.time() - boot_time  # 计算运行时间（秒）
            # 将秒数转换为格式化的时间字符串（如"2 days, 3:45:12"）
            uptime_str = str(timedelta(seconds=int(uptime_seconds)))
            return {
                # 将启动时间戳转换为可读格式
                'boot_time': datetime.fromtimestamp(boot_time).strftime('%Y-%m-%d %H:%M:%S'),
                'uptime_seconds': uptime_seconds,  # 运行时间（秒，浮点数）
                'uptime_formatted': uptime_str  # 格式化的运行时间字符串
            }
        except Exception as e:
            return {'error': f'获取系统运行时间失败: {str(e)}'}

    @staticmethod
    def get_disk_usage():
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
                        'percent': usage.percent
                    })
                except PermissionError:
                    continue
            return disk_info
        except Exception as e:
            return {'error': f'获取磁盘信息失败: {str(e)}'}

    @staticmethod
    def terminate_process(pid):
        """终止指定PID的进程"""
        try:
            process = psutil.Process(pid)
            process.terminate()
            return True
        except psutil.NoSuchProcess:
            print(f"进程 {pid} 不存在")
            return False
        except psutil.AccessDenied:
            print(f"无权限终止进程 {pid}")
            return False
        except Exception as e:
            print(f"终止进程失败: {str(e)}")
            return False

    @staticmethod
    def run_command(command, timeout=30):
        """运行命令并返回结果"""
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=timeout
            )
            return {
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'success': result.returncode == 0
            }
        except subprocess.TimeoutExpired:
            return {'error': '命令执行超时'}
        except Exception as e:
            return {'error': f'执行命令失败: {str(e)}'}

    @staticmethod
    def lock_workstation():
        """锁定工作站"""
        try:
            ctypes.windll.user32.LockWorkStation()
            return True
        except Exception as e:
            print(f"锁定工作站失败: {str(e)}")
            return False

    @staticmethod
    def set_wallpaper(image_path):
        """设置桌面壁纸"""
        try:
            # 需要绝对路径
            if not os.path.isabs(image_path):
                image_path = os.path.abspath(image_path)
                
            # 设置壁纸
            ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 3)
            return True
        except Exception as e:
            print(f"设置壁纸失败: {str(e)}")
            return False

    @staticmethod
    def get_active_window():
        """获取当前活动窗口信息"""
        try:
            hwnd = win32gui.GetForegroundWindow()
            window_title = win32gui.GetWindowText(hwnd)
            window_class = win32gui.GetClassName(hwnd)
            
            # 获取窗口位置和大小
            rect = win32gui.GetWindowRect(hwnd)
            
            return {
                'hwnd': hwnd,
                'title': window_title,
                'class': window_class,
                'position': {
                    'x': rect[0],
                    'y': rect[1],
                    'width': rect[2] - rect[0],
                    'height': rect[3] - rect[1]
                }
            }
        except Exception as e:
            return {'error': f'获取活动窗口失败: {str(e)}'}

    @staticmethod
    def system_shutdown(force=False, reboot=False, timer=0):
        """关机或重启系统"""
        try:
            flags = win32con.EWX_SHUTDOWN
            if force:
                flags |= win32con.EWX_FORCE
            if reboot:
                flags |= win32con.EWX_REBOOT
            
            if timer > 0:
                # 使用shutdown命令设置定时
                command = f"shutdown {'/r' if reboot else '/s'} /t {timer}"
                if force:
                    command += " /f"
                subprocess.run(command, shell=True)
            else:
                # 立即执行
                win32api.InitiateSystemShutdown(None, None, 0, force, reboot)
            
            return True
        except Exception as e:
            print(f"系统关机/重启操作失败: {str(e)}")
            return False

# 使用示例
if __name__ == "__main__":
    # 获取系统信息
    print("系统信息:", Windows.get_system_info())
    
    # 检查管理员权限
    print("是否管理员:", Windows.is_admin())
    
    # 显示通知
    Windows.show_notification("测试", "这是一个测试通知")
    
    # 显示Toast通知
    Windows.show_toast_notification("Toast测试", "这是一个Toast通知测试")

    # 获取进程列表
    processes = Windows.get_process_list()
    print("当前进程数量:", len(processes))
    # 打印前5个进程
    for proc in processes[:5]:
        print(f"  PID: {proc['pid']}, 名称: {proc['name']}, 内存: {proc['memory_mb']}MB")

    # 读取注册表
    version = Windows.get_registry_value("HKEY_LOCAL_MACHINE", 
                                        "SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion",
                                        "CurrentVersion")
    print("Windows版本:", version)
    
    # 获取系统运行时间
    uptime = Windows.get_system_uptime()
    print("系统运行时间:", uptime)
    
    # 获取磁盘信息
    disks = Windows.get_disk_usage()
    print("磁盘信息:")
    for disk in disks[:3]:  # 显示前3个磁盘
        print(f"  磁盘: {disk['device']}, 使用率: {disk['percent']}%")
    
    # 获取活动窗口
    active_win = Windows.get_active_window()
    print("当前活动窗口:", active_win.get('title', '未知'))