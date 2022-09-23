# Имеем сеть МО, состоящую из двух систем: 
# M/M/1 (взлётка) 
# и M/M/k (сервисы)

from math import log, prod
import random
import sys
import os
import numpy as np
from Demand import Demand
from cool_window import Ui_Simulation
from PyQt5 import QtWidgets, QtCore


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
            f"Проверьте корректность входных данных",
            # {list(map(, [(self.ui.lineEdit_5.text()), float(self.ui.lineEdit_6.text()), float(self.ui.lineEdit.text()), float(self.ui.lineEdit_2.text()), float(self.ui.lineEdit_3.text()), float(self.ui.lineEdit_4.text()), t_max]))}", 
            QtWidgets.QMessageBox.Ok)

    def run(self):
        # нажатие на запуск
        # проверка введённых данных
        global t_max
        t_max = 10**4

        lambda_0 = 1
        std_0 = 0
        mu_runway = 6
        std_runway = 0
        mu_parking = 2 
        std_parking = 0

        try:
            class DeterminationError(Exception):
                pass
            class ErlangError(Exception):
                pass

            if any(item == "Распределение" 
            for item in [self.ui.comboBox_3.currentText(), 
            self.ui.comboBox.currentText(), self.ui.comboBox_2.currentText()]):
                raise DeterminationError()
            if self.ui.comboBox.currentText() == "Эрланга" and not self.ui.spinBox_2.isEnabled() or self.ui.comboBox_2.currentText() == "Эрланга" and not self.ui.spinBox_3.isEnabled():
                raise ErlangError()
            
            lambda_0 = float(self.ui.lineEdit_5.text())
            std_0 = float(self.ui.lineEdit_6.text())
            mu_runway = float(self.ui.lineEdit.text())
            std_runway = float(self.ui.lineEdit_2.text())
            mu_parking = float(self.ui.lineEdit_3.text()) 
            std_parking = float(self.ui.lineEdit_4.text())

            # t_max = 10**6 / lambda_0
            self.system = Airport(self, self.ui.spinBox.value(), self.ui.spinBox_4.value(), 
                lambda_0, std_0, mu_runway, self.ui.spinBox_2.value(), 
                std_runway, mu_parking, 
                self.ui.spinBox_3.value(), std_parking, 
                self.ui.comboBox_3.currentText(), self.ui.comboBox.currentText(), 
                self.ui.comboBox_2.currentText(), t_max)
            self.system.thread_signal.connect(self.update_progress_bar)
            self.system.start()

        except DeterminationError:
            self.error(1)

        except ErlangError:
            self.ui.spinBox_2.setEnabled(True)
            self.ui.spinBox_3.setEnabled(True)
            self.error(2)

        except ValueError:
            self.error(3)

    def functions(self):
        # нажатие на кнопки
        self.ui.pushButton.clicked.connect(lambda: self.run())

    # взаимодействие с виджетами
    
    def demand_arrival(self, t_now, cnt):
        self.ui.textBrowser.append(f'Момент {t_now}: самолёт {cnt} появился.')
    
    def on_runway(self, t_now, num):
        self.ui.textBrowser.append(f'Момент {t_now}: самолёт {num} поступил на в/п полосу.')
    
    def on_parking(self, t_now, num):
        self.ui.textBrowser.append(f'Момент {t_now}: самолёт {num} поступил на стоянку.')
    
    def serve_runway(self, t_now, num):
        self.ui.textBrowser.append(f'Момент {t_now}: самолёт {num} прошёл в/п полосу.')
    
    def exit_airport(self, t_now, num):
        self.ui.textBrowser.append(f'Момент {t_now}: самолёт {num} покидает аэропорт.')
    
    def serve_parking(self, t_now, num):
        self.ui.textBrowser.append(f'Момент {t_now}: самолёт {num} прошёл стоянку.')
    
    def block(self):
        # блокировка кнопки запуск и полей с параметрами
        self.ui.pushButton.setEnabled(False)
        self.ui.spinBox.setEnabled(False)
        self.ui.spinBox_4.setEnabled(False)
        self.ui.lineEdit_5.setEnabled(False)
        self.ui.lineEdit_6.setEnabled(False)
        self.ui.lineEdit.setEnabled(False)
        self.ui.spinBox_2.setEnabled(False)
        self.ui.lineEdit_2.setEnabled(False)
        self.ui.lineEdit_3.setEnabled(False)
        self.ui.spinBox_3.setEnabled(False)
        self.ui.lineEdit_4.setEnabled(False)
        self.ui.comboBox_3.setEnabled(False)
        self.ui.comboBox.setEnabled(False)
        self.ui.comboBox_2.setEnabled(False)
    
    def update_progress_bar(self, t_s):
        t_now, t_max, t_act_device_runway, t_act_device_parking, t_act_source = t_s
        self.ui.progressBar.setValue(int(t_now / t_max * 100) if min(min(t_act_device_runway), min(t_act_device_parking), t_act_source) < t_max else 100)

    def update_labels(self, v, w, u):
        self.ui.label_13.setText(str(v[0]))
        self.ui.label_14.setText(str(v[1]))
        self.ui.label_15.setText(str(w[0]))
        self.ui.label_20.setText(str(w[1]))
        self.ui.label_16.setText(str(u[0]))
        self.ui.label_19.setText(str(u[1]))
        
    def update_p_1(self, tmp_string):
        self.ui.label_18.setText(str(tmp_string))

    def update_p_2(self, tmp_string):
        self.ui.label_22.setText(str(tmp_string))

    def update_n(self, n):
        self.ui.label_17.setText(str(n[0]))
        self.ui.label_21.setText(str(n[1]))


