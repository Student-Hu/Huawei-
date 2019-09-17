import logging
import sys
import pandas as pd
import numpy as np
import time
# from update import update_road
# from update import update_road_first_end
# from diaoyong import Addcar
road_path='./1-map-training-2/road.txt'
cross_path='./1-map-training-2/cross.txt'
car_path='./1-map-training-2/car.txt'
answer_path=r'C:\Users\Administrator\Desktop\新建文件夹\huawei2019-with-visualization-master\huawei2019-with-visualization-master\1-map-training-1\answer.txt'


time_start = time.time()
def Dijkstra(hh, start, end):
    dist = {}
    previous = {}
    for v in hh.keys():
        #都设置为无穷大
        dist[v] = float('inf')
        previous[v] = 'none'
    dist[start] = 0
    u = str(start)

    while u != end:
        #获得最小值对应的键
        u = min(dist, key=dist.get)
        distu = dist[u]
        # print(distu)
        del dist[u]
#            print(hh[u])#hh[u]
        for u ,v,weight,id in hh[u]:
            if v in dist:
                alt = distu + int(weight)
                if alt < dist[v]:
                    dist[v] = alt
                    previous[v] = {u:id}

    path = [end]
    path_road=[]
    last = end
    while last != start:
        nxt =min(previous[last], key=previous[last].get)
#        nxt = list(previous[last].keys())
        road=previous[last][nxt]
        path_road.append(road)
        path.append(nxt)
        last = nxt
    return path,path_road
Direction={"roadId1-roadId2":2,"roadId1-roadId4":1,"roadId2-roadId1":1,"roadId2-roadId3":2,
               "roadId3-roadId2":1,"roadId3-roadId4":2,"roadId4-roadId3":1,"roadId4-roadId1":2,
               "roadId2-roadId4":3,"roadId4-roadId2":3,"roadId1-roadId3":3,"roadId3-roadId1":3,
               "roadId1-roadId1":3,"roadId2-roadId2":3,"roadId3-roadId3":3,"roadId4-roadId4":3}

def dicrion(to,next_road,road):
    id=cross[cross['id']== to]
    directionid2=id.columns[np.where(id==next_road)[1]].tolist()[0]
    directionid1=id.columns[np.where(id==road)[1]].tolist()[0] #找到对应的列名
    direct=Direction[str(directionid1+'-'+directionid2)]#行驶方向
    return direct

def Road_Dir(second_road,run_road,cross_id):
    second_road = second_road.sort_values(["run_channel"], ascending=True)  # 按照位置sheng序
    second_road = second_road.sort_values(["weizhi"], ascending=False)
    second_road_id = second_road['next_road'].iloc[0]
    nxt = cross_id
    roading = str(run_road)
    next_road = second_road_id
    second_dir = dicrion(nxt, next_road, roading)
    return second_road_id,second_dir


def Conflict(next_going_road_id,direction,second_road_idAnd_dir):
    conflict=False
    for second_road_id_, second_dir_ in second_road_idAnd_dir:
        if (second_road_id_ == next_going_road_id) & (
                second_dir_ > direction):  # 如果第二条路的第一辆车的方向小于我的方向，或者你不和我同路，都不冲突
            conflict = True
            break
        else:
            continue
    return conflict

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

road1=[]
with open(road_path,'r') as f:
	for line in f:
		road1.append(list(line.strip('\n').replace(' ','').replace('(','').replace(')','').replace('#','').split(',')))
road=pd.DataFrame((road1)[1:])
road.columns=road1[0]
for i in range(road.shape[0]):
    if road.iloc[i]['isDuplex']=='1':
        new_road=road.iloc[i].rename({'to':'from','from':'to'})

        road=road.append(new_road,ignore_index=True)

cross1=[]
with open(cross_path,'r') as f:
	for line in f:
		cross1.append(list(line.strip('\n').replace(' ','').replace('(','').replace(')','').replace('#','').split(',')))
cross=pd.DataFrame(cross1[1:])
cross.columns=['id', 'roadId1', 'roadId2', 'roadId3', 'roadId4']


