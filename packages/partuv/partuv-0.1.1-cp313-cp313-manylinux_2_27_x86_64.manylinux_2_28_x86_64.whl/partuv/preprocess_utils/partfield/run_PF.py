# load_checkpoint.py
import torch

import os
import torch
import numpy as np
import trimesh
from sklearn.decomposition import PCA

from .partfield.config import default_argument_parser, setup
from .partfield.model_trainer_pvcnn import Model  # Replace with the actual import path of your Model class
from .AgglomerativeClustering import solve_clustering_mesh, get_tree_leaves, solve_clustering_mesh_pf20
# import line_profiler
import time
from safetensors.torch import save_file, load_file
from pathlib import Path
from typing import Optional, Union
from importlib.resources import files, as_file


def _pkg_file(rel: str) -> Path:
    pkg = __package__  # e.g., 'partuv.preprocess_utils.partfield'
    res = files(pkg).joinpath(rel)
    # Materialize to a real path (temp when zipped wheels/pyz are used)
    return as_file(res).__enter__()  # caller must ensure it's used promptly

class PFInferenceModel:
    def __init__(self, 
                 cfg_path=None, 
                 checkpoint_path="model.safetensors", 
                 device=None):
        parser = default_argument_parser()
        args = parser.parse_args([])
        
        if cfg_path is None:
            cfg_path = _pkg_file("config/partfield.yaml")
        
        args.config_file = cfg_path
        cfg = setup(args)
        self.cfg = cfg

        import time
        if device is None:
            device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.device = device
        # self.model : Model = Model.load_from_checkpoint(
        #     checkpoint_path=checkpoint_path,
        #     cfg=cfg,
        #     map_location=device
        # )

        
        self.model = Model(cfg, device=device)                    # keep __init__ lightweight
        start_time = time.time()
        # ckpt = torch.load(checkpoint_path, map_location=device)
        # state = ckpt.get('state_dict', ckpt)       # works for both PL and pure state_dict
        # self.model.load_state_dict(state, strict=True)


        # save_file(self.model.state_dict(), "model.safetensors")
        
        self.model.load_state_dict(load_file(checkpoint_path))
        
        self.model.to(self.device)
        self.model.eval()
        end_time = time.time()
        print(f"Time to load model: {end_time - start_time:.4f} seconds")
        
        
        
    def postprocess_features(self, point_feat):
        data_scaled = point_feat / np.linalg.norm(point_feat, axis=-1, keepdims=True)
        pca = PCA(n_components=3)
        data_reduced = pca.fit_transform(data_scaled)*-1
        data_reduced = (data_reduced - data_reduced.min()) / (data_reduced.max() - data_reduced.min())
        colors_255 = (data_reduced * 255).astype(np.uint8)
        colors_255 = colors_255[:, [0,1,2]]  # Swap R and B channels
        return colors_255
    
    def postprocess_features_umap(self, point_feat):
        # Normalize the features
        data_scaled = point_feat / np.linalg.norm(point_feat, axis=-1, keepdims=True)
        
        # Perform UMAP to reduce to 3D
        reducer = umap.UMAP(n_components=3, random_state=42)
        data_reduced = reducer.fit_transform(data_scaled)
        
        # Scale to [0,1]
        data_reduced = (data_reduced - data_reduced.min()) / (data_reduced.max() - data_reduced.min())
        
        # Convert to 0–255 (uint8)
        colors_255 = (data_reduced * 255).astype(np.uint8)
        return colors_255
    def generate_colored_mesh(self, obj_path, colors_255, output_path):
        if type(obj_path) == str:
            mesh = trimesh.load(obj_path, force='mesh')
        else:
            mesh = obj_path
        print(colors_255.shape)
        print(mesh.vertices.shape)
        colored_mesh = trimesh.Trimesh(vertices=mesh.vertices, faces=mesh.faces, face_colors=colors_255)
        colored_mesh.export(output_path)

    def process(self, obj_path, output_path,max_cluster=20, udf_mesh=False, save_features = False, save_segmentation = True):
        point_feat, mesh, num_bridge_face  = self.model.run_inference(obj_path, return_udf_mesh=udf_mesh, combine_components=True)
        if save_features:
            colors_255 = self.postprocess_features(point_feat)
            self.generate_colored_mesh(mesh, colors_255, os.path.join(output_path, f'feat_pca_{os.path.basename(obj_path)}'))

        # if save_segmentation:
        tree, root =  solve_clustering_mesh(mesh, point_feat, output_path, max_cluster=max_cluster, return_color_mesh=save_segmentation,)
        return tree,root,mesh

    #@line_profiler.profile
    def process_face(self, obj_path, output_path,max_cluster=20, udf_mesh=False, save_features = False, save_segmentation = False, seed = 42, sample_on_faces=10, sample_batch_size=100_000, pca_dim=None, device="cuda"):
        if output_path is not None:
            os.makedirs(output_path, exist_ok=True)
        else:
            save_features = False
            save_segmentation = False
            
        time1 = time.time()
        print(f"Device: {device}")
        point_feat, mesh, num_bridge_face = self.model.run_inference(obj_path, return_udf_mesh=udf_mesh, sample_batch_size=sample_batch_size, sample_on_faces=sample_on_faces, seed=seed, device=device)
        time2 = time.time()
        print(f"Time for inference: {time2-time1}")
        if save_features:
            colors_255 = self.postprocess_features(point_feat.cpu().numpy())
            self.generate_colored_mesh(obj_path, colors_255, os.path.join(output_path, f'feat_pca_{os.path.basename(obj_path).split(".")[0]}.ply'))
        if num_bridge_face > 0:
            print(f"Bridge faces: {num_bridge_face}")
        # num_bridge_face = 0
        # if save_segmentation:
        tree, root =  solve_clustering_mesh(mesh, point_feat, output_path,num_bridge_faces=num_bridge_face, max_cluster=max_cluster, return_color_mesh=save_segmentation,sample_on_faces=True, pca_dim=pca_dim)
        time3 = time.time()
        print(f"Time for clustering: {time3-time2}")
        if num_bridge_face > 0:
            mesh.faces = mesh.faces[:-num_bridge_face]
        return tree,root,mesh
    
   

    def run_clustering(self, point_feat, mesh, output_path, max_cluster=10):
        
        tree, root = solve_clustering_mesh(mesh, point_feat, output_path, max_cluster=max_cluster)
        print(get_tree_leaves(tree, root))
            
            
    def visualize(self, obj_path, output_path):
        point_feat, mesh = self.model.run_inference(obj_path, return_udf_mesh=False, combine_components=True)
        colors_255 = self.postprocess_features(point_feat)
        self.generate_colored_mesh(obj_path, colors_255, output_path)
        
        
