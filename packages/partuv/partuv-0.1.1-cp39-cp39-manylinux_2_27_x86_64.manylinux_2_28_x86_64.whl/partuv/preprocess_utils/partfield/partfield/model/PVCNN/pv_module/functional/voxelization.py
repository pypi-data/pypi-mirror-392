from torch.autograd import Function

from .backend import _backend
import torch

__all__ = ['avg_voxelize']


class AvgVoxelization(Function):
    @staticmethod
    def forward(ctx, features, coords, resolution):
        """
        :param ctx:
        :param features: Features of the point cloud, FloatTensor[B, C, N]
        :param coords: Voxelized Coordinates of each point, IntTensor[B, 3, N]
        :param resolution: Voxel resolution
        :return:
            Voxelized Features, FloatTensor[B, C, R, R, R]
        """
        features = features.contiguous().float()
        coords = coords.int().contiguous()
        b, c, _ = features.shape
        import ipdb
        ipdb.set_trace()
        out, indices, counts = _backend.avg_voxelize_forward(features, coords, resolution)
        ctx.save_for_backward(indices, counts)
        return out.view(b, c, resolution, resolution, resolution)

    @staticmethod
    def backward(ctx, grad_output):
        """
        :param ctx:
        :param grad_output: gradient of output, FloatTensor[B, C, R, R, R]
        :return:
            gradient of inputs, FloatTensor[B, C, N]
        """
        b, c = grad_output.shape[:2]
        indices, counts = ctx.saved_tensors
        grad_features = _backend.avg_voxelize_backward(grad_output.contiguous().view(b, c, -1), indices, counts)
        return grad_features, None, None


avg_voxelize = AvgVoxelization.apply


def my_voxelization(features, coords, resolution):
    import ipdb
    ipdb.set_trace()
    features = features.contiguous().float()
    coords = coords.int().contiguous()
    b, c, _ = features.shape
    result = torch.zeros(b, c, resolution * resolution * resolution, device=features.device, dtype=torch.float)
    r = resolution
    r2 = resolution * resolution
    indices = coords[:, 0] * r2 + coords[:, 1] * r + coords[:, 2]
    indices = indices.unsqueeze(dim=0)
    torch.scatter(
        input=result,
        index=indices, value=features, dim=2)
    return result.view(b, c, resolution, resolution, resolution)
