"""
Tests for multi-temporal dataset manifest and sequence builder.

Note: These tests use small in-memory software fixtures.
Fixtures are for software logic testing only.
They MUST NOT be used for model training or scientific results.
"""

import sys
import unittest
from pathlib import Path
from datetime import datetime, timedelta

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.data.temporal_matcher import match_temporally
from src.data.sequence_builder import build_temporal_sequences


def _make_l1b(dt: datetime, filename: str = None) -> dict:
    """Software fixture: one L1B entry."""
    fname = filename or f"3RIMG_{dt.strftime('%d%b%Y').upper()}_{dt.strftime('%H%M')}_L1B_STD.h5"
    return {"timestamp": dt, "filename": fname, "full_path": f"/fake/l1b/{fname}", "file_size": 1024}


def _make_l2b(dt: datetime, filename: str = None) -> dict:
    """Software fixture: one L2B entry."""
    fname = filename or f"3RIMG_{dt.strftime('%d%b%Y').upper()}_{dt.strftime('%H%M')}_L2B_IMC.h5"
    return {"timestamp": dt, "filename": fname, "full_path": f"/fake/l2b/{fname}", "file_size": 512}


T0 = datetime(2026, 8, 17, 22, 15)


def _sequence_of(n: int, step_min: int = 30) -> tuple:
    """Build n perfectly-spaced matched pairs."""
    l1bs = [_make_l1b(T0 + timedelta(minutes=i * step_min)) for i in range(n)]
    l2bs = [_make_l2b(T0 + timedelta(minutes=i * step_min)) for i in range(n)]
    matched, _, _ = match_temporally(l1bs, l2bs, tolerance_minutes=0)
    return matched


class TestTemporalMatcher(unittest.TestCase):

    def test_exact_match(self):
        l1bs = [_make_l1b(T0)]
        l2bs = [_make_l2b(T0)]
        matched, un_l1b, un_l2b = match_temporally(l1bs, l2bs, tolerance_minutes=0)
        self.assertEqual(len(matched), 1)
        self.assertEqual(matched[0]["time_diff_minutes"], 0.0)
        self.assertEqual(len(un_l1b), 0)
        self.assertEqual(len(un_l2b), 0)

    def test_exact_match_fails_at_nonzero_diff(self):
        l1bs = [_make_l1b(T0)]
        l2bs = [_make_l2b(T0 + timedelta(minutes=5))]
        matched, un_l1b, un_l2b = match_temporally(l1bs, l2bs, tolerance_minutes=0)
        self.assertEqual(len(matched), 0)
        self.assertEqual(len(un_l1b), 1)
        self.assertEqual(len(un_l2b), 1)

    def test_tolerance_matches_within_window(self):
        l1bs = [_make_l1b(T0)]
        l2bs = [_make_l2b(T0 + timedelta(minutes=5))]
        matched, un_l1b, un_l2b = match_temporally(l1bs, l2bs, tolerance_minutes=10)
        self.assertEqual(len(matched), 1)
        self.assertAlmostEqual(matched[0]["time_diff_minutes"], 5.0, places=3)

    def test_multiple_exact_matches(self):
        l1bs = [_make_l1b(T0 + timedelta(minutes=i * 30)) for i in range(6)]
        l2bs = [_make_l2b(T0 + timedelta(minutes=i * 30)) for i in range(6)]
        matched, un_l1b, un_l2b = match_temporally(l1bs, l2bs, tolerance_minutes=0)
        self.assertEqual(len(matched), 6)
        self.assertEqual(len(un_l1b), 0)

    def test_unmatched_l1b_reported(self):
        l1bs = [_make_l1b(T0), _make_l1b(T0 + timedelta(hours=5))]
        l2bs = [_make_l2b(T0)]
        matched, un_l1b, un_l2b = match_temporally(l1bs, l2bs, tolerance_minutes=0)
        self.assertEqual(len(matched), 1)
        self.assertEqual(len(un_l1b), 1)

    def test_unmatched_l2b_reported(self):
        l1bs = [_make_l1b(T0)]
        l2bs = [_make_l2b(T0), _make_l2b(T0 + timedelta(hours=3))]
        matched, un_l1b, un_l2b = match_temporally(l1bs, l2bs, tolerance_minutes=0)
        self.assertEqual(len(matched), 1)
        self.assertEqual(len(un_l2b), 1)

    def test_chronological_order(self):
        ts = [T0 + timedelta(minutes=i * 30) for i in range(4)]
        import random
        l1bs = [_make_l1b(t) for t in ts]
        l2bs = [_make_l2b(t) for t in ts]
        random.shuffle(l1bs)
        random.shuffle(l2bs)
        matched, _, _ = match_temporally(l1bs, l2bs, tolerance_minutes=0)
        timestamps = [m["timestamp"] for m in matched]
        self.assertEqual(timestamps, sorted(timestamps))

    def test_no_l1b(self):
        l2bs = [_make_l2b(T0)]
        matched, un_l1b, un_l2b = match_temporally([], l2bs, tolerance_minutes=0)
        self.assertEqual(len(matched), 0)
        self.assertEqual(len(un_l2b), 1)

    def test_no_l2b(self):
        l1bs = [_make_l1b(T0)]
        matched, un_l1b, un_l2b = match_temporally(l1bs, [], tolerance_minutes=0)
        self.assertEqual(len(matched), 0)
        self.assertEqual(len(un_l1b), 1)


