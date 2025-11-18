import numpy as np
import matplotlib.pyplot as plt

class GBMSimulator:
    """GBM Simulator class."""
    def __init__(self, y0, mu, sigma):
        self.y0 = float(y0)
        self.mu = float(mu)
        self.sigma = float(sigma)

    def simulate_path(self, T, N):
        """
        Simulate GBM over [0, T] with N steps (N+1 points).
        Returns (t_values, y_values).
        """
        if N < 1:
            raise ValueError("N must be at least 1.")

        dt = T / N
        t_values = np.linspace(0.0, float(T), N + 1)
        
        dW = np.sqrt(dt) * np.random.randn(N)
        W = np.empty(N + 1)
        W[0] = 0.0
        W[1:] = np.cumsum(dW)

        x_values = (self.mu - 0.5 * self.sigma ** 2) * t_values + self.sigma * W

        return t_values, self.y0 * np.exp(x_values)

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