for i in range(road.shape[0]):
    road['isDuplex'][i]=int((int(road['length'][i])+int(road['speed'][i])-1)/int(road['speed'][i]))

hh={}
node=cross['id'].values.tolist()
for  i in node:
     list_key=[]
     TO=road[road['from']==i][['to','isDuplex','id']].values.tolist()
     for to ,length ,id in TO:
         list_key.append((i,to,length,id))
     hh.update({i:list_key})

car1=[]
car_f = open(car_path, 'r').read().split('\n')[1:]
for line in car_f:
     car1.append(list(line.strip('\n').replace(' ','').replace('(','').replace(')','').replace('#','').split(',')))
car=pd.DataFrame(car1[:])
car.columns=['id','from','to','speed','planTime']
car['path1to']=None
Z_luxian={}
car=car.sort_values(['id'],ascending=True)#按照车id升序
car=car.sort_values(["speed"],ascending=False)
k=1000/(int(min(car['speed']))-int(max(car['speed'])))
b=-1000*int(max(car['speed']))/(int(min(car['speed']))-int(max(car['speed'])))
np.random.seed(10)
for j in range(car.shape[0]):
   from_node = car.iloc[j]['from']
   to_node = car.iloc[j]['to']
   path,path_road =Dijkstra(hh, from_node, to_node)#通过的路口
   path.reverse()
   path_road.reverse()
   car.iloc[j]['path1to']=path[1]
   print(path)
   if j<200:
       palntime1=int(int(car.iloc[j]['speed'])*k+b+np.random.randint(1))
       if int(car.iloc[j]['planTime'])<palntime1:
           car.iloc[j]['planTime']=str(palntime1).split('.0')[0]
   else:
       plantime2=int(int(car.iloc[j]['speed'])*k+b+np.random.randint(1,100))
       if int(car.iloc[j]['planTime'])<plantime2:
           car.iloc[j]['planTime']=str(plantime2).split('.0')[0]
   Z_luxian.update({car.iloc[j]['id']:{'path':path,'path_road':path_road}})

time_end = time.time()
print('time cost', time_end - time_start, 's')


T = 0
current = pd.DataFrame(columns=['carid', 'run_road', 'from', 'to',
                                'run_channel', 'weizhi', 'state',
                              'next_road'])  ##装车的集合
sisuo=False
conflict=False
while True:

    T = T + 1
    time_start = time.time()
    print('Time'+str(T))
    #################出库+行驶模型#########################
    caring = car[(car['planTime'] == str(T))]  # ['id'].index.tolist() #出发时间为T的车
    caring = caring.sort_values(["id"], ascending=True)  # 升序
    if caring.empty:
        print('没有车辆出发'+T)
    #################单一道路模型#########################
    for index,row in road.iterrows():  # 以起始点判断那一条路
        start_id = row['from']
        end_id = row['to']
        caing_start2end = caring[(caring['from'] == start_id) & (caring['path1to'] == end_id)]  ##这一时刻要在这个form-to出发的所有车
        if  caing_start2end.shape[0]!=0:
            caing_start2end = caing_start2end.sort_values(["id"], ascending=True)  # 按照车的ID升序
            current,car=Addcar(Z_luxian,current,road,index,caing_start2end,car,start_id,end_id)
        roading = current[(current['from'] == start_id )&(current['to'] == end_id )]  # 对每个单一道路进行操作
        if roading.empty:
             continue
        else:
             roading = roading.sort_values(["run_channel"], ascending=True)  # 按车道升序
             roading = roading.sort_values(["weizhi"], ascending=False)  # 按照位置降序
             for k in range(int(road.loc[index]['channel'])):
                 current= update_road(roading, current, k + 1, road, car)

