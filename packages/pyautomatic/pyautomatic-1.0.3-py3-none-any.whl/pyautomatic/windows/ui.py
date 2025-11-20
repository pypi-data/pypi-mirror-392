import sys
import os
import win32api
import win32con
import win32gui
import win32ui
from typing import Optional, List, Tuple, Callable, Dict, Any, Union
import logging

# 配置日志
logger = logging.getLogger(__name__)

class Style:
    """样式系统"""
    # 颜色
    COLORS = {
        'white': 0xFFFFFF,
        'black': 0x000000,
        'red': 0xFF0000,
        'green': 0x00FF00,
        'blue': 0x0000FF,
        'gray': 0x808080,
        'lightgray': 0xD3D3D3,
        'darkgray': 0x404040,
        'yellow': 0xFFFF00,
        'cyan': 0x00FFFF,
        'magenta': 0xFF00FF,
        'orange': 0xFFA500,
        'purple': 0x800080,
        'brown': 0xA52A2A,
    }
    
    # 字体
    FONTS = {
        'default': ('Microsoft YaHei', 10),
        'title': ('Microsoft YaHei', 14, True),
        'small': ('Microsoft YaHei', 8),
        'large': ('Microsoft YaHei', 16, True),
        'monospace': ('Consolas', 10),
    }
    
    # 预定义样式
    STYLES = {
        'default': {
            'bg_color': 'white',
            'text_color': 'black',
            'font': 'default'
        },
        'primary': {
            'bg_color': 'blue',
            'text_color': 'white',
            'font': 'default'
        },
        'success': {
            'bg_color': 'green',
            'text_color': 'white',
            'font': 'default'
        },
        'warning': {
            'bg_color': 'orange',
            'text_color': 'black',
            'font': 'default'
        },
        'danger': {
            'bg_color': 'red',
            'text_color': 'white',
            'font': 'default'
        }
    }
    
    @staticmethod
    def get_color(color_name: str) -> int:
        """获取颜色值"""
        return Style.COLORS.get(color_name.lower(), Style.COLORS['black'])
        
    @staticmethod
    def get_font(font_name: str) -> Tuple:
        """获取字体信息"""
        return Style.FONTS.get(font_name.lower(), Style.FONTS['default'])
    
    @staticmethod
    def get_style(style_name: str) -> Dict[str, Any]:
        """获取预定义样式"""
        return Style.STYLES.get(style_name.lower(), Style.STYLES['default'])

class WindowStyle:
    """窗口样式常量"""
    OVERLAPPED = win32con.WS_OVERLAPPEDWINDOW
    POPUP = win32con.WS_POPUPWINDOW
    CHILD = win32con.WS_CHILDWINDOW
    MINIMIZE = win32con.WS_MINIMIZEBOX
    MAXIMIZE = win32con.WS_MAXIMIZEBOX
    THICKFRAME = win32con.WS_THICKFRAME
    BORDER = win32con.WS_BORDER
    CAPTION = win32con.WS_CAPTION
    SYSMENU = win32con.WS_SYSMENU

class ControlStyle:
    """控件样式常量"""
    BUTTON = win32con.BS_PUSHBUTTON
    CHECKBOX = win32con.BS_AUTOCHECKBOX
    RADIO = win32con.BS_RADIOBUTTON
    GROUPBOX = win32con.BS_GROUPBOX
    EDIT_TEXT = win32con.ES_LEFT | win32con.ES_AUTOHSCROLL
    EDIT_MULTILINE = win32con.ES_MULTILINE | win32con.ES_AUTOVSCROLL | win32con.WS_VSCROLL
    EDIT_PASSWORD = win32con.ES_PASSWORD
    LISTBOX = win32con.LBS_STANDARD | win32con.WS_VSCROLL
    COMBOBOX = win32con.CBS_DROPDOWN | win32con.WS_VSCROLL
    STATIC = win32con.SS_LEFT

