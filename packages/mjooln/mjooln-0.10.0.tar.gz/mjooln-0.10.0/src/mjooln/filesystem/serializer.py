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

import json

import simplejson  # type: ignore[import-untyped]
import yaml  # type: ignore[import-untyped]


class Serializer:
    @classmethod
    def json_dumps(cls, di, human=True, sort_keys=False, indent=4 * " "):
        """Convert from dict to JSON string

        :param di: Input dictionary
        :type di: dict
        :param human: Human readable flag
        :param sort_keys: Sort key flag (human readable only)
        :param indent: Indent to use (human readable only)
        :return: JSON string
        :rtype: str
        """
        if human:
            return simplejson.dumps(di, sort_keys=sort_keys, indent=indent)
        else:
            return json.dumps(di)

    @classmethod
    def json_loads(cls, json_string):
        """Parse JSON string to dictionary

        :param json_string: JSON string
        :type json_string: str
        :return: Dictionary
        :rtype: dict
        """
        return simplejson.loads(json_string)

    @classmethod
    def json_to_yaml(cls, json_string):
        di = cls.json_loads(json_string)
        return cls.yaml_dumps(di)

    @classmethod
    def yaml_dumps(cls, di: dict):
        """
        Convert dictionary to YAML string

        :param di: Input dictionary
        :type di: dict
        :return: YAML string
        :rtype: str
        """
        return yaml.safe_dump(di)

    @classmethod
    def yaml_loads(cls, yaml_str):
        """
        Convert YAML string to dictionary

        :param yaml_str: Input YAML string
        :type yaml_str: str
        :return: Dictionary
        :rtype: dict
        """
        return yaml.safe_load(yaml_str)

    @classmethod
    def yaml_to_json(cls, yaml_str, human=False):
        di = cls.yaml_loads(yaml_str)
        return cls.json_dumps(di, human=human)
