# 🦷 Training Dentescope-AI on NVIDIA Jetson Thor

## Complete Guide for Edge AI Dental Detection

This guide walks you through training a YOLOv8 dental detection model directly on Jetson Thor - much faster and more powerful than Google Colab!

---

## 🎯 What You'll Build

A production-ready AI model that:
- Detects 8 specific teeth in panoramic X-rays
- Measures tooth widths with clinical accuracy
- Runs inference in real-time on edge hardware
- Achieves >70% mAP50 (excellent detection)

**Target Teeth:**
- Primary Second Molars: 55, 65, 75, 85
- Second Premolars: 15, 25, 35, 45

---

## ⚡ Why Train on Jetson Thor?

| Feature | Google Colab (Free) | Jetson Thor |
|---------|---------------------|-------------|
| GPU Memory | 15 GB T4 | 128 GB LPDDR5X |
| Training Speed | 2-3 hours | 30-60 minutes |
| Session Limits | 12 hours max | Unlimited |
| Batch Size | Limited to 16 | Up to 64+ |
| Data Access | Upload required | Local storage |
| Multi-task | Single notebook | Multiple workflows |

---

## 📋 Prerequisites

### 1. System Setup
```bash
# Verify JetPack 7.0 installation
dpkg -l | grep nvidia-jetpack

# Set to MAXN performance mode
sudo nvpmodel -m 0

# Verify GPU
nvidia-smi
```

### 2. Install Docker (if not already done)
```bash
# Add NVIDIA Jetson repository
echo "deb https://repo.download.nvidia.com/jetson/jetson-4fed1671 r38.1 main" | \
sudo tee /etc/apt/sources.list.d/nvidia-l4t-apt-source.list > /dev/null

# Update and install JetPack
sudo apt update
sudo apt install -y nvidia-jetpack

# Configure Docker for GPU access
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

### 3. Install PyTorch Container (Option 1: Container-based)
```bash
# Download PyTorch container from Thor guide
wget https://international.download.nvidia.com/JetsonThorReview/thor_pytorch_container.tar.gz

# Load container
docker image load -i thor_pytorch_container.tar.gz

# Run container
docker run --gpus all --runtime=nvidia --privileged -it --rm \
  -v ~/dentescope-ai:/workspace \
  -u 0:0 --name=dental-training \
  thor_pytorch_container:25.08-py3-base
```

### 4. OR Install Directly on System (Option 2: Native)
```bash
# Install Python dependencies
sudo apt install -y python3-pip python3-opencv

# Install PyTorch for Jetson
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install Ultralytics (YOLOv8)
pip3 install ultralytics

# Install other dependencies
pip3 install opencv-python pillow numpy pandas matplotlib roboflow
```

---

## 🚀 Quick Start (3 Steps)

### Step 1: Clone Your Repository
```bash
cd ~
git clone https://github.com/ajeetraina/dentescope-ai.git
cd dentescope-ai
```

### Step 2: Install Dependencies
```bash
pip3 install -r scripts/requirements.txt
```

### Step 3: Verify Dataset
```bash
# Check your annotated images
ls data/samples/

# Verify annotations exist
ls dataset/labels/

# Count images
echo "Images: $(ls data/samples/*.jpg 2>/dev/null | wc -l)"
echo "Annotations: $(ls dataset/labels/*.txt 2>/dev/null | wc -l)"
```

---

## 📊 Training Pipeline

### Option A: Use Existing Annotations (If Available)

```bash
# 1. Prepare dataset
python3 scripts/prepare_dataset.py

# 2. Start training
python3 scripts/train_yolo.py
```

### Option B: Create New Annotations First

```bash
# 1. Run the smart annotator
python3 scripts/smart_annotator.py

# 2. Prepare dataset
python3 scripts/prepare_dataset.py

# 3. Train model
python3 scripts/train_yolo.py
```

---

## 🎓 Detailed Training Steps

### Step 1: Data Annotation (Skip if done)

```bash
python3 scripts/smart_annotator.py
```

**Annotation Tips:**
- Press `a` for auto-suggestions (AI-assisted region detection)
- Press `n` for next image
- Press `s` to save annotations
- Press `q` to quit

The tool will:
- Auto-detect tooth regions using CV algorithms
- Suggest bounding boxes
- Save annotations in YOLO format

### Step 2: Dataset Preparation

```bash
python3 scripts/prepare_dataset.py
```

This script:
- Validates all annotations
- Splits data 80/20 (train/val)
- Creates YOLO dataset structure:
  ```
  dataset/
  ├── train/
  │   ├── images/
  │   └── labels/
  ├── val/
  │   ├── images/
  │   └── labels/
  └── data.yaml
  ```

### Step 3: Training Configuration

Edit `scripts/train_yolo.py` to optimize for Thor:

```python
# Recommended settings for Jetson Thor
model = YOLO('yolov8n.pt')  # Start with nano

