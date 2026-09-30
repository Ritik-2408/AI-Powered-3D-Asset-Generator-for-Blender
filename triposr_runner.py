import os
import sys

# Make TripoSR's "tsr" package importable from the project root
TRIPOSR_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "TripoSR")
if TRIPOSR_DIR not in sys.path:
    sys.path.insert(0, TRIPOSR_DIR)

import numpy as np
import rembg
import torch
from PIL import Image

from tsr.system import TSR
from tsr.utils import remove_background, resize_foreground

MODEL_PATH = "stabilityai/TripoSR"
DEVICE = "cpu"  # forced CPU per project constraints
CHUNK_SIZE = 8192
MC_RESOLUTION = 256
FOREGROUND_RATIO = 0.85

_model = None
_rembg_session = None


def load_model():
    """Load TripoSR once at server startup. Do NOT call this per-request."""
    global _model, _rembg_session
    if _model is not None:
        return _model

    print("[triposr_runner] Loading TripoSR model on CPU... this may take a while.")
    _model = TSR.from_pretrained(
        MODEL_PATH,
        config_name="config.yaml",
        weight_name="model.ckpt",
    )
    _model.renderer.set_chunk_size(CHUNK_SIZE)
    _model.to(DEVICE)
    _rembg_session = rembg.new_session()
    print("[triposr_runner] Model loaded.")
    return _model


def preprocess_image(image_path: str) -> Image.Image:
    image = remove_background(Image.open(image_path), _rembg_session)
    image = resize_foreground(image, FOREGROUND_RATIO)
    image = np.array(image).astype(np.float32) / 255.0
    image = image[:, :, :3] * image[:, :, 3:4] + (1 - image[:, :, 3:4]) * 0.5
    image = Image.fromarray((image * 255.0).astype(np.uint8))
    return image


def generate_mesh(image_path: str, output_dir: str) -> str:
    if _model is None:
        raise RuntimeError("Model not loaded. Call load_model() at startup first.")

    os.makedirs(output_dir, exist_ok=True)
    image = preprocess_image(image_path)

    with torch.no_grad():
        scene_codes = _model([image], device=DEVICE)

    meshes = _model.extract_mesh(scene_codes, True, resolution=MC_RESOLUTION)

    if meshes[0].vertices.shape[0] == 0:
        raise RuntimeError("Mesh extraction failed: no surface found (empty geometry).")

    out_mesh_path = os.path.join(output_dir, "mesh.obj")
    meshes[0].export(out_mesh_path)
    return out_mesh_path