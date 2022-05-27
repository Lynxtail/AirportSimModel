# -*- coding: utf-8 -*-

# Имеем сеть МО, состоящую из двух систем: 
# M/M/1 (взлётка) 
# и M/M/k (сервисы тех обслуживания)
# требование поступает на взлётку, обслуживается,
# после чего с вероятностью p_out = 0.3 покидает систему.
# Иначе оно отправляется на тех обслуживание, обрабатывается.
# Затем вновь отправляется на взлётку.
# (для моделирования используем библиотеку simpy)


from math import log
import random
import numpy as np
import simpy
import os
import sys
from Demand import Demand
from Airport import Airport
from cool_window import Ui_Simulation
from PyQt5 import QtCore, QtGui, QtWidgets


class Application(QtWidgets.QMainWindow):
    def __init__(self):
        super(Application, self).__init__()
        self.ui = Ui_Simulation()
        self.ui.setupUi(self)
        self.functions()

    def error(self, code):
        # коды ошибок:
        # 1 -- выберите распределение
        # 2 -- установить порядок распределения
        # 3 -- неподходящие входные данные
        if code == 1:
            QtWidgets.QMessageBox.critical(self, "Ошибка ", 
            "Укажите законы распределения вероятностей для всех элементов", 
            QtWidgets.QMessageBox.Ok)
        if code == 2:
            QtWidgets.QMessageBox.warning(self, "Предупреждение ", 
            "Укажите порядок для распределения Эрланга", 
            QtWidgets.QMessageBox.Ok)
        if code == 3:
            QtWidgets.QMessageBox.critical(self, "Ошибка ", 
            "Проверьте корректность входных данных", 
            QtWidgets.QMessageBox.Ok)

    def run(self):
        # нажатие на запуск
        # проверка введённых данных
        global t_max
        t_max = 100000000
        try:
            class DeterminationError(Exception):
                pass
            class ErlangError_1(Exception):
                pass
            class ErlangError_2(Exception):
                pass

            if any(item == "Распределение" 
            for item in [self.ui.comboBox_3.currentText(), self.ui.comboBox.currentText(), self.ui.comboBox_2.currentText()]):
                raise DeterminationError()
            if self.ui.comboBox.currentText() == "Эрланга" and not self.ui.spinBox_2.isEnabled():
                raise ErlangError_1()
            if self.ui.comboBox_2.currentText() == "Эрланга" and not self.ui.spinBox_3.isEnabled():
                raise ErlangError_2
            simulation_input(self, self.ui.spinBox.value(), self.ui.spinBox_4.value(), 
                float(self.ui.lineEdit_5.text()), float(self.ui.lineEdit_6.text()), 
                float(self.ui.lineEdit.text()), self.ui.spinBox_2.value(), float(self.ui.lineEdit_2.text()),
                float(self.ui.lineEdit_3.text()), self.ui.spinBox_3.value(), float(self.ui.lineEdit_4.text()), 
                self.ui.comboBox_3.currentText(), self.ui.comboBox.currentText(), self.ui.comboBox_2.currentText(), t_max)

        except DeterminationError:
            self.error(1)

        except ErlangError_1:
            self.ui.spinBox_2.setEnabled(True)
            self.error(2)

        except ErlangError_2:
            self.ui.spinBox_3.setEnabled(True)
            self.error(2)

        except ValueError:
            self.error(3)
        

    def stop_simulation(self):
        print("Click stop")

    def continue_simulation(self):
        print("Click continue")

    def functions(self):
        # нажатие на кнопки
        self.ui.pushButton.clicked.connect(lambda: self.run())
        self.ui.pushButton_2.clicked.connect(lambda: self.continue_simulation())
        self.ui.pushButton_3.clicked.connect(lambda: self.stop_simulation())


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

    if demand.takeoff:
        times = open('times_out.txt', 'a')
        times.write(demand.get_info())
        times.close()
        # print(f'...и самолёт {demand.num} успешно улетел!')
        application.ui.progressBar.setValue(int(env.now / t_max * 100))
        application.ui.textBrowser.append(f'...и самолёт {demand.num} успешно улетел!')
    else:
        demands_out_1 = open('demands_out_1.txt', 'a')
        demands_out_1.write(str(system.server.count + len(system.server.queue) + 1) + '\n')
        demands_out_1.close()
        # system.cnt_demands[1].append(system.server.count + len(system.server.queue) + 1)
      
        # print(f"Самолёт {demand.num} поступил на обслуживание в {env.now} -- ({'взлёт' if demand.takeoff else 'посадка'})")
        application.ui.progressBar.setValue(int(env.now / t_max * 100))
        application.ui.textBrowser.append(f"Самолёт {demand.num} поступил на обслуживание в {env.now} -- ({'взлёт' if demand.takeoff else 'посадка'})")
        # print(f'В момент {env.now} было {system.runway.count + len(system.runway.queue)} + {system.server.count + len(system.server.queue)} самолётов')
        application.ui.textBrowser.append(f'В момент {env.now} было {system.runway.count + len(system.runway.queue)} + {system.server.count + len(system.server.queue)} самолётов')
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
    demand.takeoff = True

    # рассчёт м.о.
    demand.calc_times()

    demands_out_0 = open('demands_out_0.txt', 'a')
    demands_out_0.write(str(system.runway.count + len(system.runway.queue) + 1) + '\n')
    demands_out_0.close()
    # system.cnt_demands[0].append(system.runway.count + len(system.runway.queue) + 1)
    # print(f"Самолёт {demand.num} поступил на взлётку в {env.now} -- ({'взлёт' if demand.takeoff else 'посадка'})")
    application.ui.progressBar.setValue(int(env.now / t_max * 100))
    application.ui.textBrowser.append(f"Самолёт {demand.num} поступил на взлётку в {env.now} -- ({'взлёт' if demand.takeoff else 'посадка'})")
    # print(f'В момент {env.now} было {system.runway.count + len(system.runway.queue)} + {system.server.count + len(system.server.queue)} самолётов')
    application.ui.textBrowser.append(f'В момент {env.now} было {system.runway.count + len(system.runway.queue)} + {system.server.count + len(system.server.queue)} самолётов')
    env.process(go_to_runway(env, demand, system))

