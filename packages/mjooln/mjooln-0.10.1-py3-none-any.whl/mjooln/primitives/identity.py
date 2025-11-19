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
import uuid

from mjooln.exception import IdentityError
from mjooln.core import Seed, Glass


class Identity(Seed, Glass):
    """UUID string generator with convenience functions

    Inherits str, and is therefore an immutable string, with a fixed format
    as illustrated below.

    Examples::

        Identity()
            'BD8E446D_3EB9_4396_8173_FA1CF146203C'

        Identity.is_in('Has BD8E446D_3EB9_4396_8173_FA1CF146203C within')
            True

        Identity.find_one('Has BD8E446D_3EB9_4396_8173_FA1CF146203C within')
            'BD8E446D_3EB9_4396_8173_FA1CF146203C'

    """

    REGEX = r"[0-9A-F]{8}\_[0-9A-F]{4}\_[0-9A-F]{4}\_[0-9A-F]{4}" r"\_[0-9A-F]{12}"

    REGEX_CLASSIC = (
        r"[0-9a-f]{8}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{4}" r"\-[0-9a-f]{12}"
    )
    REGEX_COMPACT = r"[0-9a-f]{32}"
    LENGTH = 36

    @classmethod
    def from_seed(cls, seed: str):
        """
        Create Identity from seed string

        :rtype: Identity
        """
        return cls(seed)

    @classmethod
    def is_classic(cls, classic: str):
        """
        Check if string is uuid on classic format

        :rtype: bool
        """
        if len(classic) != 36:
            return False
        _regex_exact = rf"^{cls.REGEX_CLASSIC}$"
        return re.compile(_regex_exact).match(classic) is not None

    @classmethod
    def from_classic(cls, classic: str):
        """
        Create Identity from classic format uuid

        :rtype: Identity
        """
        classic = classic.replace("-", "_").upper()
        return cls(classic)

    @classmethod
    def is_compact(cls, compact: str):
        """
        Check if string is compact format uuid

        :rtype: bool
        """
        if len(compact) != 32:
            return False
        _regex_exact = rf"^{cls.REGEX_COMPACT}$"
        return re.compile(_regex_exact).match(compact) is not None

    @classmethod
    def from_compact(cls, compact: str):
        """
        Create identity from compact format uuid

        :rtype: Identity
        """
        compact = "_".join(
            [compact[:8], compact[8:12], compact[12:16], compact[16:20], compact[20:]]
        ).upper()
        return cls(compact)

    @classmethod
    def elf(cls, input_):
        """
        Try to create an identity based on input

        :raises AngryElf: If an identity cannot be created
        :rtype: Identity
        """
        if isinstance(input_, Identity):
            return input_
        elif isinstance(input_, str):
            if cls.is_seed(input_):
                return cls(input_)
            elif cls.is_classic(input_):
                return cls.from_classic(input_)
            elif cls.is_compact(input_):
                return cls.from_compact(input_)
            elif cls.is_classic(input_.lower()):
                return cls.from_classic(input_.lower())
            elif cls.is_compact(input_.lower()):
                return cls.from_compact(input_.lower())

            # Try to find one or more identities in string
            ids = cls.find_seeds(input_)
            if len(ids) > 0:
                # If found, return the first
                return ids[0]
        raise IdentityError(
            f"This useless excuse for a string has no soul, "
            f"and hence no identity: '{input_}'"
        )

    def __init__(self, identity: str | None = None):
        if not identity:
            identity = str(uuid.uuid4()).replace("-", "_").upper()
        elif not self.is_seed(identity):
            raise IdentityError(f"String is not valid identity: {identity}")
        self.__identity = identity

    def __str__(self):
        return self.__identity

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
        return hash(self.__identity)

    def __repr__(self):
        return f"Identity('{self.__identity}')"

    def classic(self):
        """
        Return uuid string on classic format::

            Identity().classic()
                '18a9e538-3b5e-4442-b2b9-f728fbe8f240'

        :rtype: str
        """
        return self.__identity.replace("_", "-").lower()

    def compact(self):
        """
        Return uuid string on compact format::

            Identity().compact()
                '18a9e5383b5e4442b2b9f728fbe8f240'

        :rtype: str
        """
        return self.__identity.replace("_", "").lower()