class WindowType:
    """窗口类型常量"""
    MAIN = "main"
    CHILD = "child"
    MODAL = "modal"
    TOOL = "tool"
    POPUP = "popup"

class WindowMessage:
    """窗口消息常量"""
    WM_USER = win32con.WM_USER
    WM_CUSTOM = WM_USER + 1
    WM_NCLBUTTONDOWN = win32con.WM_NCLBUTTONDOWN
    HTCAPTION = win32con.HTCAPTION

class CustomInfo:
    """自定义信息类"""
    def __init__(self):
        self.data = {}
        
    def set(self, key: str, value: Any):
        """设置自定义信息"""
        self.data[key] = value
        
    def get(self, key: str, default: Any = None) -> Any:
        """获取自定义信息"""
        return self.data.get(key, default)
        
    def remove(self, key: str):
        """删除自定义信息"""
        if key in self.data:
            del self.data[key]

class Control:
    """基础控件类"""
    _control_id = 1000
    
    def __init__(self, parent, x: int, y: int, width: int, height: int, 
                 style: int = 0, class_name: str = None):
        self.parent = parent
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.style = style
        self.class_name = class_name
        self.hwnd = None
        self.events = {}
        self.info = CustomInfo()
        self.enabled = True
        self.visible = True
        self.id = Control._control_id
        Control._control_id += 1
        
    def create(self):
        """创建控件（子类需要重写）"""
        pass
        
    def bind_event(self, event_name: str, callback: Callable):
        """绑定事件处理函数"""
        self.events[event_name] = callback
        
    def trigger_event(self, event_name: str, *args):
        """触发事件"""
        if event_name in self.events:
            try:
                self.events[event_name](*args)
            except Exception as e:
                logger.error(f"事件处理错误: {e}")
                
    def set_position(self, x: int, y: int):
        """设置控件位置"""
        self.x = x
        self.y = y
        if self.hwnd:
            win32gui.SetWindowPos(self.hwnd, None, x, y, 0, 0,
                                 win32con.SWP_NOSIZE | win32con.SWP_NOZORDER)
                                 
    def set_size(self, width: int, height: int):
        """设置控件大小"""
        self.width = width
        self.height = height
        if self.hwnd:
            win32gui.SetWindowPos(self.hwnd, None, 0, 0, width, height,
                                 win32con.SWP_NOMOVE | win32con.SWP_NOZORDER)
    
    def set_enabled(self, enabled: bool):
        """设置控件启用状态"""
        self.enabled = enabled
        if self.hwnd:
            win32gui.EnableWindow(self.hwnd, enabled)
    
    def set_visible(self, visible: bool):
        """设置控件可见性"""
        self.visible = visible
        if self.hwnd:
            win32gui.ShowWindow(self.hwnd, win32con.SW_SHOW if visible else win32con.SW_HIDE)
    
    def get_text(self) -> str:
        """获取控件文本（修复解码错误和过时警告）"""
        if self.hwnd:
            # 第一步：获取文本长度（不含终止符）
            length = win32gui.SendMessage(self.hwnd, win32con.WM_GETTEXTLENGTH, 0, 0)
            if length == 0:
                return ""
            
            # 第二步：创建宽字符缓冲区（包含终止符，长度+1）
            # 使用 ctypes 更可靠地处理宽字符
            import ctypes
            buffer = ctypes.create_unicode_buffer(length + 1)
            
            # 第三步：获取文本（wParam 为缓冲区长度，lParam 为缓冲区指针）
            win32gui.SendMessage(self.hwnd, win32con.WM_GETTEXT, length + 1, ctypes.addressof(buffer))
            
            # 直接返回缓冲区内容（已自动处理 UTF-16 解码）
            return buffer.value
        return ""
    
    def set_text(self, text: str):
        """设置控件文本"""
        if self.hwnd:
            win32gui.SendMessage(self.hwnd, win32con.WM_SETTEXT, 0, text)