# функция запуска работы модели
def run_system(application:Application, env:simpy.Environment, system:Airport, source_distribution, lambda_0, std_0):
    cnt = 1
    demand = Demand(cnt, random.choice([True, False]), env.now)
    application.ui.progressBar.setValue(int(env.now / t_max * 100))
    # print(f"Самолёт {demand.num} поступил на взлётку в {env.now} -- ({'взлёт' if demand.takeoff else 'посадка'})")
    application.ui.textBrowser.append(f"Самолёт {demand.num} поступил на взлётку в {env.now} -- ({'взлёт' if demand.takeoff else 'посадка'})")
    env.process(go_to_runway(env, demand, system))
    
    # print(f'В момент {env.now} было {system.runway.count + len(system.runway.queue)} + {system.server.count + len(system.server.queue)} самолётов')
    application.ui.textBrowser.append(f'В момент {env.now} было {system.runway.count + len(system.runway.queue)} + {system.server.count + len(system.server.queue)} самолётов')
    demands_out_0 = open('demands_out_0.txt', 'a')
    demands_out_0.write(str(system.runway.count + len(system.runway.queue) + 1) + '\n')
    demands_out_0.close()
    # system.cnt_demands[0].append(system.runway.count + len(system.runway.queue) + 1)
    
    while True:
        # генерация требования
        if source_distribution == system.distribution_types[0]:
            yield env.timeout(env.now - log(random.random()) / lambda_0)
        if source_distribution == system.distribution_types[1]:
            tmp = lambda_0 + std_0 * (sum([random.random() for _ in range(12)]) - 6)
            if tmp < 0: tmp = 0.001
            yield env.timeout(env.now + tmp)
        if source_distribution == system.distribution_types[2]:
            yield env.timeout(env.now + lambda_0)
        demands_out_0 = open('demands_out_0.txt', 'a')
        demands_out_0.write(str(system.runway.count + len(system.runway.queue) + 1) + '\n')
        demands_out_0.close()
        # system.cnt_demands[0].append(system.runway.count + len(system.runway.queue) + 1) 
        cnt += 1
        # random.choice([True, False])
        demand = Demand(cnt, False, env.now)
        # print(f"Самолёт {demand.num} поступил на взлётку в {env.now} -- ({'взлёт' if demand.takeoff else 'посадка'})")
        application.ui.progressBar.setValue(int(env.now / t_max * 100))
        application.ui.textBrowser.append(f"Самолёт {demand.num} поступил на взлётку в {env.now} -- ({'взлёт' if demand.takeoff else 'посадка'})")
        # print(f'В момент {env.now} было {system.runway.count + len(system.runway.queue)} + {system.server.count + len(system.server.queue)} самолётов')  
        application.ui.textBrowser.append(f'В момент {env.now} было {system.runway.count + len(system.runway.queue)} + {system.server.count + len(system.server.queue)} самолётов')
        env.process(go_to_runway(env, demand, system))  
        
        # промежуточные результаты
        v = [[], []]
        w = [[], []]
        u = [[], []]
        if os.stat("times_out.txt").st_size != 0:
            times = open('times_out.txt', 'r')
            for line in times:
                _, _, v_1_, w_1_, u_1_, v_2_, w_2_, u_2_ = [float(item) for item in line.split(' ')]
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

            application.ui.label_13.setText(str(v[0]))
            application.ui.label_14.setText(str(v[1]))
            application.ui.label_15.setText(str(w[0]))
            application.ui.label_20.setText(str(w[1]))
            application.ui.label_16.setText(str(u[0]))
            application.ui.label_19.setText(str(u[1]))
            # print(f'\nСреднее время обслуживания на взлётке: {v[0]}')
            # print(f'Среднее время обслуживания на стоянке: {v[1]}')
            # print(f'\nСреднее время ожидания на взлётке: {w[0]}')
            # print(f'Среднее время ожидания на стоянке: {w[1]}')
            # print(f'\nСреднее время пребывания на взлётке: {u[0]}')
            # print(f'Среднее время пребывания на стоянке: {u[1]}')
        else:
            application.ui.textBrowser.append('There are no serviced demands!')        

        states = [[], []]
        p = [[], []]

        cnt_demands = [[], []] 
        f = open('demands_out_0.txt', 'r')
        for line in f:
            cnt_demands[0].append(line)
        f.close()
        f = open('demands_out_1.txt', 'r')
        for line in f:
            cnt_demands[1].append(line)
        f.close()
        cnt_demands = list(map(sorted, cnt_demands))
        # system.cnt_demands = list(map(sorted, system.cnt_demands))
        for item in cnt_demands[0]:
            if item in states[0]:
                continue
            else:
                states[0].append(item)
                p[0].append(cnt_demands[0].count(item) / len(cnt_demands[0]))
        for item in cnt_demands[1]:
            if item in states[1]:
                continue
            else:
                states[1].append(item)
                p[1].append(cnt_demands[1].count(item) / len(cnt_demands[1]))
        for item in p:
            if len(item) == 0:
                item.append(1)
                break
        # print(f'\nСтационарное распределение:\n{p}')
        tmp_string = ''
        for i in range(len(p[0])):
            tmp_string += f'{p[0][i]:.4f} '
            if (i + 1) % 4 == 0:
                tmp_string += '\n'
        application.ui.label_18.setText(str(tmp_string))
        tmp_string = ''
        for i in range(len(p[1])):
            tmp_string += f'{p[1][i]:.4f} '
            if (i + 1) % 4 == 0:
                tmp_string += '\n'
        application.ui.label_22.setText(str(tmp_string))

        n = [[sum([item * p[0][item] for item in range(len(p[0]))])], [sum([item * p[1][item] for item in range(len(p[1]))])]]
        # print(f'\nСреднее число требований в сети:\n{n}')
        application.ui.label_17.setText(str(n[0]))
        application.ui.label_21.setText(str(n[1]))


