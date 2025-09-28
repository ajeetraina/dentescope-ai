# Dental Width Predictor

A professional AI-powered tool for measuring and predicting tooth width differences between primary second molars and second premolars in dental radiographs.

## Overview

This advanced dental analysis system automates the process of measuring the width difference between primary second molars and underlying second premolars in dental panoramic radiographs. These measurements are essential for orthodontic treatment planning and prediction of tooth development patterns.

## Features

- **AI-Powered Analysis**: Advanced computer vision algorithms for precise tooth detection and measurement
- **Real-time Processing**: Fast analysis of dental radiographs with immediate results
- **Clinical Insights**: Automated generation of clinical recommendations based on measurements
- **Visual Annotations**: Interactive display of measurements overlaid on original X-ray images
- **Professional Interface**: Modern, user-friendly web application designed for clinical use
- **Sample Dataset**: Comprehensive collection of dental radiographs for testing and demonstration

## Technology Stack

This project is built with modern web technologies:

- **Frontend**: React + TypeScript + Vite
- **UI Components**: shadcn-ui + Tailwind CSS
- **Backend**: Supabase Edge Functions
- **AI/ML**: Computer vision algorithms with OpenCV
- **Database**: Supabase PostgreSQL
- **Deployment**: Lovable Cloud Platform

## Clinical Applications

The system provides valuable insights for:
- Orthodontic treatment planning
- Space analysis in mixed dentition
- Prediction of crowding or spacing issues
- Early intervention planning
- Monitoring tooth development patterns

## Getting Started

### Using the Application

1. **Upload X-ray**: Upload a dental panoramic radiograph or select from sample images
2. **AI Analysis**: The system automatically processes the image and detects teeth
3. **View Results**: Review measurements, confidence scores, and clinical recommendations
4. **Annotated Images**: Examine the visual overlay showing detected teeth and measurements

### Sample Dataset

The application includes real dental radiographs from diverse patient cases:
- Various age groups (6-11 years)
- Different clinical presentations
- Normal and abnormal width relationships
- Multiple patient demographics

## Model Performance

- High accuracy tooth detection and identification
- Precise width measurements within clinical tolerance
- Reliable confidence scoring for quality assurance
- Fast processing times suitable for clinical workflows


## Development

To run locally:

```sh
# Clone the repository
git clone <YOUR_GIT_URL>

# Navigate to project directory
cd <YOUR_PROJECT_NAME>

# Install dependencies
npm i

# Start development server
npm run dev
```

