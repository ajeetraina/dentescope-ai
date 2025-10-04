from roboflow import Roboflow

rf = Roboflow(api_key="40NFqklaKRRkEDSxmjww")
project = rf.workspace("teeth-images").project("rev-dental-test")
version = project.version(1)
dataset = version.download("yolov8")

print(f"Model downloaded to: {dataset.location}")
print(f"Weights: {dataset.location}/train/weights/best.pt")