results = model.train(
    data='dataset/data.yaml',
    epochs=100,           # More epochs on Thor
    imgsz=640,           # Or 1024 for better accuracy
    batch=32,            # Thor can handle larger batches!
    device=0,            # Use GPU
    patience=15,         # Early stopping
    workers=8,           # Multi-threading
    cache=True,          # Cache images in RAM (128GB!)
    amp=True,            # Mixed precision training
    project='runs/detect',
    name='dental_thor_v1',
    verbose=True,
    plots=True
)
```

### Step 4: Start Training

```bash
# Basic training
python3 scripts/train_yolo.py

# OR with custom parameters
python3 -c "
from ultralytics import YOLO

model = YOLO('yolov8m.pt')  # Medium model for better accuracy
results = model.train(
    data='dataset/data.yaml',
    epochs=150,
    imgsz=1024,
    batch=32,
    device=0,
    cache=True,
    amp=True,
    name='dental_thor_production'
)
"
```

**Expected Training Time:**
- YOLOv8n (nano): 20-30 minutes
- YOLOv8m (medium): 45-60 minutes
- YOLOv8l (large): 90-120 minutes

---

## 📈 Monitoring Training

### Real-time Monitoring

```bash
# In another terminal, watch GPU usage
watch -n 1 nvidia-smi

# Monitor training logs
tail -f runs/detect/dental_thor_v1/train.log
```

### Check Training Progress

Training outputs are saved in:
```
runs/detect/dental_thor_v1/
├── weights/
│   ├── best.pt        # Best model weights
│   └── last.pt        # Last checkpoint
├── results.png        # Training curves
├── confusion_matrix.png
├── val_batch0_pred.jpg
└── args.yaml
```

---

## 🎯 Model Evaluation

### Step 1: Validate Model

```bash
python3 scripts/test_model.py
```

### Step 2: Check Metrics

```python
from ultralytics import YOLO

# Load trained model
model = YOLO('runs/detect/dental_thor_v1/weights/best.pt')

# Validate on test set
metrics = model.val()

print(f"mAP50: {metrics.box.map50:.3f}")      # Target: >0.70
print(f"mAP50-95: {metrics.box.map:.3f}")    # Target: >0.50
print(f"Precision: {metrics.box.mp:.3f}")
print(f"Recall: {metrics.box.mr:.3f}")
```

**Target Performance:**
- mAP50 > 0.70 = Excellent
- mAP50 > 0.50 = Good
- mAP50 < 0.50 = Need more data/training

### Step 3: Test on Sample Images

```bash
python3 -c "
from ultralytics import YOLO
import glob

model = YOLO('runs/detect/dental_thor_v1/weights/best.pt')

# Test on sample images
test_images = glob.glob('data/samples/*.jpg')[:5]

for img in test_images:
    results = model.predict(img, conf=0.4, save=True)
    print(f'Image: {img}')
    print(f'Detections: {len(results[0].boxes)}')
"
```

---

## 🚀 Optimization for Production

### Export Optimized Model

```bash
python3 -c "
from ultralytics import YOLO

model = YOLO('runs/detect/dental_thor_v1/weights/best.pt')

# Export to TensorRT (optimized for Jetson)
model.export(format='engine', device=0, half=True)

# Export to ONNX (portable)
model.export(format='onnx')

print('✅ Model exported for deployment!')
"
```

### Benchmark Inference Speed

```python
from ultralytics import YOLO
import time

model = YOLO('runs/detect/dental_thor_v1/weights/best.engine')

# Warm up
for _ in range(10):
    model.predict('data/samples/sample_1.jpg', verbose=False)

# Benchmark
start = time.time()
for _ in range(100):
    model.predict('data/samples/sample_1.jpg', verbose=False)
end = time.time()

