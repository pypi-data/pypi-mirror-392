import winreg
import logging
from typing import Any, Union, Optional, List, Tuple
from contextlib import contextmanager

class RegistryError(Exception):
    """注册表操作异常基类"""
    pass

class RegistryKeyNotFoundError(RegistryError):
    """注册表键不存在异常"""
    pass

class RegistryValueNotFoundError(RegistryError):
    """注册表值不存在异常"""
    pass

class RegistryAccessDeniedError(RegistryError):
    """注册表访问被拒绝异常"""
    pass

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

    def write_value(self, name: str, value: Union[str, int, bytes], 
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
            self._logger.debug(f"Wrote value '{name}' of type {value_type}: {value}")
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
            self._logger.debug(f"Deleted value: {name}")
            return True
        except WindowsError as e:
            if e.winerror == 2:  # ERROR_FILE_NOT_FOUND
                raise RegistryValueNotFoundError(f"Registry value not found: {name}")
            raise RegistryError(f"Failed to delete registry value: {name}") from e

    def list_subkeys(self) -> List[str]:
        """列出所有子键"""
        if not self._handle:
            raise RuntimeError("No registry key is opened")
        try:
            subkeys = []
            index = 0
            while True:
                subkey = winreg.EnumKey(self._handle, index)
                subkeys.append(subkey)
                index += 1
        except WindowsError as e:
            if e.winerror != 259:  # ERROR_NO_MORE_ITEMS
                raise RegistryError("Failed to enumerate subkeys") from e
        return subkeys

    def list_values(self) -> List[Tuple[str, int, Any]]:
        """列出所有值及其类型和数据"""
        if not self._handle:
            raise RuntimeError("No registry key is opened")
        try:
            values = []
            index = 0
            while True:
                name, value, value_type = winreg.EnumValue(self._handle, index)
                values.append((name, value_type, value))
                index += 1
        except WindowsError as e:
            if e.winerror != 259:  # ERROR_NO_MORE_ITEMS
                raise RegistryError("Failed to enumerate values") from e
        return values

    def key_exists(self, root: int, sub_key: str) -> bool:
        """检查注册表键是否存在"""
        try:
            with self.open_key(root, sub_key):
                return True
        except RegistryKeyNotFoundError:
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

    def backup_key(self, root: int, sub_key: str, file_path: str) -> bool:
        """备份注册表键到文件"""
        try:
            import win32api
            import win32con
            import win32security
            
            # 获取当前进程令牌
            handle = win32api.GetCurrentProcess()
            token = win32security.OpenProcessToken(handle, win32security.TOKEN_ADJUST_PRIVILEGES | win32security.TOKEN_QUERY)
            
            # 启用备份权限
            privilege_id = win32security.LookupPrivilegeValue(None, "SeBackupPrivilege")
            win32security.AdjustTokenPrivileges(token, False, [(privilege_id, win32security.SE_PRIVILEGE_ENABLED)])
            
            # 执行备份
            win32api.RegSaveKey(root, sub_key, file_path)
            
            # 恢复权限
            win32security.AdjustTokenPrivileges(token, True, [(privilege_id, win32security.SE_PRIVILEGE_USED_FOR_ACCESS)])
            
            return True
        except Exception as e:
            self._logger.error(f"Failed to backup registry key: {e}")
            return False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._handle:
            winreg.CloseKey(self._handle)
            self._handle = None
