import os.path

import numpy as np
import torch

from utils.general import check_mkdir, echo
from utils.utils_torch import findDevice
from utils_particle import write_down_infor, plot_particles, overlap_check, plot_E_history, plot_f_history


def main(
        packing='dense',  # dense triangle
        device=findDevice()
):
    # load information
    save_dir_name = './img/%s_PSD_servo' % packing
    check_mkdir(save_dir_name,
                os.path.join(save_dir_name, 'laod_infor'))
    confining = 1e5

    # material constants
    youngs = 1e6
    r = 0.5  # radius of the particle (or the mean radius if graded)
    rho = 2600
    g = 9.8
    E, E_contact, E_potential = [], [], []
    fx_list, fy_list = [], []
    np.random.seed(10001)

    patience = 50

    # particle positions
    if packing == 'dense':
        X, Y = np.meshgrid(np.linspace(1, 10, 10), np.linspace(1, 5, 5))
        X += np.array([r, 0, r, 0, r]).reshape([-1, 1])
        xx = np.concatenate((X.reshape(-1, 1), Y.reshape(-1, 1)), axis=1)
    else:
        xx = []
        for i in range(3, 8):
            for j in range(i - 2, 8 - 2):
                if packing == 'stable':
                    xx.append([i + (j % 2) * r, j])
                else:
                    xx.append([i, j])
        xx = np.array(xx, dtype=float)
    rr = np.random.rand(len(xx)) * 0.5 + 0.2

    plot_particles(xx=xx, r=rr, step=0, save_dir_name=None, force_flag=False)

    # set a torch tensor to save the particles' coordinates
    left_boundary = torch.nn.Parameter(torch.ones(1), requires_grad=False)
    right_boundary = torch.nn.Parameter(torch.ones(1) * 11., requires_grad=False)
    top_boundary = torch.nn.Parameter(torch.ones(1) * 5.5, requires_grad=False)
    bottom_boundary = torch.nn.Parameter(torch.ones(1) * 0., requires_grad=True)
    x = torch.tensor(xx, device=device).float().requires_grad_()
    r = torch.tensor(rr, device=device, requires_grad=False).float()

    # optimizer
    optimizer = torch.optim.Adam([x])

    energy_lowest, trial_num = 1e32, 0
    for i in range(int(1e5) + 1):
        # ---------------------------------------
        # Energy calculation

        # calculate the contact energy
        overlap, overlap_0, overlap_1 = overlap_check(x=x, r=r)

        overlap_x_partile = torch.abs(torch.sum(overlap_0, dim=0))
        overlap_y_partile = torch.abs(torch.sum(overlap_1, dim=0))

        unbalanced_x_index = torch.where(overlap_x_partile > 100. / youngs, 1., 0.)
        unbalanced_y_index = torch.where(overlap_y_partile > 100. / youngs, 1., 0.)

        force_x = torch.sum(unbalanced_x_index * overlap_x_partile) * youngs/2.0
        force_y = torch.sum(unbalanced_y_index * overlap_y_partile) * youngs/2.0

        energy_contact = 0.5 * torch.sum(overlap ** 2 * youngs)

        # gravity potential
        energy_potential = torch.sum(x[:, 1] * torch.pi * r ** 2 * rho * g)

        energy_boundary_penalty = torch.sum(
            (torch.where(x[:, 0] - r - left_boundary[0] < 0., torch.abs(x[:, 0] - r - left_boundary[0]), 0.) +  # left
             torch.where(x[:, 0] + r - right_boundary[0] > 0., torch.abs(x[:, 0] + r - right_boundary[0]),
                         0.) +  # right
             torch.where(x[:, 1] - r - bottom_boundary[0] < 0., torch.abs(x[:, 1] - r - bottom_boundary[0]),
                         0.) +  # bottom
             torch.where(x[:, 1] + r - top_boundary[0] > 0., torch.abs(x[:, 1] + r - top_boundary[0]), 0.)  # top
             ) * torch.pi * r ** 2 * rho * g * 100.
        )

        energy = energy_contact + energy_boundary_penalty + energy_potential

        # ----------------------------------------
        # update
        optimizer.zero_grad()
        energy.backward()
        optimizer.step()

        E.append(energy.item())
        E_potential.append(energy_potential.item())
        E_contact.append(energy_contact.item())
        fx_list.append(force_x.item())
        fy_list.append(force_y.item())

        if i % 1000 == 0 and i != 0:
            x_numpy = x.cpu().detach().numpy()
            plot_particles(
                xx=x_numpy, r=rr, step=i,
                energy=energy.item(), energy_potential=energy_potential.item(), energy_contact=energy_contact.item(),
                save_dir_name=save_dir_name, force_flag=True,
                left_boundary=left_boundary[0].item(), right_boundary=right_boundary[0].item(),
                top_boundary=top_boundary[0].item(), bottom_boundary=bottom_boundary[0].item(),
                unbalanced_x_index=unbalanced_x_index.cpu().detach().numpy(),
                unbalanced_y_index=unbalanced_y_index.cpu().detach().numpy()
            )

        if i % 100 == 0:
            echo('Epoch %d Total energy: %.2e, contact energy: %.2e, potential: %.2e fx_:%.2e fy_:%.2e' %
                 (i, energy.item(), energy_contact.item(), energy_potential.item(),
                  force_x.item(), force_y.item()))
            write_down_infor(xx=x, rr=rr, save_dir_name=save_dir_name, step=i,
                             energy=energy.item(), energy_potential=energy_potential.item(),
                             energy_contact=energy_contact.item(),
                             fx=force_x.item(), fy=force_y.item())

            # check if the engergy is still decreasing
            if energy.item() < energy_lowest:
                trial_num = 0
                energy_lowest = energy.item()
            else:
                trial_num += 1
                if trial_num > patience:
                    echo('No improvement, optimization stop!')
                    break

    # plot the training history
    plot_E_history(E=E, E_contact=E_contact, E_potential=E_potential, save_dir_name=save_dir_name)
    plot_f_history(fx_list=fx_list, fy_list=fy_list, save_dir_name=save_dir_name)
    return


if __name__ == '__main__':
    main()
