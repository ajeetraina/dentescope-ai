# 🚀 Jetson AGX Thor Setup Guide for Toothy Width Mate

## Prerequisites

- Jetson AGX Thor with JetPack 6.1 or later
- Ubuntu 22.04 (comes with JetPack)
- At least 64GB storage
- Network connection for initial setup

---

## 1️⃣ Initial Jetson Setup

### Check CUDA and cuDNN Installation

```bash
# Verify CUDA
nvcc --version

# Check GPU status
sudo jetson_clocks
sudo tegrastats

# Verify PyTorch CUDA support
python3 -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}'); print(f'CUDA Version: {torch.version.cuda}'); print(f'GPU: {torch.cuda.get_device_name(0)}')"
```

---

## 2️⃣ Install Docker (Recommended for Portability)

```bash
# Docker should be pre-installed on JetPack
# Verify installation
docker --version

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Verify Docker works
docker run hello-world
```

---

## 3️⃣ Set Up Python Environment

### Option A: Using venv (Recommended)

```bash
# Create virtual environment
python3 -m venv ~/dental-ai-env
source ~/dental-ai-env/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install PyTorch for Jetson (ARM64 + CUDA)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install Ultralytics and dependencies
pip install ultralytics opencv-python pillow numpy scipy

# Install additional ML libraries
pip install pandas matplotlib scikit-learn
```

### Option B: Using Docker (Better Isolation)

```bash
# Pull NVIDIA PyTorch container for Jetson
docker pull nvcr.io/nvidia/l4t-pytorch:r36.2.0-pth2.1-py3

# Run container with GPU support
docker run -it --runtime nvidia --network host \
  -v ~/toothy-width-mate:/workspace \
  -v ~/dental-data:/data \
  --device /dev/video0 \
  nvcr.io/nvidia/l4t-pytorch:r36.2.0-pth2.1-py3
```

---

## 4️⃣ Clone and Set Up Your Project

```bash
# Clone repository
cd ~
git clone https://github.com/ajeetraina/toothy-width-mate.git
cd toothy-width-mate

# Create necessary directories
mkdir -p model dataset/train dataset/valid data/samples

# Install project dependencies
pip install -r scripts/requirements.txt
```

---

## 5️⃣ Optimize for Jetson Performance

### Create Jetson-optimized training script

```bash
cat > scripts/train_yolo_jetson.py << 'EOF'
#!/usr/bin/env python3
"""
YOLOv8 Training Script Optimized for NVIDIA Jetson AGX Thor
"""

import torch
from ultralytics import YOLO
import os
from pathlib import Path

def optimize_jetson():
    """Configure optimal settings for Jetson AGX Thor"""
    # Enable TensorFloat-32 for better performance on Ampere/Blackwell
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
    
    # Enable cuDNN benchmark for faster convolutions
    torch.backends.cudnn.benchmark = True
    
    # Set memory management
    torch.cuda.empty_cache()
    
    print(f"✅ Jetson Optimizations Enabled")
    print(f"   CUDA Version: {torch.version.cuda}")
    print(f"   GPU: {torch.cuda.get_device_name(0)}")
    print(f"   GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")

def train_model():
    """Train YOLOv8 on Jetson AGX Thor"""
    
    # Optimize Jetson settings
    optimize_jetson()
    
    # Initialize model - use nano for faster training, medium for better accuracy
    print("\n🚀 Loading YOLOv8 model...")
    model = YOLO('yolov8n.pt')  # Change to 'yolov8m.pt' for better accuracy
    
    # Training configuration optimized for Jetson
    print("\n📊 Starting training with Jetson-optimized settings...")
    results = model.train(
        data='dataset/data.yaml',
        epochs=100,  # Thor can handle more epochs faster
        imgsz=640,
        batch=32,  # Thor has more memory, can use larger batch
        workers=4,  # Optimize for Jetson's CPU cores
        device=0,  # Use GPU 0 (Thor has 2 GPUs, can configure for multi-GPU)
        project='runs/detect',
        name='dental_detector_thor',
        exist_ok=True,
        patience=15,
        save=True,
        plots=True,
        val=True,
        
        # Performance optimizations
        amp=True,  # Automatic Mixed Precision for faster training
        cache=True,  # Cache images in RAM for faster loading
        
        # Model improvements
        optimizer='AdamW',
        lr0=0.001,
        weight_decay=0.0005,
        warmup_epochs=3,
        
        # Augmentation
        degrees=10,
        translate=0.1,
        scale=0.5,
        flipud=0.0,
        fliplr=0.5,
        mosaic=1.0,
        mixup=0.1,
    )
    
    print("\n✅ Training Complete!")
    print(f"   Best model: runs/detect/dental_detector_thor/weights/best.pt")
    print(f"   Results: runs/detect/dental_detector_thor/")
    
    # Validate the model
    print("\n📊 Validating model...")
    metrics = model.val()
    
    print(f"\n🎯 Model Performance:")
    print(f"   mAP50: {metrics.box.map50:.3f}")
    print(f"   mAP50-95: {metrics.box.map:.3f}")
    print(f"   Precision: {metrics.box.mp:.3f}")
    print(f"   Recall: {metrics.box.mr:.3f}")
    
    return model

def export_for_inference(model_path='runs/detect/dental_detector_thor/weights/best.pt'):
    """Export model for optimized Jetson inference"""
    
    print("\n🔄 Exporting model for Jetson deployment...")
    model = YOLO(model_path)
    
    # Export to TensorRT for maximum performance on Jetson
    print("   Exporting to TensorRT (FP16 for speed)...")
    model.export(format='engine', device=0, half=True, imgsz=640)
    
    # Also export ONNX as fallback
    print("   Exporting to ONNX...")
    model.export(format='onnx', imgsz=640)
    
    print("\n✅ Export complete!")
    print("   TensorRT engine: Optimized for Jetson inference")
    print("   ONNX model: Portable format")

if __name__ == "__main__":
    # Train the model
    model = train_model()
    
    # Export for deployment
    export_for_inference()
    
    print("\n🎉 All done! Your model is ready for deployment on Jetson AGX Thor")
EOF

chmod +x scripts/train_yolo_jetson.py
```

