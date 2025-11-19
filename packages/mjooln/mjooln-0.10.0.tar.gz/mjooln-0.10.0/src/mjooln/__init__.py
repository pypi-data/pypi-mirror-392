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

import importlib.metadata as md

try:
    __version__: str = md.version("mjooln")
except md.PackageNotFoundError:
    __version__ = "N/A"


from mjooln.environment import HOME

from mjooln.core import Glass, Seed, Serializable
from mjooln.utils import Math, Text, Tic, Waiter
from mjooln.primitives import Word, Key, Identity, Zulu, Atom
from mjooln.encryption import Crypt
from mjooln.filesystem import Path, Folder, File, Archive, Serializer

HOME = Folder.glass(HOME)

__all__ = [
    "HOME",
    "Glass",
    "Seed",
    "Serializable",
    "Math",
    "Text",
    "Tic",
    "Waiter",
    "Word",
    "Key",
    "Identity",
    "Zulu",
    "Crypt",
    "Path",
    "Folder",
    "File",
    "Archive",
    "Serializer",
    "Atom",
]