###########################路口模型#########################
    if current.empty:  # 判断所有车是否运行完全
        break
    time_end = time.time()
    print('time cost', time_end - time_start, 's')
    last_state_id = current[current['state'] == 1]['carid'].values.tolist()  # 上一个状态的等待车的数量
    while current[current['state'] == 1].shape[0] != 0:  # 当前时刻所有车辆不是终止状态的话
        for cross_index in cross['id'].index:  # 对每个路口进行循环（按照路口ID升序）
            roading_cross = current[(current['to'] == cross['id'][cross_index])]  # 目标为同一个路口，且为等待状态的车
            roading_cross=roading_cross[roading_cross['state']==1]
            if roading_cross.empty:
                continue

            #####找到此路口的链接的各个路道ID ￥#############
            print('分析的路口'+cross['id'][cross_index])#
            # road1 = cross['roadId1'][cross_index]
            # road2 = cross['roadId1'][cross_index]
            # road3 = cross['roadId3'][cross_index]
            # road4 = cross['roadId4'][cross_index]
            min_id = [int(cross['roadId1'][cross_index]), int(cross['roadId2'][cross_index]),
                      int(cross['roadId3'][cross_index]), int(cross['roadId4'][cross_index])]
            min_id.sort()  ###################对4个路口进行排序#############
            while min_id[0] == -1:
                min_id.pop(0)
            numble_road = len(min_id)  #########确定交叉路口道路的个数
            #####交叉路口的情况##########################
            second_road_idAnd_dir = []
            for j in range(numble_road):
                second_road = roading_cross[(roading_cross['run_road'] == str(min_id[j]))]
                if second_road.shape[0] != 0:
                    second_road_id_, second_dir_ = Road_Dir(second_road, min_id[j], cross['id'][cross_index])
                else:
                    second_road_id_, second_dir_=-1,0
                second_road_idAnd_dir.append([second_road_id_, second_dir_])

            for i in range(numble_road):
                conflict = False  # 初始该道路不冲突
                #            for index in roading_cross[roading_cross['run_road']==str(min_id[i])].index.tolist():##对于In_road1分析
                roading_cross = current[(current['to'] == cross['id'][cross_index])]  # 目标为同一个路口，且为等待状态的车
                roading_cross = roading_cross[roading_cross['state'] == 1]  # 判断还有等待的车吗
                if roading_cross.shape[0] == 0:
                    break
                cishu=1

                while 1:
                    In_road = current[(current['to'] == cross['id'][cross_index]) & (
                    current['run_road'] == str(min_id[i]))]  # 目标为同一个路口，且为等待状态的车
                    In_road = In_road[In_road['state'] == 1]
                    In_road=In_road.sort_values(["run_channel"], ascending=True)  # 按照位置sheng序
                    In_road=In_road.sort_values(["weizhi"],ascending=False)  # 按照位置降序
                    if In_road.empty:
                        break
                    if cishu>1:
                        next_going_road_id = In_road['next_road'].iloc[0]  # 第一个车的下一条路的ID
                        # 当前车的运行方向
                        nxt = cross['id'][cross_index]
                        roading = str(min_id[i])
                        next_road = next_going_road_id
                        direction = dicrion(nxt, next_road, roading)
                        second_road_idAnd_dir[i]=[next_going_road_id, direction ]
                    next_going_road_id, direction=second_road_idAnd_dir[i]
                    conflict=Conflict(next_going_road_id,direction,second_road_idAnd_dir)
                    if conflict:
                        break
                    cishu += 1

