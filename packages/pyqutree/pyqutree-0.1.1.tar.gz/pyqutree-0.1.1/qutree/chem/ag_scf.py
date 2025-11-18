import torch
from pyscf import gto



class ERI(torch.autograd.Function):
    @staticmethod
    def forward(ctx, coords, atom_charges, basis):
        coords_np = coords.detach().cpu().numpy()
        atom_charges = atom_charges.detach().cpu().numpy().astype(int)

        mol = gto.Mole()
        mol.atom = [[int(z), tuple(r)] for z, r in zip(atom_charges, coords_np)]
        mol.basis = basis
        mol.build()

        eri = mol.intor('int2e')
        d_eri = mol.intor('int2e_ip1')  # gradient of (ij|kl) w.r.t. nuclear coords

        ctx.save_for_backward(torch.tensor(d_eri))
        return torch.tensor(eri)

    # @staticmethod
    # def backward(ctx, grad_output):
    #     (d_eri,) = ctx.saved_tensors
    #     # grad_output: shape (nao, nao, nao, nao)
    #     # d_eri: shape (natm, 3, nao, nao, nao, nao)
    #     grad_coords = torch.einsum('aijkl,nijkl->na', grad_output, d_eri)
    #     return grad_coords, None, None

    @staticmethod
    def backward(ctx, grad_output):
        (d_eri,) = ctx.saved_tensors
        print(grad_output)
        print(d_eri.shape)
        
        grad_coords = torch.einsum('ijkl,najkl->an', grad_output, d_eri)
        # return None, None, None
        return grad_coords, None, None