def simulation_input(application:Application, cnt_runways, cnt_servers, lambda_0, std_0, 
mu_runway, k_runway, std_runway, 
mu_server, k_server, std_server, 
source_distribution, runway_distribution, server_distribution, t_max=10**10):
    
    # блокировка кнопки запуск и полей с параметрами
    application.ui.pushButton.setEnabled(False)
    application.ui.spinBox.setEnabled(False)
    application.ui.spinBox_4.setEnabled(False)
    application.ui.lineEdit_5.setEnabled(False)
    application.ui.lineEdit_6.setEnabled(False)
    application.ui.lineEdit.setEnabled(False)
    application.ui.spinBox_2.setEnabled(False)
    application.ui.lineEdit_2.setEnabled(False)
    application.ui.lineEdit_3.setEnabled(False)
    application.ui.spinBox_3.setEnabled(False)
    application.ui.lineEdit_4.setEnabled(False)
    application.ui.comboBox_3.setEnabled(False)
    application.ui.comboBox.setEnabled(False)
    application.ui.comboBox_2.setEnabled(False)
    
    # Запуск моделирования
    times = open('times_out.txt', 'w')
    times.close()
    demands_out_0 = open('demands_out_0.txt', 'w')
    demands_out_0.close()
    demands_out_1 = open('demands_out_1.txt', 'w')
    demands_out_1.close()
    env = simpy.Environment()
    system = Airport(application, env, t_max, cnt_runways, cnt_servers, runway_distribution, server_distribution, mu_runway, mu_server, k_runway, std_runway, k_server, std_server)
    env.process(run_system(application, env, system, source_distribution, lambda_0, std_0))
    env.run(until=t_max)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    application = Application()
    application.show()
    sys.exit(app.exec_())    