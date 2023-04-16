import numpy as np
import matplotlib.pyplot as plt
from finite_difference import FDM
from galerkin_FEM import FEM

'''
    Reference:
    [1]: https://zhuanlan.zhihu.com/p/543086700
    
       y' = x^3 e^x
       y(x) = (x^3-3x^2+6x-6)e^x + 6
    
'''


def get_basis(x, order=3):
    basis = [x]
    for i in range(1, order):
        basis.append(x**(i+1))
    return np.array(basis)


def get_d_basis(x, order=3):
    d_basis = [np.ones_like(x)]
    for i in range(1, order):
        d_basis.append((i+1)*x**i)
    return np.array(d_basis)


def get_a(x, order):
    basis = get_basis(x, order=order)
    d_basis = get_d_basis(x, order=order)
    n = len(basis)
    A = np.zeros(shape=[n, n])
    B = np.zeros(shape=n)
    f = np.exp(x)*x**3
    for i in range(n):
        for j in range(n):
            A[i, j] = np.trapz(y=basis[i]*d_basis[j], x=x)
        B[i] = np.trapz(y = basis[i] * f, x = x)
    a = np.linalg.solve(A, B)
    return a


def main():
    x_end = 3
    x = np.linspace(0, x_end, 50)
    y_accurate = (x**3-3*x**2+6*x-6)*np.exp(x) + 6
    index = np.arange(0, len(x), len(x)//10+1)

    fig = plt.figure()
    plt.scatter(x[index], y_accurate[index], c='r', label='Accurate')

    for order in [2, 3, 4, 5]:
        basis = get_basis(x, order=order)
        a = get_a(x, order=order)
        y_galerkin = np.einsum('i, ij->j', a, basis)
        plt.plot(x, y_galerkin, linestyle='--', lw=3, label='Galerkin order=%d' % order)

    # FDM
    x = np.linspace(0, x_end, 1000)
    plt.plot(x, FDM(x), lw=5, label='FDM', alpha=0.5)

    # FEM
    for num_ele in [5, 20]:
        x, u = FEM(num_ele=num_ele)
        plt.plot(x, u, lw=8, label='FEM %d' % num_ele, alpha=0.5)

    plt.legend()
    plt.tight_layout()
    plt.savefig('./img/comparison_solution.png', dpi=200)
    return


if __name__ == '__main__':
    main()