if __name__ == "__main__":
    model = PFInferenceModel(cfg_path="/ariesdv0/zhaoning/workspace/partuv/preprocess_utils/partfield/config/partfield.yaml")
    
    # mesh_path = "/ariesdv0/zhaoning/workspace/IUV/IUV/meshes/samesh_output/bear_1_sub.obj"
    mesh_path = "/ariesdv0/zhaoning/workspace/IUV/lscm/libigl-example-project/meshes/test_meshes/new_hard/2067f161fa4443e3b4453201c0d73d3d.obj"
    mesh_path = "/ariesdv0/zhaoning/workspace/IUV/IUV/PF_main/pl-mesh/00790c705e4c4a1fbc0af9bf5c9e9525.glb"
    mesh_path = "/ariesdv0/zhaoning/workspace/IUV/IUV/mesh_processing/output_meshes/random_obj_aa_udf/output/000a82b4e6bf4e909fbe5a3b0e6d67dc/000a82b4e6bf4e909fbe5a3b0e6d67dc_parts/000a82b4e6bf4e909fbe5a3b0e6d67dc_part_0.obj"
    
    mesh_path="/ariesdv0/zhaoning/workspace/IUV/IUV/mesh_processing/obja_meshes/random_obj_aa_out/output/000a82b4e6bf4e909fbe5a3b0e6d67dc/000a82b4e6bf4e909fbe5a3b0e6d67dc.obj"
    # mesh_path = "/ariesdv0/zhaoning/workspace/IUV/IUV/meshes/input/mug.obj"
    # mesh_path = "/ariesdv0/zhaoning/workspace/IUV/IUV/meshes/samesh_output/moter_mid_baked_seg.obj"
    
    # mesh = trimesh.load(mesh_path)
    
    # print(f"vertices: {mesh.vertices.shape[0]}, faces: {mesh.faces.shape[0]}")
    # for i in range(2):
    #     new_vertices, new_faces = trimesh.remesh.subdivide(mesh.vprocess_faceertices, mesh.faces)
    #     mesh = trimesh.Trimesh(vertices=new_vertices, faces=new_faces)
    # print(f"vertices: {mesh.vertices.shape[0]}, faces: {mesh.faces.shape[0]}")
    
    # mesh.export(f"./run_PF_test/{os.path.basename(mesh_path)}")
    # print(f"exported to ./run_PF_test/{os.path.basename(mesh_path)}")

    # model.process(f"./run_PF_test/{os.path.basename(mesh_path)}", "./run_PF_test/", udf_mesh=False)
    # breakpoint()
    # time1 = time.time()
    # for i in range(20):
    #     model.process(f"./run_PF_test/{os.path.basename(mesh_path)}", "./run_PF_test/", udf_mesh=False)
    # print(f"Time for vertices: {time.time()-time1}")
    
    # time1 = time.time()
    # for i in range(20):
    #     model.process_face(f"./run_PF_test/{os.path.basename(mesh_path)}", "./run_PF_test/", udf_mesh=False)
    # print(f"Time for faces: {time.time()-time1}")
    # model.process_face(f"./run_PF_test/{os.path.basename(mesh_path)}", "./run_PF_test-2/", udf_mesh=False)
    
    
    
    
    
    # ---------PF20-------
    
    # mesh_path= "/ariesdv0/zhaoning/workspace/IUV/lscm/libigl-example-project/mesh_processing/output_meshes/PartObjaverse-Tiny_mesh_all4/output/226887c32c7a4a1f97de694e9bdbd10d/226887c32c7a4a1f97de694e9bdbd10d.obj"
    
    # mesh_name = os.path.basename(mesh_path)
    # time1 = time.time()
    # # tree,root,mesh = model.process_face(mesh_path, f"./clusters/{mesh_name}", udf_mesh=False,consider_normal=False,combine_components=False, save_features=True,seed=34)
    # # tree,root,mesh = model.process_face(mesh_path, f"./clusters/{mesh_name}", udf_mesh=False,consider_normal=False,combine_components=False,save_segmentation=False, save_features=False,seed=42)
    # tree,root,mesh = model.process_face_pf20(mesh_path, f"./test_pf20/", udf_mesh=False,consider_normal=False,combine_components=False,save_segmentation=False, save_features=False,seed=42)
    
    
    # print(f"Time for faces: {time.time()-time1}")
    # mesh.export(f"./run_PF_test-3/{os.path.basename(mesh_path)}")
    
    mesh_path= "/ariesdv0/zhaoning/workspace/IUV/IUV/PF_main/shiba_sameleg.obj"
    
    mesh_name = os.path.basename(mesh_path)
    time1 = time.time()
    # tree,root,mesh = model.process_face(mesh_path, f"./clusters/{mesh_name}", udf_mesh=False,consider_normal=False,combine_components=False, save_features=True,seed=34)
    # tree,root,mesh = model.process_face(mesh_path, f"./clusters/{mesh_name}", udf_mesh=False,consider_normal=False,combine_components=False,save_segmentation=False, save_features=False,seed=42)
    tree,root,mesh = model.process_face(mesh_path, f"./teaser/", udf_mesh=False,consider_normal=False,combine_components=False,save_segmentation=False, save_features=True,seed=42)
    
    
    print(f"Time for faces: {time.time()-time1}")
    os.makedirs(f"./test/", exist_ok=True)
    mesh.export(f"./test/{os.path.basename(mesh_path)}")
    
    
    # model.process(mesh_path, "./run_PF_test-2/", udf_mesh=False, save_features=True)
    
    
    # mesh_folder_path = "/ariesdv0/zhaoning/workspace/IUV/IUV/PF_main/teddy/"
    # for mesh in os.listdir(mesh_folder_path):
    #     if mesh.endswith(".glb"):
    #         os.makedirs(f"./run_PF_test/_teddy_{mesh.split('.')[0]}/", exist_ok=True)
    #         model.process(os.path.join(mesh_folder_path, mesh),f"./run_PF_test/_teddy_{mesh.split('.')[0]}/", True)
    

