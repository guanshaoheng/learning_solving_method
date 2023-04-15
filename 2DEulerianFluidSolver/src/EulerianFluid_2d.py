import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt


'''
    Reference: https://www.zhihu.com/question/20912407/answer/2295587326
'''


def P2C(rho, vx, vy, P, vol, gamma=5/3):
    mass = rho*vol
    mx = rho * vx*vol
    my = rho * vy*vol
    energy = (P / (gamma - 1) + 0.5 * rho * (vx ** 2 + vy ** 2))*vol
    return mass, mx, my, energy


def C2P(mass, mx, my, energy, vol, gamma=5/3):
    rho = mass/vol
    vx = mx / rho/vol
    vy = my / rho/vol
    P = (energy/vol - 0.5 * rho * (vx ** 2 + vy ** 2)) * (gamma - 1)
    return rho, vx, vy, P



def construct_flux(rho_r, rho_l, vx_r, vx_l, vy_r, vy_l, P_r, P_l, gamma=5/3):

    en_r = P_r / (gamma - 1) + 0.5 * rho_r * (vx_r ** 2 + vy_r ** 2)
    en_l = P_l / (gamma - 1) + 0.5 * rho_l * (vx_l ** 2 + vy_l ** 2)

    rho_m = 0.5 * (rho_r + rho_l)
    mx_m = 0.5 * (rho_r * vx_r + rho_l * vx_l)
    my_m = 0.5 * (rho_r * vy_r + rho_l * vy_l)
    en_m = 0.5 * (en_r + en_l)
    P_m = (gamma - 1) * (en_m - 0.5 * (mx_m ** 2 + my_m ** 2) / rho_m)

    flux_mass = mx_m
    flux_mom_x = mx_m ** 2 / rho_m + P_m
    flux_mom_y = mx_m * my_m / rho_m
    flux_energy = (en_m + P_m) * mx_m / rho_m

    # find the wavespeeds
    sigma_r = np.sqrt(gamma * P_r / rho_r) + np.abs(vx_r)
    sigma_l = np.sqrt(gamma * P_l / rho_l) + np.abs(vx_l)
    sigma = np.maximum(sigma_r, sigma_l)

    # add the stbilizing diffusive term
    flux_mass -= sigma * 0.5* (rho_r-rho_l)
    flux_mom_x -= sigma * 0.5 * (rho_r * vx_r - rho_l * vx_l)
    flux_mom_y -= sigma * 0.5 * (rho_r * vy_r - rho_l * vy_l)
    flux_energy -= sigma * 0.5* (en_r - en_l)

    return flux_mass, flux_mom_x, flux_mom_y, flux_energy
    
    
def grad(f, dx):
    f_dx = (np.roll(f, -1, axis=0) - np.roll(f, 1, axis=0)) / (2 * dx)
    f_dy = (np.roll(f, -1, axis=1) - np.roll(f, 1, axis=1)) / (2 * dx)
    return f_dx, f_dy


def linear_approx(f, f_dx, f_dy, dx):
    f_Xr = np.roll(f - f_dx * dx / 2, -1, axis=0)
    f_Xl = f + f_dx * dx / 2

    f_Yr = np.roll(f - f_dy * dx / 2, -1, axis=1)
    f_Yl = f + f_dy * dx / 2

    return f_Xr, f_Xl, f_Yr, f_Yl


