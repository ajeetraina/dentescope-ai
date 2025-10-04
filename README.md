# Dental Width Detection System

AI-powered tool for measuring tooth width differences between primary second molars and second premolars in dental panoramic radiographs.

## Features

- 🦷 Automatic tooth detection using YOLOv8
- 📏 Precise width measurements with magnification correction
- 🎨 Visual annotations matching clinical standards
- 📊 Clinical insights and recommendations
- ⚡ Real-time processing

## Setup

### 1. Backend (Python)

```bash
cd backend
pip install -r requirements.txt
python app.py
```

### 2. Frontend (React)

```bash
cd frontend
npm install
npm run dev
```

### 3. Train Model

```bash
# Prepare your dataset in dataset/ folder
python scripts/train_model.py
```

### 4. Deploy

- Backend: Deploy to Render/Railway using Dockerfile
- Frontend: Deploy to Vercel
- Supabase: Deploy edge function

## Configuration

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

## Usage

1. Upload a panoramic radiograph
2. System automatically detects teeth
3. Measures widths and calculates differences
4. Displays annotated results

## Expected Results

- Primary Second Molar Width: 9-10mm
- Second Premolar Width: 7-8mm
- Width Difference: 2.0-2.8mm (normal range)

## License

MIT
