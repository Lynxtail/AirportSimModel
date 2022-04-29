# Имеем сеть МО, состоящую из двух систем: 
# M/M/1 (взлётка) 
# и M/M/k (сервисы тех обслуживания)
# требование поступает на взлётку, обслуживается,
# после чего с вероятностью p_out = 0.3 покидает систему.
# Иначе оно отправляется на тех обслуживание, обрабатывается.
# Затем вновь отправляется на взлётку.
# (для моделирования используем библиотеку simpy)

from math import log
from random import random, seed
import numpy as np
import simpy

class Demand:
    def __init__(self, num, t_born=0, t_in_1=0, t_serve_1=0, t_out_1=0, 
    t_in_2=0, t_serve_2=0, t_out_2=0):
        self.num = num
        self.t_born = t_born
        self.t_in_1 = t_in_1 
        self.t_serve_1 = t_serve_1
        self.t_out_1= t_out_1 
        self.t_in_2 = t_in_2 
        self.t_serve_2 = t_serve_2
        self.t_out_2= t_out_2 
        self.v_1 = self.t_out_1 - self.t_serve_1
        self.w_1 = self.t_serve_1 - self.t_in_1
        self.u_1 = self.t_out_1 - self.t_in_1
        self.v_2 = self.t_out_2 - self.t_serve_2
        self.w_2 = self.t_serve_2 - self.t_in_2
        self.u_2 = self.t_out_2 - self.t_in_2

    def calc_times(self):
        self.v_1 += self.t_out_1 - self.t_serve_1
        self.w_1 += self.t_serve_1 - self.t_in_1
        self.u_1 += self.t_out_1 - self.t_in_1
        self.v_2 += self.t_out_2 - self.t_serve_2
        self.w_2 += self.t_serve_2 - self.t_in_2
        self.u_2 += self.t_out_2 - self.t_in_2
    
    def get_info(self):
        return f'{self.num} {self.v_1} {self.w_1} {self.u_1} {self.v_2} {self.w_2} {self.u_2}\n'

# класс, описывающий сеть
class Airport:
    def __init__(self, env, cnt_runways, cnt_servers, mu_runway, 
    mu_server, p_out=3):
        self.env = env
        self.runway = simpy.Resource(env, cnt_runways)
        self.server = simpy.Resource(env, cnt_servers)
        self.mu_runway = mu_runway
        self.mu_server = mu_server
        self.p_out = p_out

    # обслуживание на взлётке
    def service_runway(self, demand:Demand):
        # yield self.env.timeout(rd.expovariate(self.mu))
        yield self.env.timeout(env.now - log(random()) / 
            self.mu_runway)
        global cnt_demands
        cnt_demands[0].append(self.server.count - 1)
        
        print(f'Самолёт {demand.num} прошёл взлётку в {self.env.now}')
           
    # обслуживание на стоянке
    def service_server(self, demand:Demand):
        # yield self.env.timeout(rd.expovariate(self.mu))
        yield self.env.timeout(env.now - log(random()) / 
            self.mu_server)
        global cnt_demands
        cnt_demands[1].append(self.server.count - 1)
        print(f'Самолёт {demand.num} прошёл обслуживание в {self.env.now}')


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
        global cnt_demands
        cnt_demands[1].append(system.server.count + 1)
        print(f'Самолёт {demand.num} поступил на обслуживание в {env.now}')
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
def run_system(env:simpy.Environment, cnt_runways, cnt_servers, lambda_0, 
mu_runway, mu_server):
    system = Airport(env, cnt_runways, cnt_servers, mu_runway, 
        mu_server)
    cnt = 1
    demand = Demand(cnt, env.now)
    
    print(f'Самолёт {demand.num} поступил на взлётку в {env.now}')
    env.process(go_to_runway(env, demand, system))
    
    global cnt_demands
    cnt_demands[0].append(system.runway.count + 1)
    
    while True:
        # yield env.timeout(rd.expovariate(lambda_))
        yield env.timeout(env.now - log(random()) / lambda_0)
        cnt_demands[0].append(system.runway.count + 1)
        
        cnt += 1
        demand = Demand(cnt, env.now)
        print(f'Самолёт {demand.num} поступил на взлётку в {env.now}')
        env.process(go_to_runway(env, demand, system))  

# cnt = 100
# all_times = []
# all_demands = []
# for i in range(cnt):
# print(f'\nПрогон {i+1}:')

# Начальные данные
cnt_runways = 1 # число взлёток
cnt_servers = 3 # число мест для тех обслуживания
lambda_0 = 1 
mu_runway = 2
mu_server = 3

cnt_demands = [[], []]

# Запуск моделирования
times = open('times_out.txt', 'w')
times.close()
env = simpy.Environment()
env.process(run_system(env, cnt_runways, cnt_servers, lambda_0, 
    mu_runway, mu_server))
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

average_cnt = []
for item in cnt_demands:
    if len(item) == 0:
        average_cnt.append(0)
    else:
        average_cnt.append(np.mean(item))
# print(cnt_demands)
print(f'\nСреднее число требований на взлётке: {average_cnt[0]}')
print(f'Среднее число требований на взлётке: {average_cnt[1]}\n')

# all_times.append(average_time)
# all_demands.append(average_cnt)

# print('-'*50)
# print(f'\nСреднее время пребывания требования в сети: \
# {np.mean([sum(all_times[i]) for i in range(len(all_times))])}')
# print(f'Среднее число требований в сети: \
# {np.mean([sum(all_demands[i]) for i in range(len(all_demands))])}')