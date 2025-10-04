# Model Training Guide

## Dataset Preparation

1. **Collect Images**: Gather panoramic radiographs
2. **Annotate**: Use LabelImg or Roboflow
3. **Organize**: Place in dataset/ following structure

## Training

```bash
python scripts/train_model.py
```

## Evaluation

Monitor training with:
- mAP (should be > 0.95)
- Precision/Recall (should be > 0.95)
- Loss curves

## Tips

- Use at least 500 images per class
- Balance dataset across all tooth types
- Apply data augmentation
- Train for 100+ epochs
