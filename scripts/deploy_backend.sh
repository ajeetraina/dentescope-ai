#!/bin/bash

echo "Deploying Python Backend..."

# Build Docker image
docker build -t dental-backend ./backend

# Tag for registry
docker tag dental-backend your-registry/dental-backend:latest

# Push to registry
docker push your-registry/dental-backend:latest

echo "Backend deployed!"