#                        In_road = roading_cross[roading_cross['run_road'] == str(min_id[i])]  # 当前道路等待的车
                    index = In_road.index.tolist()[0]

                    # 判断该车是不是到达终点的车
                    if In_road['to'][index] == Z_luxian[current['carid'][index]]['path'][-1]:
                        current=current.drop(index)
                        In_road=In_road.drop(index)
                         #当前道路等待的车In_road
                        if In_road.shape[0]!=0:
                           current=update_road(In_road ,current,k,road,car)

                    #            if roading_cross[roading_cross['run_road']==str(min_id[i])]['state'][index]==1:#判断这个路上的这个车是否仍然是等待状态
                    # 对面道路第一条道路最后一辆的信息
                    else:#过路口
                        next_going_road_id = In_road['next_road'][index]
                        next_going_road = current[
                        (current['from'] == cross['id'][cross_index])&(current['run_road'] == next_going_road_id)]
                        for k in range(int(road[road['id']==next_going_road_id]['channel'].iloc[0])):  # 判断当前将要驶入的道路总共有多少车道
                            road_of_channel = next_going_road[next_going_road['run_channel'] == k + 1]
                            road_of_channel=road_of_channel.sort_values(["weizhi"], ascending=True)
                            # 按照位置深序
                            if road_of_channel.empty:
                                next_road_speed =  road[(road['id']== next_going_road_id)]['speed'].values.tolist()[
                                    0]  # 下一条道路限速
                                car_speed = car[car['id'] == In_road['carid'][index]]['speed'].values.tolist()[0]
                                V2 = int(min(int(next_road_speed), int(car_speed)))  # 在next road最大行驶速度
                                S = int(road[(road['id'] == next_going_road_id)]['length'].values.tolist()[
                                    0] ) # 下一条道路长度
                                current['weizhi'][index] = min(V2,S)
                                current['state'][index] = 0  # 终止
                                location_path = Z_luxian[current['carid'][index]]['path_road'].index(
                                    current['run_road'][index])
                                ##进入的下一条道路包括（from，to, 路的id,下一条路id,方向，第几条到）
                                current['run_road'][index] = Z_luxian[current['carid'][index]]['path_road'][
                                    location_path + 1]
                                if len(Z_luxian[current['carid'][index]]['path_road']) > location_path + 2:
                                    current['next_road'][index] = Z_luxian[current['carid'][index]]['path_road'][
                                        location_path + 2]
                                current['from'][index] = Z_luxian[current['carid'][index]]['path'][
                                    location_path + 1]
                                current['to'][index] = Z_luxian[current['carid'][index]]['path'][
                                    location_path + 2]
                                current['run_channel'][index] = k+1
                                break
                            else:
                                state = road_of_channel["state"].iloc[0]  # 最后一辆车的状态
                                S = int(road_of_channel["weizhi"].iloc[0])-1  # 最后一辆车的位置
