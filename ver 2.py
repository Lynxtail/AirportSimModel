# Имеем сеть МО, состоящую из двух систем: 
# M/M/1 (взлётка) 
# и M/M/k (сервисы)

from math import log
from random import random
import numpy as np

# описание требования
class Demand:
    def __init__(self, born, begin_service_runway, end_service_runway, begin_service_parking, end_service_parking, death):
        # момент генерации
        self.born_time = born
        # момент поступления на взлётку
        self.begin_service_runway = begin_service_runway
        # момент окончания обслуживания на взлётке
        self.end_service_runway = end_service_runway
        # момент поступления на стоянку
        self.begin_service_parking = begin_service_parking
        # момент выхода со стоянки
        self.end_service_parking = end_service_parking
        # момент выхода из сети 
        self.death_time = death

    def getinfo(self):
        print(f'Время поступления в СеМО: {self.born_time}')
        print(f'Время поступления на взлётку: {self.begin_service_runway}')
        print(f'Время окончания обслуживания на взлётке: {self.end_service_runway}')
        print(f'Время поступления на стоянку: {self.begin_service_parking}')
        print(f'Время выхода со стоянки: {self.end_service_parking}')
        print(f'Время выхода из СеМО: {self.death_time}')


# ввод параметров
t_modeling = 10000 # время моделирования
k = 3 # число приборов во второй системе
lambda_0 = 10 # интенсивность входящего в сеть поток
mu = [2, [3]*k] # интенсивности обслуживания в системах

# инициализация моментов активации процессов и вспомогательных величин
t_act_source = 0 # момент генерации требования
t_act_device_runway = 0 # момент начала обслуживания на взлётке
t_act_device_parking = [0]*k # моменты начала обслуживания приборами на стоянке
demands = [] # коллекция с прошедшими через сеть требованиями
# cnt_getting_demands = 0 # число поступивших требований
N = [0, 0] # число требований в системах
n = [] # число требований в сети в разные моменты времени

# начальные условия
t_now = 0 # текущее время
device_runway_free = True # индикатор занятости прибора на взлётке
device_parking_free = [True]*k # индикаторы занятости приборов на стоянке

# неопознанное
t_born = [0] * k + [0] # моменты поступления требований
t_service1 = [0, 0] # поступил / обслужился
t_service2 = [0, 0]

# начальные условия
t_act_source = 0
t_act_device1 = t_modeling + 0.000001
t_act_device2 = t_modeling + 0.000001

