import os
import sys
import unittest
from pathlib import Path
import logging

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.config import load_config
from src.utils.device import get_device, get_device_info
from src.utils.logger import setup_logger

class TestUtils(unittest.TestCase):
    
    def setUp(self):
        self.config_path = Path(__file__).parent.parent / "configs" / "config.yaml"
        
    def test_load_config(self):
        """Test configuration loader."""
        config = load_config(str(self.config_path))
        self.assertIn("data", config)
        self.assertIn("model", config)
        self.assertIn("training", config)
        
    def test_get_device(self):
        """Test device detection."""
        device = get_device("auto")
        self.assertIsNotNone(device)
        self.assertIn(device.type, ["cpu", "cuda"])
        
    def test_get_device_info(self):
        """Test device info dictionary."""
        info = get_device_info()
        self.assertIn("cuda_available", info)
        self.assertIn("device_name", info)
        
    def test_logger(self):
        """Test logger setup."""
        log_dir = Path(__file__).parent.parent / "outputs" / "logs"
        logger = setup_logger("test_logger", log_dir=str(log_dir))
        
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, "test_logger")
        
        # Check if log file is created after logging a message
        logger.info("Test log message")
        log_file = log_dir / "test_logger.log"
        self.assertTrue(log_file.exists())
        
if __name__ == '__main__':
    unittest.main()
