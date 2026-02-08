"""
Some useful types in SCQYJ. 
"""


class GracefulIncrease:

    r"""
    Initialize and calculate the increment of speed per iteration.

    Here's how it can be worked out --we should set :code:`initial_num`` as :math: `a`, :code:`final_num` as :math: `b`, and :code:`ticks` as :math: `t`, so that we can write down this arithmetic sequence --
    .. math::
        \begin{align}
        a + (-kt) + [-k(t - 1)] + [-k(t - 2)] + ... + (-k) &= b \\
        a + \frac12(-kt)(t + 1) &= b \\
        \frac{1}{2}kt(t + 1) &= b - a \\
        kt(t+1) &= -2(y - x) \\
        k &= \frac{2(x - y)}{t(t + 1)}
        \end{align}
    """

    def __init__(self, initial_num, final_num, ticks):
        self.initial = initial_num
        self.final = final_num
        self.speed_increment =            \
            2 * (final_num - initial_num) \
                        /                 \
                    ticks * (ticks + 1)
        self._speed_initial = self.speed_increment * ticks
    
    def __iter__(self):
        self.num = self.initial
        self.speed = self._speed_initial
        return self
