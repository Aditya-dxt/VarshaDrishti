# 🌧️ VarshaDrishti

### 🛰️ Explainable AI for Satellite-Based Heavy Rainfall Prediction

> **VarshaDrishti** is an explainable satellite intelligence system that uses real **INSAT-3DR satellite observations**, temporal deep learning, and explainable AI to identify and assess rainfall risk.

<p align="center">
  <img src="https://img.shields.io/badge/Project-VarshaDrishti-0B3D91?style=for-the-badge" alt="VarshaDrishti">
  <img src="https://img.shields.io/badge/Domain-Satellite%20AI-1565C0?style=for-the-badge" alt="Satellite AI">
  <img src="https://img.shields.io/badge/Deep%20Learning-3D--CNN-6A1B9A?style=for-the-badge" alt="3D CNN">
  <img src="https://img.shields.io/badge/XAI-Grad--CAM%20%7C%20SHAP-E65100?style=for-the-badge" alt="XAI">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Data-INSAT--3DR-00897B?style=flat-square" alt="INSAT-3DR">
  <img src="https://img.shields.io/badge/Source-MOSDAC-455A64?style=flat-square" alt="MOSDAC">
  <img src="https://img.shields.io/badge/Framework-PyTorch-EE4C2C?style=flat-square" alt="PyTorch">
  <img src="https://img.shields.io/badge/Python-3.x-3776AB?style=flat-square" alt="Python">
  <img src="https://img.shields.io/badge/Status-In%20Development-F9A825?style=flat-square" alt="Status">
</p>

---

## 📌 Table of Contents