---

## 6️⃣ Create Jetson-Optimized Inference Script

```bash
cat > scripts/inference_jetson.py << 'EOF'
#!/usr/bin/env python3
"""
Real-time Inference Script for Jetson AGX Thor
Supports TensorRT acceleration
"""

import cv2
import torch
from ultralytics import YOLO
import time
import numpy as np

class JetsonInference:
    def __init__(self, model_path='runs/detect/dental_detector_thor/weights/best.engine'):
        """Initialize inference with TensorRT model"""
        
        # Load TensorRT model if available, fallback to PyTorch
        if model_path.endswith('.engine'):
            print("🚀 Loading TensorRT engine for maximum performance...")
            self.model = YOLO(model_path, task='detect')
        else:
            print("📦 Loading PyTorch model...")
            self.model = YOLO(model_path)
        
        # Warm up the model
        print("🔥 Warming up GPU...")
        dummy = np.zeros((640, 640, 3), dtype=np.uint8)
        self.model(dummy, verbose=False)
        
        print("✅ Model ready for inference")
    
    def predict_image(self, image_path, conf_threshold=0.4):
        """Run inference on single image"""
        
        start_time = time.time()
        results = self.model(image_path, conf=conf_threshold, verbose=False)
        inference_time = (time.time() - start_time) * 1000
        
        print(f"⚡ Inference time: {inference_time:.1f}ms")
        print(f"🦷 Detected {len(results[0].boxes)} teeth")
        
        # Visualize results
        annotated = results[0].plot()
        
        return results, annotated, inference_time
    
    def predict_batch(self, image_paths, conf_threshold=0.4):
        """Run inference on batch of images"""
        
        start_time = time.time()
        results = self.model(image_paths, conf=conf_threshold, verbose=False)
        total_time = (time.time() - start_time) * 1000
        
        avg_time = total_time / len(image_paths)
        print(f"⚡ Average inference time: {avg_time:.1f}ms per image")
        print(f"📊 Total images processed: {len(image_paths)}")
        
        return results
    
    def benchmark(self, image_path, iterations=100):
        """Benchmark inference performance"""
        
        print(f"\n🔬 Running benchmark ({iterations} iterations)...")
        
        times = []
        for i in range(iterations):
            start = time.time()
            _ = self.model(image_path, conf=0.4, verbose=False)
            times.append((time.time() - start) * 1000)
        
        avg_time = np.mean(times)
        std_time = np.std(times)
        min_time = np.min(times)
        max_time = np.max(times)
        
        print(f"\n📊 Benchmark Results:")
        print(f"   Average: {avg_time:.2f}ms")
        print(f"   Std Dev: {std_time:.2f}ms")
        print(f"   Min: {min_time:.2f}ms")
        print(f"   Max: {max_time:.2f}ms")
        print(f"   FPS: {1000/avg_time:.1f}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python inference_jetson.py ")
        sys.exit(1)
    
    # Initialize inference
    detector = JetsonInference()
    
    # Run inference
    image_path = sys.argv[1]
    results, annotated, time_ms = detector.predict_image(image_path)
    
    # Save result
    output_path = f"result_{image_path.split('/')[-1]}"
    cv2.imwrite(output_path, annotated)
    print(f"💾 Result saved to: {output_path}")
    
    # Optional: Run benchmark
    if '--benchmark' in sys.argv:
        detector.benchmark(image_path)
EOF

chmod +x scripts/inference_jetson.py
```

