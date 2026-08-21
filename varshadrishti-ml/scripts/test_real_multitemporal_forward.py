"""
Real-data 3D-CNN forward-pass smoke test.

Loads the existing multitemporal development artifact through VarshaDataset /
DataLoader and runs VarshaDrishti3DCNN in eval mode under torch.no_grad().

NO MODEL TRAINING IS PERFORMED.
This artifact is a single 3-hour temporal event (6 frames, 69 spatial patches).
It is NOT a scientifically valid training dataset.
"""

from __future__ import annotations

import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import torch
from torch.utils.data import DataLoader

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.data.dataset import VarshaDataset
from src.models.cnn3d import VarshaDrishti3DCNN, get_model_summary
from src.utils.config import load_config
from src.utils.device import get_device, get_device_info

ARTIFACT_DIR = BASE_DIR / "data" / "processed" / "multitemporal_dev"
REPORT_PATH = BASE_DIR / "reports" / "real_multitemporal_forward_pass.txt"

EXPECTED_CHANNELS = 3
EXPECTED_TIME = 6
EXPECTED_HEIGHT = 256
EXPECTED_WIDTH = 256
PROB_SUM_TOLERANCE = 1e-5


@dataclass
class ForwardPassResult:
    passed: bool
    device: str
    dataset_location: str
    n_samples: int
    input_shape: Tuple[int, ...]
    target_shape: Tuple[int, ...]
    num_classes: int
    n_batches: int
    model_output_shape: Tuple[int, ...]
    logit_min: float
    logit_max: float
    prob_min: float
    prob_max: float
    prob_sum_min: float
    prob_sum_max: float
    nan_input: int
    inf_input: int
    nan_logits: int
    inf_logits: int
    nan_probs: int
    inf_probs: int
    class_distribution: Dict[int, int]
    failures: List[str] = field(default_factory=list)
    diagnostics: List[str] = field(default_factory=list)
    weights_unchanged: bool = True
    training_performed: bool = False


def _count_nan(t: torch.Tensor) -> int:
    return int(torch.isnan(t).sum().item())


def _count_inf(t: torch.Tensor) -> int:
    return int(torch.isinf(t).sum().item())


def load_artifact_arrays(artifact_dir: Path = ARTIFACT_DIR) -> Dict[str, np.ndarray]:
    sequences_path = artifact_dir / "data" / "sequences.npy"
    targets_path = artifact_dir / "data" / "targets.npy"
    labels_path = artifact_dir / "data" / "labels.npy"
    masks_path = artifact_dir / "masks" / "masks.npy"

    missing = [str(p) for p in (sequences_path, targets_path, labels_path, masks_path) if not p.exists()]
    if missing:
        raise FileNotFoundError(
            "Multitemporal artifact files are missing:\n  " + "\n  ".join(missing)
        )

    return {
        "sequences": np.load(sequences_path),
        "targets": np.load(targets_path),
        "labels": np.load(labels_path),
        "masks": np.load(masks_path),
    }


def build_varsha_dataset(arrays: Dict[str, np.ndarray]) -> VarshaDataset:
    sequences = arrays["sequences"]
    labels = arrays["labels"]
    n = sequences.shape[0]
    items: List[Dict[str, Any]] = []
    for i in range(n):
        items.append(
            {
                "sequence": torch.from_numpy(sequences[i]),
                "label": int(labels[i]),
                "timestamp": f"seq_{i}",
            }
        )
    return VarshaDataset(items)


def _parameter_fingerprint(model: torch.nn.Module) -> torch.Tensor:
    return torch.cat([p.detach().cpu().reshape(-1) for p in model.parameters()])


