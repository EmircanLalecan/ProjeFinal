from ultralytics import YOLO

model = YOLO("yolo11x.pt")

model.train(data = "dataset_custom.yaml" , imgsz = 480, batch = 8, epochs = 100, workers = 0, device = 0)