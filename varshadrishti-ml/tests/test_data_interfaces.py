import os
import sys
import unittest
from pathlib import Path
import torch

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.hdf5_reader import INSAT3DRReader
from src.data.metadata import Metadata, SatelliteFrame
from src.data.spatial_crop import SpatialCropper
from src.data.temporal_matcher import TemporalMatcher
from src.data.sequence_builder import build_sequences
from src.data.label_builder import RainfallLabelBuilder
from src.data.dataset import VarshaDataset
from src.data.splitter import split_by_time

class TestDataInterfaces(unittest.TestCase):

    def test_hdf5_reader_no_file(self):
        """Test that HDF5 reader raises correct error when file is missing."""
        reader = INSAT3DRReader()
        with self.assertRaises(FileNotFoundError) as context:
            reader.inspect("non_existent.h5")
        self.assertIn("REAL HDF5 FILE REQUIRED", str(context.exception))

    def test_metadata_structure(self):
        """Test metadata structures initialize properly."""
        meta = Metadata(source="MOSDAC")
        self.assertEqual(meta.source, "MOSDAC")
        self.assertIsNone(meta.timestamp)
        
        frame = SatelliteFrame(metadata=meta)
        self.assertEqual(frame.metadata.source, "MOSDAC")
        self.assertIsNone(frame.data)

    def test_spatial_cropper_unconfigured(self):
        """Test spatial cropper fails safely if ROI is unconfigured."""
        roi_unconfigured = {"min_lat": None, "max_lat": None, "min_lon": None, "max_lon": None}
        cropper = SpatialCropper(roi_unconfigured)
        with self.assertRaises(ValueError):
            cropper.crop(None)

    def test_temporal_matcher_interface(self):
        """Test temporal matcher interface."""
        matcher = TemporalMatcher(tolerance=1800)
        self.assertEqual(matcher.match([], []), [])

    def test_sequence_builder_unconfigured(self):
        """Test sequence builder requires configured length."""
        with self.assertRaises(ValueError):
            build_sequences([SatelliteFrame()], sequence_length=None)

    def test_label_builder_unconfigured(self):
        """Test label builder requires configured thresholds."""
        builder = RainfallLabelBuilder({"no_rain": None})
        with self.assertRaises(ValueError):
            builder.build_label(None)

    def test_varshadrishti_dataset(self):
        """Test dataset interface."""
        # TEST ONLY
        # Synthetic fixture - not satellite training data.
        # Never used for final model training or hackathon results.
        dummy_sequence = torch.zeros((4, 6, 128, 128))
        dummy_label = 0
        
        items = [{"sequence": dummy_sequence, "label": dummy_label, "timestamp": "2026-08-20T00:00:00"}]
        dataset = VarshaDataset(items)
        
        self.assertEqual(len(dataset), 1)
        sample = dataset[0]
        self.assertIn("sequence", sample)
        self.assertIn("label", sample)
        self.assertEqual(sample["label"], 0)

    def test_chronological_splitter(self):
        """Test the data splitter logic."""
        # Using simple integer sequence as proxy for chronologically sorted items
        samples = list(range(100))
        train, val, test = split_by_time(samples, 0.7, 0.15, 0.15)
        
        self.assertEqual(len(train), 70)
        self.assertEqual(len(val), 15)
        self.assertEqual(len(test), 15)
        
        # Verify chronological ordering is maintained
        self.assertEqual(train[0], 0)
        self.assertEqual(train[-1], 69)
        self.assertEqual(val[0], 70)
        self.assertEqual(test[0], 85)

if __name__ == '__main__':
    unittest.main()
