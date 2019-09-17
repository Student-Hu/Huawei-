# -*- coding: utf-8 -*-
"""
Created on Thu Mar 21 21:06:57 2019

@author: Administrator
"""

def Floyd_Path(node,node_map,path_map,from_node,to_node):   
    node_length = len(node_map)    
    for k in range(node_length):
        for i in range(node_length):
            for j in range(node_length):
                tmp = node_map[i][k] + node_map[k][j]
                if node_map[i][j] > tmp:
                    node_map[i][j] = tmp
                    path_map[i][j] = path_map[i][k]
    node_list = []  
    temp_node = from_node
    obj_node = to_node 
    node_list.append(node[temp_node])
    while True:
        node_list.append(node[path_map[temp_node][obj_node]])
        temp_node = path_map[temp_node][obj_node]
        if temp_node == obj_node:
            break;
    
    return node_list                   
                        
#        print ('_init_Floyd is end')


from pylab import *
import numpy as np
INFINITY = 65535   
                     #代表无穷大
D =np.array([[0,10,INFINITY,INFINITY,INFINITY,11,INFINITY,INFINITY,INFINITY],#邻接矩阵
        [10,0,18,INFINITY,INFINITY,INFINITY,16,INFINITY,12],
        [INFINITY,18,0,22,INFINITY,INFINITY,INFINITY,INFINITY,8],
        [INFINITY,INFINITY,22,0,20,INFINITY,INFINITY,16,21],
        [INFINITY,INFINITY,INFINITY,20,0,26,INFINITY,7,INFINITY],
        [11,INFINITY,INFINITY,INFINITY,26,0,17,INFINITY,INFINITY],
        [INFINITY,16,INFINITY,24,INFINITY,17,0,19,INFINITY],
        [INFINITY,INFINITY,INFINITY,16,7,INFINITY,19,0,INFINITY],
        [INFINITY,12,8,21,INFINITY,INFINITY,INFINITY,INFINITY,0]])
lengthD = len(D)                    #邻接矩阵大小
p = list(range(lengthD))
P = []
for i in range(lengthD):
    P.append(p)
P = np.array(P)

for i in range(lengthD):
    for j in range(lengthD):
        for k in range(lengthD):
            if(D[i,j] > D[i,k]+D[j,k]):         #两个顶点直接较小的间接路径替换较大的直接路径
                P[i,j] = P[j,k]                 #记录新路径的前驱
print(P)
print(D)
