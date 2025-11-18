import math
from collections.abc import Sequence

import torch

from .matrix import _get_random_matrix
from .rng import RNG

__all__ = [
    "random_matrix",
]

@torch.no_grad
def random_matrix(
    size: int | Sequence[int],
    dtype: torch.dtype = torch.get_default_dtype(),
    device: torch.types.Device = torch.get_default_device(),

    depth_penalty: float = 0.05,

    seed: int | None | RNG = None,
) -> torch.Tensor:
    """Generate a random structured matrix.

    Args:
        size (int | Sequence[int]):
            Size of the matrix with two or more dimensions.
            All but last two dimensions are considered batch dimensions.
            All matrices in a batch will be generated using the same tree of operations.
        dtype (torch.dtype, optional): dtype of the matrix. Defaults to torch.get_default_dtype().
        device (torch.types.Device, optional): device to generate on. Defaults to torch.get_default_device().
        depth_penalty (float, optional):
            larger values make matrices less structured but faster to generate, value must be in (0,1) range where 1 means there is only one level of nesting at most. Defaults to 0.05.
        seed (int | None | RNG, optional): random seed. Defaults to None.

    """
    rng = RNG(seed)

    if isinstance(size, int):
        size = (size, size)
    else:
        size = tuple(size)

    *b_l, h, w = size
    if len(b_l) == 0:
        b = 1
    else:
        b = math.prod(b_l)

    A = _get_random_matrix(
        b=b, h=h, w=w, parent=None, base=True, level=0, num_ops=1, branch_penalty=(1-depth_penalty),
        ops_penalty=(1-depth_penalty), dtype=dtype, device=device, rng=rng,
    )

    # scale = (1 + torch.randn((A.shape[0], 1, 1), device=A.device, dtype=A.dtype, generator=rng.torch(A.device)))
    # shift = (rng.numpy.triangular(left=-1, mode=0, right=1, size=(A.shape[0], 1, 1))**10) * 100

    # A *= scale
    # A += torch.as_tensor(shift, device=A.device, dtype=A.dtype)

    if len(b_l) == 0: return A[0]

    return A.reshape(*b_l, h, w)