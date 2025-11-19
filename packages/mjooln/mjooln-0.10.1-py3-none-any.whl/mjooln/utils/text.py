# Copyright (c) 2020 Vemund Halmø Aarstrand
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import re


class Text:
    """String utility functions"""

    _CAMEL_TO_SNAKE = r"(?<!^)(?=[A-Z])"
    _SNAKE_TO_CAMEL = r"(.+?)_([a-z])"
    _RE_CAMEL_TO_SNAKE = re.compile(_CAMEL_TO_SNAKE)
    _RE_SNAKE_TO_CAMEL = re.compile(_SNAKE_TO_CAMEL)

    @classmethod
    def camel_to_snake(cls, camel: str) -> str:
        """
        Convert camel to snake::

            Text.camel_to_snake('ThisIsCamel')
                this_is_camel
        """
        return cls._RE_CAMEL_TO_SNAKE.sub("_", camel).lower()

    @classmethod
    def snake_to_camel(cls, snake: str) -> str:
        """
        Convert snake to camel::

            Text.snake_to_camel('this_is_snake')
                ThisIsSnake
        """
        # TODO: Implement regex instead
        return "".join(x[0].upper() + x[1:] for x in snake.split("_"))
