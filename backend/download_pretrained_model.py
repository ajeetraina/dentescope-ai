from roboflow import Roboflow
import os

# Initialize Roboflow (you'll need a free account)
# Get API key from: https://app.roboflow.com/settings/api

API_KEY = input("Enter your Roboflow API key: ")
rf = Roboflow(api_key=API_KEY)

print("\nSearching for dental detection models...")
print("\nPopular options:")
print("1. Tooth Detection - panoramic X-rays")
print("2. Dental Segmentation")
print("3. Mixed Dentition Analysis")

# Example: Download a specific project
# workspace = rf.workspace("workspace-name")
# project = workspace.project("project-name")
# dataset = project.version(1).download("yolov8")

print("\nManual steps:")
print("1. Go to: https://universe.roboflow.com")
print("2. Search: 'dental tooth detection' or 'panoramic radiograph'")
print("3. Find a model with good performance (mAP > 0.80)")
print("4. Click 'Download Dataset'")
print("5. Select 'YOLOv8' format")
print("6. Copy the download code")
