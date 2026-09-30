import torch
import torch.nn as nn
from typing import Tuple
import numpy as np


class IsosurfaceHelper(nn.Module):
    points_range: Tuple[float, float] = (0, 1)

    def __init__(self, resolution: int) -> None:
        super().__init__()
        self.resolution = resolution


class MarchingCubeHelper(IsosurfaceHelper):
    def __init__(self, resolution: int) -> None:
        super().__init__(resolution)
        self.resolution = resolution
        self._grid_vertices = None

    @property
    def grid_vertices(self):
        if self._grid_vertices is None:
            x, y, z = (
                torch.linspace(*self.points_range, self.resolution),
                torch.linspace(*self.points_range, self.resolution),
                torch.linspace(*self.points_range, self.resolution),
            )
            x, y, z = torch.meshgrid(x, y, z, indexing="ij")
            verts = torch.cat(
                [x.reshape(-1, 1), y.reshape(-1, 1), z.reshape(-1, 1)], dim=-1
            ).reshape(-1, 3)
            self._grid_vertices = verts
        return self._grid_vertices

    def forward(self, level: torch.FloatTensor) -> Tuple[torch.FloatTensor, torch.LongTensor]:
        level = -level.view(self.resolution, self.resolution, self.resolution)
        level_np = level.detach().cpu().numpy()

        from skimage.measure import marching_cubes as mc_sk
        try:
            verts, faces, normals, values = mc_sk(level_np, level=0.0)
        except ValueError:
            verts = np.zeros((0, 3))
            faces = np.zeros((0, 3))

        v_pos = torch.from_numpy(verts.copy()).float().to(level.device)
        t_pos_idx = torch.from_numpy(faces.copy()).long().to(level.device)

        if v_pos.shape[0] > 0:
            v_pos = v_pos / (self.resolution - 1)
            v_pos = (v_pos - 0.5) * 2.0

        return v_pos, t_pos_idx