class Label(Control):
    """标签控件"""
    def __init__(self, parent, x: int, y: int, width: int, height: int,
                 text: str = "", style: int = ControlStyle.STATIC):
        super().__init__(parent, x, y, width, height, style, "STATIC")
        self.text = text
        self.create()
        
    def create(self):
        """创建标签"""
        self.hwnd = win32gui.CreateWindow(
            "STATIC",
            self.text,
            win32con.WS_CHILD | win32con.WS_VISIBLE | self.style,
            self.x, self.y, self.width, self.height,
            self.parent.hwnd,
            self.id,
            win32api.GetModuleHandle(None),
            None
        )

class Button(Control):
    """按钮控件"""
    def __init__(self, parent, x: int, y: int, width: int, height: int, 
                 text: str = "", style: int = ControlStyle.BUTTON):
        super().__init__(parent, x, y, width, height, style, "BUTTON")
        self.text = text
        self.create()
        
    def create(self):
        """创建按钮"""
        self.hwnd = win32gui.CreateWindow(
            "BUTTON",
            self.text,
            win32con.WS_CHILD | win32con.WS_VISIBLE | self.style,
            self.x, self.y, self.width, self.height,
            self.parent.hwnd,
            self.id,
            win32api.GetModuleHandle(None),
            None
        )

class CheckBox(Control):
    """复选框控件"""
    def __init__(self, parent, x: int, y: int, width: int, height: int,
                 text: str = "", checked: bool = False):
        super().__init__(parent, x, y, width, height, ControlStyle.CHECKBOX, "BUTTON")
        self.text = text
        self.checked = checked
        self.create()
        
    def create(self):
        """创建复选框"""
        self.hwnd = win32gui.CreateWindow(
            "BUTTON",
            self.text,
            win32con.WS_CHILD | win32con.WS_VISIBLE | self.style,
            self.x, self.y, self.width, self.height,
            self.parent.hwnd,
            self.id,
            win32api.GetModuleHandle(None),
            None
        )
        if self.checked:
            win32gui.SendMessage(self.hwnd, win32con.BM_SETCHECK, win32con.BST_CHECKED, 0)
            
    def is_checked(self) -> bool:
        """获取复选框状态"""
        return win32gui.SendMessage(self.hwnd, win32con.BM_GETCHECK, 0, 0) == win32con.BST_CHECKED
        
    def set_checked(self, checked: bool):
        """设置复选框状态"""
        win32gui.SendMessage(self.hwnd, win32con.BM_SETCHECK,
                           win32con.BST_CHECKED if checked else win32con.BST_UNCHECKED, 0)

class Edit(Control):
    """编辑框控件"""
    def __init__(self, parent, x: int, y: int, width: int, height: int,
                 text: str = "", multiline: bool = False, password: bool = False):
        style = ControlStyle.EDIT_MULTILINE if multiline else ControlStyle.EDIT_TEXT
        if password:
            style = ControlStyle.EDIT_PASSWORD
        super().__init__(parent, x, y, width, height, style, "EDIT")
        self.text = text
        self.multiline = multiline
        self.create()
        
    def create(self):
        """创建编辑框"""
        self.hwnd = win32gui.CreateWindow(
            "EDIT",
            self.text,
            win32con.WS_CHILD | win32con.WS_VISIBLE | win32con.WS_BORDER | self.style,
            self.x, self.y, self.width, self.height,
            self.parent.hwnd,
            self.id,
            win32api.GetModuleHandle(None),
            None
        )

