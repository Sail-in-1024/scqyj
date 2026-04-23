import sys
import platform


def _version_trans(version: str, errinfo: tuple[str, str] = ('version', 'a string')) -> tuple[int, int, int]:
    if not isinstance(version, str):
        raise TypeError(
            f'arg {errinfo[0]} must be {errinfo[1]}, not {type(version).__qualname__}'
        )
    return tuple(map(int, version.split('.')))

def _version_check(real, least) -> bool:
    if not isinstance(real, tuple):
        real = _version_trans(real, errinfo=('real', 'a string or tuple'))
    if not isinstance(least, tuple):
        least = _version_trans(least, errinfo=('least', 'a string or a tuple'))
    if real[0] > least[0]:
        return True
    elif real[0] == least[0]:
        if real[1] > least[1]:
            return True
        elif real[1] == least[1]:
            return real[2] >= least[2]
    return False

def render_surface(
    page,
    canvas_size: tuple[int, int], 
    color = 'black',
    fontsize = 16,
    background = None,
):

    # 模块检查机制
    if 'pygame' in sys.modules:
        pygame = sys.modules['pygame']
        if not hasattr(pygame, 'font'):
            pygame.init()
    else:
        import pygame
        pygame.init()
    if not hasattr(pygame, 'font'):
        print('Warning: initialize failed')
        print('警告：初始化失败')
    support_strikethrough = _version_check(pygame.version.vernum, '2.1.3')

    # Create Surface 创建画布
    canvas = pygame.Surface(canvas_size)
    color = pygame.Color(color)
    if background is not None:
        background = pygame.Color(background)
    next_pos = [0, 0]
    line_height = fontsize

    # Main loop 主循环
    for t_slice in page:
        slice_font = pygame.font.Font(None, fontsize * t_slice.size)
        if t_slice.bold:
            slice_font.set_bold(True)
        if t_slice.italic:
            slice_font.set_italic(True)
        if t_slice.underline:
            slice_font.set_underline(True)
        if support_strikethrough and t_slice.strikethrough:
            slice_font.set_strikethrough(True)
        lines = t_slice.content.splitlines()
        new_line = False
        for line in lines:
            if new_line:
                next_pos[0] = 0
                next_pos[1] += line_height
                line_height = 0
            new_line = True
            if not line:
                continue
            text = slice_font.render(line, True, color)
            need_size = text.get_size()
            if not support_strikethrough and t_slice.strikethrough:
                strike_y = need_size[1] / 2
                width_coef = .2 if t_slice.bold else .1
                if background is not None:
                    pygame.draw.line(text, background, (0, strike_y), (need_size[0], strike_y), fontsize * (width_coef + .1))
                pygame.draw.line(text, color, (0, strike_y), (need_size[0], strike_y), fontsize * width_coef)
            canvas.blit(text, next_pos)
            # need_size = slice_font.size(t_slice.content)
            # print(need_size[0], type(need_size[0])) # （猿编程中）这里的type为显示不出来，应该是因为这不是Python对象
            # 在这里调试累死人了，找了好久才发现是底层bug，好不容易补好了又发现不准，最后才想起来用 get_size() 就行了
            # if platform.python_implementation() == 'Skulpt':
            #     need_size = (float(str(need_size[0])), float(str(need_size[1])))
            next_pos[0] += need_size[0]
            line_height = max(line_height, need_size[1])
    
    # Return Surface 返回画布
    return canvas

if __name__ == '__main__':
    print(_version_check('1.9.3', '2.6.0'))