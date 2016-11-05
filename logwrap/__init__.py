#    Copyright 2016 Mirantis, Inc.
#    Copyright 2016 Alexey Stepanov aka penguinolog
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

"""logwrap module

Contents: 'get_arg_names', 'get_call_args', 'logwrap', 'pretty_repr'

Original code was made for Mirantis Inc by Alexey Stepanov,
later it has been reworked and extended for support of special cases.
"""

from __future__ import absolute_import

from .func_helpers import get_arg_names
from .func_helpers import get_call_args
from .func_helpers import get_default_args
from .log_wrap import logwrap
from .repr_utils import pretty_repr

__version__ = '0.8.0'

__all__ = [
    'get_arg_names',
    'get_call_args',
    'logwrap',
    'pretty_repr',
    'get_default_args',
]
