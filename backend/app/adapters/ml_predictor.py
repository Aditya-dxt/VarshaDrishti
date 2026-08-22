"""
Backend adapter for integrating the VarshaDrishti-ML trained model.
"""
import sys
from pathlib import Path

# Dynamically add the varshadrishti-ml directory to sys.path
# so we can import the ML module without complex environment setup.
ML_DIR = Path(__file__).resolve().parent.parent.parent.parent / "varshadrishti-ml"
if str(ML_DIR) not in sys.path:
    sys.path.insert(0, str(ML_DIR))

from src.inference.backend_adapter import VarshaDrishtiPredictor

# Re-export for the BHOOMIDRISHTI_PREDICTOR_CLASS config
Predictor = VarshaDrishtiPredictor
