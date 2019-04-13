# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 4/10/2019

import logging

logging.basicConfig(
    level=logging.WARNING,
    format='[%(levelname)s] %(message)s'
)


import platform

PYTHON_MAIN_VERSION = int(platform.python_version_tuple()[0])

