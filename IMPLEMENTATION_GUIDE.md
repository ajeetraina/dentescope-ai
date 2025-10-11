# 🦷 Toothy Width Mate - Complete Implementation Guide

## 📋 Quick Start (3 Easy Steps!)

### Step 1: Annotate Your Images
```bash
# Run the smart annotator
python scripts/smart_annotator.py
```

**Controls:**
- Click and drag to draw bounding boxes around teeth
- Press `0-7` to select tooth class:
  - 0 = Tooth 55 (Primary Second Molar)
  - 1 = Tooth 65 (Primary Second Molar)
  - 2 = Tooth 75 (Primary Second Molar)
  - 3 = Tooth 85 (Primary Second Molar)
  - 4 = Tooth 15 (Second Premolar)
  - 5 = Tooth 25 (Second Premolar)
  - 6 = Tooth 35 (Second Premolar)
  - 7 = Tooth 45 (Second Premolar)
- Press `a` to auto-suggest tooth regions
- Press `d` to delete last box
- Press `s` to save and move to next image
- Press `q` to quit

**Tip:** The annotator will automatically suggest tooth regions! Press `a` to accept suggestions, then adjust as needed.

### Step 2: Prepare Dataset
```bash
# Organize annotations into train/val splits
python scripts/prepare_dataset.py
```

This will:
- Split your data into 80% training and 20% validation
- Create proper YOLO directory structure
- Generate `dataset/dataset.yaml` config file

### Step 3: Train Model
```bash
# Train YOLOv8 on your dental X-rays
python scripts/train_yolo.py
```

Training will:
- Use transfer learning from YOLOv8n pretrained model
- Train for 100 epochs (will stop early if no improvement)
- Save best model to `model/dental_detector.pt`
- Show validation metrics (mAP50, mAP50-95)

---

## 📊 Testing Your Model

After training, test the model:

```bash
python scripts/test_model.py
```

This will:
- Run inference on sample images
- Display detected teeth with confidence scores
- Save annotated images to `test_results/`

---

## 🚀 Running the Full Application

### Using Docker Compose (Recommended)

```bash
# Start the entire application
docker-compose up --build

# Access the app
# Frontend: http://localhost:5173
# Backend: http://localhost:5001
```

### Manual Setup

#### Backend:
```bash
cd backend
pip install -r requirements.txt
python app.py
```

#### Frontend:
```bash
npm install
npm run dev
```

---

## 📁 Project Structure

```
toothy-width-mate/
├── data/
│   └── samples/              # 73+ dental X-ray images
├── dataset/
│   ├── labels/               # YOLO format annotations
│   ├── train/
│   │   ├── images/
│   │   └── labels/
│   ├── val/
│   │   ├── images/
│   │   └── labels/
│   └── dataset.yaml          # YOLO config file
├── model/
│   └── dental_detector.pt    # Trained model
├── scripts/
│   ├── smart_annotator.py    # Interactive annotation tool
│   ├── prepare_dataset.py    # Dataset preparation
│   ├── train_yolo.py         # Model training
│   └── test_model.py         # Model testing
├── backend/
│   ├── app.py                # Flask API
│   └── dental_width_analyzer.py
└── src/                      # React frontend
```

---

## 🎯 How Many Images to Annotate?

**Minimum:** 20-30 images (for basic functionality)
**Recommended:** 50-70 images (for better accuracy)
**Optimal:** All 73 images (for best performance)

**Pro Tip:** Start with 20 images, train, test, then add more if needed!

---

## 💡 Tips for Better Annotations

1. **Use Auto-Suggestions:** Press `a` to get AI-suggested tooth regions as a starting point
2. **Be Consistent:** Try to annotate all 8 teeth in each X-ray if visible
3. **Quality over Quantity:** 20 well-annotated images > 70 poorly annotated ones
4. **Check Your Work:** Review a few annotations before continuing
5. **Save Often:** Press `s` after each image to save progress

---

## 🐛 Troubleshooting

### "No annotated images found!"
- Make sure you ran `scripts/smart_annotator.py` first
- Check that `dataset/labels/` contains `.txt` files

### "Model not found!"
- Ensure training completed successfully
- Check `model/dental_detector.pt` exists

### "CUDA out of memory"
- Reduce batch size in `scripts/train_yolo.py` (change `batch: 16` to `batch: 8`)
- Or train on CPU (will be slower but works)

### Display issues with annotator
- On headless servers, use VNC or X11 forwarding
- Or use cloud instances with GUI support

---

## 📈 Expected Training Time

- **With GPU (NVIDIA):** 30-60 minutes for 100 epochs
- **Without GPU (CPU only):** 2-4 hours for 100 epochs

---

## 🎓 Understanding the Output

### Training Metrics:
- **mAP50:** Mean Average Precision at 50% IoU threshold (higher is better, aim for >0.7)
- **mAP50-95:** Mean Average Precision averaged over IoU thresholds (aim for >0.5)

### Good Results:
- mAP50 > 0.70 = Excellent
- mAP50 > 0.50 = Good
- mAP50 > 0.30 = Acceptable for initial version

---

## 🔄 Improving Model Performance

If results aren't great:

1. **Add More Annotations:** Annotate more images
2. **Improve Annotation Quality:** Review and fix existing annotations
3. **Train Longer:** Increase epochs to 150-200
4. **Adjust Augmentation:** Modify parameters in `train_yolo.py`
5. **Try Different Model:** Use `yolov8s.pt` instead of `yolov8n.pt` (slower but more accurate)

---

## 🎉 Next Steps After Training

1. **Integrate with Backend:** Update `backend/dental_width_analyzer.py` to use your trained model
2. **Update Frontend:** Enhance UI to show detected teeth
3. **Add Width Calculation:** Implement actual tooth width measurement logic
4. **Deploy:** Use Docker to deploy your application

---

## 🤝 Need Help?

- Check the GitHub Discussions: https://github.com/ajeetraina/toothy-width-mate/discussions
- Review training logs in `runs/detect/dental_tooth_detector/`
- Test on fewer images first to debug issues

---

## ⚡ Quick Commands Reference

```bash
# Complete workflow
python scripts/smart_annotator.py  # Step 1: Annotate
python scripts/prepare_dataset.py  # Step 2: Prepare
python scripts/train_yolo.py       # Step 3: Train
python scripts/test_model.py       # Step 4: Test

# Run application
docker-compose up --build          # All-in-one

# Or manually
python backend/app.py              # Backend
npm run dev                        # Frontend
```

---

## 📊 Sample Annotation Session

```
🦷 Dental X-Ray Annotator
Found 73 images

📊 AARUSH 7 YRS MALE_DR DEEPAK K_2017_07_31_2D_Image_Shot
   Found 12 suggested tooth regions
   
[User presses 'a' to auto-suggest, adjusts boxes, presses 's']
   
✅ Saved 8 annotations

📊 ABHIGNYA GOWRI 12 YRS FEMALE_DR ARATI SUNDAR_2015_09_17_PAN4708
   Found 15 suggested tooth regions
   ...
```

---

Made with ❤️ for dental professionals and AI enthusiasts!
