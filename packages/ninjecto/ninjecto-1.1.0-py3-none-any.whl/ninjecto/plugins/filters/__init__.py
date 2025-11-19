# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 KuraLabs S.R.L
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""
Class to load filter plugins.

This class bridges Jinja's filters with Ninjecto:

    http://jinja.pocoo.org/docs/2.10/api/#custom-filters
"""

from functools import wraps
from logging import getLogger

from ..loader import FunctionLoader


log = getLogger(__name__)


class FiltersLoader(FunctionLoader):
    """
    Filters plugins loader class.
    """

    def __init__(self):
        super().__init__('ninjecto', 'filters')


FiltersLoader.reset()


@wraps(FiltersLoader.register)
def register(key):
    """
    Register a filter plugin.

    This function can be used as decorator:

    Usage:

    ::

        from ninjecto.plugins import filters

        @filters.register('my_filter')
        def my_filter(arg1):
            return arg1
    """
    return FiltersLoader.register(key)


__all__ = [
    'FiltersLoader',
    'register',
]
