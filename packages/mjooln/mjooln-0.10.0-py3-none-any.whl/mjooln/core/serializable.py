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

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Any

from mjooln.environment import WORD_SEPARATOR


class Serializable(ABC):
    """
    Base class for custom serializable objects.
    Subclasses must implement to_dict() and from_dict().
    """

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Serialize this object to a dictionary."""
        pass

    def to_flat(self, sep: str = WORD_SEPARATOR) -> dict[str, Any]:
        """
        Serialize object to a flat dict, joining nested keys with `sep`.

        Example:
            {"a": {"b": 1}, "c": 2} -> {"a__b": 1, "c": 2}
        """

        def _flatten(prefix: str, value: Any, out: dict[str, Any]) -> None:
            if isinstance(value, dict):
                for k, v in value.items():
                    new_key = f"{prefix}{sep}{k}" if prefix else k
                    _flatten(new_key, v, out)
            else:
                out[prefix] = value

        nested_di = self.to_dict()
        flat_di: Dict[str, Any] = {}
        for key, val in nested_di.items():
            _flatten(key, val, flat_di)
        return flat_di

    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> Serializable:
        """Create an instance of this class from a dictionary."""
        pass

    @classmethod
    def from_flat(cls, data: Dict[str, Any], sep: str = "__") -> Serializable:
        nested: Dict[str, Any] = {}

        for flat_key, value in data.items():
            parts = flat_key.split(sep)
            current = nested
            for part in parts[:-1]:
                if part not in current or not isinstance(current[part], dict):
                    current[part] = {}
                current = current[part]  # type: ignore[assignment]
            current[parts[-1]] = value

        return cls.from_dict(nested)


# if __name__ == '__main__':
#     di = {"one": {"two": 2, "three": 3}, "four": 4, "five": 5}
#     class Test(Serializable):
#
#         def __init__(self, one: dict, four: int, five: int):
#             self.one = one
#             self.four = four
#             self.five = five
#
#         def to_dict(self) -> Dict[str, Any]:
#             return {"one": self.one, "four": self.four, "five": self.five}
#
#         @classmethod
#         def from_dict(cls, data: Dict[str, Any]) -> Test:
#             return cls(**data)
#
#     import pprint
#     t = Test.from_dict(di)
#
#     di2 = t.to_dict()
#     pprint.pprint(di2)
#     di3 = t.to_flat()
#     pprint.pprint(di3)
#     t2 = Test.from_flat(di3)
#     pprint.pprint(t2.to_dict())
#     print(3)
