import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.evaluation.metrics import calculate_metrics, high_impact_metrics
from src.evaluation.confusion_matrix import compute_confusion_matrix
from src.evaluation.report import generate_report


class TestMetrics(unittest.TestCase):

    def setUp(self):
        # TEST ONLY
        # Synthetic fixture — not satellite data.
        # Never used for final model training or hackathon results.
        self.labels = [0, 0, 1, 1, 2, 2, 3, 3]
        self.preds  = [0, 1, 1, 1, 2, 3, 3, 3]  # some errors

    def test_calculate_metrics_keys(self):
        m = calculate_metrics(self.labels, self.preds)
        self.assertIn("accuracy", m)
        self.assertIn("macro_f1", m)
        self.assertIn("weighted_f1", m)
        self.assertIn("classes", m)

    def test_per_class_keys(self):
        m = calculate_metrics(self.labels, self.preds)
        for cls in ["no_rain", "moderate", "heavy", "high_impact"]:
            self.assertIn(cls, m["classes"])
            self.assertIn("precision", m["classes"][cls])
            self.assertIn("recall",    m["classes"][cls])
            self.assertIn("f1",        m["classes"][cls])

    def test_high_impact_metrics(self):
        m = calculate_metrics(self.labels, self.preds)
        hi = high_impact_metrics(m)
        self.assertIn("precision", hi)
        self.assertIn("recall",    hi)
        self.assertIn("f1",        hi)

    def test_perfect_accuracy(self):
        labels = [0, 1, 2, 3]
        preds  = [0, 1, 2, 3]
        m = calculate_metrics(labels, preds)
        self.assertAlmostEqual(m["accuracy"], 1.0)
        self.assertAlmostEqual(m["macro_f1"], 1.0)

    def test_empty_raises(self):
        with self.assertRaises(ValueError):
            calculate_metrics([], [])


class TestConfusionMatrix(unittest.TestCase):

    def test_structure(self):
        # TEST ONLY — synthetic fixture
        labels = [0, 1, 2, 3, 0, 1]
        preds  = [0, 1, 2, 3, 1, 0]
        cm = compute_confusion_matrix(labels, preds)
        self.assertIn("class_names", cm)
        self.assertIn("matrix", cm)
        self.assertEqual(cm["class_names"], ["no_rain", "moderate", "heavy", "high_impact"])
        self.assertEqual(len(cm["matrix"]), 4)
        self.assertEqual(len(cm["matrix"][0]), 4)

    def test_empty_raises(self):
        with self.assertRaises(ValueError):
            compute_confusion_matrix([], [])


class TestReport(unittest.TestCase):

    def test_report_generation(self):
        # TEST ONLY — synthetic fixture
        import tempfile, os
        labels = [0, 1, 2, 3, 0, 1, 2, 3]
        preds  = [0, 1, 2, 3, 0, 1, 2, 3]
        with tempfile.TemporaryDirectory() as tmpdir:
            report = generate_report(labels, preds, output_dir=tmpdir)
            self.assertIn("metrics", report)
            self.assertIn("confusion_matrix", report)
            self.assertIn("high_impact", report)
            self.assertTrue(os.path.exists(os.path.join(tmpdir, "metrics.json")))
            self.assertTrue(os.path.exists(os.path.join(tmpdir, "confusion_matrix.json")))
            self.assertTrue(os.path.exists(os.path.join(tmpdir, "report.json")))


if __name__ == "__main__":
    unittest.main()
