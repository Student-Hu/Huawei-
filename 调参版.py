# -*- coding: utf-8 -*-
import logging
import sys
import pandas as pd
import numpy as np
import time

road_path = './1-map-exam-2/road.txt'
cross_path = './1-map-exam-2/cross.txt'
car_path = './1-map-exam-2/car.txt'
answer_path = r'C:\Users\Administrator\Desktop\新建文件夹\huawei2019-with-visualization-master\huawei2019-with-visualization-master\1-map-training-1\answer1.txt'

time_start = time.time()


def Algorithm(hh, start, end):
    dist = {}
    previous = {}
    for v in hh.keys():
        dist[v] = float('inf')
        previous[v] = 'none'
    dist[start] = 0
    u = str(start)

    while u != end:
        # 获得最小值对应的键
        u = min(dist, key=dist.get)
        distu = dist[u]
        del dist[u]
        for u, v, weight, id in hh[u]:
            if v in dist:
                alt = distu + int(weight)
                if alt < dist[v]:
                    dist[v] = alt
                    previous[v] = {u: id}
    path = [end]
    path_road = []
    last = end
    while last != start:
        nxt = min(previous[last], key=previous[last].get)
        #        nxt = list(previous[last].keys())
        road = previous[last][nxt]
        path_road.append(road)
        path.append(nxt)
        last = nxt
    return path, path_road


def planTime(number, numberV, tismepace):
    for i in range(len(numberV)):
        if numberV[i] <= number < numberV[i + 1]:
            k1 = tismepace / ((numberV[i + 1] - numberV[i]))
            b1 = tismepace * (i + 1) + 100 * i - k1 * (numberV[i + 1])
            plantime = int(int(k1 * number) + 1 + b1)
            break
        else:
            continue
    return plantime


def planTime1(number, numberV, tismepace):
    for i in range(len(numberV)):
        if (sum(numberV[0:i + 1])) <= number < (sum(numberV[0:i + 2])):
            k1 = (tismepace / ((numberV[i + 1])))
            b1 = (tismepace * (i + 1) + 100 * i - k1 * sum(numberV[0:i + 2]))
            plantime = int(int(k1 * number) + 1 + b1)
            break
        else:
            continue
    return plantime



road1 = []
with open(road_path, 'r') as f:
    for line in f:
        road1.append(
            list(line.strip('\n').replace(' ', '').replace('(', '').replace(')', '').replace('#', '').split(',')))
road = pd.DataFrame((road1)[1:])
road.columns = road1[0]
for i in range(road.shape[0]):
    if road.iloc[i]['isDuplex'] == '1':
        new_road = road.iloc[i].rename({'to': 'from', 'from': 'to'})

        road = road.append(new_road, ignore_index=True)

cross1 = []
with open(cross_path, 'r') as f:
    for line in f:
        cross1.append(
            list(line.strip('\n').replace(' ', '').replace('(', '').replace(')', '').replace('#', '').split(',')))
cross = pd.DataFrame(cross1[1:])
cross.columns = ['id', 'roadId1', 'roadId2', 'roadId3', 'roadId4']

for i in range(road.shape[0]):
    road['isDuplex'][i] = int((int(road['length'][i]) + int(road['speed'][i]) - 1) / int(road['speed'][i]))

hh = {}
node = cross['id'].values.tolist()
for i in node:
    list_key = []
    TO = road[road['from'] == i][['to', 'isDuplex', 'id']].values.tolist()
    for to, length, id in TO:
        list_key.append((i, to, length, id))
    hh.update({i: list_key})

car1 = []
car_f = open(car_path, 'r').read().split('\n')[1:]
for line in car_f:
    car1.append(
        list(line.strip('\n').replace(' ', '').replace('(', '').replace(')', '').replace('#', '').split(',')))
car = pd.DataFrame(car1[:])
car.columns = ['id', 'from', 'to', 'speed', 'planTime']
Z_luxian = {}
car = car.sort_values(['id'], ascending=True)  # 按照车id升序
car = car.sort_values(["speed"], ascending=False)
num_of_car = car.shape[0]
if num_of_car < 15000:
    maxtime = 600
elif 15000 <= num_of_car < 30000:
    maxtime = 1800
else:
    maxtime = 2500
numberV = list(car.groupby(by='speed').size())
numberV.reverse()
numberV.insert(0, 0)
n = len(numberV)
tismepace = (maxtime - (n - 2) * 100) // n
# np.random.seed(0)
car['path1to'] = None
fw = open(answer_path, 'w')  # 将要输出保存的文件地址
for j in range(car.shape[0]):
    from_node = car.iloc[j]['from']
    to_node = car.iloc[j]['to']
    path, path_road = Algorithm(hh, from_node, to_node)
    path.reverse()
    path_road.reverse()
    jieguo = path_road.copy()
    print(path)
    car.iloc[j]['path1to'] = path[1]
    if j < num_of_car // 100:
        palntime1 = planTime1(j, numberV, tismepace) + np.random.randint(1, 2)
        if int(car.iloc[j]['planTime']) < palntime1:
            car.iloc[j]['planTime'] = str(palntime1).split('.0')[0]
    else:
        palntime2 = planTime1(j, numberV, tismepace) + np.random.randint(10, 40)
        if int(car.iloc[j]['planTime']) < palntime2:
            car.iloc[j]['planTime'] = str(palntime2).split('.0')[0]
    jieguo.insert(0, car.iloc[j]['id'])
    jieguo.insert(1, car.iloc[j]['planTime'])
time_end = time.time()

