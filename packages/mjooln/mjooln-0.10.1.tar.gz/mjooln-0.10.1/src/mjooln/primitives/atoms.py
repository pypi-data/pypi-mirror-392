from .keys import Key, Keys, Word
from .atom import Atom


class Atoms:
    def __init__(self, atoms: list[Atom]):
        self._atoms = atoms.copy()
        for atom in self._atoms:
            if not isinstance(atom, Atom):
                raise TypeError(f"Not an Atom: {atom}")

    def __str__(self):
        return "[" + ", ".join([str(x) for x in self._atoms]) + "]"

    def __repr__(self):
        return "[" + ", ".join([x.__repr__() for x in self._atoms]) + "]"

    def __len__(self):
        return len(self._atoms)

    def __getitem__(self, key: int | slice):
        return self._atoms[key]

    def __iter__(self):
        return iter(self._atoms)

    def __iadd__(self, other):
        self._atoms.append(other)
        return self

    def append(self, atom: Atom):
        if not isinstance(atom, Atom):
            raise TypeError(f"Not an Atom: {atom}")
        self._atoms.append(atom)

    def unique(self):
        return Atoms(list(set(self._atoms)))

    def keys(self) -> Keys:
        return Keys([x.key() for x in self._atoms])

    def filter(
        self,
        key: Key | str | None = None,
        first: Word | str | None = None,
    ):
        res = self._atoms.copy()
        if key:
            key = Key.glass(key)
            res = [x for x in self._atoms if x.key() == key]

        if first:
            first = Word.glass(first)
            res = [x for x in self._atoms if x.key().words()[0] == first]

        return Atoms(res)