# процесс симуляция
while t_now < t_modeling:
    indicator = False # индикатор активности какого-либо процесса
    # генерация требования
    if (t_act_source == t_now):
        print(f"Момент формирования требования: {t_now}")
        indicator = True
        N += 1
        if t_born[0] == 0:
            t_born[0] = t_now
        elif t_born[1] == 0:
            t_born[1] = t_now
        else:
            t_born[2] = t_now
        # print(t_born)
        t_act_source = t_now - log(random()) / lambda_0
    
    # начало обслуживания требования прибором взлётки
    if (device_runway_free and N > 0):
        print(f"Момент начала обслуживания прибором взлётки: {t_now}")
        indicator = True
        device_runway_free = False
        t_act_device_runway = t_now - log(random()) / mu[0]
        # t_act_source = t_now - log(rnd) / lambda_
        # N += 1 #???
        t_service1[0] = t_now

    # начало обслуживания требования прибором 1 стоянки
    elif (device_parking_free[0] and N > 1):
        print(f"Момент начала обслуживания прибором 1 стоянки: {t_now}")
        indicator = True
        device_parking_free[0] = False
        t_act_device_parking[0] = t_now - log(random()) / mu[1][0]
        # t_act_source = t_now - log(rnd) / lambda_
        # N += 1 #???
        # t_service2[0] = t_now

    # начало обслуживания требования прибором 2 стоянки
    elif (device_parking_free[1] and N > 1):
        print(f"Момент начала обслуживания прибором 2 стоянки: {t_now}")
        indicator = True
        device_parking_free[1] = False
        t_act_device_parking[1] = t_now - log(random()) / mu[1][1]
        # t_act_source = t_now - log(rnd) / lambda_
        # N += 1 #???
        # t_service2[0] = t_now


    # начало обслуживания требования прибором 3 стоянки
    elif (device_parking_free[2] and N > 1):
        print(f"Момент начала обслуживания прибором 3 стоянки: {t_now}")
        indicator = True
        device_parking_free[2] = False
        t_act_device_parking[2] = t_now - log(random()) / mu[1][2]
        # t_act_source = t_now - log(rnd) / lambda_
        # N += 1 #???
        # t_service2[0] = t_now
        
    # отказ
    # elif N > 2:
    #     N -= 1
    #     t_born[2] = 0
    #     cnt_refuse += 1
        
    # завершение обслуживания требования прибором взлётки
    if (t_act_device_runway == t_now):
        print(f"Момент завершения обслуживания прибором взлётки: {t_now}")
        # t_service1[1] = t_now
        indicator = True
        device_runway_free = True
        t_act_device_runway = t_modeling + 0.0000001
        print(f"Момент поступления: {t_service1[0]}\nМомент выхода из СМО: {t_now}")
        N -= 1
        # запись требования в формате (в каком-то)***
        demands.append(Demand(t_born[0], t_service1[0], t_service1[1]))
        t_born[0] = 0

    # завершение обслуживания требования прибором 1 стоянки
    if (t_act_device_parking[0] == t_now):
        print(f"Момент завершения обслуживания 1 прибором стоянки: {t_now}")
        # t_service2[1] = t_now
        indicator = True
        device_parking_free[0] = True
        t_act_device_parking[0] = t_modeling + 0.0000001
        print(f"Момент поступления: {t_service2[0]}\nМомент выхода из СМО: {t_now}")
        N -= 1
        demands.append(Demand(t_born[1], t_service2[0], t_service2[1]))
        t_born[1] = 0

    # завершение обслуживания требования прибором 2 стоянки
    if (t_act_device_parking[1] == t_now):
        print(f"Момент завершения обслуживания 2 прибором стоянки: {t_now}")
        # t_service2[1] = t_now
        indicator = True
        device_parking_free[1] = True
        t_act_device_parking[1] = t_modeling + 0.0000001
        print(f"Момент поступления: {t_service2[0]}\nМомент выхода из СМО: {t_now}")
        N -= 1
        demands.append(Demand(t_born[1], t_service2[0], t_service2[1]))
        t_born[1] = 0

    # завершение обслуживания требования прибором 3 стоянки
    if (t_act_device_parking[2] == t_now):
        print(f"Момент завершения обслуживания 3 прибором стоянки: {t_now}")
        # t_service2[1] = t_now
        indicator = True
        device_parking_free[2] = True
        t_act_device_parking[2] = t_modeling + 0.0000001
        print(f"Момент поступления: {t_service2[0]}\nМомент выхода из СМО: {t_now}")
        N -= 1
        demands.append(Demand(t_born[1], t_service2[0], t_service2[1]))
        t_born[1] = 0
    
    # переход к следующему моменту
    if not indicator:
        n.append(N)
        # print(N)
        t_now = min(t_act_device_runway, min(t_act_device_parking), t_act_source)


# блок анализа данных
# u = []
# for item in demands:
#     u.append(item.death_time - item.born_time)
#     # print(u[-1])
# n_ = np.mean(n)
# u_ = np.mean(u)
# p_ref = cnt_refuse / cnt_getting_demands
# print(f'Число обслуженных требований: {len(demands)}')
# print(f'М.о. длительности пребывания требований в системе u_ = {u_}')
# print(f'М.о. числа требований в системе n_ = {n_}')
# print(f'Вероятность отказа = {p_ref}')

for item in demands:
    print(f'Требование {demands.index(item)}')
    item.getinfo()