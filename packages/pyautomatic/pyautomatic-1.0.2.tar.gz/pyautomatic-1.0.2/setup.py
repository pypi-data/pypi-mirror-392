import setuptools
import os

def check_dependencies():
    """检查必要的依赖包"""
    missing_deps = []
    
    # 检查核心依赖
    dependencies = [
        "pywin32",      # win32api, win32con, win32process, win32security, win32gui, win32event, win32com
        "psutil",       # 系统进程和系统利用率工具
        "comtypes",     # COM支持
        "pycaw",        # Windows音频控制
        "pycryptodome", # Crypto模块 (AES加密等)
        "requests",     # HTTP请求
        "tqdm",        # 进度条
    ]
    
    for dep in dependencies:
        try:
            __import__(dep.replace("-", "_"))
        except ImportError:
            missing_deps.append(dep)
    
    return missing_deps

def main():

    """     # 检查依赖
    missing_deps = check_dependencies()
    if missing_deps:
        print("Missing required dependencies. Please install them using:")
        print(f"pip install {' '.join(missing_deps)}")
        exit(1) """

    setuptools.setup(
        name="pyautomatic",
        version="1.0.2",
        author="xiaotbl",
        author_email="monios114514@outlook.com",
        description="A comprehensive Python automation toolkit for Windows",
        long_description=open("README.md", encoding="utf-8").read() if os.path.exists("README.md") else "",
        long_description_content_type="text/markdown",
        packages=setuptools.find_packages(),
        package_dir={'pyautomatic': 'pyautomatic'},
        classifiers=[
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8", 
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
            "License :: OSI Approved :: MIT License",
            "Operating System :: Microsoft :: Windows",
            "Operating System :: Microsoft :: Windows :: Windows 10",
            "Operating System :: Microsoft :: Windows :: Windows 11",
            "Development Status :: 4 - Beta",
            "Intended Audience :: Developers",
            "Topic :: Software Development :: Libraries :: Python Modules",
            "Topic :: System :: Systems Administration",
            "Topic :: Utilities",
        ],
        python_requires=">=3.7",
        install_requires=[
            "pywin32>=300",          # Windows API访问
            "psutil>=5.9.0",         # 系统进程和利用率监控
            "comtypes>=1.1.14",      # COM组件支持
            "pycaw>=20181226",       # Windows音频控制
            "pycryptodome>=3.17.0",  # 加密功能 (替代pycrypto)
            "requests>=2.28.0",      # HTTP请求
            "tqdm>=4.64.0",          # 进度条显示
        ],
        extras_require={
            'dev': [
                'pytest>=7.0.0',
                'pytest-cov>=4.0.0',
                'black>=22.0.0',
                'flake8>=5.0.0',
            ],
            'gui': [
                'PyQt5>=5.15.0',
                'wxPython>=4.2.0',
            ]
        },
        entry_points={
            'console_scripts': [
                # 示例：'pyautomatic=pyautomatic.cli:main',
            ],
        },
        include_package_data=True,
        zip_safe=False,
        keywords=[
            "automation",
            "windows", 
            "system-administration",
            "win32",
            "process-management",
            "audio-control",
            "encryption",
        ],
        project_urls={
            "Bug Reports": "https://github.com/xiaotbl/pyautomatic/issues",
            "Source": "https://github.com/xiaotbl/pyautomatic",
        },
    )

if __name__ == "__main__":
    main()