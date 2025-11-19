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

import string

from mjooln.environment import (
    MINIMUM_WORD_LENGTH,
    WORD_SEPARATOR,
    CLASS_SEPARATOR,
    PIXIE,
)
from mjooln.exception import InvalidKey, AngryElf, BadWord, PixieInPipeline
from mjooln.core import Seed, Glass
from .word import Word


class Key(Seed, Glass):
    """
    Defines key string with limitations:

    - Minimum length is 2
    - Allowed characters are:

        - Lower case ascii (a-z)
        - Digits (0-9)
        - Underscore (``_``)
        - Double underscore (``__``)

    - Underscore and digits can not be the first character
    - Underscore can not be the last character
    - The double underscore act as separator for :class:`.Word`
      in the key
    - Triple underscore is reserved for separating keys from other keys or
      seeds, such as in class :class:`.Atom`

    Sample keys::

        "simple"

        "with_longer_name"
        "digit1"
        "longer_digit2"
        "word_one__word_two__word_three"
        "word1__word2__word3"
        "word_1__word_2__word_3"

    """

    #: Allowed characters
    ALLOWED_CHARACTERS = string.ascii_lowercase + string.digits + "_"

    #: Allowed first characters
    ALLOWED_STARTSWITH = string.ascii_lowercase

    #: Allowed last characters
    ALLOWED_ENDSWITH = string.ascii_lowercase + string.digits

    #: Regular expression for verifying and finding keys
    REGEX = rf"(?!.*{CLASS_SEPARATOR}.*)[a-z][a-z_0-9]*[a-z0-9]"

    def __init__(self, key: str):
        if PIXIE:
            try:
                self.verify_key(key)
            except BadWord as ie:
                raise PixieInPipeline("Invalid word in key") from ie
            except InvalidKey as ik:
                raise PixieInPipeline("Invalid key") from ik
        if not self.is_seed(key):
            raise InvalidKey(f"Invalid key: {key}")
        self.__key = key

    def __str__(self):
        return self.__key

    def __eq__(self, other):
        return str(self) == str(other)

    def __lt__(self, other):
        return str(self) < str(other)

    def __gt__(self, other):
        return str(self) > str(other)

    def __le__(self, other):
        return str(self) <= str(other)

    def __ge__(self, other):
        return str(self) >= str(other)

    def __hash__(self):
        return hash(str(self))

    def __repr__(self):
        return f"Key('{self.__key}')"

    def __iter__(self):
        yield from self.words()

    def __add__(self, other):
        if isinstance(other, Key):
            return Key.from_words(self.words() + other.words())
        elif isinstance(other, Word):
            return Key.from_words(self.words() + [other])
        elif isinstance(other, str):
            return Key.from_words(self.words() + [Word(other)])
        return NotImplemented

    def __radd__(self, other):
        if isinstance(other, Word):
            return Key.from_words([other] + self.words())
        elif isinstance(other, str):
            return Key.from_words([Word(other)] + self.words())
        # else:
        #     raise

    @classmethod
    def verify_key(cls, key: str):
        """
        Verify that string is a valid key

        :param key: String to check
        :return: True if string is valid key, False if not
        """
        if not len(key) >= MINIMUM_WORD_LENGTH:
            raise InvalidKey(
                f"Key too short. Key '{key}' has length "
                f"{len(key)}, while minimum length is "
                f"{MINIMUM_WORD_LENGTH}"
            )
        if CLASS_SEPARATOR in key:
            raise InvalidKey(
                f"Key contains word reserved as class "
                f"separator. "
                f"Key '{key}' cannot contain "
                f"'{CLASS_SEPARATOR}'"
            )
        if key[0] not in cls.ALLOWED_STARTSWITH:
            raise InvalidKey(
                f"Invalid startswith. Key '{key}' "
                f"cannot start with '{key[0]}'. "
                f"Allowed startswith characters are: "
                f"{cls.ALLOWED_STARTSWITH}"
            )

        words = key.split(WORD_SEPARATOR)
        for word in words:
            Word.check(word)

    @classmethod
    def from_words(cls, *args):
        if len(args) == 1:
            arg = args[0]
            if isinstance(arg, str):
                return cls(arg)
            elif isinstance(arg, tuple) or isinstance(arg, list):
                args = tuple(arg)

        args = tuple([str(x) for x in args])
        return cls(WORD_SEPARATOR.join(args))

    @classmethod
    def from_seed(cls, str_: str):
        return cls(str_)

    @classmethod
    def from_branch(cls, branch: str):
        words = [Word(x) for x in branch.split("/")]
        return cls.from_words(words)

    def words(self):
        """
        Return list of words in key

        Example::

            key = Key('some_key__with_two__no_three_elements')
            key.words()
                [Word('some_key'), Word('with_two'), Word('three_elements')]
            key.words()[0]
                Word('some_key')

        :returns: [:class:`.Word`]
        """
        return [Word(x) for x in self.parts()]

    def parts(self):
        """
        Return list of words as strings in key

        Example::

            key = Key('some_key__with_two__no_three_elements')
            key.parts()
                ['some_key', 'with_two', 'three_elements']
            key.parts()[0]
                'some_key'

        :returns: [str]
        """
        return [x for x in self.__key.split(WORD_SEPARATOR)]

    def branch(self):
        return self.with_separator("/")

    def first(self):
        return self.words()[0]

    def last(self):
        return self.words()[-1]

    def with_separator(self, separator: str):
        """Replace separator

        Example::

            key = Key('some__key_that_could_be__path')
            key.with_separator('/')
                'some/key_that_could_be/path'

        :param separator: Separator of choice
        :type separator: str
        :return: str
        """
        return separator.join([str(x) for x in self.words()])

    @classmethod
    def elf(cls, key):
        """Attempts to create a valid key based on the input

        .. warning:: Elves are fickle

        :raise AngryElf: If a valid key cannot be created
        :param key: Input key string or key class
        :type key: str or Key
        :return: Key
        """
        from mjooln import Atom

        if isinstance(key, Key):
            return key
        elif isinstance(key, Word):
            return Key.from_words([key])
        elif isinstance(key, Atom):
            raise AngryElf("This is an Atom. Idiot.")
        elif isinstance(key, str) and Key.is_seed(key):
            return cls.from_seed(key)
        else:
            _original_class = None
            if not isinstance(key, str):
                _original_class = type(key).__name__
                key = str(key)

            if CLASS_SEPARATOR in key:
                raise AngryElf(
                    "This looks more like an Atom. Do I look like an Atom elf?"
                )
            if WORD_SEPARATOR in key:
                words = [Word.elf(x) for x in key.split(WORD_SEPARATOR)]
                return Key.from_words(words)

            _original = key
            if Key.is_seed(key):
                return cls(key)
            key = key.strip()
            if Key.is_seed(key):
                return cls(key)
            key = key.replace(" ", "_")
            if Key.is_seed(key):
                return cls(key)
            key = key.lower()
            if Key.is_seed(key):
                return cls(key)
            if _original_class:
                raise InvalidKey(
                    f"Creating "
                    f"a key from '{_original_class}' is, as "
                    f"you should have known, not meant to be. "
                    f"Resulting string was: {_original}"
                )
            key = _original.lower()
            new_key = ""
            for char in key:
                if char in cls.ALLOWED_CHARACTERS:
                    new_key += char
                else:
                    new_key += "_"
            while len(new_key) > MINIMUM_WORD_LENGTH:
                if new_key[0] not in cls.ALLOWED_STARTSWITH:
                    new_key = new_key[1:]
                elif new_key[-1] not in cls.ALLOWED_ENDSWITH:
                    new_key = new_key[:-1]
                else:
                    break

            if Key.is_seed(new_key):
                return cls(new_key)

            raise InvalidKey(
                f"I tried but no way I can make a key out of "
                f"this sorry excuse of a string: {_original}"
            )
