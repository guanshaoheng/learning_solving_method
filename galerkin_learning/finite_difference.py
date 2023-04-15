import numpy as np
import matplotlib.pyplot as plt


def dy_dx(x):
    '''
       y' = x^3 e^x
    '''
    y_ = x**3*np.exp(x)
    return y_


def FDM(x):
    dx = x[1]-x[0]
    n = len(x)
    y = np.zeros(n)
    for i in range(1, n):
        y[i] = y[i-1] + dx*dy_dx(x[i-1])
    # plt.plot(x, y)
    # plt.show()
    return y


if __name__ == "__main__":
    n = 1001
    x_0, x_end = 0, 3.
    dx = (x_end - x_0) / (n - 1)
    x = np.linspace(x_0, x_end, n)
    y = FDM(x)
    plt.plot(x, y)
    plt.show()
