# pyautomatic
python模块

## 模块列表
- [x] windows
- [x] rs1
- [x] pt (print的彩色输出)
- [x] math
- [x] download
- [] mail
- [] image

## 安装
```shell
pip install pyautomatic
```

## 使用
```python
from pyautomatic import windows

# 获取系统信息
print(windows.get_system_info())

# 获取进程列表
print(windows.get_process_list())

# 显示通知
windows.show_notification("标题", "内容")

# 显示toast通知
windows.show_toast_notification("标题", "内容")

# 判断是否为管理员权限
print(windows.is_admin())

# 以管理员权限运行
windows.run_as_admin()

# 获取文件属性
print(windows.get_file_properties("C:\\Windows\\System32\\notepad.exe"))

# 格式化文件大小
print(windows._format_file_size(1024))

# 创建快捷方式
windows.create_shortcut("C:\\Windows\\System32\\notepad.exe", "C:\\Users\\Public\\Desktop\\Notepad.lnk", "Notepad快捷方式", "", "C:\\Windows\\System32", "C:\\Windows\\System32\\notepad.exe")

# 获取注册表值
print(windows.get_registry_value("HKEY_LOCAL_MACHINE", "SOFTWARE\\Microsoft\\Windows\\CurrentVersion", "ProgramFilesDir"))

# 设置注册表值
windows.set_registry_value("HKEY_LOCAL_MACHINE", "SOFTWARE\\Microsoft\\Windows\\CurrentVersion", "ProgramFilesDir", "REG_SZ", "C:\\Program Files")

# 获取系统启动时间
print(windows.get_system_uptime())

# 获取磁盘使用情况
print(windows.get_disk_usage())

# 终止进程
windows.terminate_process(1234)

# 运行命令
print(windows.run_command("ipconfig"))

# 锁定工作站
windows.lock_workstation()

# 设置壁纸
windows.set_wallpaper("C:\\Users\\Public\\Pictures\\Sample Pictures\\Koala.jpg")

# 获取活动窗口
print(windows.get_active_window())

# 关机
windows.system_shutdown()

# 重启
windows.system_shutdown(reboot=True)

# 定时关机
windows.system_shutdown(timer=60) # 60秒后关机
```
还有许多功能，请查看源代码。

