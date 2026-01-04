# Model Weights

This directory contains the ONNX model files for face detection and recognition.

## Automatic Download

**Models are automatically downloaded on first startup!**

When you run the backend, it will:
1. Check if models exist
2. If missing, download the InsightFace buffalo_l model pack (~180MB)
3. Extract the required models

No manual action required.

## Required Models

| Model | File | Size | Purpose |
|-------|------|------|---------|
| SCRFD | `det_10g.onnx` | 16MB | Face detection + 5-point landmarks |
| ArcFace | `w600k_r50.onnx` | 166MB | Face embedding extraction |

## Manual Download (if automatic fails)

If automatic download fails, you can manually download:

### Option 1: Direct Download
1. Download from: https://github.com/deepinsight/insightface/releases/download/v0.7/buffalo_l.zip
2. Extract `det_10g.onnx` and `w600k_r50.onnx` to this `models/` directory

### Option 2: Using Python
```bash
cd backend
python download_models.py
```

### Option 3: Using insightface package
```python
from insightface.app import FaceAnalysis
app = FaceAnalysis(name='buffalo_l')
app.prepare(ctx_id=0)
# Models will be in ~/.insightface/models/buffalo_l/
```

Then copy from `~/.insightface/models/buffalo_l/` to this directory.

## Model Sources

- **SCRFD**: Sample and Computation Redistribution for Face Detection
  - Paper: https://arxiv.org/abs/2105.04714
  - Repo: https://github.com/deepinsight/insightface/tree/master/detection/scrfd

- **ArcFace**: Additive Angular Margin Loss for Deep Face Recognition
  - Paper: https://arxiv.org/abs/1801.07698
  - Repo: https://github.com/deepinsight/insightface/tree/master/recognition/arcface_torch

## Model Variants

The buffalo_l pack includes these models (we use det_10g and w600k_r50):

| Model | Input Size | Purpose |
|-------|------------|---------|
| det_10g.onnx | 640x640 | Face detection (high accuracy) |
| det_2.5g.onnx | 640x640 | Face detection (faster, less accurate) |
| w600k_r50.onnx | 112x112 | ArcFace recognition (ResNet-50) |
| genderage.onnx | 96x96 | Gender and age estimation |
| 2d106det.onnx | 192x192 | 106-point landmark detection |

## Note on File Size

These models are excluded from git (via .gitignore) because:
- `w600k_r50.onnx` is 166MB (exceeds GitHub's 100MB limit)
- Total ~180MB is too large for repository

They are downloaded automatically at runtime instead.
