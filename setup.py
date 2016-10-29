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

import setuptools
import sys

setuptools.setup(
    name='logwrap',
    version='0.5',
    packages=['logwrap'],
    zip_safe=True,
    url='',
    license='Apache License, Version 2.0',
    author='Alexey Stepanov',
    author_email='penguinolog@gmail.com',
    description=(
        'Decorator for logging function arguments by human-readable way'
    ),
    install_requires=[
        'six>=1.9.0'
        'pytest-runner>=2.0',
    ],
    tests_require=[
        'flake8',
        'tox>=2.0',
        'pytest>=3.0',
        'pytest-cov',
        'mock' if sys.version_info.major == 2 else ''
    ],
)