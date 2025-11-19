import tkinter as tk

# ==================== 基础数学函数 ====================

def cos(x):
    """实现cos函数 - 使用泰勒级数展开
    cos(x) = 1 - x²/2! + x⁴/4! - x⁶/6! + ...
    """
    n = 0
    term = 1
    cos_sum = 0
    while abs(term) > 1e-10:
        cos_sum += term
        n += 1
        term = (-1)**n * x**(2*n) / factorial(2*n)
    return cos_sum

def sin(x):
    """实现sin函数 - 使用泰勒级数展开
    sin(x) = x - x³/3! + x⁵/5! - x⁷/7! + ...
    """
    n = 0
    term = x
    sin_sum = 0
    while abs(term) > 1e-10:
        sin_sum += term
        n += 1
        term = (-1)**n * x**(2*n+1) / factorial(2*n+1)
    return sin_sum

def tan(x):
    """实现tan函数 - 使用sin/cos的比值
    tan(x) = sin(x) / cos(x)
    """
    return sin(x) / cos(x)

def sqrt(x):
    """实现平方根函数 - 使用牛顿迭代法
    x_(n+1) = (x_n + a/x_n) / 2
    """
    if x < 0:
        raise ValueError("math domain error")
    if x == 0:
        return 0
    guess = x
    while True:
        new_guess = (guess + x/guess) / 2
        if abs(new_guess - guess) < 1e-10:
            return new_guess
        guess = new_guess

def log(x):
    """实现自然对数函数 - 使用牛顿迭代法"""
    if x <= 0:
        raise ValueError("math domain error")
    if x == 1:
        return 0
    guess = x - 1
    while True:
        new_guess = guess + 2 * (x - exp(guess)) / (x + exp(guess))
        if abs(new_guess - guess) < 1e-10:
            return new_guess
        guess = new_guess

def exp(x):
    """实现指数函数 - 使用泰勒级数展开
    e^x = 1 + x + x²/2! + x³/3! + ...
    """
    n = 0
    term = 1
    exp_sum = 0
    while abs(term) > 1e-10:
        exp_sum += term
        n += 1
        term = x**n / factorial(n)
    return exp_sum

def factorial(n):
    """计算阶乘
    n! = n × (n-1) × (n-2) × ... × 1
    """
    if n < 0:
        raise ValueError("factorial() not defined for negative values")
    if n == 0 or n == 1:
        return 1
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

# ==================== 双曲函数 ====================

def sinh(x):
    """实现双曲正弦函数
    sinh(x) = (e^x - e^(-x)) / 2
    """
    return (exp(x) - exp(-x)) / 2

def cosh(x):
    """实现双曲余弦函数
    cosh(x) = (e^x + e^(-x)) / 2
    """
    return (exp(x) + exp(-x)) / 2

def tanh(x):
    """实现双曲正切函数
    tanh(x) = sinh(x) / cosh(x)
    """
    return sinh(x) / cosh(x)

# ==================== 反三角函数 ====================

def asin(x):
    """实现反正弦函数 - 使用牛顿迭代法"""
    if x < -1 or x > 1:
        raise ValueError("math domain error")
    guess = x
    while True:
        new_guess = guess - (sin(guess) - x) / cos(guess)
        if abs(new_guess - guess) < 1e-10:
            return new_guess
        guess = new_guess

def acos(x):
    """实现反余弦函数 - 使用asin的关系
    acos(x) = π/2 - asin(x)
    """
    if x < -1 or x > 1:
        raise ValueError("math domain error")
    return 1.5707963267948966 - asin(x)  # π/2

def atan(x):
    """实现反正切函数 - 使用牛顿迭代法"""
    guess = x
    while True:
        new_guess = guess - (tan(guess) - x) / (1 + tan(guess)**2)
        if abs(new_guess - guess) < 1e-10:
            return new_guess
        guess = new_guess

# ==================== 基础数学运算 ====================

def absolute(x):
    """实现绝对值函数"""
    return x if x >= 0 else -x