- [🌍 Overview](#-overview)
- [🎯 Problem Statement](#-problem-statement)
- [💡 Solution](#-solution)
- [✨ Key Features](#-key-features)
- [🏗️ System Architecture](#️-system-architecture)
- [🛰️ Data Sources](#️-data-sources)
- [🤖 Machine Learning Pipeline](#-machine-learning-pipeline)
- [🧠 3D-CNN](#-3d-cnn)
- [🔍 Explainable AI](#-explainable-ai)
- [📊 Rainfall Classes](#-rainfall-classes)
- [📁 Repository Structure](#-repository-structure)
- [⚙️ Configuration](#️-configuration)
- [🚀 Installation](#-installation)
- [🧪 Testing](#-testing)
- [📥 Data Acquisition](#-data-acquisition)
- [🔬 Dataset Construction](#-dataset-construction)
- [🏋️ Model Training](#️-model-training)
- [📈 Model Evaluation](#-model-evaluation)
- [🔮 Inference](#-inference)
- [🌐 Person 2 Integration](#-person-2-integration)
- [🔄 Dynamic Inference](#-dynamic-inference)
- [🛡️ Data Integrity & Scientific Rules](#️-data-integrity--scientific-rules)
- [🔐 Security](#-security)
- [🧪 Development Status](#-development-status)
- [🗺️ Roadmap](#️-roadmap)
- [👥 Team Responsibilities](#-team-responsibilities)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

---

# 🌍 Overview

**VarshaDrishti** combines satellite remote sensing, temporal deep learning, and explainable AI to provide rainfall-risk intelligence from satellite observations.

The system is designed around **real INSAT-3DR satellite data obtained through MOSDAC**.

The core idea is:

```text
🛰️ Real Satellite Observation
            ↓
      Data Ingestion
            ↓
     HDF5 Processing
            ↓
       Calibration
            ↓
      Quality Control
            ↓
    Spatial Processing
            ↓
   Temporal Sequences
            ↓
      3D-CNN Model
            ↓
    Rainfall-Risk Class
            ↓
     ┌──────┴──────┐
     ↓             ↓
  Grad-CAM       SHAP/XAI
     │             │
     └──────┬──────┘
            ↓
      RainPredictor
            ↓
     Standard Output
            ↓
       FastAPI Layer
            ↓
    VarshaDrishti UI
```

The final system is intended to be **dynamic**, **data-driven**, and **explainable** rather than a static visualization or mock AI dashboard.

---

# 🎯 Problem Statement

Extreme rainfall can develop rapidly and create significant risks for:

- 🌧️ Urban flooding
- 🚨 Disaster response
- 🏙️ Infrastructure
- 🚗 Transportation
- 🌾 Agriculture
- 🏘️ Human settlements
- 🌊 Water-management systems

Traditional weather information can provide broad forecasts, but satellite observations provide valuable spatial and temporal information about atmospheric conditions.

The challenge is not only to predict rainfall risk, but also to answer:

> **"Why did the model make this prediction?"**

VarshaDrishti addresses both parts:

```text
Prediction
    +
Explainability
    =
Actionable Satellite Intelligence
```

---

# 💡 Solution

VarshaDrishti processes temporal sequences of real INSAT-3DR satellite observations using a **3D Convolutional Neural Network (3D-CNN)**.

The model learns both:

- 🗺️ **Spatial patterns** from satellite imagery
- ⏱️ **Temporal patterns** across consecutive observations

The prediction is then explained using:

### 🔥 Grad-CAM

Answers:

> **"Where did the model focus?"**

### 📊 Feature / SHAP Explanation

Answers:

> **"Which model features or representations contributed to the prediction?"**

This produces a complete pipeline:

```text
Satellite Data
      ↓
Temporal Deep Learning
      ↓
Rainfall Risk
      ↓
Explainable AI
      ↓
Human-Interpretable Intelligence
```

---

# ✨ Key Features

## 🛰️ Real Satellite Data

Uses real **INSAT-3DR** observations rather than fabricated imagery.

Primary satellite product:

```text
3RIMG_L1B_STD
```

---

## 🌧️ Rainfall Target Data

Rainfall information is intended to be derived from:

```text
3RIMG_L2B_IMC
```

The exact temporal matching and target construction are data-dependent and will be finalized after inspection of the real datasets.

---

## 🧠 Temporal 3D-CNN

Instead of treating every satellite image independently, VarshaDrishti processes a sequence:

```text
T-5 → T-4 → T-3 → T-2 → T-1 → T
```

The model learns temporal evolution in addition to spatial patterns.

---

## 🔥 Grad-CAM

Provides a visual explanation of the model's attention.

```text
Original Satellite Image
          +
      Model Output
          ↓
       Grad-CAM
          ↓
    Heatmap / Overlay
```

---

## 📊 Explainable Features

Feature-level explanations can be provided where technically meaningful.

Potential representations may include:

- Satellite channel contribution
- Temporal-frame contribution
- Engineered feature contribution

The exact representation will be determined from the actual model and dataset.

---

## 📈 Model Evaluation

The system is designed to report:

- Accuracy
- Precision
- Recall
- F1-score
- Macro F1
- Weighted F1
- Per-class metrics
- Confusion matrix

Special attention is given to the **High Impact** rainfall class.

---

## 🔄 Dynamic Inference

Once the model and ingestion pipeline are complete:

```text
New Satellite Observation
          ↓
Data Validation
          ↓
Preprocessing
          ↓
Temporal Buffer
          ↓
Existing Trained Model
          ↓
Prediction
          ↓
XAI
```

The model does **not** retrain every time a new satellite observation arrives.

---

# 🏗️ System Architecture

```text
                         ┌─────────────────────┐
                         │       MOSDAC        │
                         │  INSAT-3DR Data     │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   Data Ingestion    │
                         │     + HDF5 Reader   │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   Preprocessing     │
                         │ Calibration / QC    │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Temporal Sequences  │
                         │  T-5 ... T-1 ... T  │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │      3D-CNN         │
                         │ Spatial + Temporal  │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Rainfall Prediction │
                         │   4 Risk Classes    │
                         └──────────┬──────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
          ┌──────────────────┐            ┌──────────────────┐
          │     Grad-CAM     │            │ Feature / SHAP   │
          │ Where did model  │            │ What influenced  │
          │      focus?      │            │   prediction?    │
          └────────┬─────────┘            └────────┬─────────┘
                   │                               │
                   └───────────────┬───────────────┘
                                   ▼
                         ┌─────────────────────┐
                         │    RainPredictor    │
                         │ Standardized Output │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │    Person 2 API     │
                         │       FastAPI       │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ VarshaDrishti Web   │
                         │      Dashboard      │
                         └─────────────────────┘
```

---

# 🛰️ Data Sources

## Primary Satellite Dataset

| Property | Value |
|---|---|
| Satellite | INSAT-3DR |
| Sensor | Imager |
| Product | `3RIMG_L1B_STD` |
| Level | Level-1B |
| Source | MOSDAC |
| Purpose | Model input |

The internal HDF5 structure is intentionally **not hardcoded**.

The following parameters will be determined from the actual downloaded file:

- Dataset paths
- Channel names
- Channel dimensions
- Calibration parameters
- Fill values
- Units
- Spatial resolution
- Timestamp representation
- Geolocation representation

---

## Rainfall Target Dataset

| Property | Value |
|---|---|
| Satellite | INSAT-3DR |
| Product | `3RIMG_L2B_IMC` |
| Purpose | Rainfall target / label construction |
| Source | MOSDAC |

The temporal matching between satellite observations and rainfall targets will use a configurable matching strategy.

---

# 🤖 Machine Learning Pipeline

The ML pipeline consists of the following stages:

```text
1. Data Acquisition
       ↓
2. HDF5 Inspection
       ↓
3. Satellite Data Reading
       ↓
4. Calibration
       ↓
5. Quality Control
       ↓
6. Spatial Processing
       ↓
7. Temporal Matching
       ↓
8. Rainfall Target Construction
       ↓
9. Temporal Sequence Creation
       ↓
10. PyTorch Dataset
       ↓
11. 3D-CNN Training
       ↓
12. Validation
       ↓
13. Evaluation
       ↓
14. Grad-CAM
       ↓
15. Feature / SHAP Explanation
       ↓
16. RainPredictor
       ↓
17. Standardized Output
```

---

# 🧠 3D-CNN

The baseline model uses 3D convolutions to learn from both spatial and temporal dimensions.

Expected input convention:

```text
[B, C, T, H, W]
```

Where:

| Symbol | Meaning |
|---|---|
| B | Batch size |
| C | Number of input channels |
| T | Number of temporal frames |
| H | Image height |
| W | Image width |

Expected output:

```text
[B, 4]
```

representing four rainfall-risk classes.

### Baseline Architecture

```text
Input
  ↓
Conv3D
  ↓
BatchNorm3D
  ↓
ReLU
  ↓
Pooling
  ↓
Conv3D
  ↓
BatchNorm3D
  ↓
ReLU
  ↓
Pooling
  ↓
Conv3D
  ↓
BatchNorm3D
  ↓
ReLU
  ↓
Adaptive Global Pooling
  ↓
Flatten
  ↓
Dropout
  ↓
Fully Connected Layer
  ↓
4-Class Output
```

The architecture is intentionally lightweight and configurable for hackathon hardware.

---

# 📊 Rainfall Classes

The initial conceptual classification scheme is:

| Class ID | Class | Description |
|---:|---|---|
| `0` | 🌤️ No Rain | No significant rainfall |
| `1` | 🌦️ Moderate | Moderate rainfall conditions |
| `2` | 🌧️ Heavy | Heavy rainfall conditions |
| `3` | ⛈️ High Impact | High-impact/extreme rainfall risk |

> ⚠️ **Important:** Final rainfall thresholds are not hardcoded until the actual rainfall target dataset has been inspected and the classification methodology has been established.

Thresholds will be configurable through:

```yaml
rainfall_thresholds:
    no_rain:
    moderate:
    heavy:
    high_impact:
```

---

# 🔍 Explainable AI

Explainability is a core component of VarshaDrishti.

## 🔥 Grad-CAM

Grad-CAM is intended to show **where the model focused** while making a prediction.

```text
Satellite Sequence
       ↓
     3D-CNN
       ↓
Prediction
       ↓
Gradients + Activations
       ↓
Grad-CAM
       ↓
Heatmap
       ↓
Overlay
```

Potential outputs:

```text
outputs/gradcam/

prediction_original.png
prediction_heatmap.png
prediction_overlay.png
prediction.json
```

### Important

Grad-CAM outputs used in the final demonstration must be generated from:

```text
REAL MODEL
+
REAL SATELLITE DATA
```

Random or manually generated heatmaps are not valid project results.

---

## 📊 SHAP / Feature Explanation

SHAP or another suitable feature-level explanation approach may be used where technically meaningful.

Potential representations include:

- Channel contribution
- Temporal-frame contribution
- Engineered feature contribution

The project will avoid forcing SHAP onto an impractical number of raw image pixels when a more interpretable representation is possible.

---

# 📁 Repository Structure

```text
varshadrishti-ml/
│
├── data/
│   ├── raw/
│   │   ├── insat3dr_l1b/
│   │   └── insat3dr_imc/
│   │
│   ├── interim/
│   │
│   └── processed/
│
├── notebooks/
│   ├── 01_inspect_hdf5.ipynb
│   ├── 02_visualize_satellite.ipynb
│   ├── 03_build_dataset.ipynb
│   ├── 04_train_model.ipynb
│   ├── 05_evaluate_model.ipynb
│   └── 06_gradcam.ipynb
│
├── src/
│   │
│   ├── ingestion/
│   │   └── mosdac_downloader.py
│   │
│   ├── data/
│   │   ├── hdf5_reader.py
│   │   ├── metadata.py
│   │   ├── spatial_crop.py
│   │   ├── temporal_matcher.py
│   │   ├── sequence_builder.py
│   │   ├── label_builder.py
│   │   ├── dataset.py
│   │   ├── splitter.py
│   │   └── validation.py
│   │
│   ├── preprocessing/
│   │   ├── calibration.py
│   │   ├── normalization.py
│   │   ├── quality_control.py
│   │   └── pipeline.py
│   │
│   ├── models/
│   │   └── cnn3d.py
│   │
│   ├── training/
│   │   ├── train.py
│   │   └── validate.py
│   │
│   ├── evaluation/
│   │   ├── metrics.py
│   │   ├── confusion_matrix.py
│   │   └── report.py
│   │
│   ├── xai/
│   │   ├── gradcam.py
│   │   └── shap_explainer.py
│   │
│   ├── inference/
│   │   ├── predictor.py
│   │   ├── rain_predictor.py
│   │   └── schema.py
│   │
│   ├── outputs/
│   │   └── serializer.py
│   │
│   └── utils/
│       ├── config.py
│       ├── device.py
│       ├── logger.py
│       └── checkpoint.py
│
├── configs/
│   └── config.yaml
│
├── models/
│   └── checkpoints/
│
├── outputs/
│   ├── predictions/
│   ├── gradcam/
│   ├── shap/
│   ├── metrics/
│   └── logs/
│
├── tests/
│
├── requirements.txt
├── README.md
├── INTEGRATION.md
└── .gitignore
```

---

# ⚙️ Configuration

Project configuration is centralized in:

```text
configs/config.yaml
```

Example:

```yaml
data:
  dataset_id: "3RIMG_L1B_STD"
  rainfall_dataset_id: "3RIMG_L2B_IMC"

  sequence_length: null
  image_size: null

  channels: []

  roi:
    min_lat: null
    max_lat: null
    min_lon: null
    max_lon: null

preprocessing:
  normalization: null
  resize_method: null
  missing_value_strategy: null

model:
  num_classes: 4
  dropout: 0.3

training:
  batch_size: 4
  epochs: 30
  learning_rate: 0.001
  weight_decay: 0.0001
  seed: 42

inference:
  checkpoint_path: "models/checkpoints/best_model.pth"

runtime:
  device: "auto"
```

### Why are some values `null`?

Because data-dependent parameters must be determined from the **actual INSAT-3DR HDF5 files**.

We intentionally do not guess:

- Channel configuration
- Sequence length
- Image dimensions
- ROI
- Normalization
- Missing-value strategy

---

# 🚀 Installation

## 1. Clone the repository

```bash
git clone https://github.com/Aditya-dxt/VarshaDrishti.git
cd VarshaDrishti
```

---

## 2. Navigate to the ML project

```bash
cd varshadrishti-ml
```

---

## 3. Create a virtual environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 4. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 5. Verify Python

```bash
python --version
```

---

## 6. Verify PyTorch

```bash
python -c "import torch; print('PyTorch:', torch.__version__); print('CUDA available:', torch.cuda.is_available())"
```

If CUDA is available, the project can use the GPU.

Otherwise, CPU fallback is supported.

---

# 🧪 Testing

Run the utility tests:

```bash
python tests/test_utils.py
```

Or, if the project uses pytest:

```bash
pytest
```

Tests are intended to verify:

- Configuration loading
- Device detection
- Logging
- Data interfaces
- Sequence construction
- Temporal splitting
- Dataset behavior
- Model forward pass
- Checkpoint utilities
- Output schemas

---

# 📥 Data Acquisition

The primary satellite data source is **MOSDAC**.

Required product:

```text
INSAT-3DR
    ↓
Imager
    ↓
3RIMG_L1B_STD
```

Rainfall target data:

```text
INSAT-3DR
    ↓
3RIMG_L2B_IMC
```

### Current access mode

The project currently operates with the satellite data available under the team's approved MOSDAC General User access.

Privileged/NRT access may be used later if approved.

### Important

Do not expose MOSDAC credentials in:

- Git
- GitHub
- source code
- README files
- screenshots
- frontend code

Use secure local configuration/environment variables.

---

# 🔬 Dataset Construction

Dataset construction follows:

```text
INSAT-3DR L1B
      ↓
HDF5 Inspection
      ↓
Data Extraction
      ↓
Calibration
      ↓
Quality Control
      ↓
Spatial Processing
      ↓
Temporal Matching
      ↓
Rainfall Target
      ↓
Sequence Builder
      ↓
PyTorch Dataset
```

---

## Temporal Sequences

The model is designed to use temporal sequences rather than isolated images.

Conceptually:

```text
T-5
 ↓
T-4
 ↓
T-3
 ↓
T-2
 ↓
T-1
 ↓
T
 ↓
3D-CNN
```

The exact sequence length will be determined after analyzing the actual satellite temporal resolution.

---

## Train / Validation / Test Split

Because this is temporal satellite data, chronological splitting is preferred.

```text
Older observations
        ↓
      TRAIN
        ↓
Later observations
        ↓
   VALIDATION
        ↓
Latest held-out observations
        ↓
       TEST
```

This reduces the risk of temporal leakage from highly overlapping sequences.

---

# 🏋️ Model Training

Training will only begin after a verified real dataset has been constructed.

Conceptual pipeline:

```text
Real Dataset
     ↓
DataLoader
     ↓
3D-CNN
     ↓
Loss Function
     ↓
Optimizer
     ↓
Validation
     ↓
Checkpoint
```

The best model should be selected using an appropriate validation criterion such as:

- Macro F1
- Weighted F1
- High-impact F1
- High-impact recall

rather than relying solely on overall accuracy.

---

# 🚫 No Synthetic Training

This project follows a strict data-integrity policy.

### Synthetic data is allowed ONLY for:

```text
Unit Tests
    ↓
Tensor Shape Tests
    ↓
Model Forward-Pass Tests
    ↓
Software Integration Tests
```

For example:

```python
dummy_input = torch.randn(
    batch_size,
    channels,
    time_steps,
    height,
    width
)

output = model(dummy_input)
```

This is acceptable as a **software smoke test**.

### Synthetic data is NOT allowed for:

```text
❌ Final model training
❌ Final checkpoint
❌ Accuracy
❌ Precision
❌ Recall
❌ F1
❌ Confusion matrix
❌ Final prediction
❌ Final Grad-CAM
❌ Final SHAP
❌ Hackathon presentation results
```

A synthetic model is **NOT** the VarshaDrishti model.

If a synthetic checkpoint is ever created for testing, it must be clearly named:

```text
TEST_ONLY_synthetic_smoke_test.pth
```

and must never be confused with:

```text
best_model.pth
```

The final:

```text
models/checkpoints/best_model.pth
```

must only represent a model trained on real satellite/rainfall data.

---

# 📈 Model Evaluation

Evaluation will include:

| Metric | Purpose |
|---|---|
| Accuracy | Overall classification performance |
| Precision | Reliability of positive predictions |
| Recall | Ability to identify actual classes |
| F1 | Balance between precision and recall |
| Macro F1 | Equal weighting across classes |
| Weighted F1 | Accounts for class distribution |
| Per-class metrics | Detailed class performance |
| Confusion Matrix | Class-level error analysis |

Special attention is given to:

```text
⛈️ HIGH IMPACT
```

because missing high-impact rainfall events can have significant consequences.

---

# 🔮 Inference

The final inference interface is:

```text
src/inference/rain_predictor.py
```

Conceptually:

```python
predictor = RainPredictor(
    checkpoint_path="models/checkpoints/best_model.pth",
    config=config
)

result = predictor.predict(
    sequence,
    metadata=metadata
)
```

Expected output structure:

```json
{
  "prediction": {
    "class_id": 3,
    "label": "high_impact",
    "confidence": 0.91
  },
  "probabilities": {
    "no_rain": 0.01,
    "moderate": 0.03,
    "heavy": 0.05,
    "high_impact": 0.91
  },
  "xai": {
    "gradcam": {
      "image_url": "..."
    },
    "shap": {
      "features": []
    }
  },
  "metadata": {
    "timestamp": "...",
    "latitude": null,
    "longitude": null
  }
}
```

> ⚠️ The numerical values above are **schema examples only**. They are not actual project results.

---

# 🌐 Person 2 Integration

Person 2 is developing the FastAPI backend and React application.

The integration boundary is:

```text
                PERSON 1
                   │
                   ▼
             RainPredictor
                   │
                   ▼
          Standardized JSON
                   │
══════════════════════════════
           HANDOFF
══════════════════════════════
                   │
                   ▼
             Person 2 API
                   │
                   ▼
                React
                   │
                   ▼
          VarshaDrishti UI
```

Person 2 should not need to know:

- PyTorch architecture
- Model weights
- Tensor internals
- Training code
- HDF5 implementation
- Preprocessing internals

Person 2 only consumes the standardized prediction contract.

See:

```text
INTEGRATION.md
```

for the complete handoff specification.

---

# 🔄 Dynamic Inference

The eventual dynamic pipeline is:

```text
             MOSDAC
                ↓
      New Satellite Observation
                ↓
        Duplicate Check
                ↓
        Data Validation
                ↓
          Preprocessing
                ↓
       Temporal Frame Buffer
                ↓
       Valid Sequence?
          ↙          ↘
        NO            YES
        ↓              ↓
      WAIT       RainPredictor
                       ↓
                  Prediction
                       ↓
                 Grad-CAM
                       ↓
                Feature XAI
                       ↓
               Standard JSON
                       ↓
                Person 2 API
```

### Important

New data should trigger **inference**, not automatic retraining.

```text
NEW DATA
   ↓
INFERENCE
```

not:

```text
NEW DATA
   ↓
RETRAIN MODEL
```

Training and inference remain separate processes.

---

# 🛡️ Data Integrity & Scientific Rules

VarshaDrishti follows these principles:

### 1. Real Data First

Final results must be based on real satellite and rainfall data.

### 2. No Fabricated Metrics

Never invent:

```text
Accuracy
Precision
Recall
F1
Confusion Matrix
```

### 3. No Fake XAI

Grad-CAM and SHAP outputs must correspond to the actual trained model and actual inputs.

### 4. No Data Leakage

Temporal data must be split carefully.

### 5. No Silent Synthetic Fallback

If real data is unavailable:

```text
STOP
```

Do not automatically generate random data.

### 6. No Credential Exposure

MOSDAC credentials must never be committed.

### 7. Reproducibility

Record:

- Configuration
- Random seed
- Dataset information
- Model configuration
- Training configuration
- Checkpoint
- Environment information

---

# 🔐 Security

Never commit:

```text
.env
config.local.json
MOSDAC credentials
API keys
passwords
tokens
```

The `.gitignore` should exclude:

```text
venv/
__pycache__/
.env
*.env
data/raw/
data/interim/
data/processed/
models/checkpoints/
outputs/
*.h5
*.hdf5
```

Raw satellite files should remain local unless a separate approved data-storage strategy is used.

---

# 🧪 Development Status

### Current Status

```text
🟢 Phase A — Environment + Configuration
🟢 Phase B — Utilities + Logging
🟢 Phase C — Data Interfaces
🟡 Phase D — 3D-CNN
⚪ Phase E — Training Infrastructure
⚪ Phase F — Real Dataset Construction
⚪ Phase G — Real Model Training
⚪ Phase H — Evaluation
⚪ Phase I — Grad-CAM
⚪ Phase J — Feature / SHAP Explanation
⚪ Phase K — RainPredictor
⚪ Phase L — Dynamic Inference
⚪ Phase M — Person 2 Integration
```

> Status should be updated as development progresses.

---

# 🗺️ Roadmap

## Phase 1 — Infrastructure

- [x] Repository setup
- [x] Python environment
- [x] Configuration system
- [x] Device detection
- [x] Logging
- [x] Git integration

---

## Phase 2 — Data Interfaces

- [ ] HDF5 reader
- [ ] Metadata representation
- [ ] Satellite frame abstraction
- [ ] Temporal matcher
- [ ] Sequence builder
- [ ] Spatial cropper
- [ ] Dataset interface
- [ ] Chronological splitter
- [ ] Data validation

---

## Phase 3 — Real Data

- [ ] Obtain real `3RIMG_L1B_STD`
- [ ] Inspect HDF5 structure
- [ ] Identify channels
- [ ] Determine dimensions
- [ ] Determine calibration
- [ ] Determine spatial resolution
- [ ] Determine geolocation
- [ ] Determine temporal characteristics
- [ ] Obtain rainfall target data
- [ ] Match observations
- [ ] Build real dataset

---

## Phase 4 — Machine Learning

- [ ] 3D-CNN baseline
- [ ] Real training
- [ ] Validation
- [ ] Checkpointing
- [ ] Hyperparameter experiments
- [ ] Class imbalance handling

---

## Phase 5 — Evaluation

- [ ] Accuracy
- [ ] Precision
- [ ] Recall
- [ ] F1
- [ ] Macro F1
- [ ] Weighted F1
- [ ] Per-class metrics
- [ ] Confusion matrix
- [ ] High-impact class analysis

---

## Phase 6 — Explainable AI

- [ ] Real Grad-CAM
- [ ] Heatmap generation
- [ ] Overlay generation
- [ ] Feature-level explanation
- [ ] SHAP investigation
- [ ] Explanation serialization

---

## Phase 7 — Inference

- [ ] RainPredictor
- [ ] Standard prediction schema
- [ ] Model loading
- [ ] Real inference
- [ ] XAI inference
- [ ] Prediction serialization

---

## Phase 8 — Dynamic Pipeline

- [ ] MOSDAC ingestion
- [ ] New-frame detection
- [ ] Duplicate prevention
- [ ] Temporal frame buffer
- [ ] Dynamic inference
- [ ] Latest prediction output

---

## Phase 9 — Product Integration

- [ ] Person 2 API integration
- [ ] Frontend integration
- [ ] Satellite viewer
- [ ] Prediction dashboard
- [ ] Grad-CAM visualization
- [ ] SHAP visualization
- [ ] Historical replay
- [ ] End-to-end testing

---

# 👥 Team Responsibilities

## 👨‍💻 Person 1 — ML / Data / XAI

Responsible for:

```text
🛰️ Satellite Data
      ↓
📦 Dataset Construction
      ↓
🧹 Preprocessing
      ↓
🧠 3D-CNN
      ↓
🏋️ Training
      ↓
📈 Evaluation
      ↓
🔥 Grad-CAM
      ↓
📊 Feature XAI / SHAP
      ↓
🔮 RainPredictor
```

---

## 👨‍💻 Person 2 — Backend / Frontend / Product

Responsible for:

```text
🔌 FastAPI
      ↓
📡 API
      ↓
🖥️ React
      ↓
🗺️ Map
      ↓
📊 Dashboard
      ↓
🛰️ Satellite Viewer
      ↓
🔥 Grad-CAM Viewer
      ↓
📈 SHAP Viewer
      ↓
⏪ Historical Replay
```

---

# 🤝 Contributing

Contributions should preserve the project's real-data and scientific integrity requirements.

Before submitting changes:

```bash
git status
```

Review all changes.

Run tests:

```bash
pytest
```

Then commit using a meaningful message:

```bash
git add .
git commit -m "feat: description of change"
git push origin main
```

### Never commit

```text
❌ Passwords
❌ API keys
❌ MOSDAC credentials
❌ Raw satellite datasets
❌ Large HDF5 files
❌ Virtual environments
❌ Temporary outputs
❌ Synthetic model checkpoints
```

---

# 📄 License

This project is being developed as a hackathon/research prototype.

A final open-source license should be selected before public distribution of the complete project.

---

# 🌧️ VarshaDrishti

<p align="center">

### 🛰️ Observe. 🧠 Predict. 🔍 Explain.

**Real Satellite Intelligence for Rainfall Risk**

</p>

---

<p align="center">
  <b>VarshaDrishti</b> — Explainable AI for Satellite-Based Heavy Rainfall Prediction
</p>

<p align="center">
  Built with 🛰️ INSAT-3DR • 🧠 PyTorch • 🔥 Grad-CAM • 📊 Explainable AI
</p>
