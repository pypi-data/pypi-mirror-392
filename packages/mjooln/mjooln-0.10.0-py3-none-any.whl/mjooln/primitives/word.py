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

import logging
import string

from mjooln.exception import (
    BadWord,
    NotAnInteger,
    PixieInPipeline,
    AngryElf,
)
from mjooln.environment import (
    PIXIE,
    MINIMUM_WORD_LENGTH,
    WORD_SEPARATOR,
    CLASS_SEPARATOR,
)
from mjooln.core import Seed, Glass
from mjooln.utils import Text


class Word(Seed, Glass):
    """
    Defines a short string with limitations

    - Minimum length is set in Environment with default 1
    - Empty word is ``n_o_n_e``
    - Allowed characters are

        - Lower case ascii ``a-z``
        - Digits ``0-9``
        - Underscore ``_``

    - Underscore and digits can not be the first character
    - Underscore can not be the last character
    - Can not contain double underscore since it acts as separator for words
      in :class:`.Key`

    Sample words::

        "simple"

        "with_longer_name"
        "digit1"
        "longer_digit2"

    """

    logger = logging.getLogger(__name__)

    REGEX = r"(?!.*__.*)[a-z0-9][a-z_0-9]*[a-z0-9]"

    #: Allowed characters
    ALLOWED_CHARACTERS = string.ascii_lowercase + string.digits + "_"

    #: Allowed first characters
    ALLOWED_STARTSWITH = string.ascii_lowercase + string.digits

    #: Allowed last characters
    ALLOWED_ENDSWITH = string.ascii_lowercase + string.digits

    NONE = "n_o_n_e"

    @classmethod
    def is_seed(cls, str_: str):
        if len(str_) == 1:
            if MINIMUM_WORD_LENGTH > 1:
                return False
            else:
                return str_ in cls.ALLOWED_STARTSWITH
        else:
            return super().is_seed(str_)

    @classmethod
    def none(cls):
        """
        Return Word repesentation of ``None``

        :return: ``n_o_n_e``
        :rtype: Word
        """
        return cls(cls.NONE)

    @classmethod
    def from_int(cls, number):
        return cls(str(number))

    @classmethod
    def from_ints(cls, numbers):
        numstr = "_".join([str(x) for x in numbers])
        return cls(numstr)

    @classmethod
    def check(cls, word: str):
        """
        Check that string is a valid word

        :param word: String to check
        :type word: str
        :return: True if ``word`` is valid word, False if not
        :rtype: bool
        """
        if len(word) < MINIMUM_WORD_LENGTH:
            raise BadWord(
                f"Element too short. Element '{word}' has "
                f"length {len(word)}, while minimum length "
                f"is {MINIMUM_WORD_LENGTH}"
            )
        if word[0] not in cls.ALLOWED_STARTSWITH:
            raise BadWord(
                f"Invalid startswith. Word '{word}' "
                f"cannot start with '{word[0]}'. "
                f"Allowed startswith characters are: "
                f"{cls.ALLOWED_STARTSWITH}"
            )
        if word[-1] not in cls.ALLOWED_ENDSWITH:
            raise BadWord(
                f"Invalid endswith. Word '{word}' "
                f"cannot end with '{word[-1]}'. "
                f"Allowed endswith characters are: "
                f"{cls.ALLOWED_ENDSWITH}"
            )
        invalid_characters = [x for x in word if x not in cls.ALLOWED_CHARACTERS]
        if len(invalid_characters) > 0:
            raise BadWord(
                f"Invalid character(s). Word '{word}' cannot "
                f"contain any of {invalid_characters}. "
                f"Allowed characters are: "
                f"{cls.ALLOWED_CHARACTERS}"
            )
        if WORD_SEPARATOR in word:
            raise BadWord(
                f"Word contains word separator, which is "
                f"reserved for separating words in a Key."
                f"Word '{word}' cannot contain "
                f"'{CLASS_SEPARATOR}'"
            )

    @classmethod
    def elf(cls, word):
        """Attempts to interpret input as a valid word

        .. warning: Elves are fickle

        :raises AngryElf: If input cannot be interpreted as Word
        :param word: Input word string or word class
        :type word: str or Word
        :rtype: Word
        """
        from mjooln import Key

        if isinstance(word, Word):
            return word
        elif isinstance(word, Key):
            raise AngryElf("This is a Key, not a word. Idiot.")
        elif isinstance(word, str) and cls.is_seed(word):
            return cls(word)
        elif isinstance(word, int):
            return cls(str(word))
        elif isinstance(word, float):
            if word.is_integer():
                return cls(str(int(word)))
            return cls(str(word).replace(".", "_"))
        else:
            _orignial_class = None
            if not isinstance(word, str):
                _original_class = type(word).__name__
                word = str(word)

            _original = word

            if WORD_SEPARATOR in word:
                raise AngryElf(
                    f"This looks more like a Key: '{_original}'; "
                    f"Try the Key.elf() not me. In case you "
                    f"didn't notice I'm the Word.elf()"
                )

            # Test camel to snake
            if " " not in word and "_" not in word:
                word = Text.camel_to_snake(word)
                if cls.is_seed(word):
                    return cls(word)
                word = _original

            word = word.replace("_", " ")
            word = word.strip()
            word = word.replace(" ", "_")
            while "__" in word:
                word = word.replace("__", "_")
            word = Text.camel_to_snake(word)
            while "__" in word:
                word = word.replace("__", "_")
            if cls.is_seed(word):
                return cls(word)
            word = _original
            word = word.lower()
            new_word = ""
            for letter in word:
                if letter in cls.ALLOWED_CHARACTERS:
                    new_word += letter
                else:
                    new_word += "_"
            while "__" in new_word:
                new_word = new_word.replace("__", "_")

            while len(new_word) > MINIMUM_WORD_LENGTH:
                if new_word[0] not in cls.ALLOWED_STARTSWITH:
                    new_word = new_word[1:]
                elif new_word[-1] not in cls.ALLOWED_ENDSWITH:
                    new_word = new_word[:-1]
                else:
                    break

            if Word.is_seed(new_word):
                return Word(new_word)

            raise AngryElf(
                f"Cannot for the bleeding world figure out "
                f"how to make a Word from this sorry "
                f"excuse of a string: {_original}"
            )

    def __init__(self, word: str):
        if PIXIE:
            try:
                self.check(word)
            except BadWord as ie:
                raise PixieInPipeline(f"Invalid word: {ie}") from ie
        else:
            if not self.is_seed(word):
                raise BadWord(f"Invalid word: {word}")
        self.__word = word

    def __str__(self):
        return self.__word

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
        return hash(self.__word)

    def __repr__(self):
        return f"Word('{self.__word}')"

    def __add__(self, other):
        if isinstance(other, str):
            return Word(f"{self}_{other}")
        elif isinstance(other, Word):
            from mjooln import Key

            return Key.from_words([self, other])
        return NotImplemented

    def __radd__(self, other):
        if isinstance(other, str):
            return Word(f"{other}_{self}")

    @staticmethod
    def _int(element):
        try:
            return int(element)
        except ValueError:
            return None

    @classmethod
    def _is_int(cls, element):
        return cls._int(element) is not None

    def is_none(self):
        """
        Check if word is ``n_o_n_e``, i.e. word representation of ``None``

        :rtype: bool
        """
        return self.__word == self.NONE

    def is_int(self):
        """
        Check if word is an integer

        :rtype: bool
        """
        ints = self._ints()
        return len(ints) == 1 and ints[0] is not None

    def _elements(self):
        return self.__word.split("_")

    def _ints(self):
        return [self._int(x) for x in self._elements()]

    def index(self):
        """
        Get index of word

        :raises BadWord: If word is an integer and thus cannot have an index
        :return: 0 if word has no index, otherwise returns index
        :rtype: int
        """
        elements = self._elements()
        if len(elements) == 1:
            if self._is_int(elements[0]):
                raise BadWord(f"Word is an integer, cannot get index: {self}")
            return 0
        else:
            idx = elements[-1]
            if self._is_int(idx):
                return self._int(idx)
            else:
                return 0

    @classmethod
    def _is_numeric(cls, ints):
        return all(ints)

    def is_numeric(self):
        """
        Check if word is numeric, i.e. can be converted to integer

        :rtype: bool
        """
        return self._is_numeric(self._ints())

    def to_int(self):
        """
        Convert word to integer

        :raise NotAnInteger: If word is not an integer
        :rtype: int
        """
        ints = self._ints()
        if len(ints) == 1 and ints[0] is not None:
            return ints[0]
        else:
            raise NotAnInteger(f"Word is not an integer: {self}")

    def to_ints(self):
        """
        Convert word to list of integers

        :rtype: int
        """
        return self._ints()

    def increment(self):
        """
        Create a new word with index incremented

        Example::

            word = Word('my_word_2')
            word.increment()
                Word('my_word_3')

        :rtype: Word
        """
        elements = self._elements()
        if len(elements) == 1:
            if self._is_int(elements[0]):
                raise BadWord(f"Word is an integer and cannot be incremented: {self}")
            elements = elements + ["1"]
        else:
            idx = self._int(elements[-1])
            if idx is None:
                elements += ["1"]
            else:
                elements[-1] = str(idx + 1)
        return Word("_".join(elements))
