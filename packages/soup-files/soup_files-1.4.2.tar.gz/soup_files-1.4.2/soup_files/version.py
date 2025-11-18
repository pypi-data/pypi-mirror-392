#!/usr/bin/env python3

"""
import os
import tomllib

_file_version = os.path.relpath(__file__)
_dir_version = os.path.abspath(os.path.dirname(_file_version))
base_dir = os.path.abspath(os.path.join(_dir_version, '..'))
file_py_project = os.path.join(base_dir, 'pyproject.toml')

try:
    with open(file_py_project, 'rb') as f:
        _data = tomllib.load(f)
except Exception as e:
    print(e)
else:
    __version__ = _data['project']['version']

"""

__version__ = "1.4.2"


