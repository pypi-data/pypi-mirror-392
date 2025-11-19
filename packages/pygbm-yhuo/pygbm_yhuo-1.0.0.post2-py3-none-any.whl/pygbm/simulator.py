import numpy as np
import matplotlib.pyplot as plt
from .base import GBM_setup

class GBM_simulator(GBM_setup):
    def __init__(self, y0, mu, sigma):
        super().__init__(y0, mu, sigma)
    
    def exact_method(self, t_values, B_values):
        y_values = self.y0*np.exp((self.mu - 0.5*(self.sigma**2))*t_values[1:] + self.sigma*B_values)
        y_values = np.insert(y_values, 0, self.y0, axis=0)
        return t_values, y_values
    
    def euler_method(self, t_values, B_values):
        y_values = [self.y0]
        dt = t_values[-1]/(len(t_values)-1)
        dB_values =np.insert(np.diff(B_values), 0, [B_values[0]], axis=0)
        for dB in dB_values:
            y_pre = y_values[-1]
            y_values.append(y_pre + y_pre*self.mu*dt + self.sigma*y_pre*dB)
        y_values = np.array(y_values)
        return t_values, y_values
    
    def milstein_method(self, t_values, B_values):
        y_values = [self.y0]
        dt = t_values[-1]/(len(t_values)-1)
        dB_values =np.insert(np.diff(B_values), 0, [B_values[0]], axis=0)
        for dB in dB_values:
            y_pre = y_values[-1]
            y_values.append(
                y_pre + y_pre*self.mu*dt + self.sigma*y_pre*dB 
                + 0.5*(self.sigma**2)*y_pre*(dB**2-dt)
                )
        y_values = np.array(y_values)
        return t_values, y_values

    def simulate_path(self, T, N, method = "exact_method", seed = None):
        t_values = np.linspace(0, T, N+1)
        dt = T/N
        rng = np.random.default_rng(seed)
        dB =  rng.normal(0,np.sqrt(dt),size=N)
        B_values = np.cumsum(dB)
        simulation = getattr(self, method)
        t_values, y_values = simulation(t_values, B_values)
        return t_values, y_values
    
    def plot_path(self, t_values, y_values):
        plt.plot(t_values , y_values , label ="GBM Path ")
        plt.xlabel("Time")
        plt.ylabel("Y(t)")
        plt.title("Simulated Geometric Brownian Motion Path")
        plt.legend()
        # plt.show()
    
    def simulate_compare(self, T, N, seed, methods = ["exact_method", "euler_method", "milstein_method"]):
        t_values = np.linspace(0, int(T), int(N+1))
        dt = T/N
        rng = np.random.default_rng(seed)
        dB =  rng.normal(0,np.sqrt(dt),size=N)
        B_values = np.cumsum(dB)
        for method in methods:
            simulation = getattr(self, method)
            t_values, y_values = simulation(t_values, B_values)
            plt.plot(t_values , y_values , label = method)
        plt.xlabel("Time")
        plt.ylabel("Y(t)")
        plt.title("Simulated Geometric Brownian Motion Path")
        plt.legend()
        # plt.show()
