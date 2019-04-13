# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 4/11/2019

import os

opd = os.path.dirname


class AttrDict(dict):
    def __getattr__(self, attr):
        return self[attr]


LOCAL_FARM_ROOT = opd(opd(opd(opd(os.path.abspath(__file__)))))
LOCAL_FARM_DB_FILE = os.path.join(LOCAL_FARM_ROOT, 'database.sqlite')


LOCAL_FARM_STATUS = AttrDict(
    new='new',
    pending='pending',
    running='running',
    complete='complete',
    block='block',
    failed='failed',
)


LOCAL_FARM_VARIABLES = AttrDict(
    FRAME_START='FARM_FRAME_START',
    FRAME_END='FARM_FRAME_END',
    FRAME_INTERVAL='FARM_FRAME_INTERVAL',
    FRAME_STRING='FARM_FRAME_STRING',
)

