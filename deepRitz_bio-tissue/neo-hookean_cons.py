import numpy as np
import torch


class neo_hookean_single:

    '''
        The model is constructed with referring to the wikipedia
        **Rivlin neo-Hookean material**

        [1] https://en.wikipedia.org/wiki/Neo-Hookean_solid
    '''
    def __init__(self,
                 # material constants:
                 E=1e6, nu = 0.2,
                 p0=1e5, ndim=3,
                 verboseFlag=False, explicitFlag=True):
        # super(neo_hookean_single, self).__init__(p0=p0, ndim=ndim, explicitFlag=explicitFlag)
        self.verboseFlag = verboseFlag

        # material constants calculation
        self.E, self.nu = E, nu
        self.lam = E* nu /(1+nu)/(1-2*nu)
        self.G = E/2./(1+nu)
        self.C1 = 0.5 * self.G
        self.D1 = 0.5*self.lam

    def solver(self, F_np):
        '''
            The energy function can be presented as:


        :input: the deformation tensor
        :return:
        '''
        F = torch.from_numpy(F_np).float()
        F.requires_grad = True
        C = F.T @ F
        B = F @ F.T
        I1 = torch.trace(C)
        J = torch.linalg.det(F)
        J_root3 = torch.pow(J, 1/3)
        C_ = C / J_root3**2
        I1_ = I1 / J_root3**2
        B_ = B / J_root3**2
        # W = self.C1 * (I1_-3.) + (self.C1/6. + self.D1/4.) * (J**2 + 1/J**2 - 2)
        W = self.C1 * (I1_-3. - 2.*torch.log(J)) + self.D1 * (J-1)**2
        # W = self.C1 * (I1_-3.) + 2.*self.D1 * (0.5 * J**2 - J + 0.5)
        # sigma = 2.*self.C1/J * self.dev(B_=B_, I1_=I1_) + 2*self.D1 * (J-1)*np.eye(3)
        dW_dF = torch.autograd.grad(W, F, create_graph=True, allow_unused=True)[0]
        sigma = dW_dF@F.T/J

        return W.item(), sigma.detach().numpy()

    def dev(self, B_, I1_):
        return B_ - I1_*torch.eye(3)/3

    def forward(self, F_arr):
        W_list, sig_list = [], []
        for F in F_arr:
            w, sig = self.solver(F)
            W_list.append(w)
            sig_list.append(sig)
        return np.array(W_list), np.array(sig_list)


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    eps_rate = 0.008
    t = 100
    time = np.arange(0, t)
    axial_strain = time*eps_rate
    F_arr = np.array([np.eye(3) for _ in range(t)])
    F_arr[:, 2, 2] += axial_strain

    model = neo_hookean_single()
    w_arr, sig_arr = model.forward(F_arr)

    # plot
    fig = plt.figure()
    ax = plt.subplot(111)
    ax.plot(axial_strain, w_arr, label = r'$E$', color='red')
    plt.legend(loc='upper left')
    ax2 = ax.twinx()
    for i in range(3):
        plt.plot(axial_strain, sig_arr[:, i, i], label = r'$\sigma_{%d%d}$' % (i+1, i+1))
    plt.legend(loc='lower right')
    plt.tight_layout()
    plt.show()
    print()




