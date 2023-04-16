import numpy as np
import matplotlib.pyplot as plt


def get_B(x, h):
    n = len(x)
    B = np.zeros(len(x))
    B[0] = h/6. * (f(x[0]) + 2.*f(x[0] + 0.5*h))
    for i in range(1, n-1):
        B[i] = h/3. * (f(x[i]) + f(x[i] + 0.5*h) + f(x[i]-0.5*h))
    B[-1] = h/6. * (f(x[n-1]) + 2.*f(x[n-1] - 0.5*h))

    return B


def f(x):
    return x**3*np.exp(x)


def get_A(n):
    A = np.zeros(shape=[n, n])
    for i in range(1, n-1):
        A[i, i-1:i+2] = np.array([-0.5, 0., 0.5])
    A[0, 0:2] = np.array([-0.5, 0.5])
    A[n-1, n-2:n] = np.array([-0.5, 0.5])
    return A


def boundary_condition(A, B, u, free_mask):
    B -= np.einsum('ij, j->i', A, u)
    return A[free_mask][:, free_mask], B[free_mask]


def FEM(
    num_ele = 10):
    x = np.linspace(0, 3, num_ele+1)
    h = x[1] - x[0]
    A = get_A(len(x))
    B = get_B(x, h)

    # boundary condition u0=0
    u = np.zeros_like(x)
    free_mask = (x>0)
    A_free, B_free = boundary_condition(A, B, u, free_mask)
    u_free = np.linalg.solve(A_free, B_free)
    u[free_mask] = u_free

    return x, u


if __name__ == '__main__':
    x, u = FEM(num_ele=40)
    plt.plot(x, u)
    plt.show()