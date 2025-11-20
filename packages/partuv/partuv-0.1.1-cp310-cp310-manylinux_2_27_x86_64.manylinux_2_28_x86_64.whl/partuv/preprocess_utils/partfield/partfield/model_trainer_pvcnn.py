import torch
# suppress subnormal warnings
if hasattr(torch, "set_flush_denormal"):
    torch.set_flush_denormal(False)
import lightning.pytorch as pl
from torch.optim import Adam
from torch.optim.lr_scheduler import CosineAnnealingLR
# from .dataloader_2 import MixDataset
from torch.utils.data import DataLoader
import torch.nn.functional as F
import torch.nn as nn
import os
import trimesh
import skimage
import numpy as np
import h5py
import torch.distributed as dist
from .model.UNet.model import ResidualUNet3D
from .model.triplane import TriplaneTransformer, get_grid_coord #, sample_from_planes, Voxel2Triplane
from .model.model_utils import VanillaMLP
from .model.PVCNN.encoder_pc import TriPlanePC2Encoder, sample_triplane_feat
from .utils.compute_sdf_objaverse_single import process as process_udf

from time import sleep
from tqdm import tqdm
# import line_profiler


def merge_mesh_components(mesh, bridge_closest=True):
    
    components = mesh.split(only_watertight=False)
    base_mesh = components[0]
    
    if len(components) == 1:
        return mesh,0
    
    
    # Find closest points between components and connect them
    bridge_faces = []
    for next_mesh in tqdm(components[1:]):
        if bridge_closest:
            edges1 = base_mesh.edges_unique
            edges2 = next_mesh.edges_unique

            # Compute the midpoints for each edge in mesh1 and mesh2
            midpoints1 = np.array([base_mesh.vertices[edge].mean(axis=0) for edge in edges1])
            midpoints2 = np.array([next_mesh.vertices[edge].mean(axis=0) for edge in edges2])


            dists = np.linalg.norm(midpoints1[:, np.newaxis, :] - midpoints2[np.newaxis, :, :], axis=-1)

            # Find the indices (i, j) of the smallest distance
            i, j = np.unravel_index(np.argmin(dists), dists.shape)
            base_edge_indices = edges1[i]
            next_edge_indices = edges2[j]
            
            next_edge_indices = next_edge_indices + len(base_mesh.vertices)
            
            # Add connecting triangle
            next_faces = next_mesh.faces + len(base_mesh.vertices)
            bridge_face = np.array([[base_edge_indices[0], 
                                next_edge_indices[0], 
                                next_edge_indices[1]],
                                    [
                                    base_edge_indices[0],
                                    next_edge_indices[1],
                                    base_edge_indices[1]],
                                    ])
        else:
            base_vertex_idx = base_mesh.faces[0][0]
            next_vertex_idx = base_mesh.faces[0][1]
            
            
            # Combine vertices and faces
            next_faces = next_mesh.faces + len(base_mesh.vertices)

            
            # Add connecting triangle
            bridge_face = np.array([[base_vertex_idx, 
                                next_faces[0][0], 
                                next_faces[0][1]],
                                    [
                                    base_vertex_idx,
                                    next_faces[0][1],
                                    next_vertex_idx],
                                    ])
        # Combine vertices and faces
        new_vertices = np.vstack((base_mesh.vertices, next_mesh.vertices))
        new_faces = np.vstack((base_mesh.faces, next_faces))
        
        # new_faces = np.vstack((new_faces, bridge_face))
        bridge_faces.append(bridge_face)
        
        base_mesh = trimesh.Trimesh(vertices=new_vertices, faces=new_faces, process=False)
    
    assert(max(np.max(arr) for arr in bridge_faces) <= new_vertices.shape[0])
    base_mesh = trimesh.Trimesh(vertices=new_vertices, faces= np.vstack((new_faces, np.concatenate(bridge_faces))), process=False)
    return base_mesh, (len(components)-1) *2

# ---------- 1. helper: sample with full coverage --------------------
def sample_surface_cover(mesh: trimesh.Trimesh,
                         n_points: int,
                         seed: int | None = None):
    """
    Uniformly sample `n_points` over `mesh`, guaranteeing ≥1 point on *every* face.
    Returns (points, face_ids) parallel NumPy arrays.
    """
    F = len(mesh.faces)
    if n_points < F:
        n_points = F
    rng = np.random.default_rng(seed)

    # one barycentric sample per face  -------------------------------
    tri = mesh.triangles                                 # (F,3,3)
    r1, r2 = rng.random((2, F, 1))
    s      = np.sqrt(r1)
    w0, w1, w2 = 1 - s, s*(1 - r2), s*r2
    pts_1 = (tri[:, 0]*w0 + tri[:, 1]*w1 + tri[:, 2]*w2)
    ids_1 = np.arange(F, dtype=np.int64)

    # top-up to n_points via Trimesh’s fast area sampler ------------
    extra = n_points - F
    if extra:
        pts_2, ids_2 = trimesh.sample.sample_surface(mesh, extra)
        points = np.vstack((pts_1, pts_2))
        face_i = np.concatenate((ids_1, ids_2))
    else:
        points, face_i = pts_1, ids_1

    return points.astype(np.float32, copy=False), face_i
