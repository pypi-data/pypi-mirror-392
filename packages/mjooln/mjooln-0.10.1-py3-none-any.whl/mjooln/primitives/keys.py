from .key import Key, Word


class Keys:
    def __init__(self, keys: list[Key | str]):
        self._keys = [Key.glass(x) for x in keys]

    def __str__(self):
        return "[" + ", ".join([str(x) for x in self._keys]) + "]"

    def __repr__(self):
        return "[" + ", ".join([x.__repr__() for x in self._keys]) + "]"

    def __len__(self):
        return len(self._keys)

    def __iter__(self):
        return iter(self._keys)

    def __getitem__(self, i: int | slice):
        return self._keys[i]

    def __iadd__(self, other):
        if isinstance(other, str) or isinstance(other, Key):
            self._keys.append(Key.glass(other))
        elif isinstance(other, Keys):
            self._keys += other._keys
        else:
            raise TypeError(f"Invalid type {type(other)}")
        return self

    def append(self, key: str | Key):
        key = Key.glass(key)
        self._keys.append(key)

    def unique(self):
        return Keys(list(set(self._keys)))

    def filter(
        self,
        first: str | Word | None = None,
        last: str | Word | None = None,
        contains: str | Word | None = None,
        width: int | None = None,
    ):
        res = self._keys.copy()
        if first:
            first = Word.glass(first)
            res = [x for x in res if x.words()[0] == first]

        if last:
            last = Word.glass(last)
            res = [x for x in res if x.words()[-1] == last]

        if contains:
            contains = Word.glass(contains)
            res = [x for x in res if contains in x.words()]

        if width:
            res = [x for x in res if len(x.words()) == width]

        return Keys(res)
