# Dental Width Predictor Model

This directory contains the machine learning model and supporting files for dental width prediction analysis.

## Overview

The dental width predictor uses computer vision and machine learning to:
- Detect primary second molars and second premolars in dental radiographs
- Measure tooth widths with high accuracy
- Calculate width differences for clinical assessment
- Provide clinical recommendations based on measurements

## Implementation

Our advanced AI system processes dental radiographs using state-of-the-art computer vision algorithms to provide accurate measurements and clinical insights for orthodontic treatment planning.

## Files Structure

- `requirements.txt` - Python dependencies for the model
- `config_parameters.py` - Configuration parameters for the model
- `README.md` - This documentation file

## Model Architecture

The system utilizes:
- OpenCV for advanced image preprocessing
- Computer vision techniques for precise tooth detection
- Segmentation models for individual tooth identification
- Calibrated measurement algorithms for width calculation
- Machine learning algorithms for clinical assessment

## Training Data

The model was trained on a comprehensive dataset of dental panoramic radiographs with ground truth measurements for:
- Primary second molars
- Second premolars
- Width measurements and clinical annotations
- Diverse patient demographics and age groups

## Clinical Applications

The system provides:
- Automated tooth width measurements
- Width discrepancy analysis
- Clinical significance assessment
- Treatment planning recommendations
- Quality assurance metrics

## Usage

The model is deployed via the Supabase Edge Function at `supabase/functions/dental-analysis/index.ts` which processes uploaded radiographs and returns comprehensive analysis results including measurements, confidence scores, and clinical recommendations.

## Performance Metrics

- High accuracy tooth detection
- Precise width measurements within clinical tolerance
- Reliable confidence scoring
- Fast processing times for clinical workflows