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


class Math:
    """Utility math methods"""

    @classmethod
    def human_size(cls, size_bytes: int) -> tuple[float, str]:
        """Convert bytes to a human readable format

        :type size_bytes: int
        :return: Tuple of size as a float and unit as a string
        :rtype: (float, str)
        """
        # 2**10 = 1024
        power = 2**10
        n = 0
        size = float(size_bytes)
        power_labels = {0: "", 1: "k", 2: "M", 3: "G", 4: "T"}
        while size > power:
            size /= power
            n += 1
        return size, power_labels[n] + "B"

    @classmethod
    def bytes_to_human(cls, size_bytes: int, min_precision=5) -> str:
        """
        Convert size in bytes to human readable string

        :param size_bytes: Bytes
        :param min_precision: Minimum precision in number of digits
        :return:
        """
        value, unit = cls.human_size(size_bytes=size_bytes)
        len_int = len(str(int(value)))
        if len_int >= min_precision or unit == "B":
            len_dec = 0
        else:
            len_dec = min_precision - len_int
        return f"{value:.{len_dec}f} {unit}"
