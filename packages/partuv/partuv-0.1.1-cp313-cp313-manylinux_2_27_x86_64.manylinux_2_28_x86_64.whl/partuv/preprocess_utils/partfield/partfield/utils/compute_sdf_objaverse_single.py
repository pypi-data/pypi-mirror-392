import json
import argparse
import os
import math
import tempfile
import time
# import mesh2sdf
import numpy as np
import skimage
# import tetgen
import trimesh
# import vtk
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
import os
import h5py
import boto3
import pickle
import torch
import mcubes


try:
    import torchcumesh2sdf
except:
    torchcumesh2sdf = None
    print("torchcumesh2sdf not installed")
    import mesh2sdf
    
import mesh2sdf

from time import perf_counter

t = 0
def profile(block_name=""):
    global t
    if t != 0:
        print(f"{block_name}  Time: {perf_counter() - (t):.4f}s")
    t=perf_counter()


def compute_mesh2sdf(vertices: np.ndarray, faces: np.ndarray, size: int = 128,
            fix: bool = False, level: float = 0.015, return_mesh: bool = False, inf_thresh=0.13):
    
    output = mesh2sdf.compute(
        vertices, faces, size, fix=fix, level=level, return_mesh=return_mesh)
    
    if return_mesh:
        sdf, mesh = output
    else:
        sdf = output
        mesh = None
    udf =  np.abs(sdf) 
    udf[udf > inf_thresh] = 1e9
    return udf, mesh

def compute(vertices: np.ndarray, faces: np.ndarray, size: int = 128,
            fix: bool = False, level: float = 0.015, return_mesh: bool = False):
    r""" Converts a input mesh to signed distance field (SDF).

    Args:
      vertices (np.ndarray): The vertices of the input mesh, the vertices MUST be
          in range [-1, 1].
      faces (np.ndarray): The faces of the input mesh.
      size (int): The resolution of the resulting SDF.
      fix (bool): If the input mesh is not watertight, set :attr:`fix` as True.
      level (float): The value used to extract level sets when :attr:`fix` is True,
          with a default value of 0.015 (as a reference 2/128 = 0.015625). And the
          recommended default value is 2/size.
      return_mesh (bool): If True, also return the fixed mesh.
    """
    # compute sdf
    # sdf = mesh2sdf.core.compute(vertices, faces, size)
    # profile()
    R = 256
    band = 32 / R
    
    def load_and_preprocess(vertices: np.ndarray, faces: np.ndarray):
        mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)
        tris = np.array(mesh.triangles, dtype=np.float32, subok=False)
        # tris[..., [1, 2]] = tris[..., [2, 1]]
        # tris = tris - tris.min(0).min(0)
        # tris = (tris / tris.max() + band) / (1 + band * 2)
        return torch.tensor(tris, dtype=torch.float32, device='cuda:0')
    
    processed = load_and_preprocess(vertices,faces)
    udf = torchcumesh2sdf.get_udf(processed, R, band, B=1024).cpu().numpy()
    
    
    
    if not fix:
        return (udf, trimesh.Trimesh(vertices, faces)) 
    # profile("first udf")
    
    if return_mesh:
    # NOTE: the negative value is not reliable if the mesh is not watertight
    # udf = np.abs(sdf)
        vertices, faces, _, _ = skimage.measure.marching_cubes(udf, level, step_size=4)
        components = trimesh.Trimesh(vertices, faces).split(only_watertight=False)
        new_mesh = [] #trimesh.Trimesh()
        if len(components) > 100000:
            raise NotImplementedError
        for i, c in enumerate(components):
            c.fix_normals()
            new_mesh.append(c) #trimesh.util.concatenate(new_mesh, c)
        new_mesh = trimesh.util.concatenate(new_mesh)

        profile("marching cubes")

    if return_mesh:
        return udf, new_mesh  
    else:
        return udf, None

num_core_per_thread = 1
os.environ["OMP_NUM_THREADS"] = str(num_core_per_thread)
os.environ["OPENBLAS_NUM_THREADS"] = str(num_core_per_thread)
os.environ["MKL_NUM_THREADS"] = str(num_core_per_thread)
os.environ["VECLIB_MAXIMUM_THREADS"] = str(num_core_per_thread)
os.environ["NUMEXPR_NUM_THREADS"] = str(num_core_per_thread)

def save_sdf(sdf, filename):
    # save a compressed h5 file
    compression_options = {
        'compression': 'gzip',  
        'compression_opts': 9,  
    }
    sdf = sdf.astype(np.float16)
    with h5py.File(filename, 'w') as f:
        f.create_dataset('sdf', data=sdf, **compression_options)