class ListBox(Control):
    """列表框控件"""
    def __init__(self, parent, x: int, y: int, width: int, height: int):
        super().__init__(parent, x, y, width, height, ControlStyle.LISTBOX, "LISTBOX")
        self.items = []
        self.create()
        
    def create(self):
        """创建列表框"""
        self.hwnd = win32gui.CreateWindow(
            "LISTBOX",
            "",
            win32con.WS_CHILD | win32con.WS_VISIBLE | win32con.WS_BORDER | self.style,
            self.x, self.y, self.width, self.height,
            self.parent.hwnd,
            self.id,
            win32api.GetModuleHandle(None),
            None
        )
        
    def add_item(self, text: str):
        """添加列表项"""
        win32gui.SendMessage(self.hwnd, win32con.LB_ADDSTRING, 0, text)
        self.items.append(text)
        
    def remove_item(self, index: int):
        """删除列表项"""
        if 0 <= index < len(self.items):
            win32gui.SendMessage(self.hwnd, win32con.LB_DELETESTRING, index, 0)
            del self.items[index]
            
    def get_selected(self) -> int:
        """获取当前选中项索引"""
        return win32gui.SendMessage(self.hwnd, win32con.LB_GETCURSEL, 0, 0)
        
    def get_item(self, index: int) -> str:
        """获取指定索引的列表项"""
        if 0 <= index < len(self.items):
            return self.items[index]
        return ""
    
    def clear(self):
        """清空列表"""
        win32gui.SendMessage(self.hwnd, win32con.LB_RESETCONTENT, 0, 0)
        self.items.clear()

class ComboBox(Control):
    """组合框控件"""
    def __init__(self, parent, x: int, y: int, width: int, height: int):
        super().__init__(parent, x, y, width, height, ControlStyle.COMBOBOX, "COMBOBOX")
        self.items = []
        self.create()
        
    def create(self):
        """创建组合框"""
        self.hwnd = win32gui.CreateWindow(
            "COMBOBOX",
            "",
            win32con.WS_CHILD | win32con.WS_VISIBLE | win32con.WS_BORDER | self.style,
            self.x, self.y, self.width, self.height,
            self.parent.hwnd,
            self.id,
            win32api.GetModuleHandle(None),
            None
        )
        
    def add_item(self, text: str):
        """添加项"""
        win32gui.SendMessage(self.hwnd, win32con.CB_ADDSTRING, 0, text)
        self.items.append(text)
        
    def get_selected(self) -> int:
        """获取选中项索引"""
        return win32gui.SendMessage(self.hwnd, win32con.CB_GETCURSEL, 0, 0)
        
    def set_selected(self, index: int):
        """设置选中项"""
        win32gui.SendMessage(self.hwnd, win32con.CB_SETCURSEL, index, 0)
        
    def get_text(self) -> str:
        """获取选中文本"""
        index = self.get_selected()
        if index >= 0 and index < len(self.items):
            return self.items[index]
        return ""

class ProgressBar(Control):
    """进度条控件"""
    # 手动定义进度条消息常量
    PBM_SETRANGE = 0x0402
    PBM_SETRANGE32 = 0x0406
    PBM_SETPOS = 0x0400
    PBM_GETPOS = 0x0401
    
    def __init__(self, parent, x: int, y: int, width: int, height: int):
        super().__init__(parent, x, y, width, height, 0, "msctls_progress32")
        self.min_value = 0
        self.max_value = 100
        self.create()
        
    def create(self):
        """创建进度条"""
        self.hwnd = win32gui.CreateWindow(
            "msctls_progress32",
            "",
            win32con.WS_CHILD | win32con.WS_VISIBLE,
            self.x, self.y, self.width, self.height,
            self.parent.hwnd,
            self.id,
            win32api.GetModuleHandle(None),
            None
        )
        # 设置范围（使用手动定义的常量）
        win32gui.SendMessage(self.hwnd, self.PBM_SETRANGE, 0, self.max_value << 16)
        
    def set_range(self, min_val: int, max_val: int):
        """设置进度范围"""
        self.min_value = min_val
        self.max_value = max_val
        # 使用手动定义的常量
        win32gui.SendMessage(self.hwnd, self.PBM_SETRANGE32, min_val, max_val)
        
    def set_value(self, value: int):
        """设置进度值"""
        win32gui.SendMessage(self.hwnd, self.PBM_SETPOS, value, 0)
        
    def get_value(self) -> int:
        """获取进度值"""
        return win32gui.SendMessage(self.hwnd, self.PBM_GETPOS, 0, 0)

