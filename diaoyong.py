import numpy as np
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

def update_road_first_end(In_road, index, current, road, car):
    # roading = In_road.sort_values(["run_channel"], ascending=True)  # 按车道升序
    # roading = roading.sort_values(["weizhi"], ascending=False)  # 按照位置降序
    k = current['run_channel'][index]
    #     for k in range(int(road[road['id']==roading['id']]['channel'].iloc[0])):  # 判断当前道路总共有多少车道
    channel_index = In_road[In_road['run_channel'] == k].index.tolist()
    last_i = index  # 上一个车
    for i in channel_index:  # 对每条道路上每个车道的车辆进行分析
        car_speed = car[car['id'] == current['carid'][i]]['speed'].values.tolist()[0]  ###第一辆车的速度
        road_speed = road[(road['id'] == current['run_road'][i])]['speed'].values.tolist()[0]
        V1 = int(min(int(car_speed), int(road_speed)))  # 最大行驶速度
        s = current['weizhi'][last_i] - current['weizhi'][i] - 1  # 间距
        if (s < V1):  # 且间距小于s < v*t--->有阻挡
            if (current['state'][last_i] == 0):  # 如果前车为终止状态
                current['state'][i] = 0  # 终止
                #                current['V1'][i] = min(current['V1'][i], s)
                S_ = current['weizhi'][i] + min(V1, s)
                current['weizhi'][i] = S_
            if (current['state'][last_i] == 1):  # 如果前车为等待状态
                current['state'][i] = 1  # 等待
        last_i = i
    return current

def Addcar(Z_luxian,current,road,index,caing_start2end,car,start_id,end_id):
    ##判断当前道路的状况
    road_id = road.iloc[index]['id']  # 当前道路
    road_speed = road.iloc[index]['speed']  # 当前道路限速
    road_channel = int(road.iloc[index]['channel'])  # 当前道路车道数
    road_length = int(road.iloc[index]['length'])  # 当前道路长度
    capacity = road_channel * road_length
    for k in range(road_channel):
        for car_in_road in caing_start2end['id'].values.tolist():
            if current[(current['from'] == start_id) & (current['to'] == end_id)].shape[0] <= int(0.8 * capacity):  # 道路容量的80%
                enough = False  #
                roading = current[(current['from'] == start_id) & (current['to'] == end_id) & (current['run_channel'] == k + 1)]
                if roading.empty:
                    S = road_length
                else:
                    roading = roading.sort_values(["weizhi"], ascending=True)  # 按照位置深序
                    S = roading["weizhi"].iloc[0] - 1  # 最后一辆车的位置                #                            print(S)
                car_speed = caing_start2end[caing_start2end['id'] == car_in_road]['speed'].values.tolist()[
                    0]  ###第一辆车的速度
                V1 = int(min(int(car_speed), int(road_speed)))  # 最大行驶速度
                ## 第一辆车可不可以放
                if S > 0:  # 能放
                    next_road = Z_luxian[car_in_road]['path_road'][1]  # 下一条出发路线
                    run_channel = 1 + k  #
                    S_ = min(V1, S)  # 当前位置
                    state = 0
                    row = {'carid': car_in_road, 'run_road': road_id, 'from': start_id, 'to': end_id,
                           'run_channel': run_channel, 'weizhi': S_, 'state': state,
                           'next_road': next_road}
                    current = current.append(row, ignore_index=True)  # 运行的集合中加入这个车
                    caing_start2end = caing_start2end[~caing_start2end['id'].str.contains(car_in_road)]  # 带出发的车删除这个车
                    continue
                else:  # 这条道不能放
                    break
            else:
                enough=True
                index = caing_start2end.index
                car['planTime'].loc[index] = (car.loc[index]['planTime'].astype(int) + 1).astype(str)
                break
        if enough:
            break
    return current,car

Direction={"roadId1-roadId2":2,"roadId1-roadId4":1,"roadId2-roadId1":1,"roadId2-roadId3":2,
               "roadId3-roadId2":1,"roadId3-roadId4":2,"roadId4-roadId3":1,"roadId4-roadId1":2,
               "roadId2-roadId4":3,"roadId4-roadId2":3,"roadId1-roadId3":3,"roadId3-roadId1":3,
               "roadId1-roadId1":3,"roadId2-roadId2":3,"roadId3-roadId3":3,"roadId4-roadId4":3}