def save_udf(udf, filename):
    # save a compressed h5 file
    compression_options = {
        'compression': 'gzip',  
        'compression_opts': 9,  
    }
    udf = udf.astype(np.float16)
    with h5py.File(filename, 'w') as f:
        f.create_dataset('udf', data=udf, **compression_options)

def process(filename, return_mesh=False, return_udf_mesh = False, sample_on_udf = True, seed=42):

    size = 256
    level = 2 / size
    # try:
    print(filename)
    time1 = time.time()
    obj_path = f'{filename}'
    uid = filename.split('/')[-1].split('.')[0]
    mesh = trimesh.load(obj_path, force='mesh', process=False)

    # normalize mesh
    mesh_scale = 0.9
    vertices = mesh.vertices
    bbmin = vertices.min(0)
    bbmax = vertices.max(0)
    center = (bbmin + bbmax) * 0.5

    scale = mesh_scale / (bbmax - bbmin).max()
    vertices = (vertices - center) * scale + 0.5

    sample_on_udf |= return_udf_mesh
    
    # return_mesh = True
    # _, cu_udf_mesh = compute(vertices, mesh.faces, size, fix=True, level=level, return_mesh=True and sample_on_udf)
    # cu_udf_mesh.export('cu_udf_mesh.obj')
    # _, udf_mesh = compute_mesh2sdf(vertices, mesh.faces, size, fix=True, level=level, return_mesh=return_mesh and sample_on_udf)
    # udf_mesh.export('udf_mesh.obj')
    
    
    # breakpoint()
    
    if torchcumesh2sdf is not None and torch.cuda.is_available():
        udf, udf_mesh = compute(vertices, mesh.faces, size, fix=True, level=level, return_mesh=return_mesh and sample_on_udf)
    else:
        udf, udf_mesh = compute_mesh2sdf(vertices, mesh.faces, size, fix=True, level=level, return_mesh=return_mesh and sample_on_udf)
        
    # time1 = time.time()
    # udf2, udf_mesh2 = compute_mesh2sdf(vertices, mesh.faces, size, fix=False, level=level, return_mesh=return_mesh and sample_on_udf)
    # time2 = time.time()
    # print(f"Time for compute_mesh2sdf: {time2-time1}, num_vertices: { vertices.shape[0]}, num_faces: {mesh.faces.shape[0]}")
    
        
    if return_udf_mesh:
        mesh = udf_mesh
    if sample_on_udf:
        # save_udf(udf, f"{uid}_udf.h5")
        udf_mesh.vertices = udf_mesh.vertices * (2.0 / 256) - 1.0
        pc, _ = trimesh.sample.sample_surface(udf_mesh, 100000, seed=0)
    else:
        vertices = mesh.vertices
        bbmin = vertices.min(0)
        bbmax = vertices.max(0)
        center = (bbmin + bbmax) * 0.5
        

        scale = 0.9 / (bbmax - bbmin).max()
        mesh.vertices = (vertices - center) * scale * 2
        pc, _ = trimesh.sample.sample_surface(mesh, 100000, seed=seed)

    return udf, mesh, pc

def gen_sdf_mask( sdf_clip_val, sdf, total_cells=1000000, ratio=0.8):

    mask = np.zeros_like(sdf, dtype=bool)
    abs_sdf_mask = np.abs(sdf) < sdf_clip_val
    cells_from_abs_sdf = min(int(ratio * total_cells), abs_sdf_mask.sum())
    cells_uniform = total_cells - cells_from_abs_sdf
    abs_sdf_indices = np.array(np.where(abs_sdf_mask)).T
    selected_abs_sdf_indices = abs_sdf_indices[np.random.choice(abs_sdf_indices.shape[0], cells_from_abs_sdf, replace=False)]
    mask[tuple(selected_abs_sdf_indices.T)] = True
    flat_mask = mask.flatten()
    all_indices = np.arange(sdf.size)
    remaining_indices = all_indices[~flat_mask]
    selected_uniform_indices = np.random.choice(remaining_indices, cells_uniform, replace=False)
    mask[np.unravel_index(selected_uniform_indices, sdf.shape)] = True
    return mask

        
if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument('--obj_path', type=str, default="/zhaoning-vol/workspace/partfield-main/check_obja/kshared/glb/3dd0f09d-35b7-5021-a2bc-caf3d28f5e89.glb")
    args = args.parse_args()
    
    if "tmp/" not in os.listdir():
        os.makedirs("tmp/", exist_ok=True)
    
    process(args.obj_path)