import unittest
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Import the main function from the script
from scripts.export_development_metrics import main

class TestExportMetrics(unittest.TestCase):
    def test_export_generates_artifacts(self):
        """
        Verify that running the export_development_metrics script successfully generates
        metrics.json, confusion_matrix.json, and report.json.
        """
        # Run the script main function
        result = main()
        
        # Verify successful execution (exit code 0)
        self.assertEqual(result, 0)
        
        # Verify the artifacts exist
        metrics_dir = BASE_DIR / "outputs" / "metrics"
        self.assertTrue((metrics_dir / "metrics.json").exists(), "metrics.json should be generated")
        self.assertTrue((metrics_dir / "confusion_matrix.json").exists(), "confusion_matrix.json should be generated")
        self.assertTrue((metrics_dir / "report.json").exists(), "report.json should be generated")

if __name__ == '__main__':
    unittest.main()