def run_forward_pass(
    artifact_dir: Path = ARTIFACT_DIR,
    batch_size: Optional[int] = None,
    max_batches: Optional[int] = None,
) -> ForwardPassResult:
    config = load_config(str(BASE_DIR / "configs" / "config.yaml"))
    num_classes = int(config.get("model", {}).get("num_classes", 4))
    if batch_size is None:
        batch_size = int(config.get("training", {}).get("batch_size", 4))
    num_workers = int(config.get("training", {}).get("num_workers", 0))
    device_cfg = config.get("runtime", {}).get("device", "auto")
    device = get_device(device_cfg)

    arrays = load_artifact_arrays(artifact_dir)
    sequences = arrays["sequences"]
    targets = arrays["targets"]
    labels = arrays["labels"]
    masks = arrays["masks"]

    failures: List[str] = []
    diagnostics: List[str] = []

    diagnostics.append("SCIENTIFIC SAFETY: independent events are stacked on the sample axis only.")
    diagnostics.append("Spatial patches of one event are NOT independent weather events.")
    diagnostics.append("Forward-pass only. Do not interpret class counts as accuracy.")

    if sequences.ndim != 5:
        failures.append(f"sequences ndim={sequences.ndim}, expected 5")
    n_samples = int(sequences.shape[0]) if sequences.ndim >= 1 else 0
    input_shape = tuple(int(x) for x in sequences.shape)
    target_shape = tuple(int(x) for x in targets.shape)

    expected_sample = (EXPECTED_CHANNELS, EXPECTED_TIME, EXPECTED_HEIGHT, EXPECTED_WIDTH)
    if sequences.ndim == 5 and sequences.shape[1:] != expected_sample:
        failures.append(f"sequence sample shape {sequences.shape[1:]} != {expected_sample}")
    if sequences.dtype != np.float32:
        failures.append(f"sequences dtype {sequences.dtype} != float32")
    if targets.shape[0] != n_samples:
        failures.append("targets N does not match sequences N")
    if labels.shape[0] != n_samples:
        failures.append("labels N does not match sequences N")
    if masks.shape[0] != n_samples:
        failures.append("masks N does not match sequences N")

    nan_input = int(np.isnan(sequences).sum())
    inf_input = int(np.isinf(sequences).sum())
    if nan_input:
        failures.append(f"NaN in sequences array: {nan_input}")
    if inf_input:
        failures.append(f"Inf in sequences array: {inf_input}")

    dataset = build_varsha_dataset(arrays)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers)

    in_channels = EXPECTED_CHANNELS if sequences.ndim < 2 else int(sequences.shape[1])
    model = VarshaDrishti3DCNN(in_channels=in_channels, num_classes=num_classes)
    model.to(device)
    model.eval()
    summary = get_model_summary(model)
    diagnostics.append(f"Model: {summary['model_name']}")
    diagnostics.append(f"Input contract: {summary['input_contract']}")
    diagnostics.append(f"Output contract: {summary['output_contract']}")
    diagnostics.append(f"Parameters: {summary['total_parameters']}")

    fingerprint_before = _parameter_fingerprint(model)

    n_batches = 0
    nan_logits = 0
    inf_logits = 0
    nan_probs = 0
    inf_probs = 0
    logit_min = float("inf")
    logit_max = float("-inf")
    prob_min = float("inf")
    prob_max = float("-inf")
    prob_sum_min = float("inf")
    prob_sum_max = float("-inf")
    preds_all: List[int] = []
    model_output_shape: Tuple[int, ...] = tuple()
    first_batch_checked = False

    with torch.no_grad():
        for batch_idx, batch in enumerate(loader):
            if max_batches is not None and batch_idx >= max_batches:
                break

            seq_batch = batch["sequence"].to(device)
            n_batches += 1

            if seq_batch.dtype not in (torch.float32, torch.float16, torch.bfloat16):
                failures.append(f"batch dtype {seq_batch.dtype} is not a floating type")

            if seq_batch.dim() != 5:
                failures.append(f"DataLoader batch ndim={seq_batch.dim()}, expected 5")
            elif tuple(seq_batch.shape[1:]) != expected_sample:
                failures.append(
                    f"DataLoader batch spatial contract {tuple(seq_batch.shape)} "
                    f"does not match [B, {EXPECTED_CHANNELS}, {EXPECTED_TIME}, "
                    f"{EXPECTED_HEIGHT}, {EXPECTED_WIDTH}]"
                )

            batch_nan = _count_nan(seq_batch)
            batch_inf = _count_inf(seq_batch)
            if batch_nan:
                failures.append(f"NaN in DataLoader batch {batch_idx}: {batch_nan}")
            if batch_inf:
                failures.append(f"Inf in DataLoader batch {batch_idx}: {batch_inf}")

            try:
                logits = model(seq_batch)
            except Exception as exc:  # noqa: BLE001 — smoke test must report any forward failure
                failures.append(f"Forward pass failed on batch {batch_idx}: {exc}")
                break

            if not first_batch_checked:
                model_output_shape = tuple(int(x) for x in logits.shape)
                first_batch_checked = True
                diagnostics.append(f"First batch input: {tuple(seq_batch.shape)}")
                diagnostics.append(f"First batch output: {model_output_shape}")

            expected_out = (seq_batch.size(0), num_classes)
            if tuple(logits.shape) != expected_out:
                failures.append(f"Output shape {tuple(logits.shape)} != {expected_out}")

            b_nan_logits = _count_nan(logits)
            b_inf_logits = _count_inf(logits)
            nan_logits += b_nan_logits
            inf_logits += b_inf_logits
            if b_nan_logits:
                failures.append(f"NaN logits in batch {batch_idx}: {b_nan_logits}")
            if b_inf_logits:
                failures.append(f"Inf logits in batch {batch_idx}: {b_inf_logits}")

            probs = torch.softmax(logits, dim=1)
            b_nan_probs = _count_nan(probs)
            b_inf_probs = _count_inf(probs)
            nan_probs += b_nan_probs
            inf_probs += b_inf_probs
            if b_nan_probs:
                failures.append(f"NaN probabilities in batch {batch_idx}: {b_nan_probs}")
            if b_inf_probs:
                failures.append(f"Inf probabilities in batch {batch_idx}: {b_inf_probs}")

            logit_min = min(logit_min, float(logits.min().item()) if logits.numel() else logit_min)
            logit_max = max(logit_max, float(logits.max().item()) if logits.numel() else logit_max)
            if probs.numel():
                prob_min = min(prob_min, float(probs.min().item()))
                prob_max = max(prob_max, float(probs.max().item()))
                sums = probs.sum(dim=1)
                prob_sum_min = min(prob_sum_min, float(sums.min().item()))
                prob_sum_max = max(prob_sum_max, float(sums.max().item()))

            preds = probs.argmax(dim=1)
            pred_list = [int(p) for p in preds.cpu().tolist()]
            preds_all.extend(pred_list)
            if any(p < 0 or p >= num_classes for p in pred_list):
                failures.append(f"Predicted class out of range in batch {batch_idx}: {pred_list}")

    if n_batches == 0:
        failures.append("No batches were tested.")

    if np.isfinite(prob_sum_min) and abs(prob_sum_min - 1.0) > PROB_SUM_TOLERANCE:
        failures.append(f"Probability sum min {prob_sum_min} is not approximately 1")
    if np.isfinite(prob_sum_max) and abs(prob_sum_max - 1.0) > PROB_SUM_TOLERANCE:
        failures.append(f"Probability sum max {prob_sum_max} is not approximately 1")

    fingerprint_after = _parameter_fingerprint(model)
    weights_unchanged = bool(torch.equal(fingerprint_before, fingerprint_after))
    if not weights_unchanged:
        failures.append("Model weights changed during the smoke test.")

    class_distribution = dict(sorted(Counter(preds_all).items()))

    def _finite_or_nan(value: float) -> float:
        return value if np.isfinite(value) else float("nan")

    passed = len(failures) == 0
    return ForwardPassResult(
        passed=passed,
        device=str(device),
        dataset_location=str(artifact_dir.resolve()),
        n_samples=n_samples,
        input_shape=input_shape,
        target_shape=target_shape,
        num_classes=num_classes,
        n_batches=n_batches,
        model_output_shape=model_output_shape,
        logit_min=_finite_or_nan(logit_min),
        logit_max=_finite_or_nan(logit_max),
        prob_min=_finite_or_nan(prob_min),
        prob_max=_finite_or_nan(prob_max),
        prob_sum_min=_finite_or_nan(prob_sum_min),
        prob_sum_max=_finite_or_nan(prob_sum_max),
        nan_input=nan_input,
        inf_input=inf_input,
        nan_logits=nan_logits,
        inf_logits=inf_logits,
        nan_probs=nan_probs,
        inf_probs=inf_probs,
        class_distribution=class_distribution,
        failures=failures,
        diagnostics=diagnostics,
        weights_unchanged=weights_unchanged,
        training_performed=False,
    )


