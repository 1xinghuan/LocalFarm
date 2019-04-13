# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 4/12/2019


def get_frame_list1(frameIn, frameOut, interval=1, framesPerInstance=1):
    inout = [str(i) for i in range(int(frameIn), int(frameOut) + 1, int(interval))]
    framesEach = framesPerInstance
    n = len(inout) / framesEach
    if len(inout) % framesEach > 0:
        n = n + 1

    frameList = [[] for i in range(n + 1)]
    for i in range(1, n):
        frameList[i] = inout[((i - 1) * framesEach):(i * framesEach)]
    frameList[n] = inout[((n - 1) * framesEach):]
    frameStrs = ["" for i in range(n + 1)]
    for i in range(1, n + 1):
        tempList = []
        if frameList[i] != []:
            tempList.append(frameList[i][0])
            tempList.append(frameList[i][-1])
            frameStrs[i] = "-".join(tempList)
            frameStrs[i] += 'x{}'.format(interval)
    if '' in frameStrs:
        frameStrs.remove('')
    return frameStrs


def get_frame_list2(frameStr, framesPerInstance):
    frameList = frameStr.split(',')
    frameNum = len(frameList)
    framesEach = framesPerInstance
    instanceNum = frameNum / framesEach
    if frameNum % framesEach > 0:
        instanceNum = instanceNum + 1
    frameStrs = []
    for i in range(instanceNum - 1):
        indexIn = framesEach * i
        indexOut = framesEach * (i + 1)
        eachFrameStr = ','.join(frameList[indexIn:indexOut])
        frameStrs.append(eachFrameStr)

    frameStrs.append(','.join(frameList[(framesEach * (instanceNum - 1)):]))

    return frameStrs


def get_frame_list(frameStr, framesPerInstance):
    tempStr = frameStr
    if tempStr.find(',') != -1:
        return get_frame_list2(tempStr, framesPerInstance)
    elif tempStr.find('-') != -1:
        if tempStr.find('x') != -1:
            interval = int(tempStr.split('x')[-1])
            tempStr = tempStr.split('x')[0]
        else:
            interval = 1
        frameIn = int(tempStr.split('-')[0])
        frameOut = int(tempStr.split('-')[-1])
        return get_frame_list1(frameIn, frameOut, interval, framesPerInstance)
    else:
        return [int(tempStr)]


def get_frame_info(frameStr):
    tempStr = frameStr
    if tempStr.find(',') != -1:
        return '', '', ''
    elif tempStr.find('-') != -1:
        if tempStr.find('x') != -1:
            interval = tempStr.split('x')[-1]
            tempStr = tempStr.split('x')[0]
        else:
            interval = '1'
        frameIn = tempStr.split('-')[0]
        frameOut = tempStr.split('-')[-1]

        return frameIn, frameOut, interval