#                                print(S)
                                next_road_speed = road[(road['id'] == next_going_road_id)]['speed'].values.tolist()[0]  # 下一条道路限速
                                car_speed=car[car['id']==In_road['carid'][index]]['speed'].values.tolist()[0]
                                V2 = int(min(int(next_road_speed), int(car_speed)))  # 在next road最大行驶速度
                                road_length=int(road[road['id']==In_road['run_road'][index]]['length'].values.tolist()[0])#当前道路的长度
                                S1 = road_length - int(In_road['weizhi'][index])  # 离路口的距离
                                S2 = V2 - S1
                                if S == 0:  # 当前车道满了，进入下一条车道
                                    continue
                                if S > 0:  # 当前车道没满
                                    if state == 0:  # 当车为终止状态时

                                        if S2 <= 0:  # 不能通过路口
                                            current['weizhi'][index] = int(road_length)
                                            current['state'][index] = 0  # 终止
                                        else:  # 能进入，相对应的更新
                                            current['weizhi'][index] = min(S, S2)
                                            current['state'][index] = 0  # 终止
                                            location_path = Z_luxian[current['carid'][index]]['path_road'].index(
                                                current['run_road'][index])
                                            ##进入的下一条道路包括（from，to, 路的id,下一条路id,方向，第几条到）
                                            current['run_road'][index] = \
                                            Z_luxian[current['carid'][index]]['path_road'][
                                                location_path + 1]
                                            if len(Z_luxian[current['carid'][index]]['path_road']) > location_path + 2:
                                                current['next_road'][index] = \
                                                Z_luxian[current['carid'][index]]['path_road'][
                                                    location_path + 2]
                                            current['from'][index] = Z_luxian[current['carid'][index]]['path'][
                                                location_path + 1]
                                            current['to'][index] = Z_luxian[current['carid'][index]]['path'][
                                                location_path + 2]
                                            current['run_channel'][index] = k + 1
                                    if state == 1:  # 当前车为等待状态时
                                        if S2 <= 0:  # 不能通过路口
                                            current['weizhi'][index] = int(road_length)
                                            current['state'][index] = 0  # 终止
                                        elif S2 > S:
                                            current['state'][index] = 1  # 等待
                                        elif 0 < S2 <=S:  # 能进入，相对应的更新
                                            current['weizhi'][index] = min(S, S2)
                                            current['state'][index] = 0  # 终止
                                            location_path = Z_luxian[current['carid'][index]]['path_road'].index(
                                                current['run_road'][index])
                                            ##进入的下一条道路包括（from，to, 路的id,下一条路id,方向,第几条到）
                                            current['run_road'][index] = \
                                            Z_luxian[current['carid'][index]]['path_road'][
                                                location_path + 1]
                                            if len(Z_luxian[current['carid'][index]]['path_road']) > location_path + 2:
                                                current['next_road'][index] = \
                                                Z_luxian[current['carid'][index]]['path_road'][
                                                    location_path + 2]
                                            current['from'][index] = Z_luxian[current['carid'][index]]['path'][
                                                location_path + 1]
                                            current['to'][index] = Z_luxian[current['carid'][index]]['path'][
                                                location_path + 2]
                                            current['run_channel'][index] = k+1
                                    break
                        if S == 0:
                            current['state'][index] = 0

                        if current['state'][index] == 1:  # 如果对第一优先级调度后还是等待，跳至下一路口
                            break
                        else:
                            In_road = current[(current['to'] == cross['id'][cross_index])&(current['run_road']==str(min_id[i]))]  # 目标为同一个路口，且为等待状态的车
                            In_road = In_road[In_road['state'] == 1]
                            In_road=In_road.sort_values(["run_channel"], ascending=True)  # 按照channel升序
                            In_road=In_road.sort_values(["weizhi"],ascending=False)  # 按照位置降序
                            k = current['run_channel'][index]
                            if In_road.empty:
                                break
                                ##一旦有一辆等待车辆（记为车A，所在车道记为C）通过路口而成为终止状态，则会该道路R的车道C上所有车辆进行一次调度
                            if current['run_road'][index]==str(min_id[i]):#第一优先级的车不过路口终止
                                current=update_road_first_end( In_road ,index,current,road,car)
                            else:#第一优先级的车过路口终止
                            # 对第一个车调度后要对当前车道调度一下，排除因第一个车等待而等待的车（即非真正等待车）
                                current=update_road(In_road ,current,k,road,car)
        present_state_id = current[current['state'] == 1]['carid'].values.tolist()
        if len(last_state_id) == len(present_state_id):  # 如果上一个循环与这一次循环后等待状态的车的数量没有变化，及锁死
            print('死锁')
            # sisuo = True
            # int(len(present_state_id)//2)
            # delcar=present_state_id[0:int(len(present_state_id)//2)]
            # index=car[car['id'].isin(delcar)].index
            # car['planTime'].loc[index]=(car['planTime'].loc[index].astype(int) + 10).astype(str)
            # break
            continue
        else:
            last_state_id= present_state_id.copy()

    if sisuo:
        # T = 0
        # current = pd.DataFrame(columns=['carid', 'run_road', 'from', 'to',
        #                                 'run_channel', 'weizhi', 'state',
        #                                 'next_road'])  ##装车的集合
        # sisuo = False
        # conflict = False
        continue
jieguo=[]
for j in range(car.shape[0]):
    jieguo=jieguo.append(Z_luxian[car.iloc[j]['id']]['path_road'])
    planTime = car.iloc[j]['planTime']    
    jieguo[j].insert(0, car.iloc[j]['id'])
    jieguo[j].insert(1, planTime)

fw = open(answer_path, 'w')  # 将要输出保存的文件地址
for line in jieguo:  # 读取的文件
    fw.write("(" + str(','.join(line)) + ")")  # 将字符串写入文件中
    # line.rstrip("\n")为去除行尾换行符
    fw.write("\n")  # 换行
fw.close()

time_end = time.time()
print('time cost', time_end - time_start, 's')