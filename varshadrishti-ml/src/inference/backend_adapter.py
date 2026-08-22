"""
Adapter for the backend API to interface with VarshaDrishti3DCNN.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Optional

import numpy as np
import torch

# Add varshadrishti-ml to sys.path so we can import src.*
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.models.cnn3d import VarshaDrishti3DCNN
from src.utils.checkpoint import load_checkpoint

class VarshaDrishtiPredictor:
    def __init__(
        self,
        checkpoint_path: Optional[str] = None,
        artifact_path: Optional[str] = None
    ):
        self.device = torch.device("cpu")
        self.model = VarshaDrishti3DCNN(in_channels=3, num_classes=4, dropout=0.0)
        
        if checkpoint_path is None:
            checkpoint_path = str(BASE_DIR / "models" / "checkpoints" / "dev_poc_best.pth")
        if artifact_path is None:
            artifact_path = str(BASE_DIR / "data" / "processed" / "multitemporal_dev" / "data" / "sequences.npy")
            
        cp_path = Path(checkpoint_path)
        if not cp_path.exists():
            raise RuntimeError(f"Missing checkpoint: {checkpoint_path}. Ensure training has completed.")
            
        art_path = Path(artifact_path)
        if not art_path.exists():
            raise RuntimeError(f"Missing dataset artifact: {artifact_path}. Ensure preprocessing has completed.")
            
        load_checkpoint(self.model, str(cp_path), optimizer=None, device=self.device)
        self.model.eval()
        
        self.sequences = np.load(str(art_path), mmap_mode="r")
        self.num_samples = self.sequences.shape[0]

        # Load manifest to fetch metadata
        manifest_path = art_path.parent.parent / "manifest" / "sequence_manifest.json"
        self.manifest = []
        if manifest_path.exists():
            with open(manifest_path, 'r', encoding='utf-8') as f:
                self.manifest = json.load(f)

    def _get_latest_patch_idx(self) -> int:
        if not self.manifest:
            return 0
        
        latest_event_id = None
        latest_time = ""
        
        for item in self.manifest:
            ts_list = item.get("timestamps", [])
            if not ts_list:
                continue
            final_ts = ts_list[-1]
            if final_ts > latest_time:
                latest_time = final_ts
                latest_event_id = item.get("temporal_sequence_id")
                
        if latest_event_id is not None:
            patches_in_event = sorted(
                [p for p in self.manifest if p.get("temporal_sequence_id") == latest_event_id],
                key=lambda x: x.get("patch_idx", 0)
            )
            if patches_in_event:
                return patches_in_event[0].get("patch_idx", 0)
                
        return 0

    def predict(self, observation: Optional[Mapping[str, Any]]) -> Mapping[str, Any]:
        """
        Runs inference on the provided observation or default to the latest available event.
        """
        if observation and "patch_idx" in observation:
            idx = int(observation["patch_idx"]) % self.num_samples
        else:
            idx = self._get_latest_patch_idx()
            
        # Shape: [3, 6, 256, 256]
        seq = self.sequences[idx]
        # Shape: [1, 3, 6, 256, 256]
        tensor = torch.from_numpy(np.array(seq, dtype=np.float32)).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            logits = self.model(tensor)
            probs = torch.softmax(logits, dim=1).squeeze(0).cpu().numpy()
            
        class_id = int(np.argmax(probs))
        confidence = float(probs[class_id])
        
        # Generate Grad-CAM
        from src.xai.gradcam import GradCAM3D, save_heatmap_image
        cam_generator = GradCAM3D(self.model, target_layer_name='conv3')
        cam_heatmap = cam_generator.generate(tensor, target_class=class_id)
        cam_generator.remove_hooks()
        
        out_dir = BASE_DIR.parent / "backend" / "generated" / "gradcam"
        out_filename = f"heatmap_patch_{idx}.png"
        out_path = out_dir / out_filename
        save_heatmap_image(cam_heatmap, str(out_path))
        
        # The frontend proxy might not serve this automatically, but this fits the backend schema.
        # Alternatively, using the frontend public directory allows immediate display.
        # Following the prompt's deterministic backend location requirement:
        image_url = f"http://localhost:8000/generated/gradcam/{out_filename}"
        
        # Determine metadata
        lat = 20.0
        lon = 75.0
        timestamp = datetime.now(timezone.utc).isoformat()
        
        manifest_item = None
        if self.manifest:
            for item in self.manifest:
                if item.get("patch_idx") == idx:
                    manifest_item = item
                    break

        if manifest_item:
            ts_list = manifest_item.get("timestamps", [])
            if ts_list:
                timestamp = ts_list[-1]
            # NOTE: Exact geographic coordinates per patch are NOT currently computed 
            # in the multitemporal artifact. They only exist within the raw INSAT-3DR HDF5 grids. 
            # Per project constraints, we leave the fallback behavior unchanged rather than 
            # fabricating data or reopening the raw datasets here.
        
        if observation:
            lat = observation.get("latitude", lat)
            lon = observation.get("longitude", lon)
            if "timestamp" in observation:
                timestamp = observation["timestamp"]
            
        return {
            "prediction": {
                "class_id": class_id,
                "label": ["no_rain", "moderate", "heavy", "high_impact"][class_id],
                "confidence": confidence
            },
            "probabilities": {
                "no_rain": float(probs[0]),
                "moderate": float(probs[1]),
                "heavy": float(probs[2]),
                "high_impact": float(probs[3])
            },
            "xai": {
                "gradcam": {
                    "image_url": image_url
                },
                "shap": None
            },
            "metadata": {
                "timestamp": timestamp,
                "latitude": float(lat),
                "longitude": float(lon)
            }
        }
