#!/bin/bash
# 🦷 Dentescope-AI Quick Setup for Jetson Thor
# This script prepares your Thor system for training

set -e  # Exit on error

echo "🦷 Dentescope-AI Setup for Jetson Thor"
echo "========================================"
echo ""

# Check if running on Jetson
if [ ! -f /etc/nv_tegra_release ] && [ "$(uname -m)" != "aarch64" ]; then
    echo "⚠️  Warning: This doesn't appear to be a Jetson system"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "Step 1/6: Checking system requirements..."
echo "=========================================="

# Check for CUDA
if ! command -v nvidia-smi &> /dev/null; then
    echo "❌ nvidia-smi not found!"
    echo "Please install JetPack 7.0 first"
    exit 1
fi

nvidia-smi
echo "✅ CUDA detected"
echo ""

echo "Step 2/6: Installing Python dependencies..."
echo "==========================================="

# Update pip
python3 -m pip install --upgrade pip

# Install core dependencies
echo "Installing PyTorch and Ultralytics..."
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip3 install ultralytics opencv-python pillow numpy pandas matplotlib

echo "✅ Dependencies installed"
echo ""

echo "Step 3/6: Cloning repository..."
echo "==============================="

if [ -d "dentescope-ai" ]; then
    echo "Directory dentescope-ai already exists"
    read -p "Pull latest changes? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cd dentescope-ai
        git pull
        cd ..
    fi
else
    git clone https://github.com/ajeetraina/dentescope-ai.git
fi

cd dentescope-ai
echo "✅ Repository ready"
echo ""

echo "Step 4/6: Setting up project structure..."
echo "=========================================="

# Create necessary directories
mkdir -p runs/detect
mkdir -p backend/models
mkdir -p logs

# Copy training scripts
if [ -f ../train_thor.py ]; then
    cp ../train_thor.py scripts/
    chmod +x scripts/train_thor.py
    echo "✅ Thor training script installed"
fi

if [ -f ../benchmark_thor.py ]; then
    cp ../benchmark_thor.py scripts/
    chmod +x scripts/benchmark_thor.py
    echo "✅ Benchmark script installed"
fi

echo ""

echo "Step 5/6: Checking dataset..."
echo "============================="

# Count images and annotations
NUM_IMAGES=$(find data/samples -name "*.jpg" 2>/dev/null | wc -l)
NUM_LABELS=$(find dataset/labels -name "*.txt" 2>/dev/null | wc -l)

echo "Images found: $NUM_IMAGES"
echo "Annotations found: $NUM_LABELS"

if [ $NUM_IMAGES -eq 0 ]; then
    echo "⚠️  No sample images found in data/samples/"
    echo "Please add your dental X-ray images"
elif [ $NUM_LABELS -eq 0 ]; then
    echo "⚠️  No annotations found"
    echo "Run annotation tool: python3 scripts/smart_annotator.py"
else
    echo "✅ Dataset ready for training"
fi

echo ""

echo "Step 6/6: Optimizing Thor performance..."
echo "========================================="

echo "Setting performance mode..."
if command -v nvpmodel &> /dev/null; then
    sudo nvpmodel -m 0 || echo "Could not set nvpmodel (may need sudo)"
fi

if command -v jetson_clocks &> /dev/null; then
    sudo jetson_clocks || echo "Could not set jetson_clocks (may need sudo)"
fi

echo "✅ Performance optimization complete"
echo ""

echo "========================================"
echo "✅ Setup Complete!"
echo "========================================"
echo ""
echo "📋 Next Steps:"
echo ""
echo "1️⃣  If you need to annotate images:"
echo "   python3 scripts/smart_annotator.py"
echo ""
echo "2️⃣  Prepare dataset:"
echo "   python3 scripts/prepare_dataset.py"
echo ""
echo "3️⃣  Start training (recommended - medium model):"
echo "   python3 scripts/train_thor.py"
echo ""
echo "   Or train different sizes:"
echo "   python3 scripts/train_thor.py --model n  # Fast (nano)"
echo "   python3 scripts/train_thor.py --model s  # Small"
echo "   python3 scripts/train_thor.py --model m  # Medium (recommended)"
echo "   python3 scripts/train_thor.py --model l  # Large"
echo "   python3 scripts/train_thor.py --model x  # Extra-large"
echo ""
echo "4️⃣  Validate model:"
echo "   python3 scripts/train_thor.py --validate"
echo ""
echo "5️⃣  Export to TensorRT (3-5x speedup):"
echo "   python3 scripts/train_thor.py --export"
echo ""
echo "6️⃣  Benchmark performance:"
echo "   python3 scripts/benchmark_thor.py --all"
echo ""
echo "📖 Full documentation:"
echo "   cat ~/dentescope_thor_training_guide.md"
echo ""
echo "💡 Thor Advantages:"
echo "   - 128GB RAM for large batch sizes"
echo "   - 2070 FP4 TFLOPS AI compute"
echo "   - 3-5x faster than Google Colab"
echo "   - Unlimited training time"
echo ""
echo "🚀 Ready to train world-class dental AI!"
