import torch
from torch.utils.data import Dataset
from typing import List, Dict, Any

class VarshaDataset(Dataset):
    """
    PyTorch Dataset for VarshaDrishti.
    Yields: sequence (tensor), label (int), metadata (dict).
    """
    
    def __init__(self, sequences: List[Dict[str, Any]]):
        """
        Expects pre-built sequences and labels.
        """
        self.sequences = sequences

    def __len__(self) -> int:
        return len(self.sequences)

    def __getitem__(self, idx: int) -> Dict[str, Any]:
        item = self.sequences[idx]
        
        if "sequence" not in item or "label" not in item:
            raise ValueError("Dataset items must contain 'sequence' and 'label'.")
            
        return {
            "sequence": item["sequence"],
            "label": item["label"],
            "timestamp": item.get("timestamp"),
            "latitude": item.get("latitude"),
            "longitude": item.get("longitude"),
            "metadata": item.get("metadata")
        }
