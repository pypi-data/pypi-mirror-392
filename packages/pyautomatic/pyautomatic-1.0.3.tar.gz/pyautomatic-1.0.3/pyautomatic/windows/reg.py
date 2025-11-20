# reg.py - 改进版本
import winreg
import logging
from typing import Any, Union, Optional, List, Tuple, Dict
from contextlib import contextmanager
import os

class RegistryError(Exception):
    """注册表操作异常基类"""
    def __init__(self, message: str = "注册表操作错误"):
        self.message = message
        super().__init__(self.message)

class RegistryKeyNotFoundError(RegistryError):
    """注册表键不存在异常"""
    def __init__(self, key_path: str = ""):
        message = f"注册表键不存在: {key_path}" if key_path else "注册表键不存在"
        super().__init__(message)

class RegistryValueNotFoundError(RegistryError):
    """注册表值不存在异常"""
    def __init__(self, value_name: str = ""):
        message = f"注册表值不存在: {value_name}" if value_name else "注册表值不存在"
        super().__init__(message)

class RegistryAccessDeniedError(RegistryError):
    """注册表访问被拒绝异常"""
    def __init__(self, operation: str = ""):
        message = f"注册表访问被拒绝: {operation}" if operation else "注册表访问被拒绝"
        super().__init__(message)

