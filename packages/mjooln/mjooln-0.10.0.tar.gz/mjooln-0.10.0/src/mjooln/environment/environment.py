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

import os

#: Home folder. Default is '~/.mjooln'. Override by setting environment variable MJOOLN__HOME
HOME = os.getenv("MJOOLN__HOME", "~/.mjooln").replace("\\", "/")

# TODO: Add check to make sure word and class separator don't interfere with each other, and path separator
#: Default values. Override by adding MJOOLN__ first, and put in environment
#: variables
DEFAULT = {
    "PIXIE": "false",
    "MINIMUM_WORD_LENGTH": 1,
    "WORD_SEPARATOR": "__",
    "CLASS_SEPARATOR": "___",
    "COMPRESSED_EXTENSION": "gz",
    "ENCRYPTED_EXTENSION": "aes",
    "ZULU_TO_ISO": "true",
}


def get_env(name) -> str:
    public_name = "MJOOLN__" + name
    return os.getenv(public_name, str(DEFAULT[name]))


#: When flag is set to 'true', the Pixie will slow down your code, but
#: in return be very picky about your mistakes
PIXIE: bool = get_env("PIXIE") == "true"

#: Minimum word length. Default is 1
MINIMUM_WORD_LENGTH: int = int(get_env("MINIMUM_WORD_LENGTH"))

#: Word separator. Default is double underscore
WORD_SEPARATOR: str = get_env("WORD_SEPARATOR")

#: Class separator. Default is triple underscore
CLASS_SEPARATOR: str = get_env("CLASS_SEPARATOR")

#: Compressed (reserved) extension. Default is '.gz'
COMPRESSED_EXTENSION: str = get_env("COMPRESSED_EXTENSION")

#: Encrypted (reserved) extension. Default is '.aes'
ENCRYPTED_EXTENSION: str = get_env("ENCRYPTED_EXTENSION")

#: Flags converting Zulu to iso string when creating doc
ZULU_TO_ISO: bool = get_env("ZULU_TO_ISO") == "true"
