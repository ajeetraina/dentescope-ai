from ultralytics import YOLO

def train():
    model = YOLO('yolov8n.pt')
    
    results = model.train(
        data='dataset/data.yaml',
        epochs=100,
        imgsz=640,
        batch=16,
        device='0',
        patience=20,
        save=True,
        project='runs/train',
        name='dental_detection',
        hsv_h=0.015,
        hsv_s=0.7,
        hsv_v=0.4,
        degrees=10,
        translate=0.1,
        scale=0.5,
        flipud=0.0,
        fliplr=0.5,
        mosaic=1.0,
    )
    
    print("Training complete!")
    print(f"Best model saved to: {results.save_dir}")

if __name__ == '__main__':
    train()
