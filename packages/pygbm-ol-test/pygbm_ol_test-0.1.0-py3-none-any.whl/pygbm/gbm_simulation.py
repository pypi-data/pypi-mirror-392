import numpy as np
import matplotlib.pyplot as plt
from .base_pygbm import BaseGBM

class GBMSimulator(BaseGBM):
    def __init__(self, y0, mu, sigma):
        super().__init__(y0, mu, sigma)

    def simulate_path(self, T, N):
        dt = T / N
        t_values = np.linspace(0, T, N + 1)
        y_values = [self.y0]
        
        for _ in range(N):
            y_prev = y_values[-1]
            dB = np.random.normal(0, np.sqrt(dt))
            y_next = y_prev * np.exp((self.mu - 0.5 * self.sigma ** 2) * dt + self.sigma * dB)
            y_values.append(y_next)
        
        return t_values, y_values

    def plot_path(self, t_values, y_values, output=None):
        plt.plot(t_values, y_values, label="GBM Path")
        plt.xlabel("Time")
        plt.ylabel("Y(t)")
        plt.title("Simulated Geometric Brownian Motion Path")
        plt.legend()
        if output:
            plt.savefig(output)
        else:
            plt.show()