class Airport(QtCore.QThread):
    thread_signal = QtCore.pyqtSignal(list)

    def __init__(self, application:Application, cnt_runways, cnt_parking, 
    lambda_0, std_0, mu_runway, k_runway, std_runway, mu_parking, k_parking, std_parking, 
    source_distribution, runway_distribution, parking_distribution, t_max):
        super(Airport, self).__init__()
        self.application = application
        self.cnt_runways = cnt_runways
        self.cnt_parking = cnt_parking 
        self.lambda_0 = lambda_0 
        self.std_0 = std_0 
        self.mu_runway = mu_runway
        self.k_runway = k_runway 
        self.std_runway = std_runway 
        self.mu_parking = mu_parking
        self.k_parking = k_parking
        self.std_parking = std_parking
        self.source_distribution = source_distribution
        self.runway_distribution = runway_distribution
        self.parking_distribution = parking_distribution
        self.t_max = t_max

    def generate_random_value(self, type, lambda_:float, std=0, k=1):
        distribution_types = ('Эрланга', 'Нормальное', 'Константа')
        # Эрланга или экспоненциальное (при k = 1)
        if type == distribution_types[0]:
            # tmp = lambda_ / k
            # return -log(prod([random.random() for _ in range(k)])) / tmp)
            return -log(prod([random.random() for _ in range(k)])) / lambda_
        # нормальное
        elif type == distribution_types[1]:
            tmp = lambda_ + std * (sum([random.random() 
                for _ in range(12)]) - 6)
            if tmp < 0: tmp = 0.001
            return tmp
        # постоянная величина
        elif type == distribution_types[2]:
            return lambda_
        else:
            print(type)
            raise Exception

    def run(self):
    
        application.block()
        
        # очистка логов
        times = open('times_1.txt', 'w')
        times.close()
        times = open('times_2.txt', 'w')
        times.close()
        demands_out = open('demands_out_1.txt', 'w')
        demands_out.close()
        demands_out = open('demands_out_2.txt', 'w')
        demands_out.close()

        # инициализация моментов активации процессов и вспомогательных величин
        t_act_source = 0 # момент генерации требования
        t_act_device_runway = [t_max + 0.0000001]*self.cnt_runways # момент начала обслуживания на взлётке
        t_act_device_parking = [t_max + 0.0000001]*self.cnt_parking # моменты начала обслуживания приборами на стоянке
        runway_queue_demands = [] # требования в очереди на взлётке
        parking_queue_demands = [] # требования в очереди на парковке
        runway_service_demands = [] # требования на приборах на взлётке 
        parking_service_demands = [] # требования на приборах на парковке
        times = [[0, 0, 0], [0, 0, 0]] # длительности в системах

        # начальные условия
        t_now = 0 # текущее время
        device_runway_free = [True]*self.cnt_runways # индикаторы занятости приборов на взлётке
        device_parking_free = [True]*self.cnt_parking # индикаторы занятости приборов на стоянке

        serviced_demands = [0, 0] # число обслуженных требований в 1 и 2 системах
        cnt = 0 # номер требования

        try:

            # процесс симуляция
            while t_now < t_max:
                indicator = False # индикатор активности какого-либо процесса
                
                # генерация требования
                if (t_act_source == t_now):
                    cnt += 1
                    # print(f"Самолёт {cnt}; Момент формирования требования: {t_now}")
                    # application.print_data(0, t_now, cnt)
                    application.demand_arrival(t_now, cnt)
                    indicator = True
                    # if t_born[0] == 0:
                    #     t_born[0] = t_now
                    # elif t_born[1] == 0:
                    #     t_born[1] = t_now
                    # else:
                    #     t_born[2] = t_now
                    # # print(t_born)
                    # t_act_source = t_now - log(random()) / lambda_0
                    runway_queue_demands.append(Demand(cnt, False, t_now, t_now))
                    t_act_source = t_now + self.generate_random_value(self.source_distribution, self.lambda_0, self.std_0)
                
                # начало обслуживания требования прибором взлётки
                if (any(device_runway_free) and any(runway_queue_demands)):
                    # print(f"Самолёт {runway_queue_demands[0].num}; Момент начала обслуживания прибором взлётки: {t_now}")
                    application.on_runway(t_now, runway_queue_demands[0].num)
                    indicator = True
                    t_act_device_runway[device_runway_free.index(True)] = t_now + self.generate_random_value(self.runway_distribution, self.mu_runway, self.std_runway, self.k_runway)
                    runway_service_demands.append(runway_queue_demands.pop(0))
                    runway_service_demands[-1].begin_service_runway = t_now
                    runway_service_demands[-1].end_service_runway = t_act_device_runway[device_runway_free.index(True)]
                    device_runway_free[device_runway_free.index(True)] = False
                    # t_act_source = t_now - log(rnd) / lambda_
                    # N += 1 #???
                    # t_service1[0] = t_now

                # начало обслуживания требования прибором стоянки
                elif (any(device_parking_free) and any(parking_queue_demands)):
                    # print(f"Самолёт {parking_queue_demands[0].num}; Момент начала обслуживания прибором стоянки: {t_now}")
                    application.on_parking(t_now, parking_queue_demands[0].num)
                    indicator = True
                    t_act_device_parking[device_parking_free.index(True)] = t_now + self.generate_random_value(self.parking_distribution, self.mu_parking, self.std_parking, self.k_parking)
                    parking_service_demands.append(parking_queue_demands.pop(0))
                    parking_service_demands[-1].begin_service_parking = t_now
                    parking_service_demands[-1].end_service_parking = t_act_device_parking[device_parking_free.index(True)]
                    device_parking_free[device_parking_free.index(True)] = False
                    # t_act_source = t_now - log(rnd) / lambda_
                    # N += 1 #???
                    # t_service2[0] = t_now
                
                # отказ
                # elif N > 2:
                #     N -= 1
                #     t_born[2] = 0
                #     cnt_refuse += 1
                    
                # завершение обслуживания требования прибором взлётки
                if (any(item == t_now for item in t_act_device_runway)):
                    # t_service1[1] = t_now
                    indicator = True
                    device_runway_free[t_act_device_runway.index(t_now)] = True
                    t_act_device_runway[t_act_device_runway.index(t_now)] = t_max + 0.0000001

                    for item in runway_service_demands:
                        if item.end_service_runway == t_now:
                            ind = runway_service_demands.index(item)
                            break
                    
                    # print(f"Самолёт {runway_service_demands[ind].num}; Момент завершения обслуживания прибором взлётки: {t_now}")
                    application.serve_runway(t_now, runway_service_demands[ind].num)

                    runway_service_demands[ind].end_service_runway = t_now
                    runway_service_demands[ind].queue_parking = t_now
                    
                    serviced_demands[0] += 1

                    _, _, a, b, c = runway_service_demands[ind].calc_times(1)
                    times[0][0] += a
                    times[0][1] += b
                    times[0][2] += c
                    # print(runway_service_demands[ind].calc_times(1))
                    # f = open('times_1.txt', 'a')
                    # f.write(runway_service_demands[ind].calc_times(1))
                    # f.close()

                    if runway_service_demands[ind].takeoff == True:
                        application.exit_airport(t_now, runway_service_demands[ind].num)
                        runway_service_demands.pop(ind)
                    else:
                        parking_queue_demands.append(runway_service_demands.pop(ind))

                    # print(f"Момент поступления: {t_service1[0]}\nМомент выхода из СМО: {t_now}")
                    # N -= 1
                    # # запись требования в формате (в каком-то)***
                    # demands.append(Demand(t_born[0], t_service1[0], t_service1[1]))
                    # t_born[0] = 0

                # завершение обслуживания требования прибором стоянки
                if (any(item == t_now for item in t_act_device_parking)):
                    # t_service2[1] = t_now
                    indicator = True
                    device_parking_free[t_act_device_parking.index(t_now)] = True
                    t_act_device_parking[t_act_device_parking.index(t_now)] = t_max + 0.0000001
                    
                    for item in parking_service_demands:
                        if item.end_service_parking == t_now:
                            ind = parking_service_demands.index(item)
                            break
                    
                    if ind > len(parking_service_demands):
                        if parking_service_demands[ind - 1] == t_now:
                            ind -= 1

                    # print(f"Самолёт {parking_service_demands[ind].num}; Момент завершения обслуживания прибором стоянки: {t_now}")
                    application.serve_parking(t_now, parking_service_demands[ind].num)

                    parking_service_demands[ind].end_service_parking = t_now
                    parking_service_demands[ind].queue_runway = t_now
                    
                    serviced_demands[1] += 1
                    
                    _, _, a, b, c = parking_service_demands[ind].calc_times(2)
                    times[1][0] += a
                    times[1][1] += b
                    times[1][2] += c
                    # print(parking_service_demands[ind].calc_times(2))
                    # f = open('times_2.txt', 'a')
                    # f.write(parking_service_demands[ind].calc_times(2))
                    # f.close()
                    
                    runway_queue_demands.append(parking_service_demands.pop(ind))
                    runway_queue_demands[-1].takeoff = True

                    # print(f"Момент поступления: {t_service2[0]}\nМомент выхода из СМО: {t_now}")
                    # N -= 1
                    # demands.append(Demand(t_born[1], t_service2[0], t_service2[1]))
                    # t_born[1] = 0

                # переход к следующему моменту
                if not indicator:
                    
                    self.thread_signal.emit([t_now, t_max, t_act_device_runway, t_act_device_parking, t_act_source])
                    # application.update_progress_bar(t_now, t_max, t_act_device_runway, t_act_device_parking, t_act_source)

                    tmp_1 = 1 if serviced_demands[0] == 0 else serviced_demands[0]
                    tmp_2 = 1 if serviced_demands[1] == 0 else serviced_demands[1]
                    v = [[times[0][0] / tmp_1], [times[1][0] / tmp_2]]
                    w = [[times[0][1] / tmp_1], [times[1][1] / tmp_2]]
                    u = [[times[0][2] / tmp_1], [times[1][2] / tmp_2]]

                    application.update_labels(v, w, u)

                    print(f'Среднее время обслуживания на взлётке: {v[0]}')
                    print(f'Среднее время обслуживания на стоянке: {v[1]}')
                    print(f'Среднее время ожидания на взлётке: {w[0]}')
                    print(f'Среднее время ожидания на стоянке: {w[1]}')
                    print(f'Среднее время пребывания на взлётке: {u[0]}')
                    print(f'Среднее время пребывания на стоянке: {u[1]}')


                    demands_out = open('demands_out_1.txt', 'a')
                    demands_out.write(str(len(runway_service_demands) + len(runway_queue_demands)) + '\n')
                    demands_out.close()
                    demands_out = open('demands_out_2.txt', 'a')
                    demands_out.write(str(len(parking_service_demands) + len(parking_queue_demands)) + '\n')
                    demands_out.close()

                    states = [[], []]
                    p = [[], []]

                    cnt_demands = [[], []] 
                    f = open('demands_out_1.txt', 'r')
                    for line in f:
                        cnt_demands[0].append(line)
                    f.close()
                    f = open('demands_out_2.txt', 'r')
                    for line in f:
                        cnt_demands[1].append(line)
                    f.close()
                    cnt_demands = list(map(sorted, cnt_demands))
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
                    print(f'Стационарное распределение:{p}')
                    print(f'check: {sum(p[0])}, {sum(p[1])}')
                    
                    if len(p[0]) > 16:
                        tmp_string = ''
                        for i in range(8):
                            tmp_string += f'{p[0][i]:.4f} '
                            if (i + 1) % 4 == 0:
                                tmp_string += '\n'
                        tmp_string += '\n\t...\t\n'
                        for i in range(len(p[0]) - 8, len(p[0])):
                            tmp_string += f'{p[0][i]:.4f} '
                            if (i + 1) % 4 == 0:
                                tmp_string += '\n'
                        application.update_p_1(tmp_string)
                    else:
                        tmp_string = ''
                        for i in range(len(p[0])):
                            tmp_string += f'{p[0][i]:.4f} '
                            if (i + 1) % 4 == 0:
                                tmp_string += '\n'
                        application.update_p_1(tmp_string)
                    
                    if len(p[1]) > 16:
                        tmp_string = ''
                        for i in range(8):
                            tmp_string += f'{p[1][i]:.4f} '
                            if (i + 1) % 4 == 0:
                                tmp_string += '\n'
                        tmp_string += '\n\t...\t\n'
                        for i in range(len(p[1]) - 8, len(p[1])):
                            tmp_string += f'{p[1][i]:.4f} '
                            if (i + 1) % 4 == 0:
                                tmp_string += '\n'
                        application.update_p_2(tmp_string)
                    else:
                        tmp_string = ''
                        for i in range(len(p[1])):
                            tmp_string += f'{p[1][i]:.4f} '
                            if (i + 1) % 4 == 0:
                                tmp_string += '\n'
                        application.update_p_2(tmp_string)

                    # n = [[sum([item * p[0][item] for item in range(len(p[0]))])], 
                    #     [sum([item * p[1][item] for item in range(len(p[1]))])]]
                    n = [[u[0][0] * serviced_demands[0] / t_max], [u[1][0] * serviced_demands[1] / t_max]]
                    print(f'Среднее число требований в сети:{n}')
                    application.update_n(n)

                    states.clear()
                    p.clear()

                    # переход к следующему событию
                    t_now = min(min(t_act_device_runway), min(t_act_device_parking), t_act_source)
        except:
            print(t_now)
            raise Exception

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    application = Application()
    application.show()
    sys.exit(app.exec_())