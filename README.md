# 🌧️ VarshaDrishti

### 🛰️ Explainable AI for Satellite-Based Rainfall Risk Intelligence

<p align="center">
  <strong>Observe. Predict. Explain.</strong>
</p>

<p align="center">
  An end-to-end explainable AI prototype combining satellite observations,
  temporal deep learning, rainfall-risk classification, Grad-CAM,
  FastAPI, and a React-based intelligence dashboard.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Project-VarshaDrishti-0B3D91?style=for-the-badge" alt="VarshaDrishti">
  <img src="https://img.shields.io/badge/AI-Satellite%20Intelligence-1565C0?style=for-the-badge" alt="Satellite AI">
  <img src="https://img.shields.io/badge/Model-3D--CNN-6A1B9A?style=for-the-badge" alt="3D CNN">
  <img src="https://img.shields.io/badge/XAI-Grad--CAM-E65100?style=for-the-badge" alt="Grad-CAM">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Data-INSAT--3DR-00897B?style=flat-square" alt="INSAT-3DR">
  <img src="https://img.shields.io/badge/Source-MOSDAC-455A64?style=flat-square" alt="MOSDAC">
  <img src="https://img.shields.io/badge/Framework-PyTorch-EE4C2C?style=flat-square" alt="PyTorch">
  <img src="https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square" alt="FastAPI">
  <img src="https://img.shields.io/badge/Frontend-React-61DAFB?style=flat-square" alt="React">
  <img src="https://img.shields.io/badge/Status-Working%20Prototype-F9A825?style=flat-square" alt="Working Prototype">
</p>

---

# 📌 Table of Contents

