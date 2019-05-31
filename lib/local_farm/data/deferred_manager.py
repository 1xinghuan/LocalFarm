# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 6/23/2018


from local_farm.module.db.peewee import DeferredForeignKey, ManyToManyField, DeferredThroughModel


class DeferredManager2(object):
    fk_model_names = []
    deferred_fks = []
    links = {}

    def __init__(self):
        super(DeferredManager2, self).__init__()

    @classmethod
    def fk(cls, fk_model_name, *args, **kwargs):
        if fk_model_name not in cls.fk_model_names:
            cls.fk_model_names.append(fk_model_name)
        deferred_fk = DeferredForeignKey(fk_model_name, *args, **kwargs)
        cls.deferred_fks.append(deferred_fk)
        return deferred_fk

    @classmethod
    def mtm(cls, model_name, through_model_name, *args, **kwargs):
        deferred_through_model = DeferredThroughModel()
        many_to_many = ManyToManyField(model=model_name, through_model=deferred_through_model, *args, **kwargs)
        link = {}
        link['model_name'] = model_name
        link['field'] = many_to_many
        cls.links[through_model_name] = link

        return many_to_many

    @classmethod
    def connect(cls, model_dict):
        for fk_model_name in cls.fk_model_names:
            DeferredForeignKey.resolve(model_dict[fk_model_name])
        for through_model_name in cls.links:
            link = cls.links[through_model_name]
            many_to_many = link['field']
            many_to_many.rel_model = model_dict[link['model_name']]
            many_to_many.through_model.set_model(model_dict[through_model_name])

    @classmethod
    def create_fk(cls):
        for deferred_fk in cls.deferred_fks:
            model = deferred_fk.model
            fk = getattr(model, deferred_fk.name)
            model._schema.create_foreign_key(fk)