class Window:
    """窗口类，支持拖动和通信"""
    _windows = {}  # 存储所有窗口实例
    _message_handlers = {}  # 存储消息处理器
    
    def __init__(self, title: str = "Window", width: int = 800, height: int = 600,
                 window_type: str = WindowType.MAIN, style: int = WindowStyle.OVERLAPPED):
        self.title = title
        self.width = width
        self.height = height
        self.window_type = window_type
        self.style = style
        self.hwnd = None
        self.controls = []
        self.events = {}
        self._message_map = {}
        self.info = CustomInfo()
        self.parent = None
        self._dragging = False
        self._drag_pos = (0, 0)
        self.center_on_screen = True
        
    def create(self):
        """创建窗口"""
        if self.hwnd is not None:
            return
            
        # 注册窗口类
        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = self.wnd_proc
        wc.lpszClassName = f"MyWindowClass_{id(self)}"
        wc.hInstance = win32api.GetModuleHandle(None)
        wc.hCursor = win32gui.LoadCursor(0, win32con.IDC_ARROW)
        wc.hbrBackground = win32gui.GetStockObject(win32con.WHITE_BRUSH)
        
        class_atom = win32gui.RegisterClass(wc)
        
        # 计算窗口位置
        if self.center_on_screen:
            screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
            screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
            x = (screen_width - self.width) // 2
            y = (screen_height - self.height) // 2
        else:
            x = win32con.CW_USEDEFAULT
            y = win32con.CW_USEDEFAULT
        
        # 根据窗口类型设置样式
        if self.window_type == WindowType.CHILD:
            style = self.style | win32con.WS_CHILD
        elif self.window_type == WindowType.MODAL:
            style = self.style | win32con.WS_POPUP | win32con.WS_CAPTION | win32con.WS_SYSMENU
        elif self.window_type == WindowType.TOOL:
            style = self.style | win32con.WS_EX_TOOLWINDOW
        else:
            style = self.style
            
        # 创建窗口
        self.hwnd = win32gui.CreateWindow(
            class_atom,
            self.title,
            style,
            x, y,
            self.width, self.height,
            self.parent.hwnd if self.parent else 0,
            0,
            wc.hInstance,
            None
        )
        
        Window._windows[self.hwnd] = self
        
    def wnd_proc(self, hwnd, msg, wParam, lParam):
        """窗口过程函数"""
        # 处理窗口拖动
        if msg == win32con.WM_LBUTTONDOWN:
            # 检查是否点击在标题栏区域
            rect = win32gui.GetWindowRect(hwnd)
            title_bar_height = win32api.GetSystemMetrics(win32con.SM_CYCAPTION)
            click_y = win32api.HIWORD(lParam)
            
            if click_y < title_bar_height:
                self._dragging = True
                self._drag_pos = (win32api.LOWORD(lParam), win32api.HIWORD(lParam))
                win32gui.SetCapture(hwnd)
                
        elif msg == win32con.WM_MOUSEMOVE:
            if self._dragging:
                x = win32api.LOWORD(lParam) - self._drag_pos[0]
                y = win32api.HIWORD(lParam) - self._drag_pos[1]
                win32gui.SetWindowPos(hwnd, None, x, y, 0, 0,
                                    win32con.SWP_NOSIZE | win32con.SWP_NOZORDER)
                                    
        elif msg == win32con.WM_LBUTTONUP:
            self._dragging = False
            win32gui.ReleaseCapture()
            
        # 处理控件事件
        elif msg == win32con.WM_COMMAND:
            control_id = win32api.LOWORD(wParam)
            notification_code = win32api.HIWORD(wParam)
            
            for control in self.controls:
                if control.id == control_id:
                    if notification_code == win32con.BN_CLICKED:  # 按钮点击
                        control.trigger_event("click")
                    elif notification_code == win32con.EN_CHANGE:  # 编辑框内容改变
                        control.trigger_event("change")
                    elif notification_code == win32con.LBN_SELCHANGE:  # 列表框选择改变
                        control.trigger_event("select")
                    
        elif msg == win32con.WM_DESTROY:
            if hwnd in Window._windows:
                del Window._windows[hwnd]
            if not Window._windows:  # 如果没有其他窗口，退出消息循环
                win32gui.PostQuitMessage(0)
            return 0
            
        # 处理自定义消息
        elif msg == WindowMessage.WM_CUSTOM:
            self.handle_custom_message(wParam, lParam)
            
        # 处理其他自定义事件
        if msg in self._message_map:
            return self._message_map[msg](hwnd, msg, wParam, lParam)
            
        return win32gui.DefWindowProc(hwnd, msg, wParam, lParam)
        
    def handle_custom_message(self, wParam: int, lParam: int):
        """处理自定义消息"""
        message_id = wParam
        data = self.info.get('last_message', '')
        
        if isinstance(data, int):
            try:
                data = win32gui.PyGetString(data)
            except:
                data = str(data)
        
        if message_id in Window._message_handlers:
            Window._message_handlers[message_id](self, data)
            
    @staticmethod
    def register_message_handler(message_id: int, handler: Callable):
        """注册消息处理器"""
        Window._message_handlers[message_id] = handler
        
    @staticmethod
    def send_message(target_hwnd: int, message_id: int, data: Any = None):
        """发送消息到指定窗口"""
        if target_hwnd in Window._windows:
            if isinstance(data, str):
                window = Window._windows[target_hwnd]
                window.info.set('last_message', data)
            win32gui.SendMessage(target_hwnd, WindowMessage.WM_CUSTOM, message_id, 0)

    def bind_message(self, message: int, handler: Callable):
        """绑定Windows消息处理函数"""
        self._message_map[message] = handler
        
    def add_control(self, control: Control):
        """添加控件"""
        self.controls.append(control)
        
    def show(self):
        """显示窗口"""
        if self.hwnd is None:
            self.create()
        win32gui.ShowWindow(self.hwnd, win32con.SW_SHOW)
        win32gui.UpdateWindow(self.hwnd)
        
    def hide(self):
        """隐藏窗口"""
        if self.hwnd:
            win32gui.ShowWindow(self.hwnd, win32con.SW_HIDE)
        
    def close(self):
        """关闭窗口"""
        if self.hwnd:
            win32gui.DestroyWindow(self.hwnd)
            
    def set_title(self, title: str):
        """设置窗口标题"""
        self.title = title
        if self.hwnd:
            win32gui.SetWindowText(self.hwnd, title)
            
    def set_size(self, width: int, height: int):
        """设置窗口大小"""
        self.width = width
        self.height = height
        if self.hwnd:
            win32gui.SetWindowPos(self.hwnd, None, 0, 0, width, height,
                                 win32con.SWP_NOMOVE | win32con.SWP_NOZORDER)

