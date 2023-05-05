import numpy as np
import matplotlib.pyplot as plt

'''
    这是用来计算圆球面积积分的公式，参考：
        [1] Eq. 7 in Rolf-Pissarczyk M et. al.,  https://doi.org/10.1016/j.cma.2020.113511
'''


def func_to_be_integrated(theta, psi, be=1.0, E_r=np.array([0., 0., 1.])):
    N = np.array([
        np.cos(theta) * np.cos(psi),
        np.cos(theta) * np.sin(psi),
        np.sin(theta)])
    v = np.exp(-2.*be*(np.dot(N, E_r))**2)*np.cos(theta)
    return v


def integration(
    num_pieces=20):
    dh = 0.5*np.pi/num_pieces
    num_psi = num_pieces*4+1
    num_theta = num_pieces+1
    theta = np.linspace(0., 0.5 * np.pi, num_theta)
    psi = np.linspace(0., 2. * np.pi, num_psi)
    sum = 0.
    for i in theta[:-1]:
        for j in psi[:-1]:
            v = func_to_be_integrated(theta=i+0.5*dh, psi=j+0.5*dh)  # NOTE: use the mid points of the square
            # v = func_to_be_integrated(theta=i, psi=j)              # NOTE: use the mid points of the square
            sum += v*dh**2

    sum *= np.sqrt(2./np.pi)
    print('Num_pieces %d integration: %.2e' % (num_pieces, sum))
    return sum


def main():
    num_pieces_list = [3, 5, 10, 20, 40, 50, 100, 200]
    sum_list = []
    for i in num_pieces_list:
        sum_list.append(integration(i))

    plt.semilogx(num_pieces_list, sum_list)
    plt.tight_layout()
    plt.show()
    return


if __name__ == '__main__':
    main()