# mesh, num_bridge_face = merge_mesh_components(mesh)
# # after clustering:
# mesh.faces = mesh.faces[:-num_bridge_face]



# def sample_points_from_faces(vertices, faces, samples_per_face=10):
#     """
#     Sample random points from each face of a trimesh.
    
#     Parameters:
#     vertices: np.array of shape (num_vertices, 3)
#         The vertex coordinates of the mesh
#     faces: np.array of shape (num_faces, 3)
#         The face indices of the mesh
#     samples_per_face: int
#         Number of points to sample per face
        
#     Returns:
#     np.array of shape (num_faces, samples_per_face, 3)
#         Random points sampled from each face
#     """
#     num_faces = len(faces)
    
#     # Generate random barycentric coordinates
#     r1 = np.random.random((num_faces, samples_per_face, 1))
#     r2 = np.random.random((num_faces, samples_per_face, 1))
    
#     # Convert to barycentric coordinates
#     sqrt_r1 = np.sqrt(r1)
#     barycentric = np.concatenate([
#         1 - sqrt_r1,
#         sqrt_r1 * (1 - r2),
#         sqrt_r1 * r2
#     ], axis=2)
    
#     # Get vertices for each face
#     face_vertices = vertices[faces]  # Shape: (num_faces, 3, 3)
    
#     # Compute random points using barycentric coordinates
#     points = np.einsum('fik,fij->fjk', barycentric, face_vertices)
    
#     return points
def sample_points_on_mesh(vertices, faces, num_samples_per_face=10, seed=42):
    """
    Sample points uniformly from each face of a triangular mesh.

    Parameters:
    - vertices: np.ndarray of shape (num_vertices, 3)
        Array of vertex coordinates.
    - faces: np.ndarray of shape (num_faces, 3)
        Array of indices into the vertices array, defining each triangular face.
    - num_samples_per_face: int
        Number of points to sample per face.

    Returns:
    - samples: np.ndarray of shape (num_faces, num_samples_per_face, 3)
        Array of sampled points for each face.
    """
    num_faces = faces.shape[0]

    # Get vertex positions for each face
    v0 = vertices[faces[:, 0]]  # (num_faces x 3)
    v1 = vertices[faces[:, 1]]
    v2 = vertices[faces[:, 2]]

    # Expand dimensions for broadcasting
    v0 = v0[:, np.newaxis, :]  # (num_faces x 1 x 3)
    v1 = v1[:, np.newaxis, :]
    v2 = v2[:, np.newaxis, :]

    # Generate random barycentric coordinates
    np.random.seed(seed)
    u1 = np.random.rand(num_faces, num_samples_per_face)
    u2 = np.random.rand(num_faces, num_samples_per_face)

    sqrt_u1 = np.sqrt(u1)
    a = 1 - sqrt_u1
    b = sqrt_u1 * (1 - u2)
    c = sqrt_u1 * u2

    # Expand dimensions
    a = a[:, :, np.newaxis]  # (num_faces x num_samples_per_face x 1)
    b = b[:, :, np.newaxis]
    c = c[:, :, np.newaxis]

    # Compute sampled points
    samples = a * v0 + b * v1 + c * v2  # (num_faces x num_samples_per_face x 3)

    return samples


def sample_points_on_mesh_cuda(
        vertices: torch.Tensor,      # (V,3) float32/float16  – already on GPU
        faces:    torch.Tensor,      # (F,3) int64            – already on GPU
        k:        int,               # samples / face
        generator: torch.Generator   # for reproducibility
) -> torch.Tensor:
    """
    Return (F, k, 3) points sampled uniformly on each triangular face.
    """
    # Gather vertex triplets for every face: (F,3,3)
    v0 = vertices[faces[:, 0]]          # (F,3)
    v1 = vertices[faces[:, 1]]
    v2 = vertices[faces[:, 2]]

    # GPU uniform barycentric coordinates
    u1 = torch.rand((faces.shape[0], k), device=vertices.device, generator=generator)
    u2 = torch.rand(u1.shape, dtype=u1.dtype, device=u1.device, generator=generator)

    sqrt_u1 = u1.sqrt()                 # √u₁
    a = 1.0 - sqrt_u1                   # (F,k)
    b = sqrt_u1 * (1.0 - u2)
    c = sqrt_u1 * u2

    # Broadcast and mix the three corners → (F,k,3)
    samples = (
        a[..., None] * v0[:, None, :] +
        b[..., None] * v1[:, None, :] +
        c[..., None] * v2[:, None, :]
    ).to(torch.float16)                # keep everything FP16 to match triplane net
    return samples

