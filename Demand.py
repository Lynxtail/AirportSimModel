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