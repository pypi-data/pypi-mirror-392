import sys
import os
import win32api
import win32con
import win32gui
import win32ui
from typing import Optional, List, Tuple, Callable, Dict, Any, Union

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
    }
    
    # 字体
    FONTS = {
        'default': ('Arial', 10),
        'title': ('Arial', 14, True),
        'small': ('Arial', 8),
    }
    
    @staticmethod
    def get_color(color_name: str) -> int:
        """获取颜色值"""
        return Style.COLORS.get(color_name.lower(), Style.COLORS['black'])
        
    @staticmethod
    def get_font(font_name: str) -> Tuple[str, int, bool]:
        """获取字体信息"""
        return Style.FONTS.get(font_name.lower(), Style.FONTS['default'])

class WindowStyle:
    """窗口样式常量"""
    OVERLAPPED = win32con.WS_OVERLAPPEDWINDOW
    POPUP = win32con.WS_POPUPWINDOW
    CHILD = win32con.WS_CHILDWINDOW
    MINIMIZE = win32con.WS_MINIMIZEBOX
    MAXIMIZE = win32con.WS_MAXIMIZEBOX
    THICKFRAME = win32con.WS_THICKFRAME

class ControlStyle:
    """控件样式常量"""
    BUTTON = win32con.BS_PUSHBUTTON
    CHECKBOX = win32con.BS_CHECKBOX
    RADIO = win32con.BS_RADIOBUTTON
    GROUPBOX = win32con.BS_GROUPBOX
    EDIT_TEXT = win32con.ES_AUTOHSCROLL
    EDIT_MULTILINE = win32con.ES_MULTILINE | win32con.ES_AUTOVSCROLL
    LISTBOX = win32con.LBS_STANDARD
    COMBOBOX = win32con.CBS_DROPDOWN

class WindowType:
    """窗口类型常量"""
    MAIN = "main"
    CHILD = "child"
    MODAL = "modal"
    TOOL = "tool"
    POPUP = "popup"

class WindowMessage:
    """窗口消息常量"""
    # 自定义消息范围
    WM_USER = win32con.WM_USER
    WM_CUSTOM = WM_USER + 1
    
    # 窗口拖动相关
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
    def __init__(self, parent, x: int, y: int, width: int, height: int, style: int = 0):
        self.parent = parent
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.style = style
        self.hwnd = None
        self.events = {}
        self.info = CustomInfo()
        
    def bind_event(self, event_name: str, callback: Callable):
        """绑定事件处理函数"""
        self.events[event_name] = callback
        
    def trigger_event(self, event_name: str, *args):
        """触发事件"""
        if event_name in self.events:
            self.events[event_name](*args)
            
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

class Button(Control):
    """按钮控件"""
    def __init__(self, parent, x: int, y: int, width: int, height: int, 
                 text: str = "", style: int = ControlStyle.BUTTON):
        super().__init__(parent, x, y, width, height, style)
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
            0,
            win32api.GetModuleHandle(None),
            None
        )

class CheckBox(Control):
    """复选框控件"""
    def __init__(self, parent, x: int, y: int, width: int, height: int,
                 text: str = "", checked: bool = False):
        super().__init__(parent, x, y, width, height, ControlStyle.CHECKBOX)
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
            0,
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
                 text: str = "", multiline: bool = False):
        style = ControlStyle.EDIT_MULTILINE if multiline else ControlStyle.EDIT_TEXT
        super().__init__(parent, x, y, width, height, style)
        self.text = text
        self.create()
        
    def create(self):
        """创建编辑框"""
        self.hwnd = win32gui.CreateWindow(
            "EDIT",
            self.text,
            win32con.WS_CHILD | win32con.WS_VISIBLE | win32con.WS_BORDER | self.style,
            self.x, self.y, self.width, self.height,
            self.parent.hwnd,
            0,
            win32api.GetModuleHandle(None),
            None
        )
        
    def get_text(self) -> str:
        """获取编辑框文本"""
        length = win32gui.SendMessage(self.hwnd, win32con.WM_GETTEXTLENGTH, 0, 0)
        buffer = win32gui.PyGetString(length + 1)
        win32gui.SendMessage(self.hwnd, win32con.WM_GETTEXT, length + 1, buffer)
        return buffer
        
    def set_text(self, text: str):
        """设置编辑框文本"""
        win32gui.SendMessage(self.hwnd, win32con.WM_SETTEXT, 0, text)

