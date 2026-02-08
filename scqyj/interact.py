"""
交互脚本
Interactive Script
"""
# =======================================================================


# 先用较为简陋的ybc_ui代替 Use ybc_ui instead of pgzero temporarily
try:
    from ybc_ui import index_button, picker_button, input as input_text
except ModuleNotFoundError:
    def index_button(message, buttons):
        return 0
    def picker_button(message, buttons):
        return '1'
    def input_text(message, buttons):
        return ''


exception_flag = False

# 检查与获取环境信息 Check and get environmental information
try:
    with open('./data.rst.txt', 'r') as data_file: # 为什么不用json：reST更方便读写和调试
        content = data_file.readlines() # Why not using json: reST is more convenient for reading, writing and debugging
except Exception as e:
    if type(e).__name__ not in ('OSError', 'FileNotFoundError'):
        raise
    exception_flag = True
    print('Initializing... \n')
    with open('./data.rst.txt', 'w') as new_data:
        content = ['.. projectnames::\n']
        new_data.write(''.join(content))
    print('Succeed. ')

'''
# Deprecated 已弃用

def get_indentation(line: str) -> str:
    """
    获取行前用于缩进的字符。
    Get characters that have been used to indent. 

    :param line: A line of sentences. 一行文字
    :type line: str
    :return: The characters that have been used to indent. 用于缩进的字符
    :rtype: str
    :raise TypeError: If line is not str. 若line不是str类型
    """
    
    if not isinstance(line, str):
        raise TypeError(
            f'Argument line must be str, not {type(str).__qualname__}. '
        )
    indentation = ''
    for i in line:
        if i == ' ' or i == '\t':
            indentation += i
        else:
            return indentation
'''

class SCQYJProject:

    """
    Create an instance that supports turning your idea into code. 

    You give the instructions, then a pgzero project borns. 
    """

    def __init__(self):
        pass
    
    def load(self, instr_lines):
        """
        Load from str forms of SCQYJ instructions
        """

class ProjectData:

    """
    Create an instance of the data from ``data.rst.txt``. 

    These arguments will be stored as attributes with the same names: 
    :param projectnames:
    :param projects:

    :ivar projectnames: The name list of all projects. 
    :type projectnames: list[str]
    :ivar projects: A mapping of all information of the projects. 
    :type projects: dict[str, list[str]]
    """

    __slots__ = ['projectnames', 'projects']

    def __init__(self):
        self.projectnames = []
        self.projects = {}
    
    def load(self, lines: list[str]) -> None:
        """
        Load from a list of text. 

        :param lines: A list of text, usually from method ``readlines()`` of a file object. 
        :type lines: list[str]
        :raise TypeError: If argument ``lines`` is not a list. 
        """
        if not isinstance(lines, list):
            raise TypeError(
            f'Argument "lines" must be a list, not {type(lines).__name__}. '
            )
        mode = 0
        temp_name = ''
        for i in content:
            strip_i = i.strip()
            if not strip_i:
                continue
            if i.startswith('.. '):
                rest_i = i[3:].lstrip()
                if '::' in rest_i:
                    if rest_i.startswith('projectnames'):
                        mode = 1
                    elif rest_i.startswith('project'):
                        mode = 2
                        temp_name = rest_i[rest_i.find('::') + 2:].strip()
                        self.projects[temp_name] = []
            elif mode == 1:
                self.projectnames.append(strip_i)
            elif mode == 2:
                self.projects[temp_name].append(strip_i)
    
    def new(self, name: str) -> list:
        """
        Create a new project. 

        :param name: The name of the project. 
        :type name: str
        :return: An empty list(:code:`[]`). 
        :rtype: list
        :raise TypeError: If ``name`` is not an str. 
        """
        if not isinstance(name, str):
            raise TypeError(
            f'Argument "name" must be str, not {type(name).__name__}. '
            )
        self.projectnames.append(name)
        self.projects[name] = []
        return self.projects[name]
    
    def open(self, projectname: str) -> list[str]:
        """
        Open an project with ybc_ui. 

        :param project_name: The name of the project. 
        :type project_name: str
        :return: Handled project content. 
        :rtype: list[str]
        """
        content = self.projects.get(projectname)
        if content is None:
            print('The project is not found, trying creating... ')
            content = self.new(projectname)
            print('Created. ')
        for i in content:
            instructions = i.split(' ')

# 处理环境信息 Deal with environmental information
data = ProjectData()

# Conditions 条件与判断
welcome_prompt = 'Welcome\n欢迎' if exception_flag else 'Welcome back\n欢迎回来'
running = __name__ == '__main__'

while running:
    op = picker_button(
        welcome_prompt, 
        [
            '+ 新项目', 
            *map(lambda x: f'[{x}]', data.projectnames), 
            '- 设置', 
            '× 关闭'
        ]
    )
    if op == '× 关闭':
        break
    elif op == '+ 新项目':
        new_pname = input_text('+ 请输入项目名称')
        if new_pname:
            data.new(new_pname)
    elif op == '- 设置':
        while True:
            op_set = index_button()
    else:
        data.open(op)