# def dicrion(to,next_road,road,cross):
#     id=cross[cross['id']== to]
#     directionid2=id.columns[np.where(id==next_road)[1]].tolist()[0]
#     directionid1=id.columns[np.where(id==road)[1]].tolist()[0] #找到对应的列名
#     direct=Direction[str(directionid1+'-'+directionid2)]#行驶方向
#     return direct
#
#
# def conflict(second_road_,run_road,cross_id,cross):
#     second_road = second_road_.sort_values(["run_channel"], ascending=True)  # 按照位置sheng序
#     second_road = second_road.sort_values(["weizhi"], ascending=False)
#     second_road_id = second_road['next_road'].iloc[0]
#     nxt = cross_id
#     roading = str(run_road)
#     next_road = second_road_id
#     second_dir = dicrion(nxt, next_road, roading,cross)
#     return second_road_id,second_dir
def Addcar(Z_luxian,current,road,index,caing_start2end,car,start_id,end_id):
    ##判断当前道路的状况
    road_id = road.iloc[index]['id']  # 当前道路
    road_speed = road.iloc[index]['speed']  # 当前道路限速
    road_channel = int(road.iloc[index]['channel'])  # 当前道路车道数
    road_length = int(road.iloc[index]['length'])  # 当前道路长度
    capacity = road_channel * road_length
    for k in range(road_channel):
        if caing_start2end.shape[0]!=0:#判断是否加车在这个路线上
            for car_in_road in caing_start2end['id'].values.tolist():
                if current[(current['from'] == start_id) & (current['to'] == end_id)].shape[0] <= int(
                            0.8 * capacity):  # 道路容量的80%
                    enough = False  #
                    roading = current[(current['from'] == start_id) & (current['to'] == end_id) & (current['run_channel'] == k + 1)]
                    if roading.empty:
                        S = road_length
                    else:
                        roading = roading.sort_values(["weizhi"], ascending=True)  # 按照位置深序
                        S = roading["weizhi"].iloc[0] - 1  # 最后一辆车的位置                #                            print(S)
                    car_speed = caing_start2end[caing_start2end['id'] == car_in_road]['speed'].values.tolist()[
                        0]  ###第一辆车的速度
                    V1 = int(min(int(car_speed), int(road_speed)))  # 最大行驶速度
                    ## 第一辆车可不可以放
                    if S > 0:  # 能放
                        next_road = Z_luxian[car_in_road]['path_road'][1]  # 下一条出发路线
                        run_channel = 1 + k  #
                        S_ = min(V1, S)  # 当前位置
                        #                            print(S_)
                        state = 0
                        row = {'carid': car_in_road, 'run_road': road_id, 'from': start_id, 'to': end_id,
                               'run_channel': run_channel, 'weizhi': S_, 'state': state,
                               'next_road': next_road}
                        current = current.append(row, ignore_index=True)  # 运行的集合中加入这个车
                        caing_start2end = caing_start2end[~caing_start2end['id'].str.contains(car_in_road)]  # 带出发的车删除这个车
                        if caing_start2end.shape[0]==0:#车在这条路上放完了
                            In_road =current[(current['from'] == start_id) & (current['to'] == end_id) & (current['run_channel'] == k + 1)]
                            current = update_road(In_road, current, k + 1, road, car)
                        continue
                    else:  # 这条道不能放
                        In_road=current[(current['from'] == start_id) & (current['to'] == end_id) & (current['run_channel'] == k + 1)]
                        current=update_road(In_road, current, k+1, road, car)
                        break
                else:#足够了
                    enough=True
                    roading = current[(current['from'] == start_id) & (current['to'] == end_id) & (current['run_channel'] == k + 1)]
                    current = update_road( roading, current, k + 1, road, car)
                    index = caing_start2end.index
                    car['planTime'].loc[index] = (car.loc[index]['planTime'].astype(int) + 1).astype(str)
                    break
            if enough:#足够的情况，对剩下其他道进行更新
                for k in range(k+1,road_channel):
                    roading = current[(current['from'] == start_id) & (current['to'] == end_id) & (current['run_channel'] == k + 1)]
                    if roading.shape[0] != 0:
                        current = update_road(roading, current, k + 1, road, car)
                break

        else:####不加车就直接更新
            roading = current[(current['from'] == start_id) & (current['to'] == end_id) & (current['run_channel'] == k + 1)]
            if roading.shape[0]!=0:
                current = update_road(roading , current, k + 1, road, car)
    return current,car