"""Inverting pair mappings helper tool."""

import os
import pathlib

from typing import Union  # py39 does not handle |

__version__ = '2025.11.16'
__version_info__ = tuple(
    e if '-' not in e else e.split('-')[0] for part in __version__.split('+') for e in part.split('.') if e != 'parent'
)
__all__: list[str] = [
    'APP_ALIAS',
    'APP_NAME',
    'DEBUG',
    'ENCODING',
    'ENC_ERRS',
    'GENERATOR_CAVEAT_KEY',
    'GENERATOR_CAVEAT_VALUE',
    'JSON_FORMAT',
    'LOG_AMBIGUITY',
    'LOG_MISSING',
    'PathLike',
    'VERSION',
    'VERSION_INFO',
    'YAML_FORMAT',
]

APP_ALIAS = str(pathlib.Path(__file__).parent.name)
APP_ENV = APP_ALIAS.upper()
APP_NAME = locals()['__doc__']

DEBUG = bool(os.getenv(f'{APP_ENV}_DEBUG', ''))

ENCODING = 'utf-8'
ENC_ERRS = 'ignore'

GENERATOR_CAVEAT_KEY = 'Please do not edit manually!'
GENERATOR_CAVEAT_VALUE = 'Cf. documentation'

LOG_AMBIGUITY = 'Error: source has ambiguous values.'
LOG_MISSING = 'Error: source file does not exist.'

JSON_FORMAT = 'json'
YAML_FORMAT = 'yaml'

PathLike = Union[pathlib.Path, str]
VERSION = __version__
VERSION_INFO = __version_info__