- [🌍 Overview](#-overview)
- [🎯 Problem Statement](#-problem-statement)
- [💡 Solution](#-solution)
- [✨ Key Features](#-key-features)
- [🏗️ System Architecture](#️-system-architecture)
- [🔄 End-to-End Pipeline](#-end-to-end-pipeline)
- [🛰️ Satellite Data](#️-satellite-data)
- [🤖 Machine Learning](#-machine-learning)
- [🌧️ Rainfall Risk Classes](#️-rainfall-risk-classes)
- [🔍 Explainable AI](#-explainable-ai)
- [🌐 Application Architecture](#-application-architecture)
- [📡 API](#-api)
- [🖥️ Dashboard](#️-dashboard)
- [📊 Model Performance](#-model-performance)
- [📜 Historical Events](#-historical-events)
- [🛡️ Data Integrity](#️-data-integrity)
- [📁 Repository Structure](#-repository-structure)
- [⚙️ Technology Stack](#️-technology-stack)
- [🚀 Installation](#-installation)
- [▶️ Running the Application](#️-running-the-application)
- [🧪 Testing](#-testing)
- [🔐 Security](#-security)
- [⚠️ Current Limitations](#️-current-limitations)
- [🗺️ Roadmap](#️-roadmap)
- [👥 Team Responsibilities](#-team-responsibilities)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

---

# 🌍 Overview

**VarshaDrishti** is an explainable satellite intelligence system designed to analyze rainfall risk using satellite observations and temporal deep learning.

The system combines:

- 🛰️ INSAT-3DR satellite observations
- 🧠 Temporal 3D-CNN inference
- 🌧️ Four-class rainfall-risk prediction
- 🔥 Grad-CAM visual explanations
- ⚡ FastAPI backend services
- 🖥️ React-based intelligence dashboard
- 📊 Model-performance visualization
- 📜 Historical event analysis

The central objective is not only to produce a rainfall-risk prediction, but also to provide a visual explanation of **where the model focused while producing that prediction**.

---

# 🎯 Problem Statement

Heavy and extreme rainfall can create significant risks for:

- 🌧️ Urban flooding
- 🚨 Disaster response
- 🏙️ Infrastructure
- 🚗 Transportation
- 🌾 Agriculture
- 🏘️ Human settlements
- 🌊 Water-management systems

Satellite observations provide valuable spatial and temporal information that can complement conventional weather information.

However, an AI system used for such applications should answer two questions:

> **What is the predicted rainfall risk?**

and

> **Why did the model make this prediction?**

VarshaDrishti addresses both.

```text
Prediction
    +
Explainability
    =
Actionable Satellite Intelligence
```

---

# 💡 Solution

VarshaDrishti processes satellite observations through a machine-learning inference pipeline.

The conceptual flow is:

```text
🛰️ Satellite Observation
        ↓
   Data Processing
        ↓
 Temporal Sequence
        ↓
     3D-CNN
        ↓
Rainfall Risk Prediction
        ↓
 ┌──────┴──────┐
 ↓             ↓
Grad-CAM    Feature XAI
 ↓             ↓
 └──────┬──────┘
        ↓
 Standardized Output
        ↓
      FastAPI
        ↓
   React Dashboard
```

The current application provides an integrated prototype of this pipeline with working backend APIs and frontend visualization.

---

# ✨ Key Features

## 🛰️ Satellite-Based Intelligence

The project is designed around real INSAT-3DR satellite observations obtained through the MOSDAC ecosystem.

The primary satellite input product used in the project architecture is:

```text
3RIMG_L1B_STD
```

---

## 🧠 Temporal Deep Learning

Rainfall behavior is not purely spatial.

The system therefore uses temporal observations rather than treating every image as an isolated sample.

Conceptually:

```text
T-5 → T-4 → T-3 → T-2 → T-1 → T
                         ↓
                       3D-CNN
                         ↓
                 Rainfall Risk
```

The 3D-CNN is designed to learn spatial and temporal representations simultaneously.

---

## 🌧️ Four-Class Risk Prediction

The current prediction interface supports four rainfall-risk classes:

```text
0 → No Rain
1 → Moderate
2 → Heavy
3 → High Impact
```

The backend returns both the predicted class and the probability distribution across all four classes.

---

## 🔥 Grad-CAM Explainability

Grad-CAM provides a visual representation of the regions receiving stronger model attention.

```text
Satellite Input
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
```

The resulting heatmap is displayed directly inside the web dashboard.

---

## 📊 Model Performance Dashboard

The application provides:

- Accuracy
- F1 score
- Per-class precision
- Per-class recall
- Per-class F1
- Confusion matrix
- Class-wise performance visualization

The performance page also communicates when an evaluation is based on a limited development dataset.

---

## 📜 Historical Event Analysis

Historical prediction records can be selected from the dashboard.

For each available event, the interface can display:

- Event date
- Prediction class
- Confidence
- Probability distribution
- Location availability
- Grad-CAM visualization

---

## ⚡ Real-Inference Frontend Mode

The frontend is configured to use the backend inference APIs rather than mock responses.

Current configuration:

```env
VITE_USE_MOCK=false
VITE_API_BASE=http://localhost:8000/api
```

This ensures that the dashboard communicates with the running FastAPI service.

---

# 🏗️ System Architecture

```text
                         ┌──────────────────────────┐
                         │        MOSDAC            │
                         │    INSAT-3DR Data        │
                         └────────────┬─────────────┘
                                      │
                                      ▼
                         ┌──────────────────────────┐
                         │    Data Processing       │
                         │   HDF5 / Calibration     │
                         │       / QC               │
                         └────────────┬─────────────┘
                                      │
                                      ▼
                         ┌──────────────────────────┐
                         │   Temporal Sequences     │
                         │      T-n ... T           │
                         └────────────┬─────────────┘
                                      │
                                      ▼
                         ┌──────────────────────────┐
                         │        3D-CNN            │
                         │ Spatial + Temporal       │
                         │       Features           │
                         └────────────┬─────────────┘
                                      │
                                      ▼
                         ┌──────────────────────────┐
                         │   Rainfall Prediction    │
                         │     4 Risk Classes       │
                         └────────────┬─────────────┘
                                      │
                         ┌────────────┴────────────┐
                         ▼                         ▼
                ┌─────────────────┐       ┌─────────────────┐
                │    Grad-CAM     │       │ Feature XAI     │
                │  Visual Focus   │       │   Extension     │
                └────────┬────────┘       └────────┬────────┘
                         │                         │
                         └────────────┬────────────┘
                                      ▼
                         ┌──────────────────────────┐
                         │ Standardized Prediction  │
                         │         Output           │
                         └────────────┬─────────────┘
                                      │
                                      ▼
                         ┌──────────────────────────┐
                         │       FastAPI            │
                         │       Backend            │
                         └────────────┬─────────────┘
                                      │
                                      ▼
                         ┌──────────────────────────┐
                         │      React Frontend      │
                         │                          │
                         │  Dashboard               │
                         │  Historical Events       │
                         │  Model Performance       │
                         │  Grad-CAM Viewer         │
                         └──────────────────────────┘
```

---

# 🔄 End-to-End Pipeline

The current system can be understood through the following layers:

```text
┌─────────────────────────────────────────────┐
│ 1. DATA                                     │
│                                             │
│ INSAT-3DR satellite observations            │
└──────────────────────┬──────────────────────┘
                       ↓
┌─────────────────────────────────────────────┐
│ 2. PREPROCESSING                            │
│                                             │
│ HDF5 reading                                │
│ Calibration                                 │
│ Quality control                             │
│ Spatial processing                          │
│ Temporal preparation                        │
└──────────────────────┬──────────────────────┘
                       ↓
┌─────────────────────────────────────────────┐
│ 3. MACHINE LEARNING                         │
│                                             │
│ Temporal sequence → 3D-CNN → prediction    │
└──────────────────────┬──────────────────────┘
                       ↓
┌─────────────────────────────────────────────┐
│ 4. EXPLAINABILITY                           │
│                                             │
│ Grad-CAM → heatmap / visual attention       │
└──────────────────────┬──────────────────────┘
                       ↓
┌─────────────────────────────────────────────┐
│ 5. BACKEND                                  │
│                                             │
│ FastAPI → standardized JSON                 │
└──────────────────────┬──────────────────────┘
                       ↓
┌─────────────────────────────────────────────┐
│ 6. APPLICATION                              │
│                                             │
│ React dashboard                             │
│ Historical events                           │
│ Model performance                           │
│ Explainability viewer                       │
└─────────────────────────────────────────────┘
```

---

# 🛰️ Satellite Data

## Primary Satellite

```text
Satellite : INSAT-3DR
Sensor    : Imager
Source    : MOSDAC
```

Primary input product:

```text
3RIMG_L1B_STD
```

The project architecture is designed to inspect the actual HDF5 structure rather than assuming fixed internal dataset paths.

Important data-dependent properties include:

- Dataset paths
- Channel names
- Channel dimensions
- Calibration parameters
- Fill values
- Units
- Spatial resolution
- Timestamp representation
- Geolocation information

---

## Rainfall Target Data

The project architecture also supports rainfall target information associated with:

```text
3RIMG_L2B_IMC
```

The temporal relationship between satellite observations and rainfall targets is treated as a data-dependent component rather than being blindly hardcoded.

---

# 🤖 Machine Learning

## 3D-CNN

The model uses 3D convolutional operations to learn from both spatial and temporal dimensions.

Expected tensor convention:

```text
[B, C, T, H, W]
```

Where:

| Symbol | Meaning |
|---|---|
| B | Batch size |
| C | Number of input channels |
| T | Temporal frames |
| H | Image height |
| W | Image width |

The classifier produces four output classes:

```text
[B, 4]
```

---

## Conceptual Model

```text
Input Sequence
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

The architecture is intended to remain lightweight enough for hackathon experimentation and inference.

---

# 🌧️ Rainfall Risk Classes

| Class ID | Class | Meaning |
|---:|---|---|
| `0` | No Rain | No significant rainfall risk |
| `1` | Moderate | Moderate rainfall conditions |
| `2` | Heavy | Heavy rainfall conditions |
| `3` | High Impact | High-impact rainfall risk |

The final interpretation of rainfall thresholds depends on the underlying target construction and dataset methodology.

---

# 🔍 Explainable AI

Explainability is a core component of VarshaDrishti.

## 🔥 Grad-CAM

Grad-CAM answers:

> **Where did the model focus?**

The current system generates Grad-CAM heatmaps that are served through the backend and displayed by the React interface.

Example backend response:

```json
{
  "xai": {
    "gradcam": {
      "image_url": "http://localhost:8000/generated/gradcam/heatmap_patch_69.png"
    }
  }
}
```

The frontend provides a dedicated Grad-CAM viewer.

Conceptual interpretation:

```text
Blue / cooler regions
        ↓
Lower model attention

Green / yellow regions
        ↓
Moderate model attention

Red / warmer regions
        ↓
Higher model attention
```

The heatmap should always be interpreted as a model-attention explanation, not as a direct physical rainfall measurement.

---

## 📊 Feature-Level XAI / SHAP

The architecture reserves a place for feature-level explanations.

However, the current integrated API may return:

```json
"shap": null
```

when feature-level SHAP information is not available for a prediction.

This is intentional.

The project does **not** fabricate SHAP values merely to populate the UI.

Future feature-level explainability can investigate:

- Satellite channel contribution
- Temporal-frame contribution
- Engineered feature contribution
- Other interpretable model representations

---

# 🌐 Application Architecture

The application consists of three primary layers.

## 1. ML Layer

```text
varshadrishti-ml/
```

Responsible for:

- Inference
- Model logic
- XAI
- Evaluation
- ML tests
- Data processing utilities

---

## 2. Backend Layer

```text
backend/
```

Built with:

```text
Python
FastAPI
Pydantic
PyTorch integration
```

Responsible for:

- API routing
- ML adapter
- Prediction serialization
- Historical event APIs
- Metrics APIs
- Grad-CAM asset serving
- Health checks

---

## 3. Frontend Layer

```text
frontend/
```

Built with:

```text
React
Vite
JavaScript
CSS
```

Responsible for:

- Dashboard
- Prediction visualization
- Probability distribution
- Historical events
- Model performance
- Grad-CAM visualization
- Application navigation

---

# 📡 API

The backend runs locally on:

```text
http://127.0.0.1:8000
```

The frontend communicates with:

```text
http://localhost:8000/api
```

---

## Health Check

### Request

```http
GET /health
```

### Example response

```json
{
  "status": "ok"
}
```

---

## Latest Prediction

### Request

```http
GET /api/latest
```

### Example response

```json
{
  "prediction": {
    "class_id": 0,
    "label": "no_rain",
    "confidence": 0.637073278427124
  },
  "probabilities": {
    "no_rain": 0.637073278427124,
    "moderate": 0.26433658599853516,
    "heavy": 0.07095792889595032,
    "high_impact": 0.0276322178542614
  },
  "xai": {
    "gradcam": {
      "image_url": "http://localhost:8000/generated/gradcam/heatmap_patch_69.png"
    },
    "shap": null
  },
  "metadata": {
    "timestamp": "2026-08-18T23:45:00Z",
    "latitude": 20.0,
    "longitude": 75.0
  }
}
```

> The numerical values above represent a development/runtime response and should not be interpreted as a general scientific performance claim.

---

## Historical Events

### Request

```http
GET /api/historical
```

Returns available historical prediction events.

Example:

```json
{
  "events": [
    {
      "id": "event_2026-08-17",
      "name": "Development Event — 17 Aug 2026",
      "date": "2026-08-17",
      "location": null,
      "latitude": null,
      "longitude": null,
      "type": "high_impact",
      "description": "Development dataset event."
    }
  ]
}
```

When geographic coordinates are unavailable in the source dataset, the application explicitly reports that location data is unavailable instead of inventing coordinates.

---

# 🖥️ Dashboard

The React application currently provides three major views.

## 1. Overview

The Overview dashboard provides:

- Impact location
- Current prediction
- Confidence
- Probability distribution
- Model explanation
- Grad-CAM visualization
- Satellite evidence

---

## 2. Historical Events

Historical Events provides:

```text
Available Events
      ↓
Select Event
      ↓
Prediction Result
      ↓
Probability Distribution
      ↓
Location Information
      ↓
Grad-CAM
```

If coordinates are not available, the interface displays:

```text
Location data unavailable
```

instead of generating fake geographic information.

---

## 3. Model Performance

The Model Performance view provides:

- Accuracy
- F1 score
- Per-class precision
- Per-class recall
- Per-class F1
- Confusion matrix

The page also provides a development/proof-of-concept warning where the available evaluation sample is too limited to support broad scientific generalization.

---

# 📊 Model Performance

The current development evaluation displayed by the application includes:

```text
Accuracy : 60.9%
F1 Score : 40.2%
```

The per-class evaluation shown by the dashboard includes:

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| No Rain | 64.3% | 96.4% | 77.1% |
| Moderate Rain | 0.0% | 0.0% | 0.0% |
| Heavy Rain | 100.0% | 8.3% | 15.4% |
| High Impact | 53.8% | 93.3% | 68.3% |

### ⚠️ Important Evaluation Disclaimer

The current dashboard explicitly identifies the displayed evaluation as a:

```text
DEVELOPMENT / PROOF-OF-CONCEPT TRAINING ONLY
```

The available development evaluation contains only a small number of independent weather events.

Therefore:

> These metrics should not be interpreted as statistically representative operational or production model performance.

The purpose of the current evaluation is to verify that the inference and evaluation pipeline is functioning correctly.

A larger scientifically representative evaluation dataset is required before making operational performance claims.

---

# 📜 Historical Events

The current development API exposes historical events for:

```text
17 August 2026
18 August 2026
```

The application supports selecting an event and inspecting:

- Prediction
- Confidence
- Class probabilities
- Geographic metadata
- Grad-CAM visualization

Where source data does not contain geographic coordinates, the dashboard explicitly displays their unavailability.

---

# 🛡️ Data Integrity

VarshaDrishti follows a strict data-integrity policy.

## 1. No Fabricated Metrics

The project does not intentionally invent:

```text
Accuracy
Precision
Recall
F1
Confusion Matrix
```

---

## 2. No Fake XAI

Grad-CAM visualizations should correspond to the model inference pipeline and the associated input.

The system should never generate random heatmaps and present them as explanations of model behavior.

---

## 3. No Silent Mock Fallback

The frontend is currently configured with:

```env
VITE_USE_MOCK=false
```

Therefore, the deployed development UI is intended to consume the backend inference APIs rather than silently switching to mock prediction data.

---

## 4. No Fabricated Geographic Coordinates

When historical source records do not contain latitude or longitude information, the API returns:

```json
"latitude": null,
"longitude": null
```

The frontend communicates this limitation directly to the user.

---

## 5. No Automatic Retraining During Inference

New observations should trigger inference rather than silently retraining the model.

```text
NEW OBSERVATION
      ↓
VALIDATION
      ↓
PREPROCESSING
      ↓
TEMPORAL BUFFER
      ↓
INFERENCE
      ↓
EXPLANATION
```

Training and inference remain separate processes.

---

# 📁 Repository Structure

```text
VarshaDrishti/
│
├── backend/
│   ├── app/
│   │   ├── adapters/
│   │   │   └── ml_predictor.py
│   │   │
│   │   ├── routes/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── config.py
│   │   ├── dependencies.py
│   │   └── main.py
│   │
│   ├── generated/
│   │   └── gradcam/
│   │
│   └── tests/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── utils/
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   │
│   ├── package.json
│   └── vite.config.*
│
├── varshadrishti-ml/
│   ├── src/
│   │   ├── inference/
│   │   │   └── backend_adapter.py
│   │   │
│   │   └── xai/
│   │       └── gradcam.py
│   │
│   ├── scripts/
│   │   ├── export_development_metrics.py
│   │   └── export_historical_events.py
│   │
│   └── tests/
│       ├── test_inference.py
│       ├── test_xai_gradcam.py
│       ├── test_export_metrics.py
│       └── test_export_historical_events.py
│
├── README.md
└── .gitignore
```

---

# ⚙️ Technology Stack

## Machine Learning

| Technology | Purpose |
|---|---|
| Python | ML development |
| PyTorch | Deep learning |
| 3D-CNN | Temporal-spatial modeling |
| Grad-CAM | Visual explainability |
| HDF5 tooling | Satellite data processing |

---

## Backend

| Technology | Purpose |
|---|---|
| Python | Backend runtime |
| FastAPI | REST API |
| Pydantic | API schemas |
| ML Adapter | Backend ↔ model integration |

---

## Frontend

| Technology | Purpose |
|---|---|
| React | UI |
| Vite | Frontend build system |
| JavaScript | Application logic |
| CSS | Interface styling |

---

## Data / Domain

| Technology | Purpose |
|---|---|
| INSAT-3DR | Satellite observations |
| MOSDAC | Satellite data source |
| HDF5 | Satellite product format |

---

# 🚀 Installation

## Prerequisites

Install:

```text
Python 3.x
Node.js
npm
Git
```

For ML development, a compatible PyTorch installation is also required.

---

# 📥 Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd VarshaDrishti
```

---

# 🧠 ML Environment

Navigate to:

```bash
cd varshadrishti-ml
```

Create a virtual environment:

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

Install ML dependencies if a requirements file is available:

```bash
pip install -r requirements.txt
```

Verify Python:

```bash
python --version
```

Verify PyTorch:

```bash
python -c "import torch; print('PyTorch:', torch.__version__); print('CUDA available:', torch.cuda.is_available())"
```

---

# ⚙️ Backend Setup

Navigate to the backend:

```bash
cd ../backend
```

If using a dedicated backend environment:

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Install backend dependencies according to the backend environment configuration.

---

# 🖥️ Frontend Setup

Navigate to:

```bash
cd ../frontend
```

Install dependencies:

```bash
npm install
```

The frontend environment file should contain:

```env
VITE_USE_MOCK=false
VITE_API_BASE=http://localhost:8000/api
```

---

# ▶️ Running the Application

The application consists of two services.

---

## 1. Start Backend

From:

```text
VarshaDrishti/backend
```

run:

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

The backend will be available at:

```text
http://127.0.0.1:8000
```

Verify:

```bash
curl http://127.0.0.1:8000/health
```

Expected:

```json
{
  "status": "ok"
}
```

---

## 2. Start Frontend

Open another terminal.

Navigate to:

```text
VarshaDrishti/frontend
```

run:

```bash
npm run dev
```

The Vite development server will normally be available at:

```text
http://localhost:5173
```

---

# 🔎 Demo Verification

Once both services are running, verify the following.

## Backend

```bash
curl http://127.0.0.1:8000/health
```

Then:

```bash
curl http://127.0.0.1:8000/api/latest
```

Then:

```bash
curl http://127.0.0.1:8000/api/historical
```

---

## Frontend

Open:

```text
http://localhost:5173/
```

Verify:

```text
✓ Overview
✓ Historical Events
✓ Model Performance
✓ Prediction probabilities
✓ Grad-CAM visualization
✓ Historical event selection
✓ Backend connectivity
```

---

# 🧪 Testing

The project contains ML and backend tests.

## ML Tests

From:

```text
varshadrishti-ml
```

run:

```bash
python -m unittest discover -s tests -v
```

---

## Backend Tests

From:

```text
backend
```

run:

```bash
python -m pytest tests -v
```

---

## Frontend Build

From:

```text
frontend
```

run:

```bash
npm run build
```

A successful build should produce the Vite production output under:

```text
frontend/dist/
```

---

# ✅ Verified Development Pipeline

The current repository has been verified through the following checks:

```text
Backend Health
      ✓
      ↓
Latest Inference API
      ✓
      ↓
Historical API
      ✓
      ↓
Grad-CAM Assets
      ✓
      ↓
React Development Server
      ✓
      ↓
Frontend Production Build
      ✓
      ↓
Git Integrity
      ✓
      ↓
GitHub Push
      ✓
```

The repository's current development commit contains the integrated real-inference and explainability pipeline.

---

# 🔐 Security

Never commit sensitive information.

Do not commit:

```text
.env
*.env
API keys
Passwords
Tokens
MOSDAC credentials
Private credentials
```

Raw satellite datasets and large model artifacts should also remain outside the repository unless an explicit approved storage strategy is being used.

Use environment variables for credentials and private configuration.

Example:

```env
MOSDAC_USERNAME=your_username
MOSDAC_PASSWORD=your_password
```

Do not commit the actual values.

---

# ⚠️ Current Limitations

VarshaDrishti is currently a **working research/hackathon prototype**, not a production meteorological forecasting system.

## 1. Limited Evaluation Dataset

The current development evaluation is based on a limited number of independent weather events.

Therefore, the displayed metrics should not be interpreted as statistically representative production performance.

---

## 2. SHAP Feature Explanation

The current integrated API may return:

```json
"shap": null
```

when a feature-level SHAP explanation is not available.

The application deliberately communicates this instead of fabricating an explanation.

---

## 3. Geographic Metadata

Some development historical events do not contain geographic coordinates.

The API therefore returns:

```json
"latitude": null,
"longitude": null
```

and the frontend displays:

```text
Location data unavailable
```

---

## 4. Operational Satellite Ingestion

The current project demonstrates the integrated inference and application pipeline.

A fully automated operational pipeline would additionally require:

```text
Satellite Data Retrieval
        ↓
Automatic New-Frame Detection
        ↓
Duplicate Prevention
        ↓
Preprocessing
        ↓
Temporal Buffer
        ↓
Inference
        ↓
XAI
        ↓
API Update
```

---

## 5. Scientific Validation

Before operational deployment, the model should be evaluated on a substantially larger and geographically/temporally representative dataset.

Important future validation areas include:

- Multiple weather systems
- Multiple geographic regions
- Seasonal variation
- Extreme rainfall events
- Class imbalance
- Temporal generalization
- Spatial generalization
- Independent test periods

---

# 🗺️ Roadmap

## Phase 1 — Core Integration

- [x] Repository setup
- [x] ML project structure
- [x] Backend integration
- [x] Frontend integration
- [x] Standardized prediction schema
- [x] Real-inference frontend mode
- [x] FastAPI health endpoint
- [x] Latest prediction endpoint

---

## Phase 2 — Explainability

- [x] Grad-CAM pipeline
- [x] Heatmap generation
- [x] Backend Grad-CAM serving
- [x] Frontend Grad-CAM viewer
- [ ] Advanced feature-level explanation
- [ ] SHAP integration where technically meaningful

---

## Phase 3 — Historical Intelligence

- [x] Historical event API
- [x] Historical event selection
- [x] Historical prediction visualization
- [x] Historical Grad-CAM visualization
- [x] Missing-coordinate handling
- [ ] Larger historical event dataset

---

## Phase 4 — Evaluation

- [x] Accuracy reporting
- [x] F1 reporting
- [x] Per-class metrics
- [x] Confusion matrix
- [x] Development evaluation dashboard
- [ ] Larger independent test dataset
- [ ] Robust cross-event evaluation
- [ ] Seasonal evaluation
- [ ] Geographic generalization analysis

---

## Phase 5 — Dynamic Inference

- [ ] Automated satellite ingestion
- [ ] New-frame detection
- [ ] Duplicate prevention
- [ ] Temporal frame buffer
- [ ] Automated inference trigger
- [ ] Automatic Grad-CAM generation
- [ ] Automatic dashboard update

---

## Phase 6 — Production Readiness

- [ ] Production model validation
- [ ] Larger representative dataset
- [ ] Model monitoring
- [ ] API authentication
- [ ] Containerized deployment
- [ ] Cloud deployment
- [ ] Operational alerting
- [ ] Performance optimization

---

# 👥 Team Responsibilities

## 👨‍💻 ML / Data / XAI

Responsibilities include:

```text
Satellite Data
      ↓
Data Processing
      ↓
Temporal Dataset
      ↓
3D-CNN
      ↓
Inference
      ↓
Evaluation
      ↓
Grad-CAM
      ↓
Feature XAI
```

---

## 👨‍💻 Backend / Frontend / Product

Responsibilities include:

```text
FastAPI
   ↓
REST APIs
   ↓
React
   ↓
Dashboard
   ↓
Historical Events
   ↓
Model Performance
   ↓
Grad-CAM Viewer
```

---

# 🧩 Integration Contract

The ML layer communicates with the application through a standardized prediction structure.

```json
{
  "prediction": {
    "class_id": 0,
    "label": "no_rain",
    "confidence": 0.63
  },
  "probabilities": {
    "no_rain": 0.63,
    "moderate": 0.26,
    "heavy": 0.07,
    "high_impact": 0.03
  },
  "xai": {
    "gradcam": {
      "image_url": "..."
    },
    "shap": null
  },
  "metadata": {
    "timestamp": "...",
    "latitude": null,
    "longitude": null
  }
}
```

This separation allows the frontend and backend to consume predictions without depending directly on internal PyTorch implementation details.

---

# 🧠 Scientific Design Principles

VarshaDrishti follows several principles intended to improve trustworthiness.

### Real Data

Final scientific claims should be based on real satellite/rainfall observations.

### Explainable AI

Model predictions should be accompanied by interpretable evidence where technically possible.

### No Fabricated Results

Metrics, predictions, coordinates, and explanations should never be fabricated to make the dashboard appear more complete.

### Temporal Integrity

Temporal datasets should use chronological separation where appropriate to reduce leakage.

### Transparent Limitations

When data or explanations are unavailable, the application should communicate that limitation directly.

### Reproducibility

Important experiments should record:

```text
Dataset
Configuration
Random Seed
Model Configuration
Training Configuration
Evaluation Configuration
Checkpoint
Environment
```

---

# 🤝 Contributing

Before making changes:

```bash
git status
```

Review modified files.

Run the relevant tests:

```bash
pytest
```

For ML tests:

```bash
python -m unittest discover -s tests -v
```

For the frontend:

```bash
npm run build
```

Commit using a meaningful message:

```bash
git add .
git commit -m "feat: describe the change"
git push origin main
```

---

# 🚫 Do Not Commit

```text
❌ Passwords
❌ API keys
❌ MOSDAC credentials
❌ Private tokens
❌ Raw satellite datasets
❌ Large HDF5 files
❌ Virtual environments
❌ Private model checkpoints
❌ Temporary generated artifacts
❌ Personal configuration files
```

---

# 📌 Project Status

```text
🟢 Core Repository
🟢 ML Inference Integration
🟢 FastAPI Backend
🟢 React Frontend
🟢 Real-Inference Mode
🟢 Four-Class Prediction
🟢 Probability Distribution
🟢 Grad-CAM
🟢 Historical Events
🟢 Model Performance Dashboard
🟢 Confusion Matrix
🟢 Backend Tests
🟢 ML Tests
🟢 Frontend Production Build

🟡 Larger Scientific Evaluation
🟡 Feature-Level SHAP
🟡 Automated Satellite Ingestion
🟡 Fully Dynamic Operational Pipeline
🟡 Production Deployment
```

---

# 🏆 Why VarshaDrishti?

Most AI dashboards stop at:

```text
INPUT
  ↓
PREDICTION
```

VarshaDrishti aims to provide:

```text
INPUT
  ↓
TEMPORAL AI
  ↓
PREDICTION
  ↓
CONFIDENCE
  ↓
MODEL EXPLANATION
  ↓
HISTORICAL CONTEXT
  ↓
HUMAN-INTERPRETABLE INTELLIGENCE
```

The goal is to move from:

> **"The model predicts heavy rainfall."**

to:

> **"The model predicts this rainfall-risk class, with this probability distribution, and here is the visual evidence showing the regions receiving stronger model attention."**

---

# 🌧️ VarshaDrishti

<p align="center">

### 🛰️ Observe. 🧠 Predict. 🔍 Explain.

<strong>Explainable Satellite Intelligence for Rainfall Risk</strong>

</p>

<p align="center">
Built with 🛰️ INSAT-3DR • 🧠 PyTorch • 🔥 Grad-CAM • ⚡ FastAPI • ⚛️ React
</p>

<p align="center">
<strong>VarshaDrishti — Turning Satellite Observations into Explainable Rainfall Intelligence.</strong>
</p>