class ListBox(Control):
    """列表框控件"""
    def __init__(self, parent, x: int, y: int, width: int, height: int):
        super().__init__(parent, x, y, width, height, ControlStyle.LISTBOX)
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
            0,
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
        
    def create(self):
        """创建窗口"""
        # 如果窗口已经创建，直接返回
        if self.hwnd is not None:
            return
            
        # 注册窗口类
        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = self.wnd_proc
        wc.lpszClassName = f"MyWindowClass_{id(self)}"
        wc.hInstance = win32api.GetModuleHandle(None)
        wc.hCursor = win32gui.LoadCursor(0, win32con.IDC_ARROW)
        wc.hbrBackground = win32gui.GetStockObject(win32con.WHITE_BRUSH)  # 添加背景刷
        
        class_atom = win32gui.RegisterClass(wc)
        
        # 根据窗口类型设置样式
        if self.window_type == WindowType.CHILD:
            style = self.style | win32con.WS_CHILD | win32con.WS_CLIPCHILDREN | win32con.WS_CLIPSIBLINGS
        elif self.window_type == WindowType.MODAL:
            style = self.style | win32con.WS_POPUP | win32con.WS_CAPTION
        elif self.window_type == WindowType.TOOL:
            style = self.style | win32con.WS_EX_TOOLWINDOW
        else:
            style = self.style
            
        # 创建窗口
        self.hwnd = win32gui.CreateWindow(
            class_atom,
            self.title,
            style,
            win32con.CW_USEDEFAULT,
            win32con.CW_USEDEFAULT,
            self.width,
            self.height,
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
            for control in self.controls:
                if control.hwnd and win32gui.GetWindowLong(control.hwnd, win32con.GWL_ID) == control_id:
                    control.trigger_event("click")
                    
        elif msg == win32con.WM_DESTROY:
            del Window._windows[hwnd]
            if not Window._windows:  # 如果没有其他窗口，退出消息循环
                win32gui.PostQuitMessage(0)
            return 0
            
        # 处理自定义消息
        elif msg == WindowMessage.WM_CUSTOM:
            self.handle_custom_message(wParam, lParam)
            
        # 处理其他自定义事件
        if msg in self._message_map:
            return self._message_map[msg](hwnd,msg,wParam,lParam)
            
        return win32gui.DefWindowProc(hwnd, msg, wParam, lParam)
        
    def handle_custom_message(self, wParam: int, lParam: int):
        """处理自定义消息"""
        message_id = wParam
        # 从窗口实例中获取存储的消息
        data = self.info.get('last_message', '')
        
        if message_id in Window._message_handlers:
            Window._message_handlers[message_id](self,data)

        
        # 如果是指针，转换为字符串
        if isinstance(data, int):
            try:
                data = win32gui.PyGetString(data)
            except:
                data = str(data)
        
        if message_id in Window._message_handlers:
            Window._message_handlers[message_id](self,data)

            
    @staticmethod
    def register_message_handler(message_id: int, handler: Callable):
        """注册消息处理器"""
        Window._message_handlers[message_id] = handler
        
    @staticmethod
    def send_message(target_hwnd: int, message_id: int, data: Any = None):
        """发送消息到指定窗口"""
        if target_hwnd in Window._windows:
            # 直接使用字符串数据
            if isinstance(data, str):
                # 将字符串存储在窗口类的实例中
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
        win32gui.UpdateWindow(self.hwnd)  # 强制立即重绘窗口
        
    def close(self):
        """关闭窗口"""
        if self.hwnd:
            win32gui.DestroyWindow(self.hwnd)

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

def show_message(title: str, message: str, msg_type: str = "info") -> int:
    """显示消息框"""
    type_map = {
        "info": win32con.MB_OK | win32con.MB_ICONINFORMATION,
        "warning": win32con.MB_OK | win32con.MB_ICONWARNING,
        "error": win32con.MB_OK | win32con.MB_ICONERROR
    }
    return win32api.MessageBox(0, message, title, type_map.get(msg_type, type_map["info"]))

def select_file(title: str = "选择文件", filetypes: List[Tuple[str, str]] = None) -> Optional[str]:
    """文件选择对话框"""
    if filetypes is None:
        filetypes = [("All Files", "*.*")]
    
    filter_str = ""
    for name, pattern in filetypes:
        filter_str += f"{name}\0{pattern}\0"
    filter_str += "\0"
    
    ofn = win32gui.OPENFILENAME()
    ofn.hwndOwner = 0
    ofn.hInstance = win32api.GetModuleHandle(None)
    ofn.lpstrFilter = filter_str
    ofn.nFilterIndex = 1
    ofn.lpstrFile = ""
    ofn.nMaxFile = 256
    ofn.lpstrTitle = title
    ofn.Flags = win32con.OFN_FILEMUSTEXIST | win32con.OFN_HIDEREADONLY
    
    try:
        if win32gui.GetOpenFileName(ofn):
            return ofn.lpstrFile
    except:
        return None
    return None

if __name__ == "__main__":
    # 测试代码
    def on_button_click(window):
        """按钮点击事件处理"""
        Window.send_message(window.hwnd, 1, "Hello from button!")
        
    def handle_message(window, data):
        """消息处理器"""
        print(f"Received message: {data}")
        
    # 注册消息处理器
    Window.register_message_handler(1, handle_message)
    
    # 创建主窗口
    main_window = Window("主窗口", 400, 300)
    main_window.show()  # 先显示窗口

    # 添加按钮
    button = Button(main_window, 50, 50, 100, 30, "点击我")
    button.bind_event("click", lambda: on_button_click(main_window))
    main_window.add_control(button)

    # 添加复选框
    checkbox = CheckBox(main_window, 50, 100, 100, 30, "选择我")
    main_window.add_control(checkbox)

    # 添加列表框
    listbox = ListBox(main_window, 50, 150, 200, 100)
    listbox.add_item("选项1")
    listbox.add_item("选项2")
    listbox.add_item("选项3")
    main_window.add_control(listbox)

    # 创建子窗口
    child = Window("子窗口", 300, 200, WindowType.CHILD)
    child.parent = main_window
    child.show()  # 先显示子窗口

    # 在子窗口中添加按钮
    child_button = Button(child, 50, 50, 100, 30, "发送消息")
    child_button.bind_event("click", lambda: Window.send_message(main_window.hwnd, 1, "Hello from child!"))
    child.add_control(child_button)

    
    # 启动消息循环
    win32gui.PumpMessages()