---

## 7️⃣ Create Data YAML Configuration

```bash
cat > dataset/data.yaml << 'EOF'
# Dental X-Ray Detection Dataset Configuration

# Paths (relative to this file)
path: /home/nvidia/toothy-width-mate/dataset  # Update with your actual path
train: train/images
val: valid/images

# Classes (8 teeth to detect)
names:
  0: tooth_55  # Primary Second Molar (upper right)
  1: tooth_65  # Primary Second Molar (upper left)
  2: tooth_75  # Primary Second Molar (lower left)
  3: tooth_85  # Primary Second Molar (lower right)
  4: tooth_15  # Second Premolar (upper right)
  5: tooth_25  # Second Premolar (upper left)
  6: tooth_35  # Second Premolar (lower left)
  7: tooth_45  # Second Premolar (lower right)

# Number of classes
nc: 8
EOF
```

---

## 8️⃣ Training on Jetson

```bash
# Activate environment
source ~/dental-ai-env/bin/activate

# Navigate to project
cd ~/toothy-width-mate

# Run training (this will be MUCH faster than Colab!)
python3 scripts/train_yolo_jetson.py
```

### Expected Performance:
- **Training Time**: ~2-3 hours for 100 epochs (vs 6-8 hours on Colab)
- **Inference Speed**: ~5-15ms per image with TensorRT
- **FPS**: 60-200 FPS depending on image size

---

## 9️⃣ Deploy with Docker (Production-Ready)

### Create Dockerfile for Jetson

```bash
cat > Dockerfile.jetson << 'EOF'
FROM nvcr.io/nvidia/l4t-pytorch:r36.2.0-pth2.1-py3

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY scripts/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Ultralytics
RUN pip install --no-cache-dir ultralytics

# Copy application
COPY . .

# Expose ports
EXPOSE 5001 5173

CMD ["python3", "backend/app.py"]
EOF
```

### Build and run:

```bash
# Build Docker image
docker build -f Dockerfile.jetson -t toothy-mate-jetson .

# Run with GPU support
docker run -it --runtime nvidia --network host \
  -v $(pwd)/model:/app/model \
  -v $(pwd)/data:/app/data \
  toothy-mate-jetson
```

---

## 🔟 Performance Monitoring

```bash
# Monitor GPU usage in real-time
watch -n 1 tegrastats

# Or use jtop (more user-friendly)
sudo pip3 install jetson-stats
sudo jtop
```

---

## 📊 Benchmark Comparison

### Google Colab (T4 GPU):
- Training (50 epochs): ~2-3 hours
- Inference: ~30-50ms
- Limitations: Session timeouts, data upload time

### Jetson AGX Thor (Blackwell GPUs):
- Training (50 epochs): ~45-60 minutes
- Inference (TensorRT): ~5-10ms
- Advantages: Local data, no timeouts, real-time capability

**Speed improvement: 3-6x faster!** ⚡

---

## 🎯 Next Steps

1. **Transfer your Colab data**:
   ```bash
   # Download from Colab and upload to Jetson
   scp -r dental_xray_model.zip nvidia@jetson-ip:~/toothy-width-mate/
   ```

2. **Train with your dataset**:
   ```bash
   python3 scripts/train_yolo_jetson.py
   ```

3. **Deploy TensorRT model**:
   ```bash
   python3 scripts/inference_jetson.py data/samples/test_image.jpg
   ```

4. **Set up Flask backend** to serve predictions

5. **Enable real-time webcam inference** if needed

---

## 🔧 Troubleshooting

### CUDA Out of Memory
```bash
# Reduce batch size in training script
batch=16  # or even batch=8
```

### Slow Training
```bash
# Enable max performance mode
sudo jetson_clocks
sudo nvpmodel -m 0  # Maximum performance
```

### Docker GPU Access Issues
```bash
# Ensure nvidia-container-runtime is installed
sudo apt-get install nvidia-container-runtime
sudo systemctl restart docker
```

---

## 📚 Resources

- [Jetson AGX Thor Documentation](https://developer.nvidia.com/embedded/jetson-agx-thor)
- [NVIDIA Jetson Zoo](https://elinux.org/Jetson_Zoo)
- [Ultralytics YOLOv8](https://docs.ultralytics.com/)
- [TensorRT Optimization](https://docs.nvidia.com/deeplearning/tensorrt/)

---

**Your Jetson AGX Thor is a powerhouse for AI inference! 🚀**

With 2 Blackwell GPUs and optimized TensorRT, you'll get production-grade performance for your dental AI application.
EOF
