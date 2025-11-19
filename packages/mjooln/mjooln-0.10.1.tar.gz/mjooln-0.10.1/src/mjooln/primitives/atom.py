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

from mjooln.environment import CLASS_SEPARATOR, WORD_SEPARATOR
from mjooln.core import Seed, Glass, Serializable
from mjooln.exception import AtomError

from .key import Key
from .identity import Identity
from .zulu import Zulu

# TODO: Refactor Dic/Doc to Serializer and More generic Doc class (handles serialization)


# TODO: Add DocAtom class, which includes atom conversion to dictionary both ways (or seed, if set)
class Atom(Seed, Glass, Serializable):
    """
    Triplet identifier intended for objects and data sets alike

    Format: ``<zulu>___<key>___<identity>``

    :class:`.Zulu` represents t0 or creation time

    :class:`.Key` defines grouping of the contents

    :class:`.Identity` is a unique identifier for the contents

    Constructor initializes a valid atom, and will raise an ``AtomError``
    if a valid atom cannot be created based on input parameters.

    The constructor must as minimum have :class:`.Key` as input, although
    string version (seed) of key is allowed::

        atom = Atom('zaphod__ship_33__inventory')
        atom.key()
            'zaphod__ship_33__inventory'
        atom.zulu()
            Zulu(2020, 5, 22, 13, 13, 18, 179169, tzinfo=<UTC>)
        atom.identity()
            '060AFBD5_D865_4974_8E37_FDD5C55E7CD8'

    Output methods::

        atom = Atom('zaphod__ship_33__inventory',
                    zulu=Zulu(2020, 5, 22, 13, 13, 18, 179169),
                    identity=Identity('060AFBD5_D865_4974_8E37_FDD5C55E7CD8'))

        str(atom)
            '20200522T131318u179169Z___zaphod__ship_33__inventory___060AFBD5_D865_4974_8E37_FDD5C55E7CD8'

        atom.seed()
            '20200522T131318u179169Z___zaphod__ship_33__inventory___060AFBD5_D865_4974_8E37_FDD5C55E7CD8'

        atom.to_dict()
            {
                'zulu': Zulu(2020, 5, 22, 13, 13, 18, 179169),
                'key': Key('zaphod__ship_33__inventory'),
                'identity': Identity('060AFBD5_D865_4974_8E37_FDD5C55E7CD8')
            }

    Atom inherits :class:`.Doc` and therefore has a ``to_doc()`` method::

        atom.to_doc()
            {
                'zulu': '2020-05-22T13:13:18.179169+00:00',
                'key': 'zaphod__ship_33__inventory',
                'identity': '060AFBD5_D865_4974_8E37_FDD5C55E7CD8'
            }

    The ``to_doc()`` is used for output to the equivalent ``to_json()`` and
    ``to_yaml()``, with equivalent methods for creating an instance from
    ``dict``, doc or a JSON or YAML file.

    When storing an atom as part of another dictionary,
    the most compact method would however be ``seed``, unless readability
    is of importance.

    """

    REGEX = (
        r"\d{8}T\d{6}u\d{6}Z\_\_\_[a-z][a-z_0-9]*[a-z0-9]\_\_\_"
        r"[0-9A-F]{8}\_[0-9A-F]{4}\_[0-9A-F]{4}\_[0-9A-F]{4}\_[0-9A-F]{12}"
    )

    @classmethod
    def from_seed(cls, seed: str):
        """Creates an Atom from a seed string

        :param seed: A valid atom seed string
        :rtype: Atom
        """
        if not cls.is_seed(seed):
            raise AtomError(f"Invalid atom seed: {seed}")
        zulu, key, identity = seed.split(CLASS_SEPARATOR)
        return cls(key=Key(key), zulu=Zulu.from_seed(zulu), identity=Identity(identity))

    @classmethod
    def elf(cls, *args, **kwargs):
        """Attempts to create an atom based on the input arguments

        .. warning:: Elves are fickle

        :raise AngryElf: If input arguments cannot be converted to Atom
        :rtype: Atom
        """
        if len(args) == 1 and not kwargs:
            arg = args[0]
            if isinstance(arg, Atom):
                return arg
            if isinstance(arg, Key):
                return cls(arg)
            elif isinstance(arg, str):
                if Key.is_seed(arg):
                    return cls(arg)
                elif cls.is_seed(arg):
                    return cls.from_seed(arg)
                else:
                    raise AtomError(
                        f"This input string is nowhere near "
                        f"what I need to create an Atom: {arg}"
                    )
            elif Key.is_seed(arg):
                return cls(arg)
            else:
                raise AtomError(
                    f"How the fuck am I supposed to create an atom "
                    f"based on this ridiculous excuse for an "
                    f"input: {arg} [{type(arg)}]"
                )
        elif len(args) == 0:
            if "key" not in kwargs:
                raise AtomError(
                    "At the very least, give me a key to work "
                    "on. You know, key as thoroughly described "
                    "in class Key"
                )
            key = Key.elf(kwargs["key"])
            identity = None
            zulu = None
            if "identity" in kwargs:
                identity = Identity.elf(kwargs["identity"])
            if "zulu" in kwargs:
                zulu = Zulu.elf(kwargs["zulu"])
            return cls(key, zulu=zulu, identity=identity)
        raise AtomError(
            f"This is rubbish. Cannot make any sense of this "
            f"mindless junk of input: "
            f"args={args}; kwargs={kwargs}"
        )

    @classmethod
    def from_dict(cls, di: dict):
        """
        Create :class:`Atom` from input dictionary

        :param di: Input dictionary
        :rtype: Atom
        """
        return cls(
            key=Key.from_seed(di["key"]),
            zulu=Zulu.from_iso(di["zulu"]),
            identity=Identity.from_classic(di["identity"]),
        )

    def __init__(self, key, zulu: Zulu | None = None, identity: Identity | None = None):
        """Atom constructor

        :param key: Valid Key
        :param zulu: Valid Zulu or None
        :param identity: Valid Identity or None
        :raise AtomError: If key is missing or any arguments are invalid
        :rtype: Atom
        """
        super().__init__()
        if isinstance(key, str):
            if Key.is_seed(key):
                key = Key(key)
            elif Atom.is_seed(key):
                raise AtomError(
                    "Cannot instantiate Atom with seed. Use Atom.from_seed()"
                )
            else:
                raise AtomError(f"Invalid key: {key} [{type(key).__name__}]")

        if not isinstance(key, Key):
            raise AtomError(f"Invalid key: [{type(key)}] {key}")

        if not zulu:
            zulu = Zulu()
        if not identity:
            identity = Identity()

        self.__zulu = zulu
        self.__key = key
        self.__identity = identity

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return CLASS_SEPARATOR.join(
            [str(self.__zulu), str(self.__key), str(self.__identity)]
        )

    def __repr__(self):
        return (
            f"Atom('{self.__key}', "
            f"zulu={self.__zulu.__repr__()}, "
            f"identity={self.__identity.__repr__()})"
        )

    def __hash__(self):
        return hash((self.__zulu, self.__key, self.__identity))

    def __lt__(self, other):
        return (self.__zulu, self.__key, self.__identity) < (
            other.__zulu,
            other.__key,
            other.__identity,
        )

    def __gt__(self, other):
        return (self.__zulu, self.__key, self.__identity) > (
            other.__zulu,
            other.__key,
            other.__identity,
        )

    def key(self):
        """
        Get Atom Key

        :rtype: Key
        """
        return self.__key

    def zulu(self):
        """
        Get Atom Zulu

        :rtype: Zulu
        """
        return self.__zulu

    def identity(self):
        """
        Get Atom Identity

        :rtype: Identity
        """
        return self.__identity

    def to_dict(self):
        """Get Atom dict

        Example from class documentantion::

            atom.to_dict()
                {
                    'zulu': Zulu(2020, 5, 22, 13, 13, 18, 179169),
                    'key': Key('zaphod__ship_33__inventory'),
                    'identity': Identity('060AFBD5_D865_4974_8E37_FDD5C55E7CD8')
                }

        :param ignore_private: Ignore private attributes (not relevant)
        :param recursive: Recursive dicts (not relevant)
        :rtype: dict

        """
        return {
            "zulu": self.__zulu.iso(),
            "key": self.__key.seed(),
            "identity": self.__identity.classic(),
        }

    def with_sep(self, sep: str):
        """Atom seed string with custom separator

        Example::

            atom.with_sep('/')
                '20200522T131318u179169Z/zaphod__ship_33__inventory/060AFBD5_D865_4974_8E37_FDD5C55E7CD8'

        :param sep: Custom separator
        :rtype: str
        """
        return sep.join(str(self).split(CLASS_SEPARATOR))

    @classmethod
    def element_count(cls, elements: int | None = None):
        """
        Count number of elements represented by element input

        For examples, see:

            :meth:`.Atom.key_elements()`
            :meth:`.Atom.date_elements()`
            :meth:`.Atom.time_elements()`

        :param elements: Element parameter
        :rtype: int
        """
        if elements is None or elements < 0:
            return 1
        else:
            return elements

    @classmethod
    def _elements(cls, parts, level, sep=""):
        if level == 0:
            return []
        elif level > 0:
            return parts[:level]
        else:
            return [sep.join(parts[:-level])]

    def key_elements(self, elements=None):
        """
        Get selected key elements

        Intented usage is creating sub folders for files with atom naming

        Examples::

            atom.key_elements(None)
                ['zaphod__ship_33__inventory']
            atom.element_count(None)
                1

            atom.key_elements(0)
                []
            atom.element_count(0)
                0

            atom.key_elements(2)
                ['zaphod', 'ship_33']
            atom.element_count(2)
                2

            atom.key_elements(-2)
                ['zaphod__ship_33']
            atom.element_count(-2)
                1

        :param elements: Elements
        :return: Elements
        :rtype: list
        """
        if elements is None:
            return [str(self.__key)]
        return self._elements(self.__key.words(), elements, sep=WORD_SEPARATOR)

    def date_elements(self, elements=3):
        """
        Get selected date elements

        Intented usage is creating sub folders for files with atom naming

        Examples::

            atom.date_elements(None)
                ['20200522']
            atom.element_count(None)
                1

            atom.date_elements(0)
                []
            atom.element_count(0)
                0

            atom.date_elements(2)
                ['2020', '05']
            atom.element_count(2)
                2

            atom.date_elements(-2)
                ['202005']
            atom.element_count(-2)
                1

        :param elements: Elements
        :return: Elements
        :rtype: list
        """

        if elements is None:
            return [self.__zulu.str.date]  # type: ignore
        return self._elements(
            [self.__zulu.str.year, self.__zulu.str.month, self.__zulu.str.day], elements
        )  # type: ignore

    def time_elements(self, elements=0):
        """
        Get selected time elements

        Intented usage is creating sub folders for files with atom naming

        Examples::

            atom.time_elements(None)
                ['131318']
            atom.element_count(None)
                1

            atom.time_elements(0)
                []
            atom.element_count(0)
                0

            atom.time_elements(2)
                ['13', '13']
            atom.element_count(2)
                2

            atom.time_elements(-2)
                ['1313']
            atom.element_count(-2)
                1

        :param elements: Elements
        :return: Elements
        :rtype: list
        """
        if elements is None:
            return [self.__zulu.str.time]  # type: ignore
        return self._elements(
            [self.__zulu.str.hour, self.__zulu.str.minute, self.__zulu.str.second],
            elements,
        )  # type: ignore
