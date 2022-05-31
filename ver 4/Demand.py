# описание требования
class Demand:
    def __init__(self, num, takeoff, born, 
    queue_runway=0, begin_service_runway=0, end_service_runway=0, 
    queue_parking=0, begin_service_parking=0, end_service_parking=0, death=0):
        self.num = num
        # True -- взлёт, False -- посадка
        self.takeoff = takeoff
        # момент генерации
        self.born_time = born
        # момент поступления в очередь взлётки
        self.queue_runway = queue_runway
        # момент поступления на обслуживание на взлётке
        self.begin_service_runway = begin_service_runway
        # момент окончания обслуживания на взлётке
        self.end_service_runway = end_service_runway
        # момент поступления в очередь стоянки
        self.queue_parking = queue_parking
        # момент поступления на обслуживание стоянке
        self.begin_service_parking = begin_service_parking
        # момент выхода со стоянки
        self.end_service_parking = end_service_parking
        # момент выхода из сети 
        self.death_time = death

    def calc_times(self, system_num):
        if system_num == 1:
            self.v_1 = self.end_service_runway - self.begin_service_runway
            self.w_1 = self.begin_service_runway - self.queue_runway
            self.u_1 = self.end_service_runway - self.queue_runway
            # return f'{self.num} {1 if self.takeoff else 0} {self.v_1} {self.w_1} {self.u_1}\n'
            return self.num, 1 if self.takeoff else 0, self.v_1, self.w_1, self.u_1
        else:
            self.v_2 = self.end_service_parking - self.begin_service_parking
            self.w_2 = self.begin_service_parking - self.queue_parking
            self.u_2 = self.end_service_parking - self.queue_parking
            # return f'{self.num} {1 if self.takeoff else 0} {self.v_2} {self.w_2} {self.u_2}\n'
            return self.num, 1 if self.takeoff else 0, self.v_2, self.w_2, self.u_2

    # def get_info(self):
        # return f'{self.num} {1 if self.takeoff else 0} {self.v_1} {self.w_1} {self.u_1} {self.v_2} {self.w_2} {self.u_2}\n'
        # print(f'Время поступления в СеМО: {self.born_time}')
        # print(f'Время поступления на взлётку: {self.begin_service_runway}')
        # print(f'Время окончания обслуживания на взлётке: {self.end_service_runway}')
        # print(f'Время поступления на стоянку: {self.begin_service_parking}')
        # print(f'Время выхода со стоянки: {self.end_service_parking}')
        # print(f'Время выхода из СеМО: {self.death_time}')