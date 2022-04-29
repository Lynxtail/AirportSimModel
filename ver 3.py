# Имеем сеть МО, состоящую из двух систем: 
# M/M/1 (взлётка) 
# и M/M/k (сервисы тех обслуживания)
# требование поступает на взлётку, обслуживается,
# после чего с вероятностью p_out = 0.3 покидает систему.
# Иначе оно отправляется на тех обслуживание, обрабатывается.
# Затем вновь отправляется на взлётку.
# (для моделирования используем библиотеку simpy)

from math import log
from random import random
import sys
import numpy as np
import simpy
from Demand import Demand
from Airport import Airport

# функция поведения самолёта на взлётке
def go_to_runway(env:simpy.Environment, demand:Demand, system:Airport):
    # требование пришло в систему
    demand.t_in_1 = env.now

    with system.runway.request() as request:
        yield request
        demand.t_serve_1 = env.now
        yield env.process(system.service_runway(demand))

    demand.t_out_1 = env.now

    # рассчёт м.о.
    demand.calc_times()

    if random() <= system.p_out:
        print(f'...и самолёт {demand.num} успешно улетел!')
        times = open('times_out.txt', 'a')
        times.write(demand.get_info())
        times.close()
    else:
        # yield env.timeout(env.now - log(random()) / 
        #   (system.mu_runway * (1 - system.p_out)))
        system.cnt_demands[1].append(system.server.count + 1)
        print(f'Самолёт {demand.num} поступил на обслуживание в {env.now}')
        print(f'В момент {env.now} было {system.runway.count} + {system.server.count}')
        env.process(go_to_server(env, demand, system))

# функция поведения самолёта на стоянке
def go_to_server(env:simpy.Environment, demand:Demand, system:Airport):
    # требование пришло в систему
    demand.t_in_2 = env.now

    with system.server.request() as request:
        yield request
        demand.t_serve_2 = env.now
        yield env.process(system.service_server(demand))

    demand.t_out_2 = env.now

    # рассчёт м.о.
    demand.calc_times()

# функция запуска работы модели
def run_system(env:simpy.Environment, system:Airport):
    cnt = 1
    demand = Demand(cnt, env.now)
    
    print(f'Самолёт {demand.num} поступил на взлётку в {env.now}')
    env.process(go_to_runway(env, demand, system))
    
    print(f'В момент {env.now} было {system.runway.count} + {system.server.count}')
    system.cnt_demands[0].append(system.runway.count + 1)
    
    while True:
        # yield env.timeout(rd.expovariate(lambda_))
        yield env.timeout(env.now - log(random()) / lambda_0)
        system.cnt_demands[0].append(system.runway.count + 1) 
        cnt += 1
        demand = Demand(cnt, env.now)
        print(f'Самолёт {demand.num} поступил на взлётку в {env.now}')
        print(f'В момент {env.now} было {system.runway.count} + {system.server.count}')  
        env.process(go_to_runway(env, demand, system))  


# Начальные данные
cnt_runways = 1 # число взлёток
cnt_servers = 3 # число мест для тех обслуживания
lambda_0 = 1 
mu_runway = 2
mu_server = 3

# Запуск моделирования
times = open('times_out.txt', 'w')
times.close()
env = simpy.Environment()
system = Airport(env, cnt_runways, cnt_servers, mu_runway, mu_server)
env.process(run_system(env, system))
env.run(until=10)

# Результаты
times = open('times_out.txt', 'r')
v = [[], []]
w = [[], []]
u = [[], []]
for line in times:
    _, v_1_, w_1_, u_1_, v_2_, w_2_, u_2_ = [float(item) for item in line.split(' ')]
    v[0].append(v_1_)
    w[0].append(w_1_)
    u[0].append(u_1_)
    v[1].append(v_2_)
    w[1].append(w_2_)
    u[1].append(u_2_)
times.close()
v = [[np.mean(v[0])], [np.mean(v[1])]]
w = [[np.mean(w[0])], [np.mean(w[1])]]
u = [[np.mean(u[0])], [np.mean(u[1])]]

print(f'\nСреднее время обслуживания на взлётке: {v[0]}')
print(f'Среднее время обслуживания на стоянке: {v[1]}')
print(f'\nСреднее время ожидания на взлётке: {w[0]}')
print(f'Среднее время ожидания на стоянке: {w[1]}')
print(f'\nСреднее время пребывания на взлётке: {u[0]}')
print(f'Среднее время пребывания на стоянке: {u[1]}')

states = [[], []]
p = [[], []]
for item in system.cnt_demands[0]:
    if item in states[0]:
        continue
    else:
        states[0].append(item)
        p[0].append(system.cnt_demands[0].count(item) / len(system.cnt_demands[0]))
for item in system.cnt_demands[1]:
    if item in states[1]:
        continue
    else:
        states[1].append(item)
        p[1].append(system.cnt_demands[1].count(item) / len(system.cnt_demands[1]))
for item in p:
    if len(item) == 0:
        item.append(1)
        break
print(f'\nСтационарное распределение:\n{p}')

n = [[sum([item * p[0][item] for item in range(len(p[0]))])], [sum([item * p[1][item] for item in range(len(p[1]))])]]
print(f'\nСреднее число требований в сети:\n{n}')