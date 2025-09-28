# Dental Width Predictor Model

This directory contains the machine learning model and supporting files for dental width prediction analysis.

## Overview

The dental width predictor uses computer vision and machine learning to:
- Detect primary second molars and second premolars in dental radiographs
- Measure tooth widths with high accuracy
- Calculate width differences for clinical assessment
- Provide clinical recommendations based on measurements

## Current Implementation

**Note**: The current implementation uses a **simulated model** that generates realistic but mock data. The actual trained model from the original repository is not yet integrated.

## Files Structure

- `requirements.txt` - Python dependencies for the model
- `config_parameters.py` - Configuration parameters for the model
- `README.md` - This documentation file

## Next Steps for Model Integration

To integrate the actual trained model:

1. **Download Model Files**: Extract the actual model weights/files from the original repository
2. **Create Model Interface**: Build a Python-based API that can be called from the Supabase Edge Function
3. **Docker Integration**: Package the model in a container that can be deployed alongside the web application
4. **Model Hosting**: Deploy the model on a service like Hugging Face, Replicate, or custom infrastructure

## Model Architecture

Based on the original repository, the model likely uses:
- OpenCV for image preprocessing
- Computer vision techniques for tooth detection
- Segmentation models for individual tooth identification
- Measurement algorithms for width calculation

## Training Data

The model was trained on a dataset of dental panoramic radiographs with ground truth measurements for:
- Primary second molars
- Second premolars
- Width measurements and clinical annotations

## Usage

Currently the model is called via the Supabase Edge Function at `supabase/functions/dental-analysis/index.ts` which returns simulated results. Once the actual model is integrated, this same interface will call the real model.