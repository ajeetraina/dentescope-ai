# 🦷 Dentescope AI

AI-powered tool for measuring tooth width differences between primary second molars and second premolars in dental panoramic radiographs.

## ⚡ Quick Start

**Ready to start training your model?** 

👉 **[READ THE COMPLETE IMPLEMENTATION GUIDE](./IMPLEMENTATION_GUIDE.md)** 👈

### 3-Step Setup:

```bash
# 1. Install dependencies
pip install -r scripts/requirements.txt

# 2. Annotate your images (interactive tool)
python scripts/smart_annotator.py

# 3. Train the model
python scripts/prepare_dataset.py
python scripts/train_yolo.py
```

That's it! Your model will be ready in `model/dental_detector.pt`

---

## 📋 Features

- 🦷 **Automatic tooth detection** using YOLOv8
- 📏 **Precise width measurements** with magnification correction
- 🎨 **Visual annotations** matching clinical standards
- 📊 **Clinical insights** and recommendations
- ⚡ **Real-time processing**
- 🤖 **Smart auto-annotation** tool with AI-assisted region suggestions

## 🎯 Tooth Detection

Detects **8 specific teeth**:
- **Primary Second Molars**: 55, 65, 75, 85
- **Second Premolars**: 15, 25, 35, 45

## 📊 Current Status

✅ **Working:**
- React/Vite frontend with great UI
- 73+ real dental X-ray samples
- Flask backend infrastructure
- YOLOv8 detection class
- Smart annotation tool with auto-suggestions
- Complete training pipeline

🔨 **In Progress:**
- Model training (annotations needed)
- AI-powered detection (requires trained model)

---

## 🚀 Full Setup

### Option 1: Docker (Recommended)

```bash
docker-compose up --build

# Access:
# Frontend: http://localhost:5173
# Backend: http://localhost:5001
```

### Option 2: Manual Setup

#### Backend (Python/Flask)

```bash
cd backend
pip install -r requirements.txt
python app.py
```

#### Frontend (React/Vite)

```bash
npm install
npm run dev
```

---

## 📁 Project Structure

```
toothy-width-mate/
├── data/samples/              # 73+ dental X-ray images
├── scripts/
│   ├── smart_annotator.py    # 🆕 Interactive annotation tool
│   ├── prepare_dataset.py    # 🆕 Dataset preparation
│   ├── train_yolo.py         # 🆕 Model training
│   └── test_model.py         # 🆕 Model testing
├── backend/                   # Flask API
├── src/                       # React frontend
├── model/                     # Trained models
└── dataset/                   # Training data
```

---

## 🎓 Training Your Model

### Step 1: Annotate Images

Run the smart annotator:

```bash
python scripts/smart_annotator.py
```

**Pro tip:** Press `a` for auto-suggestions! The tool will detect tooth regions automatically.

### Step 2: Prepare Dataset

```bash
python scripts/prepare_dataset.py
```

Splits data into 80% training / 20% validation.

### Step 3: Train Model

```bash
python scripts/train_yolo.py
```

Trains YOLOv8 with transfer learning (takes 30-60 min with GPU).

### Step 4: Test Model

```bash
python scripts/test_model.py
```

---

## 📈 Expected Results

After training, your model should achieve:

### Tooth Measurements:
- **Primary Second Molar Width:** 9-10mm
- **Second Premolar Width:** 7-8mm
- **Width Difference:** 2.0-2.8mm (normal range)

### Model Metrics:
- **mAP50:** >0.70 (Excellent) or >0.50 (Good)
- **Detection Confidence:** >80% for clear X-rays

---

## 🛠️ Configuration

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Fill in your credentials (Supabase, etc.)

---

## 📖 Documentation

- **[Complete Implementation Guide](./IMPLEMENTATION_GUIDE.md)** - Detailed step-by-step instructions
- **[GitHub Discussions](https://github.com/ajeetraina/toothy-width-mate/discussions)** - Ask questions, share tips

---

## 💡 Usage Flow

1. **Upload** a panoramic radiograph
2. **Automatic detection** of target teeth
3. **Measure** widths with calibration correction
4. **Visualize** results with clinical annotations
5. **Review** insights and recommendations

---

## 🐛 Troubleshooting

### Model not found?
Make sure you've completed training: `python scripts/train_yolo.py`

### No annotations?
Run the annotator first: `python scripts/smart_annotator.py`

### Display issues?
The annotator requires a GUI. Use VNC or a system with display support.

**More help:** See [IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md)

---

## 🤝 Contributing

Contributions welcome! Please check the issues page or discussions.

---

## 📄 License

MIT

---

## 🎉 What's New

- ✨ Smart annotation tool with AI-assisted region detection
- ✨ Complete training pipeline with transfer learning
- ✨ Automated dataset preparation and splitting
- ✨ Model testing and validation scripts
- ✨ Comprehensive implementation guide

---

**Made with ❤️ for dental professionals and AI enthusiasts**

🔗 [Implementation Guide](./IMPLEMENTATION_GUIDE.md) | 💬 [Discussions](https://github.com/ajeetraina/toothy-width-mate/discussions)
