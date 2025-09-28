#!/bin/bash

# Build script for dental width predictor

echo "Building dental width predictor containers..."

# Build main application
echo "Building main application..."
docker build -t dental-width-predictor:latest .

# Build model service (optional)
echo "Building model service..."
docker build -t dental-model-service:latest ./model

echo "Build completed successfully!"
echo ""
echo "To run the application:"
echo "  docker-compose up -d"
echo ""
echo "To run with model service:"
echo "  docker-compose --profile with-model up -d"
echo ""
echo "Access the application at: http://localhost:3000"