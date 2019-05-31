# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 4/10/2019

import os
import datetime
import tempfile
from local_farm.module.db.peewee import *
from local_farm.utils.const import LOCAL_FARM_DB_FILE, LOCAL_FARM_STATUS
from local_farm.utils.frame import get_frame_list
import logging
from local_farm.data.deferred_manager import DeferredManager2

logger = logging.getLogger('local_farm_model')


database = SqliteDatabase(LOCAL_FARM_DB_FILE)
dm = DeferredManager2


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
    _env = TextField(null=True, column_name='env')
    command = CharField(null=True)
    frameRange = CharField(null=True)  # 1-100x1 or 1-100 or 100 or 1,3
    callbacks = CharField(null=True)

    class Meta:
        db_table = 'jobs'

    def get_sources(self, from_query=False):
        if not isinstance(self.sources_connection, list) or from_query:
            return (FarmJob
                    .select(FarmJob, FarmJobRelationship)
                    .join(FarmJobRelationship, on=FarmJobRelationship.from_job)
                    .where(FarmJobRelationship.to_job == self)
                    )
        else:
            return [i.from_job for i in self.sources_connection]

    def get_destinations(self):
        if not isinstance(self.destinations_connection, list):
            return (FarmJob
                    .select(FarmJob, FarmJobRelationship)
                    .join(FarmJobRelationship, on=FarmJobRelationship.to_job)
                    .where(FarmJobRelationship.from_job == self)
                    )
        else:
            return [i.to_job for i in self.destinations_connection]

    @property
    def sources(self):
        return self.get_sources()

    @property
    def destinations(self):
        return self.get_destinations()

    def set_dependency(self, sources):
        self._tempSources = sources

    def __init__(self, *args, **kwargs):
        super(FarmJob, self).__init__(*args, **kwargs)

        self._framePerInstance = None
        self._tempSources = []

    def set_name(self, name):
        self.name = name

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

    @property
    def env(self):
        env = self._env
        if env is not None:
            env = eval(env)
            return env
        else:
            return {}

    @env.setter
    def env(self, value):
        if value is not None:
            value = str(value)
        self._env = value

    def submit(self, useCurrentEnv=True):
        if self.command is None:
            logger.error('command is None!')
            return

        if useCurrentEnv:
            currentEnv = {}
            currentEnv.update(os.environ)
            currentEnv.update(self.env)
            self.env = currentEnv

        self.save()

        if len(self._tempSources) > 0:
            sources_data = [{'from_job': v, 'to_job': self} for v in self._tempSources]
            FarmJobRelationship.insert_many(sources_data).execute()

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

    def check_sources(self):
        # print 'check_sources'
        if len(self.sources) > 0:
            sourcesFinished = True
            for sourceJob in self.get_sources(from_query=True):
                # print sourceJob, sourceJob.status
                if sourceJob.status != LOCAL_FARM_STATUS.complete:
                    sourcesFinished = False
                    break
            if sourcesFinished:
                for instance in self.instances:
                    instance.status = LOCAL_FARM_STATUS.pending
                    instance.save()
                self.status = LOCAL_FARM_STATUS.pending
                self.save()
                return True


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

    def __init__(self, *args, **kwargs):
        super(FarmInstance, self).__init__(*args, **kwargs)

        self.processThread = None

    def _get_temp_std_txt(self, err=False):
        stdTxt = os.path.join(tempfile.gettempdir(), 'localfarm_stdout_{}.txt'.format(self.id))
        if err:
            stdTxt = os.path.join(tempfile.gettempdir(), 'localfarm_stderr_{}.txt'.format(self.id))
        return stdTxt

    def write_temp_std(self, text, err=False):
        stdTxt = self._get_temp_std_txt(err)
        with open(stdTxt, 'a') as f:
            f.write(text)

    def read_temp_std(self, err=False):
        stdTxt = self._get_temp_std_txt(err)
        text = ''
        if os.path.isfile(stdTxt):
            with open(stdTxt, 'r') as f:
                text = f.read()
        return text

    def write_std(self):
        stdout = self.read_temp_std()
        stderr = self.read_temp_std(err=True)
        self.stdout = stdout
        self.stderr = stderr

    def get_std(self, err=False):
        text = self.read_temp_std(err)
        if text == '':
            text = self.stderr if err else self.stdout
        return text


class FarmJobRelationship(BaseModel):
    from_job = dm.fk(fk_model_name='FarmJob', backref='destinations_connection')
    to_job = dm.fk(fk_model_name='FarmJob', backref='sources_connection')

    class Meta:
        indexes = ((('from_job', 'to_job'), True),)
        db_table = 'job_relationship'


models = [
    FarmJob,
    FarmInstance,
    FarmJobRelationship,
]


def create_class_dict(members, obj_class):
    class_dict = {}
    for name, obj in members.items():
        try:
            if issubclass(obj, obj_class):
                class_dict[name] = obj
        except:
            pass
    return class_dict


model_dict = create_class_dict(globals().copy(), Model)
dm.connect(model_dict)


def create_tables():
    for model in models:
        model.create_table()


if not os.path.exists(LOCAL_FARM_DB_FILE):
    create_tables()


