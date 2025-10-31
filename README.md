# 🦷 DenteScope AI - Dental X-ray Tooth Detection

<div align="center">

![Python](https://img.shields.io/badge/Python-3.12-blue.svg)
![PyTorch](https://img.shields.io/badge/PyTorch-2.9.0-red.svg)
![YOLOv8](https://img.shields.io/badge/YOLOv8-8.3.223-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)

**Production-ready AI system for automated tooth detection in dental panoramic X-rays**

[🚀 Live Demo](https://huggingface.co/spaces/ajeetsraina/dentescope-ai) • [📖 Blog Post](BLOG_POST.md) • [💻 GitHub](https://github.com/ajeetraina/dentescope-ai-complete)

<img src="results/width_analysis/tooth_width_analysis_charts.png" alt="Analysis Results" width="800"/>

</div>

---

## 🌐 Live Demo

**[Try DenteScope AI Now! →](https://huggingface.co/spaces/ajeetsraina/dentescope-ai)**

Upload a dental panoramic X-ray and get instant:
- ✅ Tooth detection with 99.5% accuracy
- ✅ Width & height measurements in pixels and mm
- ✅ Confidence scores for each detection
- ✅ Visual annotations on your image

*No installation required - runs entirely in your browser!*

---

## 🎯 Overview

DenteScope AI is a state-of-the-art deep learning system for automated tooth detection in dental panoramic X-rays. Built with YOLOv8 and trained on real dental imagery, it achieves production-ready performance for clinical deployment.

### Key Features

- 🎯 **99.5% mAP50 Accuracy** - Professional-grade detection
- 🚀 **Fast Inference** - ~570ms per image
- 📏 **Automated Measurements** - Width and height in pixels/mm
- 🔄 **Iterative Training** - Self-improving annotation pipeline
- 📦 **Dockerized** - Easy deployment on any platform
- 🌐 **Web Interface** - Live demo on Hugging Face Spaces

---

## 📊 Performance

### Production Model (V2) - YOLOv8s

| Metric | Score | Status |
|--------|-------|--------|
| **mAP50** | **99.5%** | 🟢 Excellent |
| **mAP50-95** | **98.5%** | 🟢 Excellent |
| **Precision** | **99.6%** | 🟢 Excellent |
| **Recall** | **100%** | 🟢 Perfect |
| **Training Time** | 2.6 hours | ⚡ Efficient |
| **Model Size** | 22.5 MB | 💾 Compact |

### Training Evolution
```
V1 Baseline:    mAP50 49.9% (auto-annotated dataset)
      ↓
Re-annotation:  Using trained V1 model
      ↓
V2 Production:  mAP50 99.5% (refined annotations) ✨
```

**Key Achievement:** +99.2% improvement through iterative training!

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Docker (optional, recommended)
- NVIDIA GPU (optional, but faster)

### Installation
```bash
# Clone repository
git clone https://github.com/ajeetraina/dentescope-ai-complete.git
cd dentescope-ai-complete

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install ultralytics opencv-python pillow pyyaml matplotlib pandas openpyxl
```

### Basic Usage
```python
from ultralytics import YOLO

# Load production model
model = YOLO('runs/train/tooth_detection7/weights/best.pt')

# Predict on image
results = model.predict('dental_xray.jpg', conf=0.25, save=True)

# Get measurements
for r in results:
    for box in r.boxes:
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        width_px = x2 - x1
        width_mm = width_px * 0.1  # Calibration factor
        conf = box.conf[0].item()
        
        print(f"Tooth detected:")
        print(f"  Width: {width_px:.1f}px ({width_mm:.1f}mm)")
        print(f"  Confidence: {conf:.1%}")
```

---

## 🐳 Docker Deployment

### Run with Docker
```bash
# Pull container
docker pull nvcr.io/nvidia/cuda:13.0.0-devel-ubuntu24.04

# Run training environment
docker run -it --rm \
  --runtime nvidia \
  --gpus all \
  -v $(pwd):/workspace \
  -w /workspace \
  nvcr.io/nvidia/cuda:13.0.0-devel-ubuntu24.04 \
  bash

# Inside container
apt-get update && apt-get install -y python3 python3-pip libgl1
pip3 install ultralytics --break-system-packages

# Train model
python3 train_tooth_model.py --dataset ./data/v2_dataset_fixed
```

---

## 🎓 Training Pipeline

### Step 1: Data Preparation
```bash
# Organize your dental X-rays
python3 prepare_data.py --source data/raw --output data/train
```

### Step 2: Auto-Annotation (Bootstrap)
```bash
# Generate initial annotations using pretrained YOLOv8
python3 auto_annotate_all.py \
  --images data/train/images \
  --output data/train/labels
```

### Step 3: V1 Baseline Training
```bash
# Train baseline model
python3 train_tooth_model.py \
  --dataset ./data/train \
  --model-size n \
  --epochs 100
```

### Step 4: Re-Annotation
```bash
# Use trained V1 model to generate better annotations
python3 reannotate_with_model.py \
  --model runs/train/tooth_detection5/weights/best.pt \
  --images data/raw \
  --output data/reannotated/labels
```

### Step 5: V2 Production Training
```bash
# Train production model with improved annotations
python3 train_tooth_model.py \
  --dataset ./data/v2_dataset_fixed \
  --model-size s \
  --epochs 100
```

---

## 📏 Width Analysis

### Analyze Tooth Measurements
```bash
# Run comprehensive width analysis
python3 view_tooth_width.py \
  --model runs/train/tooth_detection7/weights/best.pt \
  --images data/v2_dataset_fixed/images/val \
  --output results/width_analysis

# Generate statistics and visualizations
python3 analyze_tooth_widths.py
```

### Analysis Results

- **15 patients analyzed** with 100% detection rate
- **Mean width:** 165.7mm (±0.5mm)
- **Confidence:** 93.3% average
- Outputs: Annotated images, CSV report, Excel file, 4-panel charts

---

## 📁 Project Structure
```
dentescope-ai-complete/
├── data/
│   ├── raw/                    # Original 73 dental X-rays
│   ├── train/                  # Training data (V1)
│   ├── valid/                  # Validation data
│   ├── reannotated/            # Re-annotated dataset
│   └── v2_dataset_fixed/       # Final V2 training dataset
├── runs/
│   └── train/
│       ├── tooth_detection5/   # V1 model (mAP50: 49.9%)
│       └── tooth_detection7/   # V2 model (mAP50: 99.5%) ⭐
├── results/
│   └── width_analysis/         # Width measurements & charts
├── hf-deploy/                  # Hugging Face deployment files
│   ├── app.py                  # Gradio web interface
│   ├── best.pt                 # Production model
│   └── requirements.txt
├── train_tooth_model.py        # Training script
├── view_tooth_width.py         # Width analysis tool
├── analyze_tooth_widths.py     # Comprehensive analysis
├── BLOG_POST.md               # Complete guide
└── README.md                   # This file
```

---

## 💻 Tech Stack

- **Framework:** [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics) - State-of-the-art object detection
- **Deep Learning:** PyTorch 2.9.0
- **Hardware:** NVIDIA Jetson Thor (ARM64)
- **Container:** Docker with CUDA 13.0
- **Deployment:** Hugging Face Spaces with Gradio
- **Language:** Python 3.12

---

## 🎯 Use Cases

### Clinical Applications
- 🏥 Automated screening in dental clinics
- 📊 Batch processing of patient X-rays
- 📏 Dimensional analysis for orthodontics
- 🎓 Training tool for dental students

### Research Applications
- 🔬 Dental morphology studies
- 📈 Population-level statistics
- 🧪 Treatment outcome analysis
- 📝 Automated annotation for datasets

---

## 📖 Documentation

- **[Complete Blog Post](BLOG_POST.md)** - Full step-by-step guide with code
- **[Live Demo](https://huggingface.co/spaces/ajeetsraina/dentescope-ai)** - Try it now!

### External Resources

- [Ultralytics YOLOv8 Docs](https://docs.ultralytics.com/)
- [NVIDIA Jetson Thor](https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/jetson-thor/)
- [Hugging Face Spaces](https://huggingface.co/docs/hub/spaces)
- [Docker Documentation](https://docs.docker.com/)

---







