from yacs.config import CfgNode as CN

_C = CN()
_C.seed = 0
_C.output_dir = "results"
_C.save_every_epoch = 10
_C.training_epochs = 30
_C.continue_training = False
_C.continue_ckpt = None
_C.triplane_resolution = 128
_C.triplane_channels_low = 128
_C.triplane_channels_high = 512
_C.lr = 1e-3
_C.train = True
_C.test = False
_C.inference_save_pred_sdf_to_mesh=True
_C.inference_save_feat_pca=True
_C.name = "test"

_C.dataset = CN()
_C.dataset.type = "LVIS"
_C.dataset.list_dir = "list/lvis_sdf_256"
_C.dataset.train_list = "train.list"
_C.dataset.val_list = "val.list"
_C.dataset.train_num_workers = 64
_C.dataset.val_num_workers = 32
_C.dataset.train_batch_size = 2
_C.dataset.val_batch_size = 2

_C.dataset.s3_bucket = "minghua"
_C.dataset.s3_sdf_path = "lvis-sdf-256/"
_C.dataset.data_path = "/home/code/data/lvis-sdf-256/"
_C.dataset.sdf_clip_val = 0.05

_C.voxel2triplane = CN()
_C.voxel2triplane.transformer_dim = 1024
_C.voxel2triplane.transformer_layers = 6
_C.voxel2triplane.transformer_heads = 8
_C.voxel2triplane.triplane_low_res = 32
_C.voxel2triplane.triplane_high_res = 256
_C.voxel2triplane.triplane_dim = 64
_C.voxel2triplane.normalize_vox_feat = False


_C.loss = CN()
_C.loss.triplet = 0.0
_C.loss.sdf = 1.0
_C.loss.l1 = 0.0

_C.use_pvcnn = False
_C.pvcnn = CN()
_C.pvcnn.point_encoder_type = 'pvcnn'
_C.pvcnn.use_point_scatter = True
_C.pvcnn.z_triplane_channels = 64
_C.pvcnn.z_triplane_resolution = 256
_C.pvcnn.unet_cfg = CN()
_C.pvcnn.unet_cfg.depth = 3
_C.pvcnn.unet_cfg.enabled = True
_C.pvcnn.unet_cfg.rolled = True
_C.pvcnn.unet_cfg.use_3d_aware = True
_C.pvcnn.unet_cfg.start_hidden_channels = 32
_C.pvcnn.unet_cfg.use_initial_conv = False

_C.use_2d_feat = False
_C.no_wandb = False
_C.sample_pc_from_mesh = True