fps = 100 / (end - start)
print(f"Inference Speed: {fps:.1f} FPS")
print(f"Latency: {1000/fps:.1f} ms")
```

**Expected Performance on Thor:**
- PyTorch (.pt): 30-50 FPS
- TensorRT (.engine): 100-150 FPS
- With batch processing: 200+ FPS

---

## 🐛 Troubleshooting

### Issue: CUDA Out of Memory

```bash
# Reduce batch size
# In train_yolo.py, change:
batch=16  # Instead of 32
```

### Issue: Training Too Slow

```bash
# Enable more optimizations
cache=True        # Cache images
amp=True          # Mixed precision
workers=8         # More workers
close_mosaic=20   # Disable mosaic augmentation late
```

### Issue: Poor Detection Accuracy

1. **Add more annotations**: Target 100+ images
2. **Increase epochs**: Try 150-200
3. **Use larger model**: Switch to yolov8m.pt or yolov8l.pt
4. **Check data quality**: Verify annotations are correct
5. **Augmentation**: Enable more augmentation in config

### Issue: Can't Access Display for Annotation Tool

```bash
# Use VNC or remote desktop
# OR annotate on workstation, sync to Thor:
rsync -avz dataset/ ajeetraina@thor-ip:~/dentescope-ai/dataset/
```

---

## 🎯 Training Different Model Sizes

### Nano (Fastest, 3.2M params)
```python
model = YOLO('yolov8n.pt')  # Best for real-time inference
```

### Small (5.8M params)
```python
model = YOLO('yolov8s.pt')  # Balanced speed/accuracy
```

### Medium (11.2M params)
```python
model = YOLO('yolov8m.pt')  # Recommended for production
```

### Large (25.9M params)
```python
model = YOLO('yolov8l.pt')  # Best accuracy, slower
```

### Extra Large (43.7M params)
```python
model = YOLO('yolov8x.pt')  # Maximum accuracy
```

---

## 📦 Integration with Backend

### Step 1: Copy Model to Backend

```bash
# Copy trained model
cp runs/detect/dental_thor_v1/weights/best.pt backend/models/dental_detector.pt

# Or use TensorRT engine
cp runs/detect/dental_thor_v1/weights/best.engine backend/models/dental_detector.engine
```

### Step 2: Update Backend Code

In `backend/app.py`:

```python
from ultralytics import YOLO

# Load model
model = YOLO('models/dental_detector.pt')
# Or: model = YOLO('models/dental_detector.engine')

@app.route('/detect', methods=['POST'])
def detect_teeth():
    file = request.files['image']
    
    # Run inference
    results = model.predict(
        file,
        conf=0.4,
        iou=0.5,
        device=0
    )
    
    # Process results
    detections = []
    for box in results[0].boxes:
        detections.append({
            'class': int(box.cls),
            'confidence': float(box.conf),
            'bbox': box.xyxy[0].tolist()
        })
    
    return jsonify(detections)
```

### Step 3: Test Backend

```bash
cd backend
python3 app.py

# Test inference
curl -X POST -F "image=@../data/samples/sample_1.jpg" \
  http://localhost:5001/detect
```

---

## 🎉 Next Steps

### 1. Deploy to Production
- Containerize with Docker
- Set up API endpoints
- Add authentication
- Implement logging

### 2. Continuous Improvement
- Collect more X-ray images
- Re-annotate with feedback
- Retrain periodically
- A/B test model versions

### 3. Advanced Features
- Multi-model ensemble
- Uncertainty estimation
- Explainable AI visualizations
- Real-time video inference

### 4. Demo for Conferences
- Create live demo app
- Record demo videos
- Prepare slides with metrics
- Show edge deployment benefits

---

## 📊 Expected Results

After training with 73+ images:

**Detection Metrics:**
- mAP50: 0.65-0.75
- Precision: 0.70-0.80
- Recall: 0.65-0.75

**Measurement Accuracy:**
- Primary Molar Width: 9-10mm
- Premolar Width: 7-8mm
- Width Difference: 2.0-2.8mm

**Inference Speed:**
- YOLOv8n: 50-80 FPS
- YOLOv8m: 30-50 FPS
- TensorRT: 100-150+ FPS

---

## 🔗 Resources

- **YOLOv8 Docs**: https://docs.ultralytics.com
- **Jetson Thor Guide**: (Your setup guide)
- **Your Repo**: https://github.com/ajeetraina/dentescope-ai
- **Implementation Guide**: IMPLEMENTATION_GUIDE.md
- **Integration Guide**: INTEGRATION_GUIDE.md

---

## 💡 Pro Tips for Thor

1. **Use the full 128GB RAM**: Enable `cache=True` to load all images
2. **Batch size matters**: Thor can handle batch=64 for nano models
3. **Mixed precision**: Always use `amp=True` for faster training
4. **Multi-processing**: Set `workers=8` for data loading
5. **TensorRT export**: 3-5x speedup for inference
6. **Monitor thermals**: Thor has excellent cooling, use it!
7. **Save checkpoints**: Training can take time, save often
8. **Version control**: Track experiments with wandb or tensorboard

---

## 🎯 Training Checklist

- [ ] JetPack 7.0 installed
- [ ] Docker configured for GPU
- [ ] Repository cloned
- [ ] Dependencies installed
- [ ] Dataset annotated (73+ images)
- [ ] Dataset prepared and split
- [ ] Training script configured
- [ ] GPU monitoring running
- [ ] Training started
- [ ] Model validated
- [ ] Inference tested
- [ ] Model exported to TensorRT
- [ ] Backend integrated
- [ ] Production ready!

---

**Ready to train? Let's build the most powerful edge AI dental detection system! 🚀**

For questions or issues, create an issue on GitHub or reach out!
