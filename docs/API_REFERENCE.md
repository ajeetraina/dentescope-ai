# API Reference

## Analyze Endpoint

**POST** `/analyze`

### Request

```json
{
  "image_url": "https://...",
  "image_path": "filename.jpg"
}
```

### Response

```json
{
  "results": [
    {
      "primary_molar": {
        "class": "primary_second_molar_upper_right",
        "width_mm": 10.24,
        "confidence": 0.95
      },
      "premolar": {
        "class": "second_premolar_upper_right",
        "width_mm": 8.14,
        "confidence": 0.93
      },
      "difference_mm": 2.10,
      "within_normal_range": true
    }
  ],
  "total_pairs_detected": 1,
  "annotated_image_base64": "..."
}
```
