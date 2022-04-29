import simpy
from Demand import Demand
from math import log
import random

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
        yield self.env.timeout(env.now - log(random.random()) / 
            self.mu_runway)
        global cnt_demands
        cnt_demands[0].append(self.server.count - 1)
        
        print(f'Самолёт {demand.num} прошёл взлётку в {self.env.now}')
           
    # обслуживание на стоянке
    def service_server(self, demand:Demand):
        # yield self.env.timeout(rd.expovariate(self.mu))
        yield self.env.timeout(env.now - log(random.random()) / 
            self.mu_server)
        global cnt_demands
        cnt_demands[1].append(self.server.count - 1)
        print(f'Самолёт {demand.num} прошёл обслуживание в {self.env.now}')