def pow(x, y):
    """实现幂函数 - 优化精度"""
    if x < 0:
        raise ValueError("math domain error")
    if y == 0:
        return 1
    if y == 1:
        return x
    if y == 2:
        return x * x
    # 对于整数幂，使用快速幂算法
    if int(y) == y:
        result = 1
        base = x
        exponent = int(y)
        while exponent > 0:
            if exponent % 2 == 1:
                result *= base
            base *= base
            exponent //= 2
        return result
    # 对于非整数幂，使用exp和log
    return exp(y * log(x))

def ceil(x):
    """实现向上取整函数"""
    if x == int(x):
        return int(x)
    return int(x) + 1 if x > 0 else int(x)

def floor(x):
    """实现向下取整函数"""
    return int(x) if x >= 0 else int(x) - (0 if x == int(x) else 1)

# ==================== 图形绘制函数 ====================

def create_drawing_window(width=800, height=600, title="Math Drawing"):
    """创建绘图窗口
    Args:
        width: 窗口宽度
        height: 窗口高度
        title: 窗口标题
    Returns:
        tuple: (window, canvas) 窗口和画布对象
    """
    window = tk.Tk()
    window.title(title)
    canvas = tk.Canvas(window, width=width, height=height)
    canvas.pack()
    return window, canvas

def draw_chord(canvas, center_x, center_y, radius, start_angle, end_angle, color="black", width=3):
    """绘制弦
    Args:
        canvas: 画布对象
        center_x: 圆心x坐标
        center_y: 圆心y坐标
        radius: 半径
        start_angle: 起始角度（弧度）
        end_angle: 结束角度（弧度）
        color: 线条颜色
        width: 线条宽度
    """
    x1 = center_x + radius * cos(start_angle)
    y1 = center_y - radius * sin(start_angle)
    x2 = center_x + radius * cos(end_angle)
    y2 = center_y - radius * sin(end_angle)
    canvas.create_line(x1, y1, x2, y2, fill=color, width=width)

def draw_circle(canvas, center_x, center_y, radius, color="black", width=3):
    """绘制圆
    Args:
        canvas: 画布对象
        center_x: 圆心x坐标
        center_y: 圆心y坐标
        radius: 半径
        color: 线条颜色
        width: 线条宽度
    """
    x1 = center_x - radius
    y1 = center_y - radius
    x2 = center_x + radius
    y2 = center_y + radius
    canvas.create_oval(x1, y1, x2, y2, outline=color, width=width)

def draw_arc(canvas, center_x, center_y, radius, start_angle, end_angle, color="black", width=3):
    """绘制弧
    Args:
        canvas: 画布对象
        center_x: 圆心x坐标
        center_y: 圆心y坐标
        radius: 半径
        start_angle: 起始角度（弧度）
        end_angle: 结束角度（弧度）
        color: 线条颜色
        width: 线条宽度
    """
    x1 = center_x - radius
    y1 = center_y - radius
    x2 = center_x + radius
    y2 = center_y + radius
    extent = (end_angle - start_angle) * 180 / 3.141592653589793
    canvas.create_arc(x1, y1, x2, y2, start=start_angle * 180 / 3.141592653589793, 
                      extent=extent, outline=color, style="arc", width=width)

def draw_polygon(canvas, points, color="black", width=3):
    """绘制多边形
    Args:
        canvas: 画布对象
        points: 坐标列表 [(x1,y1), (x2,y2), ...]
        color: 线条颜色
        width: 线条宽度
    """
    flat_points = [coord for point in points for coord in point]
    canvas.create_polygon(flat_points, outline=color, fill="", width=width)

def draw_point(canvas, x, y, color="black", size=4):
    """绘制点
    Args:
        canvas: 画布对象
        x: x坐标
        y: y坐标
        color: 点的颜色
        size: 点的大小
    """
    canvas.create_oval(x-size, y-size, x+size, y+size, fill=color, outline=color)