class Model(pl.LightningModule):
    def __init__(self, cfg, device="cuda"):
        super().__init__()
        self.save_hyperparameters()
        self.cfg = cfg
        self.automatic_optimization = False
        self.triplane_resolution = cfg.triplane_resolution
        self.triplane_channels_low = cfg.triplane_channels_low
        self.in_channels = 2
        
        self.sdf_encoder = ResidualUNet3D(self.in_channels, self.triplane_channels_low, 
                                          f_maps=(8, 128, 256, 512, 1024), encoder_only=False) 
        self.triplane_transformer = TriplaneTransformer(
            input_dim=cfg.triplane_channels_low * 2,
            transformer_dim=1024,
            transformer_layers=6,
            transformer_heads=8,
            triplane_low_res=32,
            triplane_high_res=128,
            triplane_dim=cfg.triplane_channels_high,
        )
        self.sdf_decoder = VanillaMLP(input_dim=64,
                                      output_dim=1, 
                                      out_activation="tanh", 
                                      n_neurons=64, #64
                                      n_hidden_layers=6) #6
        self.use_pvcnn = cfg.use_pvcnn
        self.use_2d_feat = cfg.use_2d_feat
        if self.use_pvcnn:
            self.pvcnn = TriPlanePC2Encoder(
                cfg.pvcnn,
                device=device,
                shape_min=-1, 
                shape_length=2,
                use_2d_feat=self.use_2d_feat) #.cuda()
        self.logit_scale = nn.Parameter(torch.tensor([1.0], requires_grad=True))
        self.grid_coord = get_grid_coord(256)
        self.mse_loss = torch.nn.MSELoss()
        self.l1_loss = torch.nn.L1Loss(reduction='none')

    def configure_optimizers(self):
        params = [{'params': self.sdf_encoder.parameters(), 'lr': self.cfg.lr},
                  {'params': self.sdf_decoder.parameters(), 'lr': self.cfg.lr * 10},
                  {'params': self.logit_scale, 'lr': self.cfg.lr * 100},]
        if self.use_pvcnn:
            params += [{'params': self.pvcnn.parameters(), 'lr': self.cfg.lr},
                       {'params': self.triplane_transformer.parameters(), 'lr': self.cfg.lr}]

        optimizer = Adam(params)
        lr_scheduler = CosineAnnealingLR(optimizer, 10000, eta_min=0)
        return [optimizer], [lr_scheduler]
    
    def train_dataloader(self):
        if self.cfg.dataset.type == "LVIS":
            dataset = LVISDataset(self.cfg, is_train=True)
        elif self.cfg.dataset.type == "PartNet":
            dataset = PartNetDataset(self.cfg, is_train=True)
        elif self.cfg.dataset.type == "Mix":
            dataset = MixDataset(self.cfg, use_2d_feat=self.use_2d_feat, is_train=True)
        dataloader = DataLoader(dataset, 
                                num_workers=self.cfg.dataset.train_num_workers,
                                batch_size=self.cfg.dataset.train_batch_size,
                                shuffle=True, 
                                pin_memory=True,
                                drop_last=False)
        return  dataloader
        
    def calc_sdf_loss(self, sdf, mask, planes, channel=1):
        N = planes.shape[0]
        mask = mask.reshape(N, -1)
        coord = self.grid_coord.unsqueeze(0).repeat(N, 1, 1).cuda()[mask].reshape(N, -1, 3) # N, M, 3
        coord_feat = sample_triplane_feat(planes, coord) # N, M, C
        sdf_pred = self.sdf_decoder(coord_feat) # N, M, 1
        sdf_target = sdf.reshape(N, -1, channel)[mask].reshape(N, -1, channel) #[:, mask, :] # N, M, 1
        sdf_loss = self.mse_loss(sdf_pred, sdf_target).mean()
        return sdf_loss

    def calc_triplet_loss1(self, planes, PA, PB, PC):
        N, M, _ = PA.shape
        coord = torch.cat((PA, PB, PC), 1) # N, 3M, 3

        point_feat = sample_triplane_feat(planes, coord) # N, 3M, C
        l1_reg = self.l1_loss(point_feat, torch.zeros_like(point_feat)).mean()

        featA, featB, featC = torch.split(point_feat, M, dim=1)
        
        cosAB = torch.exp(F.cosine_similarity(featA, featB, dim=2) * self.logit_scale)
        cosAC = torch.exp(F.cosine_similarity(featA, featC, dim=2) * self.logit_scale)
        cosBC = torch.exp(F.cosine_similarity(featB, featC, dim=2) * self.logit_scale)

        triplet_loss = -(torch.log(cosAB / (cosAB + cosAC)) + torch.log(cosAB / (cosAB + cosBC))) / 2

        triplet_acc = torch.logical_and(cosAB > cosAC, cosAB > cosBC)
        return triplet_loss.mean(), triplet_acc.float().mean(dim=-1), l1_reg

    def inference(self, batch, save_pred_sdf_to_mesh=False, save_feat_pca=True):
        save_dir = f"test_results/{self.cfg.name}"
        uid = batch['uid'][0]
        view_id = batch['view_id'][0]

        # sdf = batch['sdf']
        udf = batch['sdf'] # 1x2x 256^3
        
        N = udf.shape[0]
        assert N == 1

        sdf_feat = self.sdf_encoder(udf)
        if self.use_2d_feat: 
            pc_feat = self.pvcnn(batch['pc'], batch['pc'], batch['mv_feat'], batch['pc2pc_idx'])
        else:
            pc_feat = self.pvcnn(batch['pc'], batch['pc'])
            
        planes = self.merge_sdf_pc_2_planes(sdf_feat, pc_feat)
        planes = self.triplane_transformer(planes)
        sdf_planes, part_planes = torch.split(planes, [64, planes.shape[2] - 64], dim=2)

                
        torch.cuda.empty_cache()
        # sleep(1)
        if save_pred_sdf_to_mesh:   
            coord = self.grid_coord.unsqueeze(0).repeat(N, 1, 1).cuda() # N, M, 3
            coord_feat = sample_triplane_feat(sdf_planes, coord) # N, M, C
            sdf_pred = self.sdf_decoder(coord_feat) # N, M, 1

            sdf_pred_ = sdf_pred.clone().cpu().detach().numpy().reshape(256, 256, 256)
            t = 256*256*256

            vertices, faces, _, _ = skimage.measure.marching_cubes(sdf_pred_, 0.025)
            mesh = trimesh.Trimesh(vertices, faces)
            mesh.vertices = mesh.vertices * (2.0 / 256) - 1.0
            os.makedirs(save_dir, exist_ok=True)
            mesh.export(f'{save_dir}/pred_sdf_{uid}_{view_id}.obj')
            print(f'{save_dir}/pred_sdf_{uid}_{view_id}.obj')
            
        vertices, faces, _, _ = skimage.measure.marching_cubes(udf.cpu().numpy()[:,0].reshape(256, 256, 256)  , 0.05)
        # vertices, faces, _, _ = skimage.measure.marching_cubes(sdf.cpu().numpy().reshape(256, 256, 256), 0)
        mesh = trimesh.Trimesh(vertices, faces)

        mesh = max(mesh.split(only_watertight=False), key=lambda m: len(m.vertices))
        
        mesh.vertices = mesh.vertices * (2.0 / 256) - 1.0
        mesh.export(f'{save_dir}/gt_sdf_{uid}_{view_id}.obj')
        print(f'{save_dir}/gt_sdf_{uid}_{view_id}.obj')
        
        tensor_vertices = torch.from_numpy(mesh.vertices.copy()).reshape(1, -1, 3).cuda().to(torch.float16)
        point_feat = sample_triplane_feat(part_planes, tensor_vertices) # N, M, C
        point_feat = point_feat.cpu().detach().numpy().reshape(-1, 448)

        np.save(f'{save_dir}/part_feat_{uid}_{view_id}.npy', point_feat)
        
        if save_feat_pca:
            from sklearn.decomposition import PCA
            data_scaled = point_feat / np.linalg.norm(point_feat, axis=-1, keepdims=True)

            pca = PCA(n_components=3)

            data_reduced = pca.fit_transform(data_scaled)
            data_reduced = (data_reduced - data_reduced.min()) / (data_reduced.max() - data_reduced.min())
            colors_255 = (data_reduced * 255).astype(np.uint8)

            colored_mesh = trimesh.Trimesh(vertices=mesh.vertices, faces=mesh.faces, vertex_colors=colors_255)
            colored_mesh.export(f'{save_dir}/feat_pca_{uid}_{view_id}.ply')
        
        torch.cuda.empty_cache()
        # sleep(1)
    
    # #@line_profiler.profile
    @torch.no_grad()
    def run_inference(self, filename, device="cuda", return_udf_mesh=False, sample_batch_size= 100_000, sample_on_faces=False, seed=42,):

        udf, mesh, pc = process_udf(filename, return_mesh=True, return_udf_mesh=return_udf_mesh, sample_on_udf=False, seed=seed)
        udf = torch.tensor(udf, dtype=torch.float32, device=device)
        
        udf = torch.clamp(udf, min=-0.05, max=0.05) / 0.05


        
        pc = torch.tensor(pc, dtype=torch.float32, device=device)
        
        occupancy = (udf < 0.25).float()
        udf = torch.stack((udf,occupancy))

        udf.unsqueeze_(0)
        pc.unsqueeze_(0)
        
        N = udf.shape[0]
        assert N == 1

        sdf_feat = self.sdf_encoder(udf)

        pc_feat = self.pvcnn(pc, pc)
            
        planes = self.merge_sdf_pc_2_planes(sdf_feat, pc_feat)
        planes = self.triplane_transformer(planes)
        sdf_planes, part_planes = torch.split(planes, [64, planes.shape[2] - 64], dim=2)


        # TODO: find a better approach than just keep the largest component?
        # mesh = max(mesh.split(only_watertight=False), key=lambda m: len(m.vertices))

        # if return_udf_mesh:
        #     mesh = max(mesh.split(only_watertight=False), key=lambda m: len(m.vertices))
        #     num_bridge_face = 0
        # else:
        num_bridge_face = 0
            # print("Merging components")
            # mesh,num_bridge_face = merge_mesh_components(mesh)
            # print("Merged components complete")


        if sample_on_faces:
            batch_size =  sample_batch_size
            device      = device
            dtype       = torch.float16            # matches part_planes / triplane weights

            # One-time host→device copies (cost amortised over all batches)
            verts_t = torch.as_tensor(mesh.vertices, device=device, dtype=dtype)
            faces_t = torch.as_tensor(mesh.faces,    device=device, dtype=torch.long)
            planes_t = part_planes.to(device=device, dtype=dtype)

            # Optional: reproducible RNG
            g = torch.Generator(device).manual_seed(seed)

            all_face_feats = []                    # will stay on GPU until the very end

            for start in range(0, faces_t.shape[0], batch_size):
                end = min(start + batch_size, faces_t.shape[0])
                f_slice = faces_t[start:end]                       # (B,3)

                # (B, k, 3) → (1, B·k, 3) for the triplane network
                pts = sample_points_on_mesh_cuda(verts_t, f_slice, sample_on_faces, g)
                pts_flat = pts.reshape(1, -1, 3)

                # (1, B·k, C)   -- keeps FP16, stays on the same GPU
                # pts_flat = pts_flat.to(torch.float32)
                feats = sample_triplane_feat(planes_t, pts_flat)

                # Store on-GPU (or immediately move to CPU if RAM permits)
                all_face_feats.append((feats.view(-1, sample_on_faces, 448)).mean(dim=1))

            # Concatenate once at the end; choose where you need the result:
            all_sampled_points = torch.cat(all_face_feats, dim=0)        # GPU tensor
            face_feat = all_sampled_points

            return face_feat, mesh, num_bridge_face
        else:
            tensor_vertices = torch.from_numpy(mesh.vertices.copy()).reshape(1, -1, 3).cuda().to(torch.float16)
            point_feat = sample_triplane_feat(part_planes.to(torch.float16), tensor_vertices.to(torch.float16)) # N, M, C
            point_feat = point_feat.cpu().detach().numpy().reshape(-1, 448)
            return point_feat, mesh, num_bridge_face
        
    
    
    
    def training_step(self, batch, batch_idx):
        if self.cfg.test:
            self.inference(batch, self.cfg.inference_save_pred_sdf_to_mesh, self.cfg.inference_save_feat_pca)
            return 
        sdf = batch['sdf']
        N = sdf.shape[0]
        sdf_feat = self.sdf_encoder(sdf) 
        if self.use_2d_feat: 
            pc_feat = self.pvcnn(batch['pc'], batch['pc'], batch['mv_feat'], batch['pc2pc_idx'])
        else:
            pc_feat = self.pvcnn(batch['pc'], batch['pc'])
        planes = self.merge_sdf_pc_2_planes(sdf_feat, pc_feat)
        planes = self.triplane_transformer(planes)
        sdf_planes, part_planes = torch.split(planes, [64, planes.shape[2] - 64], dim=2)

        #self.save_planes(pc_feat, planes-pc_feat, batch_idx, batch['uid'], sdf)
                
        sdf_loss = self.calc_sdf_loss(sdf[:,:1], batch['sdf_mask'], sdf_planes)#, self.in_channels) 
        triplet_loss, triplet_acc, l1_reg = self.calc_triplet_loss1(part_planes, batch['PA'], batch['PB'], batch['PC'])

        loss = sdf_loss * self.cfg.loss.sdf + triplet_loss * self.cfg.loss.triplet + l1_reg * self.cfg.loss.l1

        acc_gathered = [torch.zeros_like(triplet_acc) for _ in range(dist.get_world_size())]
        dist.all_gather(acc_gathered, triplet_acc)
        dataset_gathered = [torch.zeros_like(batch['dataset']) for _ in range(dist.get_world_size())]
        dist.all_gather(dataset_gathered, batch['dataset'])
        acc_gathered = torch.cat(acc_gathered)
        dataset_gathered = torch.cat(dataset_gathered)
        
        opt = self.optimizers()
        opt.zero_grad()
        self.manual_backward(loss)
        opt.step()

        self.log("train/lr", opt.param_groups[0]["lr"])
        self.log("train/sdf_loss", sdf_loss.clone().detach().item(), prog_bar=True)
        self.log("train/triplet_loss", triplet_loss.clone().detach().item(), prog_bar=True)
        self.log("train/l1_reg", l1_reg.clone().detach().item(), prog_bar=True)
        self.log("train/loss", loss.clone().detach().item(), prog_bar=True)
        self.log("train/logit_scale", self.logit_scale.clone().detach().item())
        self.log("train/triplet_acc", triplet_acc.mean().clone().detach().item(), prog_bar=True)
        self.log("train/triplet_acc_partnet", acc_gathered[dataset_gathered == 0].mean().clone().detach().item(), prog_bar=False)
        self.log("train/triplet_acc_lvis", acc_gathered[dataset_gathered == 1].mean().clone().detach().item(), prog_bar=False)
        self.log("train/current_epoch", self.current_epoch, sync_dist=True)
        self.log("train/global_step", self.global_step, sync_dist=True)
        return 
    
    def val_dataloader(self):
        if self.cfg.dataset.type == "LVIS":
            dataset = LVISDataset(self.cfg, is_train=False)
        elif self.cfg.dataset.type == "PartNet":
            dataset = PartNetDataset(self.cfg, is_train=False)
        elif self.cfg.dataset.type == "Mix":
            dataset = MixDataset(self.cfg, use_2d_feat=self.use_2d_feat, is_train=False)

        dataloader = DataLoader(dataset, 
                                num_workers=self.cfg.dataset.val_num_workers,
                                batch_size=self.cfg.dataset.val_batch_size,
                                shuffle=False, 
                                pin_memory=True,
                                drop_last=False)
        return  dataloader
    
    @torch.no_grad()
    def validation_step(self, batch, batch_idx):
        sdf = batch['sdf']
        N = sdf.shape[0]
        sdf_feat = self.sdf_encoder(sdf) 
        if self.use_2d_feat: 
            pc_feat = self.pvcnn(batch['pc'], batch['pc'], batch['mv_feat'], batch['pc2pc_idx'])
        else:
            pc_feat = self.pvcnn(batch['pc'], batch['pc'])
        planes = self.merge_sdf_pc_2_planes(sdf_feat, pc_feat)
        planes = self.triplane_transformer(planes)
        sdf_planes, part_planes = torch.split(planes, [64, planes.shape[2] - 64], dim=2)
        
        sdf_loss = self.calc_sdf_loss(sdf[:,:1], batch['sdf_mask'], sdf_planes)#, self.in_channels)   
        triplet_loss, triplet_acc, l1_reg = self.calc_triplet_loss1(part_planes, batch['PA'], batch['PB'], batch['PC'])
        loss = sdf_loss * self.cfg.loss.sdf + triplet_loss * self.cfg.loss.triplet + l1_reg * self.cfg.loss.l1

        if 'dataset' in batch:
            acc_gathered = [torch.zeros_like(triplet_acc) for _ in range(dist.get_world_size())]
            dist.all_gather(acc_gathered, triplet_acc)
            dataset_gathered = [torch.zeros_like(batch['dataset']) for _ in range(dist.get_world_size())]
            dist.all_gather(dataset_gathered, batch['dataset'])
            acc_gathered = torch.cat(acc_gathered)
            dataset_gathered = torch.cat(dataset_gathered)
            self.log("val/triplet_acc_partnet", acc_gathered[dataset_gathered == 0].mean().clone().detach().item(), prog_bar=False)
            self.log("val/triplet_acc_lvis", acc_gathered[dataset_gathered == 1].mean().clone().detach().item(), prog_bar=False)
        
        self.log("val/sdf_loss", sdf_loss.clone().detach().item(), prog_bar=True)
        self.log("val/triplet_loss", triplet_loss.clone().detach().item(), prog_bar=True)
        self.log("train/l1_reg", l1_reg.clone().detach().item(), prog_bar=True)
        self.log("val/loss", loss.clone().detach().item(), prog_bar=True)
        self.log("val/triplet_acc", triplet_acc.mean().clone().detach().item(), prog_bar=True)
        self.log("val/current_epoch", self.current_epoch, sync_dist=True)
        self.log("val/global_step", self.global_step, sync_dist=True)
        return 

    def debug(self, batch):
        save_dir = "test_results/test-2d-feat" #mix-all-overfit-single-reg01-185" #"mix-all-overfit-single-reg01" #test_mix_all_overfit_33epoch"  #mix-overfit-dis1-5epoch1"
        uid = batch['uid'][0]
        view_id = batch['view_id'][0]
        
        sdf = batch['sdf']
        N = sdf.shape[0]
        assert N == 1
        #voxel_feats = self.sdf_encoder(sdf) # N, C, D, H, W
        #voxel_feats = voxel_feats.permute(0, 2, 3, 4, 1).reshape(N, -1, voxel_feats.shape[1]) # N, 4096, C
        #planes = self.voxel2triplane(voxel_feats) # N, 3, C, H, W
        #sdf_planes, part_planes = torch.split(planes, planes.shape[2] // 2, dim=2)

        # mv_feat = batch['mv_feat']
        # feat = torch.zeros_like(mv_feat)
        # idx = batch['pc2pc_idx']
        # print(feat.shape, mv_feat.shape)
        
        # for i in range(mv_feat.shape[0]):
        #     mask = (idx[i] != -1).reshape(-1)
        #     idx_ = idx[i][mask].reshape(-1)
        #     feat[i][mask] += mv_feat[i][idx_]

        # points = batch['pc'].cpu().numpy()[0]
        # colors = (feat[i][:, :3] * 255).cpu().numpy().astype(np.uint8)
        # print(points.shape, colors.shape)

        # point_cloud = trimesh.points.PointCloud(vertices=points, colors=colors)
        # point_cloud.export(f'{save_dir}/{uid}_normal.ply')


        # colors = (feat[i][:, 3:6] * 255).cpu().numpy().astype(np.uint8)
        # point_cloud = trimesh.points.PointCloud(vertices=points, colors=colors)
        # point_cloud.export(f'{save_dir}/{uid}_rgb.ply')

        # from sklearn.decomposition import PCA
        # pca = PCA(n_components=3)
        # data_scaled = feat[i][:, 12:12+32].cpu().numpy()
        # data_reduced = pca.fit_transform(data_scaled)
        # data_reduced = (data_reduced - data_reduced.min()) / (data_reduced.max() - data_reduced.min())
        # colors = (data_reduced * 255).astype(np.uint8)
        # point_cloud = trimesh.points.PointCloud(vertices=points, colors=colors)
        # point_cloud.export(f'{save_dir}/{uid}_high_res_feats_0_normal.ply')
        # return 

        sdf_feat = self.sdf_encoder(sdf)
        if self.use_2d_feat: 
            pc_feat = self.pvcnn(batch['pc'], batch['pc'], batch['mv_feat'], batch['pc2pc_idx'])
        else:
            pc_feat = self.pvcnn(batch['pc'], batch['pc'])
        planes = self.merge_sdf_pc_2_planes(sdf_feat, pc_feat)
        planes = self.triplane_transformer(planes)
        sdf_planes, part_planes = torch.split(planes, [64, planes.shape[2] - 64], dim=2)

        #self.save_planes(pc_feat, planes-pc_feat, batch_idx, batch['uid'], sdf)
                
        sdf_loss = self.calc_sdf_loss(sdf[:,:1], batch['sdf_mask'], sdf_planes)#, 2) 
        triplet_loss, triplet_acc, l1_reg = self.calc_triplet_loss1(part_planes, batch['PA'], batch['PB'], batch['PC'])
        loss = sdf_loss * self.cfg.loss.sdf + triplet_loss * self.cfg.loss.triplet

        coord = self.grid_coord.unsqueeze(0).repeat(N, 1, 1).cuda() # N, M, 3
        coord_feat = sample_triplane_feat(sdf_planes, coord) # N, M, C
        sdf_pred = self.sdf_decoder(coord_feat) # N, M, 1

        sdf_loss = self.l1_loss(sdf_pred.reshape(1, 1, 256, 256, 256), sdf)
        print(sdf_loss.shape, torch.quantile(-sdf_loss, torch.tensor([0.005, 0.01, 0.015, 0.02, 0.025, 0.03, 0.1,  0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]).cuda()))
        print(sdf.min(), (sdf < 1).float().mean(), torch.quantile(sdf, torch.tensor([0.005, 0.01, 0.015, 0.02, 0.025, 0.03, 0.1,  0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95]).cuda()))
        # print(sdf_loss, uid, view_id)

        os.makedirs(save_dir, exist_ok=True)
        sdf_pred_ = sdf_pred.clone().cpu().detach().numpy().reshape(256, 256, 256)
        t = 256*256*256
        # print("???", sdf_pred_.min(), sdf_pred_.max(), sdf_pred_.mean(), (sdf_pred_ < 0).sum() / t, (torch.abs(sdf) < 1).float().sum() / t)
        print(uid, sdf_pred_.min(), sdf_pred_.max(), sdf_pred_.shape, sdf_loss.mean())
        vertices, faces, _, _ = skimage.measure.marching_cubes(sdf_pred_, 0)
        mesh = trimesh.Trimesh(vertices, faces)
        mesh.vertices = mesh.vertices * (2.0 / 256) - 1.0
        mesh.export(f'{save_dir}/{uid}_{view_id}.ply')

        vertices, faces, _, _ = skimage.measure.marching_cubes(sdf.cpu().numpy().reshape(256, 256, 256), 0)
        mesh = trimesh.Trimesh(vertices, faces)
        mesh.vertices = mesh.vertices * (2.0 / 256) - 1.0
        mesh.export(f'{save_dir}/gt_{uid}_{view_id}.ply')
        

        ### export voxel part feature
        # coord = self.grid_coord.unsqueeze(0).repeat(N, 1, 1).cuda().reshape(N, -1, 3) # N, M, 3
        # voxel_part_feat = sample_triplane_feat(part_planes, coord) # N, M, C
        # voxel_part_feat = voxel_part_feat.cpu().detach().numpy().reshape(256, 256, 256, 192)

        # def save_h5(data, name, filename):
        #     # save a compressed h5 file
        #     compression_options = {
        #         'compression': 'gzip',  
        #         'compression_opts': 9,  
        #     }
        #     with h5py.File(f"{filename}", 'w') as f:
        #         f.create_dataset(name, data=data, **compression_options)

        # #np.save(f'{save_dir}/voxel_part_feat_{uid}_{view_id}.npy', voxel_part_feat)
        # #np.save(f'{save_dir}/sdf_{uid}_{view_id}.npy', batch['sdf'])

        # save_h5(voxel_part_feat, 'voxel_part_feat', f'{save_dir}/voxel_part_feat_{uid}_{view_id}.npy')
        # save_h5(batch['sdf'].cpu().detach().numpy(), 'sdf', f'{save_dir}/sdf_{uid}_{view_id}.npy')


        tensor_vertices = torch.from_numpy(mesh.vertices.copy()).reshape(1, -1, 3).cuda().to(torch.float16)
        point_feat = sample_triplane_feat(part_planes, tensor_vertices) # N, M, C
        point_feat = point_feat.cpu().detach().numpy().reshape(-1, 448)
        

        from sklearn.decomposition import PCA
        # from sklearn.preprocessing import StandardScaler
        # scaler = StandardScaler()

        data_scaled = point_feat / np.linalg.norm(point_feat, axis=-1, keepdims=True) #scaler.fit_transform(point_feat)
        
        # debug chair (10dfe487e2da4fee9b37f4ad23d4e87e)
        # xyz = mesh.vertices.copy()
        # idx0 = xyz[:, 1] > -0.5
        # idx1 = np.logical_and(np.logical_and(xyz[:, 0] > 0, xyz[:, 2] > 0), xyz[:, 1] < -0.55)
        # idx2 = np.logical_and(np.logical_and(xyz[:, 0] > 0, xyz[:, 2] < 0), xyz[:, 1] < -0.55)
        # idx3 = np.logical_and(np.logical_and(xyz[:, 0] < 0, xyz[:, 2] > 0), xyz[:, 1] < -0.55)
        # idx4 = np.logical_and(np.logical_and(xyz[:, 0] < 0, xyz[:, 2] < 0), xyz[:, 1] < -0.55)
        # idx5 = np.logical_and(xyz[:, 1] <= -0.5, xyz[:, 1] >= -0.55)

        # # data_scaled *= 0
        # # data_scaled[idx0, 0] = 1
        # # data_scaled[idx1, 1] = 1
        # # data_scaled[idx2, 2] = 1
        # # data_scaled[idx3, 3] = 1
        # # data_scaled[idx4, 4] = 1
        # # data_scaled[idx5, 5] = 1

        pca = PCA(n_components=3)

        data_reduced = pca.fit_transform(data_scaled)
        data_reduced = (data_reduced - data_reduced.min()) / (data_reduced.max() - data_reduced.min())
        colors_255 = (data_reduced * 255).astype(np.uint8)

        # from scipy.spatial.distance import pdist

        # print(np.mean(pdist(data_scaled[idx1], 'cosine')))
        # print(np.mean(pdist(data_scaled[idx2], 'cosine')))
        # print(np.mean(pdist(data_scaled[idx3], 'cosine')))
        # print(np.mean(pdist(data_scaled[idx4], 'cosine')))
        # print(np.mean(pdist(np.vstack((data_scaled[idx1].mean(0), data_scaled[idx0].mean(0))), 'cosine')))
        # print(np.mean(pdist(np.vstack((data_scaled[idx2].mean(0), data_scaled[idx0].mean(0))), 'cosine')))
        # print(np.mean(pdist(np.vstack((data_scaled[idx3].mean(0), data_scaled[idx0].mean(0))), 'cosine')))
        # print(np.mean(pdist(np.vstack((data_scaled[idx4].mean(0), data_scaled[idx0].mean(0))), 'cosine')))
        # print(np.mean(pdist(np.vstack((data_scaled[idx1].mean(0), 
        #                              data_scaled[idx2].mean(0),
        #                              data_scaled[idx3].mean(0),
        #                              data_scaled[idx4].mean(0))), 'cosine')))
        # print(np.mean(pdist(data_scaled[idx5], 'cosine')))
        # print(np.mean(pdist(np.vstack((data_scaled[idx1].mean(0), data_scaled[idx5].mean(0))), 'cosine')))
        # print(np.mean(pdist(np.vstack((data_scaled[idx2].mean(0), data_scaled[idx5].mean(0))), 'cosine')))
        # print(np.mean(pdist(np.vstack((data_scaled[idx3].mean(0), data_scaled[idx5].mean(0))), 'cosine')))
        # print(np.mean(pdist(np.vstack((data_scaled[idx4].mean(0), data_scaled[idx5].mean(0))), 'cosine')))




        colored_mesh = trimesh.Trimesh(vertices=mesh.vertices, faces=mesh.faces, vertex_colors=colors_255)
        colored_mesh.export(f'{save_dir}/colored_gt_{uid}_{view_id}.ply')

        np.save(f'{save_dir}/point_feat_{uid}_{view_id}.npy', point_feat)
        #print(point_feat.shape, data_reduced.shape, data_reduced.min(), data_reduced.max(), data_scaled.min(), data_scaled.max())
        


        #sdf_target = sdf.reshape(N, -1, 1)[:, mask, :] # N, M, 1
        #sdf_loss = self.mse_loss(sdf_pred, sdf_target).mean()


        #sdf_loss = self.calc_sdf_loss(sdf, sdf_planes)   
        #triplet_loss, triplet_acc = self.calc_triplet_loss1(part_planes, batch['PA'], batch['PB'], batch['PC'])

    def merge_sdf_pc_2_planes(self, sdf_feat, pc_feat):
        dim = sdf_feat.shape[1]
        sdf_planes = torch.cat((sdf_feat.mean(dim=-1).unsqueeze(1), #xy
                                sdf_feat.mean(dim=-3).unsqueeze(1), #yz
                                sdf_feat.mean(dim=-2).unsqueeze(1)), dim=1) #xz
        sdf_planes = sdf_planes.permute(0, 1, 2, 4, 3) 
        return torch.cat((pc_feat, sdf_planes), dim=2) # N, 3, C, 256, 256

    def save_planes(self, pc_planes, sdf_planes, batch_idx, url, sdf):
        save_dir = f"test_results/debug_triplane_coord/{url[0]}"
        os.makedirs(save_dir, exist_ok=True)
        print(pc_planes.shape, sdf_planes.shape, batch_idx, url, sdf.shape)


        vertices, faces, _, _ = skimage.measure.marching_cubes(sdf[0].cpu().numpy().reshape(256, 256, 256), 0)
        mesh = trimesh.Trimesh(vertices, faces)
        mesh.vertices = mesh.vertices * (2.0 / 256) - 1.0
        mesh.export(f'{save_dir}/gt_mesh.ply')
        np.save(f'{save_dir}/sdf.npy',sdf[0].cpu().numpy().reshape(256, 256, 256))
        np.save(f'{save_dir}/pc_planes.npy', pc_planes[0].cpu().detach().numpy())
        np.save(f'{save_dir}/sdf_planes.npy', sdf_planes[0].cpu().detach().numpy())