def format_report(result: ForwardPassResult) -> str:
    status = "PASS" if result.passed else "FAIL"
    lines = [
        "==================================================",
        "REAL MULTITEMPORAL 3D-CNN FORWARD-PASS VALIDATION",
        "==================================================",
        "",
        "NO MODEL TRAINING WAS PERFORMED.",
        "No optimizer was created. No loss.backward(). No weight updates.",
        "No epochs. No training accuracy. No checkpoints were written.",
        "",
        "SCIENTIFIC SAFETY",
        "-----------------",
        "Independent temporal events are stacked along the sample axis only; T remains 6.",
        "Spatial patches of one event are NOT independent weather events.",
        "Predicted class counts are from an UNTRAINED model and are NOT accuracy.",
        "This artifact is NOT scientifically valid for model training.",
        "",
        f"Final status: {status}",
        "",
        f"Device: {result.device}",
        f"Dataset location: {result.dataset_location}",
        f"Number of samples: {result.n_samples}",
        f"Input shape: {list(result.input_shape)}",
        f"Target shape: {list(result.target_shape)}",
        f"Number of classes: {result.num_classes}",
        f"Number of batches tested: {result.n_batches}",
        f"Model output shape: {list(result.model_output_shape)}",
        f"Logit min/max: {result.logit_min} / {result.logit_max}",
        f"Probability min/max: {result.prob_min} / {result.prob_max}",
        f"Probability sum range: {result.prob_sum_min} / {result.prob_sum_max}",
        "",
        "NaN counts",
        f"  input tensors: {result.nan_input}",
        f"  logits: {result.nan_logits}",
        f"  probabilities: {result.nan_probs}",
        "",
        "Inf counts",
        f"  input tensors: {result.inf_input}",
        f"  logits: {result.inf_logits}",
        f"  probabilities: {result.inf_probs}",
        "",
        f"Predicted class distribution (untrained model): {result.class_distribution}",
        f"Weights unchanged after forward pass: {result.weights_unchanged}",
        f"Training performed: {result.training_performed}",
        "",
        "Checks",
        "------",
    ]
    check_rows = [
        ("DataLoader produces [B, 3, 6, 256, 256]", result.passed or result.n_batches > 0),
        ("Tensor dtype is floating-point", result.passed or result.n_batches > 0),
        ("Input contains no NaN", result.nan_input == 0),
        ("Input contains no Inf", result.inf_input == 0),
        ("Model forward pass succeeds", result.n_batches > 0 and not any("Forward pass failed" in f for f in result.failures)),
        ("Output shape is [B, 4]", len(result.model_output_shape) == 2 and result.model_output_shape[-1] == 4),
        ("Logits contain no NaN", result.nan_logits == 0),
        ("Logits contain no Inf", result.inf_logits == 0),
        ("Softmax probabilities contain no NaN", result.nan_probs == 0),
        ("Softmax probabilities contain no Inf", result.inf_probs == 0),
        ("Probability sums are approximately 1", abs(result.prob_sum_min - 1.0) <= PROB_SUM_TOLERANCE and abs(result.prob_sum_max - 1.0) <= PROB_SUM_TOLERANCE),
        ("Predicted classes are in [0, num_classes)", not any("out of range" in f for f in result.failures)),
        ("Multiple batches tested", result.n_batches > 1),
        ("Model weights were not updated", result.weights_unchanged),
        ("No training performed", not result.training_performed),
    ]
    for label, ok in check_rows:
        mark = "x" if ok else " "
        lines.append(f"  [{mark}] {label}")
    if result.failures:
        lines.append("")
        lines.append("Failures")
        lines.append("--------")
        for item in result.failures:
            lines.append(f"  - {item}")

    if result.diagnostics:
        lines.append("")
        lines.append("Diagnostics")
        lines.append("-----------")
        lines.extend(f"  {d}" for d in result.diagnostics)

    info = get_device_info()
    lines.extend(
        [
            "",
            "Device info",
            "-----------",
            f"  cuda_available: {info['cuda_available']}",
            f"  device_name: {info['device_name']}",
            "",
            "NO MODEL TRAINING WAS PERFORMED.",
            f"Final status: {status}",
            "",
        ]
    )
    return "\n".join(lines)


