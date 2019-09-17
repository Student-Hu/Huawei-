# -*- coding: utf-8 -*-
"""
Created on Mon Mar 25 22:25:13 2019

@author: Administrator
"""
def update_road(In_road, current, k,road, car):
    roading = In_road.sort_values(["run_channel"], ascending=True)  # 按车道升序
    roading = roading.sort_values(["weizhi"], ascending=False)  # 按照位置降序
    channel_index = roading[roading['run_channel'] == k ].index.tolist()
    if len(channel_index) != 0:
        last_i = 0  # 上一个车
        for i in channel_index:  # 对每条道路上每个车道的车辆进行分析
            car_speed = car[car['id'] == current['carid'][i]]['speed'].values.tolist()[0]  ###第一辆车的速度
            road_speed = road[(road['id'] == current['run_road'][i])]['speed'].values.tolist()[0]
            V1 = int(min(int(car_speed), int(road_speed)))  # 最大行驶速度
            if last_i > 0:
                s = current['weizhi'][last_i] - current['weizhi'][i] - 1  # 间距
                if (s < V1):  # 且间距小于s < v*t--->有阻挡
                    if (current['state'][last_i] == 0):  # 如果前车为终止状态
                        current['state'][i] = 0  # 终止
                        S_ = current['weizhi'][i] + min(V1, s)
                        current['weizhi'][i] = S_
                    if (current['state'][last_i] == 1):  # 如果前车为等待状态
                        current['state'][i] = 1  # 等待
                else:  # 没车阻挡
                    S_ = current['weizhi'][i] + V1  # 当前位置
                    current['state'][i] = 0  # 终止
                    current['weizhi'][i] = S_
            else:
                S_ = current['weizhi'][i] + V1  # 当前位置
                if int(road[road['id'] == current['run_road'][i]]['length'].values.tolist()[
                           0]) >= S_:  ##int(road[road['id']==current['id'][i]]['length'].values.tolist()[0])=S_:
                    current['state'][i] = 0  # 终止
                    current['weizhi'][i] = S_
                else:
                    current['state'][i] = 1  # 等待
            last_i = i
    return current

# def update_road( In_road ,current,road,car):
#      roading = In_road.sort_values(["run_channel"], ascending=True)  # 按车道升序
#      roading = roading.sort_values(["weizhi"], ascending=False)  # 按照位置降序
#      for k in range(int(road[road['id']==roading['run_road'].iloc[0]]['channel'].iloc[0])):  # 判断当前道路总共有多少车道
#         channel_index = roading[roading['run_channel'] == k + 1].index.tolist()
#         if len(channel_index)!=0:
#             last_i = 0  # 上一个车
#             for i in channel_index:  # 对每条道路上每个车道的车辆进行分析
# #                if roading['to'][i] == Z_luxian[current['carid'][i]]['path'][-1]:  # 第一辆车到路口了
# #                    current.drop(i)
# #                else:
#                 car_speed = car[car['id']==current['carid'][i]]['speed'].values.tolist()[0]  ###第一辆车的速度
#                 road_speed = road[(road['id'] == current['run_road'][i])]['speed'].values.tolist()[0]
#                 V1 = int(min(int(car_speed), int(road_speed)))  # 最大行驶速度
#                 if last_i > 0:
#                     s = current['weizhi'][last_i] - current['weizhi'][i] - 1  # 间距
#                     if (s < V1):  # 且间距小于s < v*t--->有阻挡
#                         if (current['state'][last_i] == 0):  # 如果前车为终止状态
#                             current['state'][i] = 0  # 终止
#                             S_ = current['weizhi'][i] + min(V1, s)
#                             current['weizhi'][i] = S_
#                         if (current['state'][last_i] == 1):  # 如果前车为等待状态
#                             current['state'][i] = 1  # 等待
#                     else:  # 没车阻挡
#                         S_ = current['weizhi'][i] + V1  # 当前位置
#                         current['state'][i] = 0  # 终止
#                         current['weizhi'][i] = S_
#                 else:
#                     S_ = current['weizhi'][i] + V1  # 当前位置
#                     if int(road[road['id']==current['run_road'][i]]['length'].values.tolist()[0])>= S_:  ##int(road[road['id']==current['id'][i]]['length'].values.tolist()[0])=S_:
#                         current['state'][i] = 0  # 终止
#                         current['weizhi'][i] = S_
#                     else:
#                         current['state'][i] = 1  # 等待
#                 last_i = i
#      return current

def update_road_first_end( In_road ,index,current,road,car):
     # roading = In_road.sort_values(["run_channel"], ascending=True)  # 按车道升序
     # roading = roading.sort_values(["weizhi"], ascending=False)  # 按照位置降序
     k=current['run_channel'][index]                         
#     for k in range(int(road[road['id']==roading['id']]['channel'].iloc[0])):  # 判断当前道路总共有多少车道
     channel_index = In_road[In_road['run_channel'] == k].index.tolist()
     last_i =index  # 上一个车
     for i in channel_index:  # 对每条道路上每个车道的车辆进行分析
        car_speed = car[car['id']==current['carid'][i]]['speed'].values.tolist()[0]  ###第一辆车的速度
        road_speed = road[(road['id'] == current['run_road'][i])]['speed'].values.tolist()[0]
        V1 = int(min(int(car_speed), int(road_speed)))  # 最大行驶速度
        s = current['weizhi'][last_i] - current['weizhi'][i] - 1  # 间距
        if (s < V1):  # 且间距小于s < v*t--->有阻挡
            if (current['state'][last_i] == 0):  # 如果前车为终止状态
                current['state'][i] = 0  # 终止
#                current['V1'][i] = min(current['V1'][i], s)
                S_ = current['weizhi'][i] +  min(V1, s)
                current['weizhi'][i] = S_
            if (current['state'][last_i] ==1):  # 如果前车为等待状态
                current['state'][i] = 1  # 等待
        last_i = i
     return current

#update_road( In_road ,Z_luxian,current,road)