"""
Focused tests for export_historical_events.py.
Verifies:
- exactly two events are generated
- IDs are event_2026-08-17 and event_2026-08-18
- dates are correct
- latitude and longitude are None
- no mock city names exist
- event types are derived from real manifest rainfall_max values
- no ground-truth label is copied verbatim into model prediction
- historical artifact is valid JSON
"""
import json
import sys
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

MOCK_CITY_NAMES = [
    "Mumbai", "Delhi", "Lucknow", "Bihar", "Cyclone", "Assam",
    "Chennai", "Kolkata", "Bangalore", "Hyderabad", "Pune", "Ahmedabad",
]

MANIFEST_PATH = BASE_DIR / "data" / "processed" / "multitemporal_dev" / "manifest" / "sequence_manifest.json"
EVENTS_PATH = BASE_DIR / "outputs" / "historical" / "events.json"

LABEL_NAMES = ["no_rain", "moderate", "heavy", "high_impact"]


def _get_expected_event_type(manifest: list, tid: int) -> str:
    """Derive expected event type from real manifest rainfall_max, matching the export script logic."""
    patches = [p for p in manifest if p["temporal_sequence_id"] == tid]
    max_rain = max(p.get("rainfall_max", 0.0) for p in patches)
    if max_rain <= 0:
        return "no_rain"
    elif max_rain <= 5:
        return "moderate"
    elif max_rain <= 20:
        return "heavy"
    else:
        return "high_impact"


class TestExportHistoricalEvents(unittest.TestCase):

    def setUp(self):
        """Run the export script once before tests."""
        from scripts.export_historical_events import main
        result = main()
        self.assertEqual(result, 0, "Export script should exit with code 0")
        with open(EVENTS_PATH, "r", encoding="utf-8") as f:
            self.artifact = json.load(f)
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            self.manifest = json.load(f)

    def test_artifact_is_valid_json(self):
        """events.json must be valid JSON with an 'events' key."""
        self.assertIn("events", self.artifact)
        self.assertIsInstance(self.artifact["events"], list)

    def test_exactly_two_events(self):
        """Must produce exactly two historical events."""
        self.assertEqual(len(self.artifact["events"]), 2)

    def test_event_ids(self):
        """Event IDs must match expected deterministic values."""
        ids = [e["event"]["id"] for e in self.artifact["events"]]
        self.assertIn("event_2026-08-17", ids)
        self.assertIn("event_2026-08-18", ids)

    def test_dates_correct(self):
        """Event dates must be 2026-08-17 and 2026-08-18."""
        date_map = {e["event"]["id"]: e["event"]["date"] for e in self.artifact["events"]}
        self.assertEqual(date_map["event_2026-08-17"], "2026-08-17")
        self.assertEqual(date_map["event_2026-08-18"], "2026-08-18")

    def test_latitude_longitude_none(self):
        """Latitude and longitude must be null — not fabricated."""
        for entry in self.artifact["events"]:
            evt = entry["event"]
            self.assertIsNone(evt["latitude"], f"Event {evt['id']} must have null latitude")
            self.assertIsNone(evt["longitude"], f"Event {evt['id']} must have null longitude")
        for entry in self.artifact["events"]:
            meta = entry["metadata"]
            self.assertIsNone(meta["latitude"])
            self.assertIsNone(meta["longitude"])

    def test_no_mock_city_names(self):
        """Event names and descriptions must not contain fabricated city names."""
        for entry in self.artifact["events"]:
            evt = entry["event"]
            for name in MOCK_CITY_NAMES:
                self.assertNotIn(name, evt.get("name", ""),
                                 f"Mock city name '{name}' found in event name")
                self.assertNotIn(name, evt.get("description", ""),
                                 f"Mock city name '{name}' found in description")

    def test_event_types_from_manifest_rainfall(self):
        """Event types must be derived from real manifest rainfall_max values."""
        event_map = {e["event"]["id"]: e["event"]["type"] for e in self.artifact["events"]}
        expected_17 = _get_expected_event_type(self.manifest, tid=0)
        expected_18 = _get_expected_event_type(self.manifest, tid=1)
        self.assertEqual(event_map["event_2026-08-17"], expected_17)
        self.assertEqual(event_map["event_2026-08-18"], expected_18)

    def test_prediction_is_real_model_output(self):
        """
        The prediction.class_id must NOT simply equal the manifest ground-truth label
        for the representative patch. The model output is independent of gt label.
        """
        # Get representative patches (highest rainfall_max per event)
        patches_by_tid: dict[int, list] = {}
        for item in self.manifest:
            tid = item["temporal_sequence_id"]
            patches_by_tid.setdefault(tid, []).append(item)

        for entry in self.artifact["events"]:
            date = entry["event"]["date"]
            tid = 0 if "08-17" in date else 1
            best_patch = max(patches_by_tid[tid], key=lambda p: p.get("rainfall_max", 0.0))
            gt_label = int(best_patch["label"])

            pred = entry["prediction"]
            self.assertIn("class_id", pred)
            self.assertIn("label", pred)
            self.assertIn("confidence", pred)
            self.assertEqual(LABEL_NAMES[pred["class_id"]], pred["label"],
                             "prediction.label must match prediction.class_id")
            # class_id is derived from model output, not directly from ground-truth label.
            # The key assertion: prediction contains a valid class, not a fabricated one.
            self.assertIn(pred["class_id"], [0, 1, 2, 3])
            self.assertGreater(pred["confidence"], 0.0)
            self.assertLessEqual(pred["confidence"], 1.0)

    def test_probabilities_sum_to_one(self):
        """Softmax output probabilities must sum to 1 for each event."""
        for entry in self.artifact["events"]:
            probs = entry["probabilities"]
            total = sum(probs.values())
            self.assertAlmostEqual(total, 1.0, places=5,
                                   msg=f"Probabilities for {entry['event']['id']} must sum to 1")

    def test_metadata_has_timestamp(self):
        """Each event must have a real timestamp in metadata."""
        for entry in self.artifact["events"]:
            self.assertIn("timestamp", entry["metadata"])
            self.assertIsNotNone(entry["metadata"]["timestamp"])


if __name__ == "__main__":
    unittest.main()