class TestSequenceBuilder(unittest.TestCase):

    def test_six_perfect_frames(self):
        matched = _sequence_of(6)
        seqs = build_temporal_sequences(matched, sequence_length=6, step_minutes=30)
        self.assertEqual(len(seqs), 1)

    def test_seven_frames_yields_two_sequences(self):
        matched = _sequence_of(7)
        seqs = build_temporal_sequences(matched, sequence_length=6, step_minutes=30)
        self.assertEqual(len(seqs), 2)

    def test_five_frames_yields_zero_sequences(self):
        matched = _sequence_of(5)
        seqs = build_temporal_sequences(matched, sequence_length=6, step_minutes=30)
        self.assertEqual(len(seqs), 0)

    def test_single_frame_yields_zero_sequences(self):
        matched = _sequence_of(1)
        seqs = build_temporal_sequences(matched, sequence_length=6, step_minutes=30)
        self.assertEqual(len(seqs), 0)

    def test_empty_matched_yields_zero_sequences(self):
        seqs = build_temporal_sequences([], sequence_length=6, step_minutes=30)
        self.assertEqual(len(seqs), 0)

    def test_gap_breaks_sequence(self):
        """Two perfect 6-frame runs with a 3-hour gap between them should NOT form a single seq."""
        matched = _sequence_of(6)
        # Insert a broken gap then 5 more frames
        gap_t = matched[-1]["timestamp"] + timedelta(hours=3)
        for i in range(1, 6):
            matched.append({
                "timestamp": gap_t + timedelta(minutes=i * 30),
                "l1b_path": "/fake/l1b/extra.h5",
                "l2b_path": "/fake/l2b/extra.h5",
                "l1b_filename": "extra_l1b.h5",
                "l2b_filename": "extra_l2b.h5",
                "time_diff_minutes": 0.0
            })
        seqs = build_temporal_sequences(matched, sequence_length=6, step_minutes=30)
        # First run gives 1 seq, second run (only 5 frames) gives 0
        self.assertEqual(len(seqs), 1)

    def test_repeated_timestamp_rejected(self):
        """Two identical timestamps in sequence must not form a valid 30-min-spaced sequence."""
        matched = _sequence_of(6)
        matched[3]["timestamp"] = matched[2]["timestamp"]  # duplicate
        seqs = build_temporal_sequences(matched, sequence_length=6, step_minutes=30)
        self.assertEqual(len(seqs), 0)

    def test_sequence_is_chronological(self):
        matched = _sequence_of(6)
        seqs = build_temporal_sequences(matched, sequence_length=6, step_minutes=30)
        seq = seqs[0]
        timestamps = [f["timestamp"] for f in seq]
        self.assertEqual(timestamps, sorted(timestamps))

    def test_sequence_has_correct_length(self):
        matched = _sequence_of(8)
        seqs = build_temporal_sequences(matched, sequence_length=6, step_minutes=30)
        for seq in seqs:
            self.assertEqual(len(seq), 6)

    def test_no_repeated_timestamps_within_sequence(self):
        matched = _sequence_of(6)
        seqs = build_temporal_sequences(matched, sequence_length=6, step_minutes=30)
        for seq in seqs:
            timestamps = [f["timestamp"] for f in seq]
            self.assertEqual(len(set(timestamps)), len(timestamps))


if __name__ == "__main__":
    unittest.main()