def dQdt(Q, sol_shape, dx, vol):
    N_ = len(Q) // 4
    mass = Q[:N_].reshape(sol_shape)
    mx = Q[N_:2 * N_].reshape(sol_shape)
    my = Q[2 * N_:3 * N_].reshape(sol_shape)
    energy = Q[3 * N_:].reshape(sol_shape)
    rho, vx, vy, P = C2P(mass=mass, mx=mx, my=my, energy=energy, vol=vol)

    ### linear approximation
    rho_dx, rho_dy = grad(rho, dx)
    vx_dx, vx_dy = grad(vx, dx)
    vy_dx, vy_dy = grad(vy, dx)
    P_dx, P_dy = grad(P, dx)

    rho_Xr, rho_Xl, rho_Yr, rho_Yl = linear_approx(rho, rho_dx, rho_dy, dx)
    vx_Xr, vx_Xl, vx_Yr, vx_Yl = linear_approx(vx, vx_dx, vx_dy, dx)
    vy_Xr, vy_Xl, vy_Yr, vy_Yl = linear_approx(vy, vy_dx, vy_dy, dx)
    P_Xr, P_Xl, P_Yr, P_Yl = linear_approx(P, P_dx, P_dy, dx)
    ####

    flux_mass_X, flux_mx_X, flux_my_X, flux_energy_X = construct_flux(
        rho_Xr, rho_Xl, vx_Xr, vx_Xl, vy_Xr, vy_Xl, P_Xr, P_Xl, )
    flux_mass_Y, flux_my_Y, flux_mx_Y, flux_energy_Y = construct_flux(
        rho_Yr, rho_Yl, vy_Yr, vy_Yl, vx_Yr, vx_Yl, P_Yr, P_Yl, )

    d_mass = _dQdt(flux_mass_X, flux_mass_Y, dx)
    d_mx = _dQdt(flux_mx_X, flux_mx_Y, dx)
    d_my = _dQdt(flux_my_X, flux_my_Y, dx)
    d_energy = _dQdt(flux_energy_X, flux_energy_Y, dx)
    return np.concatenate([d_mass.ravel(), d_mx.ravel(), d_my.ravel(), d_energy.ravel()])


def _dQdt(flux_x, flux_y, dx):
    # d_q = -(flux_x - np.roll(flux_x, 1, axis=0))/dx - (flux_y - np.roll(flux_y, 1, axis=1))/dx
    d_q = -(flux_x - np.roll(flux_x, 1, axis=0))*dx - \
          (flux_y - np.roll(flux_y, 1, axis=1))*dx
    return d_q

# res = solve_ivp(dQdt, t_span=(t0, tmax), y0=Q0, t_eval=np.linspace(t0, tmax, 50))


def main():
    tmax = 1
    N = 200
    l_unit = 1.
    gamma = 5 / 3
    dx = l_unit / N
    xx_c = np.linspace(0.5 * dx, 3 * l_unit - 0.5 * dx, N * 3)
    yy = np.linspace(0.5 * dx, l_unit - 0.5 * dx, N)
    vol = dx**2
    Y, X = np.meshgrid(yy, xx_c)
    rho = 1. + np.heaviside(0.5 - Y, 0)
    plt.imshow(rho.T)
    plt.colorbar()
    plt.title(r'$\rho$')
    plt.show()
    vx = -0.5 + np.heaviside(0.5 - Y, 0)
    plt.imshow(vx.T)
    plt.colorbar()
    plt.title('vx')
    plt.show()
    vy = 0.5 * X * np.sin(4 * np.pi * X) * (np.exp(-(Y - 0.5) ** 2 * 400))
    plt.imshow(vy.T)
    plt.colorbar()
    plt.title('vy')
    plt.show()
    P = 2.5 * np.ones_like(X)
    mass, mx, my, energy = P2C(rho, vx, vy, P, vol=vol)
    Q = np.concatenate([mass.ravel(), mx.ravel(), my.ravel(), energy.ravel()])
    sol_shape = (len(xx_c), len(yy))
    courant_fac = 0.4

    t = 0.
    see_per_dt = 0.1
    seen_num = 0
    N_ = len(Q)//4
    while t < tmax:
        rho, vx, vy, P = C2P(
            mass=Q[:N_].reshape(sol_shape),
            mx=Q[N_:N_*2].reshape(sol_shape),
            my=Q[N_*2:N_*3].reshape(sol_shape),
            energy=Q[N_*3:N_*4].reshape(sol_shape), vol=vol
        )
        # get time step (CFL) = dx / max signal speed
        dt = courant_fac * np.min(dx / (np.sqrt(gamma * P / rho) + np.sqrt(vx ** 2 + vy ** 2)))
        dq = dQdt(Q, sol_shape=sol_shape, dx=dx, vol=vol)
        plot_flag = False
        if t+dt > seen_num*see_per_dt:
            dt = t+dt - seen_num*see_per_dt
            seen_num += 1
            plot_flag = True
        Q += dq*dt

        if plot_flag:
            N_ = len(Q)//4
            rho_temp = Q[:N_].reshape(len(xx_c), len(yy))/vol
            plt.imshow(rho_temp.T, cmap='bwr')
            plt.title('time=%.4f' % (t+dt))
            plt.colorbar()
            plt.tight_layout()
            plt.show()
        t+=dt


if __name__ == '__main__':
    main()
