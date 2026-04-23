import platform

VERSION = '1.0.0'
__version__ = VERSION

# 直接运行
if __name__ == '__main__':
    from parser import *
    from renderer import *

# 猿编程环境，即Skulpt环境
elif platform.python_implementation() == 'Skulpt':
    try:
        from mdparser.parser import *
        from mdparser.renderer import *
    except ModuleNotFoundError:
        print('Import failed. Try placing the mdparser directory in the same directory as the currently running file. ')
        print('导入失败。尝试将mdparser目录放在当前运行的文件所在目录下。')
        raise

# 普通环境
else:
    from .parser import *
    from .renderer import *