class WindowManager:
    """窗口管理器"""
    @staticmethod
    def get_window_count() -> int:
        """获取当前窗口数量"""
        return len(Window._windows)
        
    @staticmethod
    def close_all():
        """关闭所有窗口"""
        for hwnd in list(Window._windows.keys()):
            win32gui.DestroyWindow(hwnd)
        Window._windows.clear()
        
    @staticmethod
    def get_window(hwnd: int) -> Optional[Window]:
        """根据窗口句柄获取窗口实例"""
        return Window._windows.get(hwnd)
        
    @staticmethod
    def find_window_by_title(title: str) -> Optional[Window]:
        """根据标题查找窗口"""
        for window in Window._windows.values():
            if window.title == title:
                return window
        return None

def show_message(title: str, message: str, msg_type: str = "info") -> int:
    """显示消息框"""
    type_map = {
        "info": win32con.MB_OK | win32con.MB_ICONINFORMATION,
        "warning": win32con.MB_OK | win32con.MB_ICONWARNING,
        "error": win32con.MB_OK | win32con.MB_ICONERROR,
        "question": win32con.MB_YESNO | win32con.MB_ICONQUESTION
    }
    return win32api.MessageBox(0, message, title, type_map.get(msg_type, type_map["info"]))

def select_file(title: str = "选择文件", filetypes: List[Tuple[str, str]] = None, 
               initial_dir: str = None) -> Optional[str]:
    """文件选择对话框"""
    if filetypes is None:
        filetypes = [("All Files", "*.*")]
    
    filter_str = ""
    for name, pattern in filetypes:
        filter_str += f"{name}\0{pattern}\0"
    filter_str += "\0"
    
    ofn = win32gui.OPENFILENAME()
    ofn.lStructSize = 76  # 结构体大小
    ofn.hwndOwner = 0
    ofn.hInstance = win32api.GetModuleHandle(None)
    ofn.lpstrFilter = filter_str
    ofn.nFilterIndex = 1
    ofn.lpstrFile = "\0" * 256
    ofn.nMaxFile = 256
    ofn.lpstrTitle = title
    ofn.Flags = win32con.OFN_FILEMUSTEXIST | win32con.OFN_PATHMUSTEXIST | win32con.OFN_HIDEREADONLY
    
    if initial_dir:
        ofn.lpstrInitialDir = initial_dir
    
    try:
        if win32gui.GetOpenFileName(ofn):
            return ofn.lpstrFile
    except Exception as e:
        logger.error(f"文件选择对话框错误: {e}")
    return None

