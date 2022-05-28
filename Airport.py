import simpy
from Demand import Demand
from math import log, prod
import random
# from source import Application

# класс, описывающий сеть
class Airport:
    # cnt_demands = [[], []]
    distribution_types = ('Эрланга', 'Нормальное', 'Константа')

    def __init__(self, application, env:simpy.Environment, t_max, cnt_runways, cnt_servers, runway_distribution, server_distribution, mu_runway, mu_server, 
    k_runway=1, std_runway=0, k_server=1, std_server=0):
        self.application = application
        self.env = env
        self.t_max = t_max
        self.runway = simpy.Resource(env, cnt_runways)
        self.server = simpy.Resource(env, cnt_servers)
        self.runway_distribution = runway_distribution
        self.server_distribution = server_distribution
        self.mu_runway = mu_runway
        self.k_runway = k_runway
        self.std_runway = std_runway
        self.mu_server = mu_server
        self.k_server = k_server
        self.std_server = std_server

    # обслуживание на взлётке
    def service_runway(self, demand:Demand):
        # Эрланга или экспоненциальное (при k = 1)
        if self.runway_distribution == self.distribution_types[0]:
            tmp = self.mu_runway / self.k_runway
            yield self.env.timeout(self.env.now - log(prod([random.random() for _ in range(self.k_runway)])) / tmp)
        # нормально
        if self.runway_distribution == self.distribution_types[1]:
            tmp = self.mu_runway + self.std_runway * (sum([random.random() for _ in range(12)]) - 6)
            if tmp < 0: tmp = 0.001
            yield self.env.timeout(self.env.now + tmp)
        # постоянная величина
        if self.runway_distribution == self.distribution_types[2]:
            yield self.env.timeout(self.env.now + 1 / self.mu_runway)
        demands_out_0 = open('demands_out_0.txt', 'a')
        demands_out_0.write(str(self.server.count + len(self.server.queue) + 1) + '\n')
        demands_out_0.close()
        # self.cnt_demands[0].append(self.runway.count + len(self.runway.queue) - 1)
        print(f"Самолёт {demand.num} прошёл взлётку в {self.env.now} -- ({'взлёт' if demand.takeoff else 'посадка'})")
        print(f'В момент {self.env.now} было {self.runway.count + len(self.runway.queue)} + {self.server.count + len(self.server.queue)} самолётов')
        self.application.ui.progressBar.setValue(int(self.env.now / self.t_max * 100) if self.env.now < self.t_max else 100)
        self.application.ui.textBrowser.append(f"Самолёт {demand.num} прошёл взлётку в {self.env.now} -- ({'взлёт' if demand.takeoff else 'посадка'})")
        self.application.ui.textBrowser.append(f'В момент {self.env.now} было {self.runway.count + len(self.runway.queue)} + {self.server.count + len(self.server.queue)} самолётов')
           
    # обслуживание на стоянке
    def service_server(self, demand:Demand):
        # Эрланга или экспоненциальное (при k = 1)
        if self.server_distribution == self.distribution_types[0]:
            tmp = self.mu_server / self.k_server
            yield self.env.timeout(self.env.now - log(prod([random.random() for _ in range(self.k_server)])) / tmp)
        # нормальное
        if self.server_distribution == self.distribution_types[1]:
            tmp = self.mu_server + self.std_server * (sum([random.random() for _ in range(12)]) - 6)
            if tmp < 0: tmp = 0.001
            yield self.env.timeout(self.env.now + tmp)
        # постоянная величина
        if self.server_distribution == self.distribution_types[2]:
            yield self.env.timeout(self.env.now + 1 / self.mu_server)
        demands_out_1 = open('demands_out_1.txt', 'a')
        demands_out_1.write(str(self.server.count + len(self.server.queue) + 1) + '\n')
        demands_out_1.close()
        # self.cnt_demands[1].append(self.server.count + len(self.server.queue) - 1)
        print(f"Самолёт {demand.num} прошёл обслуживание в {self.env.now} -- ({'взлёт' if demand.takeoff else 'посадка'})")
        print(f'В момент {self.env.now} было {self.runway.count + len(self.runway.queue)} + {self.server.count + len(self.server.queue)} самолётов')
        self.application.ui.progressBar.setValue(int(self.env.now / self.t_max * 100) if self.env.now < self.t_max else 100)
        self.application.ui.textBrowser.append(f"Самолёт {demand.num} прошёл обслуживание в {self.env.now} -- ({'взлёт' if demand.takeoff else 'посадка'})")
        self.application.ui.textBrowser.append(f'В момент {self.env.now} было {self.runway.count + len(self.runway.queue)} + {self.server.count + len(self.server.queue)} самолётов')