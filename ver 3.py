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
import numpy as np
import simpy

# класс, описывающий сеть
class Airport:
    def __init__(self, env, cnt_runways, cnt_servers, mu_runway, 
    mu_server, p_out):
        self.env = env
        self.runway = simpy.Resource(env, cnt_runways)
        self.server = simpy.Resource(env, cnt_servers)
        self.mu_runway = mu_runway
        self.mu_server = mu_server
        self.p_out = p_out

    # обслуживание на взлётке
    def service_runway(self, demand):
        # yield self.env.timeout(rd.expovariate(self.mu))
        yield self.env.timeout(env.now - log(random()) / 
            self.mu_runway)
        global cnt_demands
        cnt_demands[0].append(self.server.count - 1)
        print(f'Самолёт {demand} прошёл взлётку в {self.env.now}')
           
    # обслуживание на стоянке
    def service_server(self, demand):
        # yield self.env.timeout(rd.expovariate(self.mu))
        yield self.env.timeout(env.now - log(random()) / 
            self.mu_server)
        global cnt_demands
        cnt_demands[1].append(self.server.count - 1)
        print(f'Самолёт {demand} прошёл обслуживание в {self.env.now}')


# функция поведения самолёта на взлётке
def go_to_runway(env, demand, system):
    # требование пришло в систему
    arrival_time = env.now

    with system.runway.request() as request:
        yield request
        yield env.process(system.service_runway(demand))

    global times
    times[0].append(env.now - arrival_time)

    if random() <= system.p_out:
        print(f'...и самолёт {demand} успешно улетел!')
    else:
        # yield env.timeout(env.now - log(random()) / 
        #   (system.mu_runway * (1 - system.p_out)))
        global cnt_demands
        cnt_demands[1].append(system.server.count + 1)
        print(f'Самолёт {demand} поступил на обслуживание в {env.now}')
        env.process(go_to_server(env, demand, system))

# функция поведения самолёта на стоянке
def go_to_server(env, demand, system):
	# требование пришло в систему
	arrival_time = env.now
	
	with system.server.request() as request:
		yield request
		yield env.process(system.service_server(demand))

	global times
	times[1].append(env.now - arrival_time)

# функция запуска работы модели
def run_system(env, cnt_runways, cnt_servers, lambda_0, 
mu_runway, mu_server):
    system = Airport(env, cnt_runways, cnt_servers, mu_runway, 
        mu_server, p_out=0.3)
    demand = 1
    print(f'Самолёт {demand} поступил на взлётку в {env.now}')
    env.process(go_to_runway(env, demand, system))
    global cnt_demands
    cnt_demands[0].append(system.runway.count + 1)
    while True:
        # yield env.timeout(rd.expovariate(lambda_))
        yield env.timeout(env.now - log(random()) / lambda_0)
        cnt_demands[0].append(system.runway.count + 1)
        demand += 1
        print(f'Самолёт {demand} поступил на взлётку в {env.now}')
        env.process(go_to_runway(env, demand, system))  

cnt = 100
all_times = []
all_demands = []

for i in range(cnt):
    print(f'\nПрогон {i+1}:')

    # Начальные данные
    cnt_runways = 1 # число взлёток
    cnt_servers = 3 # число мест для тех обслуживания
    lambda_0 = 1 
    mu_runway = 2
    mu_server = 3
    times = [[], []]
    cnt_demands = [[], []]

    # Запуск моделирования
    env = simpy.Environment()
    env.process(run_system(env, cnt_runways, cnt_servers, lambda_0, 
        mu_runway, mu_server))
    env.run(until=10)

    # Результаты
    average_time = []
    for item in times:
        if len(item) == 0:
            average_time.append(0)
        else:
            average_time.append(np.mean(item))
    print(f'\nСреднее время обслуживания на взлётке: {average_time[0]}')
    print(f'Среднее время обслуживания на стоянке: {average_time[1]}')

    average_cnt = []
    for item in cnt_demands:
        if len(item) == 0:
            average_cnt.append(0)
        else:
            average_cnt.append(np.mean(item))
    # print(cnt_demands)
    print(f'\nСреднее число требований на взлётке: {average_cnt[0]}')
    print(f'Среднее число требований на взлётке: {average_cnt[1]}\n')

    all_times.append(average_time)
    all_demands.append(average_cnt)

print('-'*50)
print(f'\nСреднее время пребывания требования в сети: \
    {np.mean([sum(all_times[i]) for i in range(len(all_times))])}')
print(f'Среднее число требований в сети: \
    {np.mean([sum(all_demands[i]) for i in range(len(all_demands))])}')