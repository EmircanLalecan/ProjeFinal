from ultralytics import YOLO

model = YOLO("yolov11_custom.pt")

model.predict(source = "0", show=True, conf=0.4)