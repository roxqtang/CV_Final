import torch
import cv2
import numpy as np
from transformers import pipeline
from PIL import Image
# Move YOLO model to GPU if available

# Initialize the captioning pipeline on GPU if available
device = 0 if torch.cuda.is_available() else -1
print(device)

# Load the YOLOv5 object detection model
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

if torch.cuda.is_available():
    model.to('cuda')

# Start video capture (0 for webcam)
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Object detection
    results = model(frame)
    df = results.pandas().xyxy[0]

    # Scene understanding
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(rgb_frame)

    # Draw bounding boxes and labels for detected objects
    for index, row in df.iterrows():
        xmin, ymin, xmax, ymax = int(row['xmin']), int(row['ymin']), int(row['xmax']), int(row['ymax'])
        confidence = row['confidence']
        label = f"{row['name']} {confidence:.2f}"
        cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
        cv2.putText(frame, label, (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36,255,12), 2)


    cv2.namedWindow('Real-Time Object Detection and Scene Understanding', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Real-Time Object Detection and Scene Understanding',
                     frame.shape[1], frame.shape[0])

    # Display the resulting combined frame

    line_height = 1 + 10
    panel_height = 1
    panel = np.zeros((panel_height, frame.shape[1], 3), dtype=np.uint8)
    cv2.imshow('Real-Time Object Detection and Scene Understanding',np.vstack((frame, panel)))

    # Press 'q' to exit
    if cv2.waitKey(1) == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