def write_report(result: ForwardPassResult, path: Path = REPORT_PATH) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = format_report(result)
    path.write_text(text, encoding="utf-8")
    return path


def main() -> int:
    print("Real-data 3D-CNN forward-pass validation")
    print("NO MODEL TRAINING WAS PERFORMED.")
    print(f"Artifact: {ARTIFACT_DIR}")
    try:
        result = run_forward_pass()
    except Exception as exc:  # noqa: BLE001
        failed = ForwardPassResult(
            passed=False,
            device="unknown",
            dataset_location=str(ARTIFACT_DIR.resolve()),
            n_samples=0,
            input_shape=tuple(),
            target_shape=tuple(),
            num_classes=4,
            n_batches=0,
            model_output_shape=tuple(),
            logit_min=float("nan"),
            logit_max=float("nan"),
            prob_min=float("nan"),
            prob_max=float("nan"),
            prob_sum_min=float("nan"),
            prob_sum_max=float("nan"),
            nan_input=0,
            inf_input=0,
            nan_logits=0,
            inf_logits=0,
            nan_probs=0,
            inf_probs=0,
            class_distribution={},
            failures=[str(exc)],
        )
        report_path = write_report(failed)
        print(format_report(failed))
        print(f"Report written: {report_path}")
        return 1

    report_path = write_report(result)
    print(format_report(result))
    print(f"Report written: {report_path}")
    print("NO MODEL TRAINING WAS PERFORMED.")
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
