#    Copyright 2016-2019 Alexey Stepanov aka penguinolog

#    Copyright 2016 Mirantis, Inc.

#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

# pylint: disable=missing-docstring

"""_repr_utils (internal helpers) specific tests."""

# Standard Library
import sys
import typing
import unittest

# LogWrap Implementation
import logwrap


# noinspection PyUnusedLocal,PyMissingOrEmptyDocstring
class TestPrettyRepr(unittest.TestCase):
    def test_001_dict_subclass(self):
        class MyDict(dict):
            """Dict subclass."""

        val = MyDict(key='value')
        self.assertEqual(
            "MyDict({\n"
            "    'key': 'value',\n"
            "})",
            logwrap.pretty_repr(val)
        )

        self.assertEqual(
            '{\n'
            '    key: value,\n'
            '}',
            logwrap.pretty_str(val)
        )

    def test_002_typing_specific_dict(self):
        class MyDict(typing.Dict[str, str]):
            """Dict subclass."""

        val = MyDict(key='value')
        self.assertEqual(
            "MyDict({\n"
            "    'key': 'value',\n"
            "})",
            logwrap.pretty_repr(val)
        )

        self.assertEqual(
            '{\n'
            '    key: value,\n'
            '}',
            logwrap.pretty_str(val)
        )

    @unittest.skipIf(sys.version_info[:2] < (3, 8), 'pep-0589 is implemented in python 3.8')
    def test_003_typed_dict(self):
        class MyDict(typing.TypedDict):
            key: str

        val = MyDict(key='value')
        self.assertEqual(
            "dict({\n"
            "    'key': 'value',\n"
            "})",
            logwrap.pretty_repr(val)
        )

        self.assertEqual(
            '{\n'
            '    key: value,\n'
            '}',
            logwrap.pretty_str(val)
        )