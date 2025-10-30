# Integration Guide

## Your Model is Ready!

You've uploaded your trained model to `model/best.pt`.

## Quick Start

```bash
# Pull the latest changes
git pull origin feature/model-integration

# Install dependencies
cd backend
pip install -r requirements.txt

# Test your model
python -c "from ultralytics import YOLO; YOLO('../model/best.pt')"

# Start backend
python app.py
```

## Test API

```bash
curl http://localhost:5001/health
curl http://localhost:5001/api/model-info
```

Your trained model will automatically detect the 8 tooth classes!