def draw_line(canvas, x1, y1, x2, y2, color="black", width=3):
    """绘制直线
    Args:
        canvas: 画布对象
        x1, y1: 起点坐标
        x2, y2: 终点坐标
        color: 线条颜色
        width: 线条宽度
    """
    canvas.create_line(x1, y1, x2, y2, fill=color, width=width)

def draw_ellipse(canvas, center_x, center_y, width, height, color="black", line_width=3):
    """绘制椭圆
    Args:
        canvas: 画布对象
        center_x: 中心x坐标
        center_y: 中心y坐标
        width: 椭圆宽度
        height: 椭圆高度
        color: 线条颜色
        line_width: 线条宽度
    """
    x1 = center_x - width/2
    y1 = center_y - height/2
    x2 = center_x + width/2
    y2 = center_y + height/2
    canvas.create_oval(x1, y1, x2, y2, outline=color, width=line_width)

# ==================== 演示函数 ====================

def demo_chords():
    """演示弦的绘制 - 单独窗口"""
    window, canvas = create_drawing_window(600, 600, "Chords Demo")
    
    # 绘制主圆
    draw_circle(canvas, 300, 300, 200, "blue", 3)
    
    # 绘制多条弦，展示不同角度
    angles = [
        (0, 3.141592653589793/3),      # 60度
        (3.141592653589793/4, 3.141592653589793/2),  # 45到90度
        (3.141592653589793/2, 2*3.141592653589793/3), # 90到120度
        (2*3.141592653589793/3, 5*3.141592653589793/6) # 120到150度
    ]
    
    colors = ["red", "green", "purple", "orange"]
    for (start, end), color in zip(angles, colors):
        draw_chord(canvas, 300, 300, 200, start, end, color, 3)
    
    # 添加角度标注
    canvas.create_text(300, 50, text="Chords Demo", font=("Arial", 16, "bold"))
    canvas.create_text(300, 550, text="Different angle chords", font=("Arial", 12))
    
    window.mainloop()

def demo_general():
    """演示一般图形绘制"""
    window, canvas = create_drawing_window()
    
    # 绘制坐标系
    draw_line(canvas, 50, 300, 750, 300, "gray", 2)  # x轴
    draw_line(canvas, 400, 50, 400, 550, "gray", 2)  # y轴
    
    # 绘制圆和椭圆
    draw_circle(canvas, 400, 300, 100, "blue", 3)
    draw_ellipse(canvas, 200, 300, 120, 80, "green", 3)
    
    # 绘制弧
    draw_arc(canvas, 400, 300, 100, 0, 3.141592653589793/2, "orange", 3)
    
    # 绘制多边形
    triangle = [(600, 200), (650, 300), (550, 300)]
    draw_polygon(canvas, triangle, "brown", 3)
    
    # 绘制点
    for i in range(5):
        draw_point(canvas, 100 + i*30, 200 + i*20, "navy", 4)
    
    window.mainloop()

if __name__ == "__main__":
    # 测试数学函数
    print("=== 数学函数测试 ===")
    print("cos(0.5) =", cos(0.5))
    print("sin(0.5) =", sin(0.5))
    print("tan(0.5) =", tan(0.5))
    print("sqrt(2) =", sqrt(2))
    print("log(2) =", log(2))
    print("exp(2) =", exp(2))
    print("factorial(5) =", factorial(5))
    print("sinh(1) =", sinh(1))
    print("cosh(1) =", cosh(1))
    print("tanh(1) =", tanh(1))
    print("asin(0.5) =", asin(0.5))
    print("acos(0.5) =", acos(0.5))
    print("atan(1) =", atan(1))
    print("absolute(-5) =", absolute(-5))
    print("pow(2, 3) =", pow(2, 3))
    print("ceil(3.7) =", ceil(3.7))
    print("floor(3.7) =", floor(3.7))
    
    # 运行绘图演示
    print("\n=== 启动图形演示 ===")
    print("1. 弦的演示窗口")
    demo_chords()
    print("2. 一般图形演示窗口")
    demo_general()
