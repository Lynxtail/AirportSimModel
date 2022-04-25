from math import sqrt
import numpy as np
from random import random

# структура модели
# начальное состояние модели

# текущее модельное время
cur_time = 0

# время моделирования
T_max = 10000

# интенсивность входящего потока требований из источника
lmbd_0 = int(input('lambda_0 = '))

# Среднее квадратическое отклонение ср. потока из источника
std_0 = float(input('Среднее квадратическое отклонение ср. потока из источника = '))

# интенсивность обслуживания потока требований
mu_0 = int(input('mu_0 = '))

# Среднее квадратическое отклонение от ср. обсл. в СМО
std_in = float(input('Среднее квадратическое отклонение от ср. обсл. в СМО = '))

# TEST!!!
# lmbd_0 = 1
# std_0 = 0
# std_in = 0
# mu_0 = 2


# вспомогательная величина, равная целой части корня T_max
l = int(sqrt(T_max))

# моменты постановки требования в очередь от 1 до 1000
MpQ = np.zeros(l)

# моменты постановки и выбора требования в очереди (системы?) 
MpQS = 0
MgQS = 0

# м.о. числа требований в СМО от 0 до 1000
DS012 = np.zeros(l+1)

# м.о. числа требований в очереди от 0 до 1000
DQ012 = np.zeros(l+1)

# индикатор занятости прибора
busy_flag = False

# число требований в очереди
NDQ = 0

# число требований в системе
NDS = 0

# момент активизации СМО
sys_act_moment = T_max + 1e+5

# момент активизации источника
source_act_moment = cur_time

# момент смены состояния
change_state_Q = cur_time
change_state_S = cur_time

# число обслужанных требований
cnt_serviced_requests = 0

# выбор распределений длительностей для потоков требований
distr_types = ('экспоненциальное', 'нормальное', 'постоянная величина')
source_distr = distr_types[0]
service_distr = distr_types[0]

f = open('output.txt', 'w')

stat_results = {'MpQS': [],
                'MgQS': [],
                'Time': []}

# таблица активизации процессов

# момент прилёта p1 t1   
# момент ок обс p2 t2
# момент вылета p0 t3

# процесс моделирования
while cur_time <= T_max:
    if source_act_moment == cur_time: 
        # генерирование требования
        DS012[NDS] += cur_time - change_state_S
        DQ012[NDQ] += cur_time - change_state_Q
        change_state_Q = cur_time
        change_state_S = cur_time
        if NDQ >= l or NDS >= l:
            print(f'break at cur time {cur_time}')
            break
        else:
            NDQ += 1
            NDS += 1
        MpQ[NDQ] = cur_time
        if source_distr == distr_types[0]:
            source_act_moment = cur_time - np.log(random()) / lmbd_0
        elif source_distr == distr_types[1]:
            tmp = sum([tmp + random() for _ in range(12)])
            tmp = lmbd_0 + std_0*(tmp - 6)
            if tmp < 0: tmp = 0.001
            source_act_moment = cur_time + tmp
        elif source_distr == distr_types[2]:
            source_act_moment = cur_time + lmbd_0
    elif NDQ > 0 and not busy_flag:
        # начинается обслуживание требования
        busy_flag = True
        if service_distr == distr_types[0]:
            sys_act_moment = cur_time - np.log(random()) / mu_0
        elif service_distr == distr_types[1]:
            tmp = sum([tmp + random() for _ in range(12)])
            tmp = mu_0 + std_in*(tmp - 6)
            if tmp < 0: tmp = 0.001
            sys_act_moment = cur_time + tmp
        elif service_distr == distr_types[2]:
            sys_act_moment = cur_time + mu_0
        MpQS = MpQ[1]
        MgQS = cur_time
        for i in range(1, NDQ): MpQ[i] = MpQ[i + 1]
        MpQ[NDQ] = 0
        DQ012[NDQ] += cur_time - change_state_Q
        change_state_Q = cur_time
        NDQ -= 1
    elif busy_flag and sys_act_moment == cur_time:
        # завершается обслуживание требования
        busy_flag = False
        cnt_serviced_requests += 1
        sys_act_moment = T_max + 1e+5
#         print(f'Момент постановки требования в очередь = {MpQS}\n\
# Момент выбора требования из очереди = {MgQS}\n\
# Текущее время = {cur_time}')
        # stat_results['MpQS'].append(MpQS)
        # stat_results['MgQS'].append(MgQS)
        # stat_results['Time'].append(cur_time)

        f.write(MpQS, MgQS, cur_time, sep='\t')

        DS012[NDS] += cur_time - change_state_S
        change_state_S = cur_time
        NDS -= 1
    # время увеличивается
    else:
        cur_time = min(sys_act_moment, source_act_moment)
    
f.close()

# синхронизация и управление процессами
# сбор и обработка данных
# запись в отдельный файл
f = open('output.txt', 'r')

s1 = 0
s2 = 0
# for i in range(cnt_serviced_requests):
#     s1 += stat_results['Time'][i] - stat_results['MpQS'][i]
#     s2 += stat_results['MgQS'][i] - stat_results['MpQS'][i]
# s1 /= cnt_serviced_requests
# s2 /= cnt_serviced_requests
cnt_lines = 0
for line in f:
    s1 += line[2] - line[0]
    s2 += line[1] - line[0]
    cnt_lines += 1
s1 /= cnt_lines
s2 /= cnt_lines

sk1 = 0
sk2 = 0
# for i in range(cnt_serviced_requests):
#     sk1 += (s1 - stat_results['Time'][i] + stat_results['MpQS'][i])**2
#     sk2 += (s2 - stat_results['MgQS'][i] - stat_results['MpQS'][i])**2
# sk1 = sqrt(sk1 / (cnt_serviced_requests - 1))
# sk2 = sqrt(sk2 / (cnt_serviced_requests - 1))

for line in f:
    sk1 += (s1 - line[2] - line[0])**2
    sk2 += (s2 - line[1] - line[0])**2
sk1 /= sqrt(sk1 / (cnt_lines - 1))
sk2 /= sqrt(sk2 / (cnt_lines - 1))**2

f.close()

print(f'М.о. длительности пребывания требования в СМО: {s1}\tСреднее квадратическое отклонение: {sk1}')
print(f'М.о. длительности пребывания требования в очереди: {s2}\tСреднее квадратическое отклонение: {sk2}')

a = 0
a = sum([a + i*DS012[i-1] / T_max for i in range(1, l+1)])

b = 0
b = sum([a + i*DQ012[i-1] / T_max for i in range(1, l+1)])

print(f'М.о. числа требований в СМО: {a}')
print(f'М.о. числа требований в очереди: {b}')
