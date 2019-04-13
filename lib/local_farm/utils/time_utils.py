# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 4/13/2019

import datetime


def datetime_to_str(date, format='%m-%d %H:%M:%S'):
    """
    :param date:
    :param format:
    '%Y-%m-%d'
    '%Y-%m-%d %H:%M'
    '%m-%d %H:%M:%S'
    :return:
    """
    if date is None:
        return 'None'
    else:
        return datetime.datetime.strftime(date, format)


TIME_CHUNKS = (
    (60 * 60 * 24 * 365, 'year'),
    (60 * 60 * 24 * 30, 'month'),
    (60 * 60 * 24, 'day'),
    (60 * 60, 'hour'),
    (60, 'minute'),
    (1, 'second'),
)


def get_detail_time_delta(time_delta, split=None):
    if time_delta is None:
        return 'None'
    result = []
    for seconds, unit in TIME_CHUNKS:
        count = time_delta // seconds
        time_delta -= count * seconds
        result.append([count, unit])
    # return result
    text = ''
    for index, value in enumerate(result):
        if value[0] != 0:
            if split is None:
                valueText = '{}{}'.format(value[0], value[1])
            else:
                valueText = '{}{}'.format(split, value[0])
            text += valueText
    return text

