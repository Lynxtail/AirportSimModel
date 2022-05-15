import simpy
from Demand import Demand
from math import log
import random

# класс, описывающий сеть
class Airport:
    cnt_demands = [[], []]
    distribution_types = ('экспоненциальное', 'нормальное', 'константа')

    def __init__(self, env:simpy.Environment, cnt_runways, cnt_servers, runway_distribution, server_distribution, mu_runway, std_runway, 
    mu_server, std_server, p_out=.3):
        self.env = env
        self.runway = simpy.Resource(env, cnt_runways)
        self.server = simpy.Resource(env, cnt_servers)
        self.runway_distribution = runway_distribution
        self.server_distribution = server_distribution
        self.mu_runway = mu_runway
        self.std_runway = std_runway
        self.mu_server = mu_server
        self.std_server = std_server
        self.p_out = p_out

    # обслуживание на взлётке
    def service_runway(self, demand:Demand):
        if self.runway_distribution == self.distribution_types[0]:
            yield self.env.timeout(self.env.now - log(random.random()) / self.mu_runway)
        if self.runway_distribution == self.distribution_types[1]:
            tmp = self.mu_runway + self.std_runway * (sum([random.random() for _ in range(12)]) - 6)
            if tmp < 0: tmp = 0.001
            yield self.env.timeout(self.env.now + tmp)
        if self.runway_distribution == self.distribution_types[2]:
            yield self.env.timeout(self.env.now + self.mu_runway)
        # yield self.env.timeout(self.env.now - log(random.random()) / 
        #     self.mu_runway)
        self.cnt_demands[0].append(self.runway.count + len(self.runway.queue) - 1)
        print(f'Самолёт {demand.num} прошёл взлётку в {self.env.now}')
        print(f'В момент {self.env.now} было {self.runway.count + len(self.runway.queue)} + {self.server.count + len(self.server.queue)}')
           
    # обслуживание на стоянке
    def service_server(self, demand:Demand):
        if self.server_distribution == self.distribution_types[0]:
            yield self.env.timeout(self.env.now - log(random.random()) / self.mu_server)
        if self.server_distribution == self.distribution_types[1]:
            tmp = self.mu_server + self.std_server * (sum([random.random() for _ in range(12)]) - 6)
            if tmp < 0: tmp = 0.001
            yield self.env.timeout(self.env.now + tmp)
        if self.server_distribution == self.distribution_types[2]:
            yield self.env.timeout(self.env.now + self.mu_server)
        # yield self.env.timeout(self.env.now - log(random.random()) / 
        #     self.mu_server)
        self.cnt_demands[1].append(self.server.count + len(self.server.queue) - 1)
        print(f'Самолёт {demand.num} прошёл обслуживание в {self.env.now}')
        print(f'В момент {self.env.now} было {self.runway.count + len(self.runway.queue)} + {self.server.count + len(self.server.queue)}')