class RegistryManager:
    """Windows注册表操作管理类"""
    
    # 预定义的根键
    HKEY_CLASSES_ROOT = winreg.HKEY_CLASSES_ROOT
    HKEY_CURRENT_USER = winreg.HKEY_CURRENT_USER
    HKEY_LOCAL_MACHINE = winreg.HKEY_LOCAL_MACHINE
    HKEY_USERS = winreg.HKEY_USERS
    HKEY_CURRENT_CONFIG = winreg.HKEY_CURRENT_CONFIG

    # 预定义的值类型
    REG_NONE = winreg.REG_NONE
    REG_SZ = winreg.REG_SZ
    REG_EXPAND_SZ = winreg.REG_EXPAND_SZ
    REG_BINARY = winreg.REG_BINARY
    REG_DWORD = winreg.REG_DWORD
    REG_DWORD_LITTLE_ENDIAN = winreg.REG_DWORD_LITTLE_ENDIAN
    REG_DWORD_BIG_ENDIAN = winreg.REG_DWORD_BIG_ENDIAN
    REG_LINK = winreg.REG_LINK
    REG_MULTI_SZ = winreg.REG_MULTI_SZ
    REG_RESOURCE_LIST = winreg.REG_RESOURCE_LIST
    REG_FULL_RESOURCE_DESCRIPTOR = winreg.REG_FULL_RESOURCE_DESCRIPTOR
    REG_RESOURCE_REQUIREMENTS_LIST = winreg.REG_RESOURCE_REQUIREMENTS_LIST
    REG_QWORD = winreg.REG_QWORD

    # 常用注册表路径
    COMMON_PATHS = {
        'desktop_background': r'Control Panel\Desktop',
        'startup': r'Software\Microsoft\Windows\CurrentVersion\Run',
        'startup_once': r'Software\Microsoft\Windows\CurrentVersion\RunOnce',
        'windows_version': r'Software\Microsoft\Windows NT\CurrentVersion',
        'file_associations': r'Software\Classes',
        'environment': r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment',
        'user_environment': r'Environment'
    }

    def __init__(self, logger: Optional[logging.Logger] = None):
        self._handle = None
        self._logger = logger or logging.getLogger(__name__)

    @contextmanager
    def open_key(self, root: int, sub_key: str, 
                 access: int = winreg.KEY_READ, 
                 create_if_missing: bool = False):
        """打开注册表键的上下文管理器"""
        handle = None
        try:
            if create_if_missing:
                handle = winreg.CreateKeyEx(root, sub_key, 0, access)
            else:
                handle = winreg.OpenKey(root, sub_key, 0, access)
            self._handle = handle
            yield self
        except WindowsError as e:
            if e.winerror == 2:  # ERROR_FILE_NOT_FOUND
                raise RegistryKeyNotFoundError(f"Registry key not found: {sub_key}")
            elif e.winerror == 5:  # ERROR_ACCESS_DENIED
                raise RegistryAccessDeniedError(f"Access denied to registry key: {sub_key}")
            raise RegistryError(f"Failed to open registry key: {sub_key}") from e
        finally:
            if handle:
                winreg.CloseKey(handle)
                self._handle = None

    def read_value(self, name: str) -> Any:
        """读取注册表值"""
        if not self._handle:
            raise RuntimeError("No registry key is opened")
        try:
            value, value_type = winreg.QueryValueEx(self._handle, name)
            self._logger.debug(f"Read value '{name}' of type {value_type}: {value}")
            return value
        except WindowsError as e:
            if e.winerror == 2:  # ERROR_FILE_NOT_FOUND
                raise RegistryValueNotFoundError(f"Registry value not found: {name}")
            raise RegistryError(f"Failed to read registry value: {name}") from e

    def write_value(self, name: str, value: Union[str, int, bytes, List[str]], 
                   value_type: Optional[int] = None):
        """写入注册表值"""
        if not self._handle:
            raise RuntimeError("No registry key is opened")
        
        if value_type is None:
            # 自动检测值类型
            if isinstance(value, str):
                value_type = self.REG_SZ
            elif isinstance(value, int):
                value_type = self.REG_DWORD
            elif isinstance(value, bytes):
                value_type = self.REG_BINARY
            elif isinstance(value, list):
                value_type = self.REG_MULTI_SZ
            else:
                raise ValueError(f"Unsupported value type: {type(value)}")

        try:
            winreg.SetValueEx(self._handle, name, 0, value_type, value)
            self._logger.info(f"Wrote value '{name}' of type {value_type}: {value}")
        except WindowsError as e:
            if e.winerror == 5:  # ERROR_ACCESS_DENIED
                raise RegistryAccessDeniedError(f"Access denied to write registry value: {name}")
            raise RegistryError(f"Failed to write registry value: {name}") from e

    def delete_value(self, name: str) -> bool:
        """删除注册表值"""
        if not self._handle:
            raise RuntimeError("No registry key is opened")
        try:
            winreg.DeleteValue(self._handle, name)
            self._logger.info(f"Deleted value: {name}")
            return True
        except WindowsError as e:
            if e.winerror == 2:  # ERROR_FILE_NOT_FOUND
                raise RegistryValueNotFoundError(f"Registry value not found: {name}")
            raise RegistryError(f"Failed to delete registry value: {name}") from e

    def delete_key(self, root: int, sub_key: str, recursive: bool = False) -> bool:
        """删除注册表键"""
        try:
            if recursive:
                # 递归删除子键
                with self.open_key(root, sub_key, winreg.KEY_ALL_ACCESS) as reg:
                    subkeys = reg.list_subkeys()
                    for subkey in subkeys:
                        reg.delete_key(root, f"{sub_key}\\{subkey}", True)
            
            winreg.DeleteKey(root, sub_key)
            self._logger.info(f"Deleted key: {sub_key}")
            return True
        except WindowsError as e:
            if e.winerror == 2:
                raise RegistryKeyNotFoundError(f"Registry key not found: {sub_key}")
            elif e.winerror == 5:
                raise RegistryAccessDeniedError(f"Access denied to delete registry key: {sub_key}")
            raise RegistryError(f"Failed to delete registry key: {sub_key}") from e

    def list_subkeys(self) -> List[str]:
        """列出所有子键"""
        if not self._handle:
            raise RuntimeError("No registry key is opened")
        try:
            subkeys = []
            index = 0
            while True:
                try:
                    subkey = winreg.EnumKey(self._handle, index)
                    subkeys.append(subkey)
                    index += 1
                except WindowsError as e:
                    if e.winerror == 259:  # ERROR_NO_MORE_ITEMS
                        break
                    raise
            return subkeys
        except WindowsError as e:
            raise RegistryError("Failed to enumerate subkeys") from e

    def list_values(self) -> List[Tuple[str, int, Any]]:
        """列出所有值及其类型和数据"""
        if not self._handle:
            raise RuntimeError("No registry key is opened")
        try:
            values = []
            index = 0
            while True:
                try:
                    name, value, value_type = winreg.EnumValue(self._handle, index)
                    values.append((name, value_type, value))
                    index += 1
                except WindowsError as e:
                    if e.winerror == 259:  # ERROR_NO_MORE_ITEMS
                        break
                    raise
            return values
        except WindowsError as e:
            raise RegistryError("Failed to enumerate values") from e

    def key_exists(self, root: int, sub_key: str) -> bool:
        """检查注册表键是否存在"""
        try:
            with self.open_key(root, sub_key):
                return True
        except RegistryKeyNotFoundError:
            return False
        except Exception:
            return False

    def value_exists(self, name: str) -> bool:
        """检查注册表值是否存在"""
        if not self._handle:
            raise RuntimeError("No registry key is opened")
        try:
            self.read_value(name)
            return True
        except RegistryValueNotFoundError:
            return False
        except Exception:
            return False

    def backup_key(self, root: int, sub_key: str, file_path: str) -> bool:
        """备份注册表键到文件"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # 使用reg export命令备份
            import subprocess
            command = f'reg export "{self._get_root_name(root)}\\{sub_key}" "{file_path}" /y'
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                self._logger.info(f"Registry key backed up to: {file_path}")
                return True
            else:
                self._logger.error(f"Backup failed: {result.stderr}")
                return False
                
        except Exception as e:
            self._logger.error(f"Failed to backup registry key: {e}")
            return False

    def restore_key(self, root: int, sub_key: str, file_path: str) -> bool:
        """从文件恢复注册表键"""
        try:
            if not os.path.exists(file_path):
                self._logger.error(f"Backup file not found: {file_path}")
                return False
            
            # 使用reg import命令恢复
            import subprocess
            command = f'reg import "{file_path}"'
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                self._logger.info(f"Registry key restored from: {file_path}")
                return True
            else:
                self._logger.error(f"Restore failed: {result.stderr}")
                return False
                
        except Exception as e:
            self._logger.error(f"Failed to restore registry key: {e}")
            return False

    def get_windows_version(self) -> Dict[str, Any]:
        """获取Windows版本信息"""
        try:
            with self.open_key(self.HKEY_LOCAL_MACHINE, self.COMMON_PATHS['windows_version']) as reg:
                values = reg.list_values()
                version_info = {}
                for name, _, value in values:
                    if name in ['ProductName', 'CurrentVersion', 'CurrentBuild', 
                               'ReleaseId', 'DisplayVersion', 'BuildLabEx']:
                        version_info[name] = value
                return version_info
        except Exception as e:
            self._logger.error(f"Failed to get Windows version: {e}")
            return {}

    def get_startup_programs(self, user_scope: bool = True) -> List[Tuple[str, str]]:
        """获取启动程序列表"""
        try:
            root = self.HKEY_CURRENT_USER if user_scope else self.HKEY_LOCAL_MACHINE
            startup_path = self.COMMON_PATHS['startup']
            
            with self.open_key(root, startup_path) as reg:
                values = reg.list_values()
                startup_programs = []
                for name, _, value in values:
                    startup_programs.append((name, value))
                return startup_programs
        except Exception as e:
            self._logger.error(f"Failed to get startup programs: {e}")
            return []

    def add_startup_program(self, name: str, command: str, user_scope: bool = True) -> bool:
        """添加启动程序"""
        try:
            root = self.HKEY_CURRENT_USER if user_scope else self.HKEY_LOCAL_MACHINE
            startup_path = self.COMMON_PATHS['startup']
            
            with self.open_key(root, startup_path, winreg.KEY_WRITE, True) as reg:
                reg.write_value(name, command, self.REG_SZ)
                self._logger.info(f"Added startup program: {name}")
                return True
        except Exception as e:
            self._logger.error(f"Failed to add startup program: {e}")
            return False

    def remove_startup_program(self, name: str, user_scope: bool = True) -> bool:
        """移除启动程序"""
        try:
            root = self.HKEY_CURRENT_USER if user_scope else self.HKEY_LOCAL_MACHINE
            startup_path = self.COMMON_PATHS['startup']
            
            with self.open_key(root, startup_path, winreg.KEY_WRITE) as reg:
                reg.delete_value(name)
                self._logger.info(f"Removed startup program: {name}")
                return True
        except Exception as e:
            self._logger.error(f"Failed to remove startup program: {e}")
            return False

    def get_environment_variable(self, name: str, user_scope: bool = True) -> Optional[str]:
        """获取环境变量"""
        try:
            if user_scope:
                root = self.HKEY_CURRENT_USER
                env_path = self.COMMON_PATHS['user_environment']
            else:
                root = self.HKEY_LOCAL_MACHINE
                env_path = self.COMMON_PATHS['environment']
            
            with self.open_key(root, env_path) as reg:
                return reg.read_value(name)
        except RegistryValueNotFoundError:
            return None
        except Exception as e:
            self._logger.error(f"Failed to get environment variable: {e}")
            return None

    def set_environment_variable(self, name: str, value: str, user_scope: bool = True) -> bool:
        """设置环境变量"""
        try:
            if user_scope:
                root = self.HKEY_CURRENT_USER
                env_path = self.COMMON_PATHS['user_environment']
            else:
                root = self.HKEY_LOCAL_MACHINE
                env_path = self.COMMON_PATHS['environment']
            
            with self.open_key(root, env_path, winreg.KEY_WRITE, True) as reg:
                reg.write_value(name, value, self.REG_SZ)
                self._logger.info(f"Set environment variable: {name}={value}")
                return True
        except Exception as e:
            self._logger.error(f"Failed to set environment variable: {e}")
            return False

    def _get_root_name(self, root: int) -> str:
        """获取根键名称"""
        root_names = {
            self.HKEY_CLASSES_ROOT: "HKEY_CLASSES_ROOT",
            self.HKEY_CURRENT_USER: "HKEY_CURRENT_USER",
            self.HKEY_LOCAL_MACHINE: "HKEY_LOCAL_MACHINE",
            self.HKEY_USERS: "HKEY_USERS",
            self.HKEY_CURRENT_CONFIG: "HKEY_CURRENT_CONFIG"
        }
        return root_names.get(root, "UNKNOWN")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._handle:
            winreg.CloseKey(self._handle)
            self._handle = None

# 使用示例
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    reg_mgr = RegistryManager()
    
    try:
        # 获取Windows版本信息
        print("=== Windows版本信息 ===")
        version_info = reg_mgr.get_windows_version()
        for key, value in version_info.items():
            print(f"{key}: {value}")
        
        # 获取启动程序
        print("\n=== 当前用户启动程序 ===")
        startup_programs = reg_mgr.get_startup_programs()
        for name, command in startup_programs:
            print(f"{name}: {command}")
        
        # 读写环境变量示例
        print("\n=== 环境变量操作 ===")
        test_var = reg_mgr.get_environment_variable("TEMP")
        print(f"TEMP环境变量: {test_var}")
        
        # 备份注册表示例
        print("\n=== 注册表备份 ===")
        backup_path = "windows_version_backup.reg"
        if reg_mgr.backup_key(reg_mgr.HKEY_LOCAL_MACHINE, 
                             reg_mgr.COMMON_PATHS['windows_version'], 
                             backup_path):
            print(f"备份成功: {backup_path}")
        
    except Exception as e:
        print(f"操作失败: {e}")