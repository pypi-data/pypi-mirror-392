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

import time


class Tic:
    """
    Time counter

    Example::

        tic = Tic()

        (wait a bit)

        tic.toc()
            2.5361578464508057

        tic.toc('Elapsed time')
            'Elapsed time: 17.219 seconds'
    """

    def __init__(self):
        self.start_time = time.time()

    def elapsed_time(self):
        return time.time() - self.start_time

    def toc(self, text=""):
        if text:
            return f"{text}: {self.elapsed_time():.3f} seconds"
        else:
            return self.elapsed_time()

    def tac(self, min_sleep_s=1.0):
        remaining_time = min_sleep_s - self.elapsed_time()
        if remaining_time > 0:
            time.sleep(remaining_time)
