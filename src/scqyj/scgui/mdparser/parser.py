import re


class HTMLSyntaxError(SyntaxError):

    """Create an error that caused by HTML syntax mistakes. """

    pass

class TextSlice:

    __slots__ = 'content', 'size', 'bold', 'italic', 'underline', 'strikethrough'

    def __init__(
        self,
        content: str,
        size: int = 1,
        bold: bool = False,
        italic: bool = False,
        underline: bool = False,
        strikethrough: bool = False
    ):
        self.content = content
        self.size = size
        self.bold = bold
        self.italic = italic
        self.underline = underline
        self.strikethrough = strikethrough

    def __repr__(self):
        features = []
        for name in self.__slots__:
            if name == 'content':
                features.append(repr(self.content))
            else:
                value = getattr(self, name)
                if name == 'size' and value == 1:
                    continue
                elif value is False:
                    continue
                features.append(f'{name}={value!r}')
        return f"{type(self).__qualname__}({','.join(features)})"

class Page:

    BIGTITLEPARTTERN = re.compile(r'\n(.+)\n\s{0,3}={2,}\n')
    SUBTITLEPARTTERN = re.compile(r'\n(.+)\n\s{0,3}-{2,}\n')
    TITLEPARTTERN = re.compile(r'\n\s{0,3}(#{1,6})\s+(.+?)\n')
    BOLDPARTTERN = re.compile(r'(\*\*|__)([^\s*].*?[^\s]|[^\s*])\1')
    ITALICPARTTERN = re.compile(r'(\*|_)([^\s*].*?[^\s]|[^\s*])\1')
    STRIKETHROUGHPARTTERN = re.compile(r'~~([^\s~].*?[^\s]|[^\s~])~~')

    MDHTMLMAP = {
        BIGTITLEPARTTERN: ('\n<h1>{group1}</h1>\n', 0),
        SUBTITLEPARTTERN: ('\n<h2>{group1}</h2>\n', 0),
        TITLEPARTTERN: ('\n<h{group1}>{group2}</h{group1}>\n', len, 0),
        BOLDPARTTERN: ('<b>{group2}</b>', None, 0),
        ITALICPARTTERN: ('<i>{group2}</i>', None, 0),
        STRIKETHROUGHPARTTERN: ('<s>{group1}</s>', 0)
    }

    DOUBLEELEMENTMAP = {
        'body': {}, 
        'h1': {'template': '\n{content}\n', 'size': 2},
        'h2': {'template': '\n{content}\n', 'size': 1.5},
        'h3': {'template': '\n{content}\n', 'size': 1.17},
        'h4': {'template': '\n{content}\n', 'size': 1},
        'h5': {'template': '\n{content}\n', 'size': 0.83},
        'h6': {'template': '\n{content}\n', 'size': 0.67},
        'p': {'template': '\n{content}\n', 'size': 1},
        'b': {'bold': True},
        'i': {'italic': True},
        'u': {'underline': True},
        's': {'strikethrough': True},
    }

    def __init__(self, source, language = 'markdown'):
        lang = language.lower()
        if lang in {'markdown', 'md'}:
            source = self.md2html(source)
            lang = 'html'
        if lang == 'html':
            self.slices = self.parse_html(source)
        elif lang in {'py', 'python'}:
            if source is None:
                self.slices = []
            else:
                if not hasattr(source, '__iter__') and not hasattr(source, '__getitem__'):
                    raise TypeError(
                        f"arg source must be iterable when language is '{language}', not {type(source).__qualname__}"
                    )
                self.slices = list(source)
        else:
            raise ValueError(
                f"unsupported language '{lang}'"
            )

    def __iter__(self):
        return iter(self.slices)

    def __repr__(self):
        return f"{type(self).__qualname__}({self.slices!r}, language='Python')"

    @staticmethod
    def _html_wrapper(element_name: str, element_content=None) -> str:
        if not isinstance(element_name, str):
            raise TypeError(
                'arg element_name must be a string, not ' + type(element_name).__qualname__
            )
        if element_content is None:
            return f'<{element_name}>'
        else:
            return f'<{element_name}>{element_content}</{element_name}>'

    @staticmethod
    def _parse_template(template, content):
        return template.format(content=content)

    @classmethod
    def md2html(cls, source: str) -> str:
        """
        Turn markdown into HTML content. 

        :param source: a piece of markdown code
        :type source: str
        :return: HTML content
        :rtype: str
        """
        source = '\n' + source + '\n\n' # 不知道为什么，在Skulpt环境下要多加一个换行符
        for parttern in cls.MDHTMLMAP:
            matched = parttern.search(source)
            if matched:
                template = cls.MDHTMLMAP[parttern]
                wrappers = template[1:]
            while matched:
                matched_str = matched.group()
                fields = {}
                for name, wrapper in enumerate(wrappers, 1):
                    if wrapper is not None and wrapper is not Ellipsis:
                        if callable(wrapper):
                            field_value = wrapper(matched.group(name))
                        else:
                            field_value = matched.group(name)
                        fields['group' + str(name)] = field_value
                source = source.replace(matched.group(), template[0].format(**fields))
                # print('[LOG] replaced', repr(source), sep='\n---\n[INFO] ', end='\n===\n\n') # for security
                matched = parttern.search(source)
        return source
    
    @classmethod
    def parse_html(cls, source: str) -> list[TextSlice]:
        """
        Parse HTML code into TextSlice objects. 

        :param source: a string of HTML code
        :type source: str
        :return: the relevant TextSlice objects
        :rtype: list[TextSlice]
        """

        if '<body>' not in source:
            source = f'<body>{source}</body>' 
        slices = []
        stacks = []
        temp = ''
        temp_lineno = 1
        temp_offset = 1
        for char in source:
            if char == '>':
                # print('start', repr(temp)) # for debugging
                add_flag = 0
                for name in cls.DOUBLEELEMENTMAP:
                    collecting_name = '<' + name
                    if temp.endswith(collecting_name):
                        add_flag = 1
                    else:
                        collecting_name = '</' + name
                        if temp.endswith(collecting_name):
                            add_flag = 2
                    if add_flag:
                        index = temp.rfind(collecting_name)
                        content = temp[:index].strip()
                        if content:
                            features = {}
                            if stacks:
                                top_feature = stacks[-1]
                                for feature in stacks:
                                    for feature_name, value in cls.DOUBLEELEMENTMAP[feature].items():
                                        if feature_name == 'template':
                                            if feature == top_feature:
                                                content = cls._parse_template(value, content)
                                        else:
                                            features[feature_name] = value
                        elif stacks:
                            top_feature = stacks[-1]
                            for feature_name, value in cls.DOUBLEELEMENTMAP[top_feature].items():
                                if feature_name == 'template':
                                    content = cls._parse_template(value, content)
                        if content:
                            t_slice = TextSlice(content, **features)
                            slices.append(t_slice)
                        temp = ''
                        if add_flag == 1:
                            stacks.append(name)
                            # print('append', name, stacks)
                        elif add_flag == 2:
                            # print('remove', name, stacks)
                            if not stacks or top_feature != name:
                                lines = source.splitlines()
                                text = lines[temp_lineno - 1]
                                lineno = temp_lineno
                                end_lineno = temp_lineno
                                offset = temp_offset - len(collecting_name) + 1
                                end_offset = temp_offset + 1
                                if name in stacks:
                                    left_index = stacks.index(name)
                                    unclosed = stacks[left_index + 1:]
                                    if len(unclosed) == 1:
                                        str_unclosed = f' {unclosed[0]} was'
                                    else:
                                        last = unclosed.pop()
                                        last2 = unclosed.pop()
                                        unclosed.append(f'{last2}> and <{last}')
                                        str_unclosed = f"s {', '.join(map(cls._html_wrapper, unclosed))} were"
                                    raise HTMLSyntaxError(
                                        f'preceding double element{str_unclosed} not closed',
                                        ('<source>', lineno, offset, text, end_lineno, end_offset)
                                    ) # 注：报错时的标签名称如<h1>会被猿编程识别为真正的html标签
                                else:
                                    raise HTMLSyntaxError(
                                        f'unmatched {collecting_name}>',
                                        ('<source>', lineno, offset, text, end_lineno, end_offset)
                                    )
                            stacks.pop()
                        break
            elif char == '\n':
                temp_lineno += 1
                temp_offset = 0
            else:
                temp += char
                # print('add', repr(char), repr(temp)) # check
            temp_offset += 1
        return slices

if __name__ == '__main__':
    p = Page('**big** world\n---\n# hello\n## world')
    print(p)