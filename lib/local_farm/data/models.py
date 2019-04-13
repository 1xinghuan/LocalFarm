# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 4/10/2019

import os
import datetime
from local_farm.module.db.peewee import *
from local_farm.utils.const import LOCAL_FARM_DB_FILE, LOCAL_FARM_STATUS
from local_farm.utils.frame import get_frame_list
import logging

logger = logging.getLogger('local_farm_model')


database = SqliteDatabase(LOCAL_FARM_DB_FILE)


class BaseModel(Model):
    class Meta:
        database = database

    def __str__(self):
        return '<{}> {}'.format(self.__class__.__name__, self.id)


class FarmJob(BaseModel):
    name = CharField(null=True)
    status = CharField(null=True, default=LOCAL_FARM_STATUS.new)
    progress = IntegerField(null=True, default=0)  # 0-100
    submitTime = DateTimeField(null=True, default=datetime.datetime.now)
    startTime = DateTimeField(null=True)
    completeTime = DateTimeField(null=True)
    elapsedTime = IntegerField(null=True, default=0)
    cwd = CharField(null=True)
    env = TextField(null=True)
    command = CharField(null=True)
    frameRange = CharField(null=True)  # 1-100x1 or 1-100 or 100 or 1,3
    callbacks = CharField(null=True)

    class Meta:
        db_table = 'jobs'

    def __init__(self, *args, **kwargs):
        super(FarmJob, self).__init__(*args, **kwargs)

        self._framePerInstance = None

    def set_command(self, command):
        self.command = command

    def set_chunk(self, value):
        self._framePerInstance = value

    def set_frame_range(self, range):
        """
        :param range: list or str
            1-100
            1-100x2
            1,100
            100
            [str, ]
        :return:
        """
        self.frameRange = range

    def submit(self):
        if self.command is None:
            logger.error('command is None!')
            return

        self.save()

        if self.frameRange is not None:
            if isinstance(self.frameRange, list):
                frameRangeList = self.frameRange
            else:
                frameRangeList = [self.frameRange]
                if self._framePerInstance is not None:
                    frameRangeList = get_frame_list(
                        self.frameRange, framesPerInstance=self._framePerInstance
                    )
        else:
            frameRangeList = [None]

        for frameRange in frameRangeList:
            instance = FarmInstance()
            instance.frameRange = frameRange
            instance.job = self
            instance.save()

        return self.id

    def get_instances(self, status=None, reverse=False):
        query = (FarmInstance.select(FarmInstance, FarmJob)
                 .join(FarmJob)
                 .where(FarmInstance.job == self.id)
                 .order_by(FarmInstance.id)
                 )
        if status is not None:
            if isinstance(status, basestring):
                if not reverse:
                    query = query.where(FarmInstance.status == status)
                else:
                    query = query.where(FarmInstance.status != status)
            elif isinstance(status, list):
                if not reverse:
                    query = query.where(FarmInstance.status.in_(status))
                else:
                    query = query.where(FarmInstance.status.not_in(status))
        return [i for i in query]

    def check_self(self):
        notCompleteInstances = self.get_instances(LOCAL_FARM_STATUS.complete, reverse=True)
        if len(notCompleteInstances) == 0:
            self.status = LOCAL_FARM_STATUS.complete
            self.save()


class FarmInstance(BaseModel):
    job = ForeignKeyField(model=FarmJob, backref='instances')

    status = CharField(null=True, default=LOCAL_FARM_STATUS.new)
    progress = IntegerField(null=True, default=0)  # 0-100
    startTime = DateTimeField(null=True)
    completeTime = DateTimeField(null=True)
    elapsedTime = IntegerField(null=True, default=0)
    frameRange = CharField(null=True)
    stdout = TextField(null=True)
    stderr = TextField(null=True)
    pid = IntegerField(null=True)

    class Meta:
        db_table = 'instances'


models = [
    FarmJob,
    FarmInstance,
]


def create_tables():
    for model in models:
        model.create_table()


if not os.path.exists(LOCAL_FARM_DB_FILE):
    create_tables()


