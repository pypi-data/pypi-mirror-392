class BaseGBM:
    def __init__(self, y0, mu, sigma):
        self.y0 = y0  # Initial value
        self.mu = mu  # Drift coefficient
        self.sigma = sigma  # Diffusion coefficient