def select_folder(title: str = "选择文件夹", initial_dir: str = None) -> Optional[str]:
    """文件夹选择对话框"""
    try:
        from win32com.shell import shell, shellcon
        pidl = shell.SHBrowseForFolder(
            0, None, title, 0, None, None
        )
        if pidl:
            path = shell.SHGetPathFromIDList(pidl)
            return path
    except Exception as e:
        logger.error(f"文件夹选择对话框错误: {e}")
    return None

# 使用示例
if __name__ == "__main__":
    def on_button_click(window):
        """按钮点击事件处理"""
        Window.send_message(window.hwnd, 1, "Hello from button!")
        
    def handle_message(window, data):
        """消息处理器"""
        print(f"Received message: {data}")
        show_message("消息", f"收到消息: {data}")
        
    # 注册消息处理器
    Window.register_message_handler(1, handle_message)
    
    # 创建主窗口
    main_window = Window("主窗口示例", 500, 400)
    main_window.show()
    
    # 添加标签
    label = Label(main_window, 20, 20, 200, 25, "这是一个标签:")
    main_window.add_control(label)
    
    # 添加编辑框
    edit = Edit(main_window, 20, 50, 200, 25, "编辑框内容")
    edit.bind_event("change", lambda: print(f"编辑框内容改变: {edit.get_text()}"))
    main_window.add_control(edit)
    
    # 添加按钮
    button = Button(main_window, 20, 90, 100, 30, "点击我")
    button.bind_event("click", lambda: on_button_click(main_window))
    main_window.add_control(button)
    
    # 添加复选框
    checkbox = CheckBox(main_window, 20, 130, 100, 30, "选择我")
    checkbox.bind_event("click", lambda: print(f"复选框状态: {checkbox.is_checked()}"))
    main_window.add_control(checkbox)
    
    # 添加列表框
    listbox = ListBox(main_window, 20, 170, 200, 100)
    listbox.add_item("选项1")
    listbox.add_item("选项2")
    listbox.add_item("选项3")
    listbox.bind_event("select", lambda: print(f"选中项: {listbox.get_selected()}"))
    main_window.add_control(listbox)
    
    # 添加组合框
    combobox = ComboBox(main_window, 20, 280, 150, 25)
    combobox.add_item("选项A")
    combobox.add_item("选项B")
    combobox.add_item("选项C")
    main_window.add_control(combobox)
    
    # 添加进度条
    progress = ProgressBar(main_window, 20, 320, 200, 20)
    progress.set_value(50)
    main_window.add_control(progress)
    
    # 启动消息循环
    win32gui.PumpMessages()