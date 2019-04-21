# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 4/10/2019

# import logging
#
# logging.basicConfig(
#     level=logging.WARNING,
#     format='[%(levelname)s] %(message)s'
# )


import os
import platform

this_file = os.path.abspath(__file__)
bin_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(this_file))), 'bin')

os.environ['PATH'] = bin_dir + os.pathsep + os.environ['PATH']

PYTHON_MAIN_VERSION = int(platform.python_version_tuple()[0])

