import cv2
import numpy as np
from transformers import pipeline

obj_detection_pipeline = pipeline("object-detection", model="facebook/detr-resnet-50")

def process_frame(frame):
    # Convert frame (numpy array) to RGB PIL Image for pipeline
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    # The pipeline expects PIL images or similar
    # We'll convert ndarray to PIL
    from PIL import Image
    pil_image = Image.fromarray(rgb_frame)

    # Run inference
    results = obj_detection_pipeline(pil_image)
    detected_objects = []
    for r in results:
        label = r["label"]
        conf = float(r["score"])
        box = r["box"]
        bbox = [box["xmin"], box["ymin"], box["xmax"], box["ymax"]]
        detected_objects.append({
            "label": label,
            "confidence": conf,
            "bbox": bbox
        })

    # draw the bounding boxes
    annotated_frame = frame.copy()
    # for obj in detected_objects:
    #     x_min, y_min, x_max, y_max = map(int, obj["bbox"])
    #     label = obj["label"]
    #     conf = obj["confidence"]
    #     cv2.rectangle(annotated_frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
    #     text = f"{label} {conf:.2f}"
    #     (text_width, text_height), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
    #     cv2.rectangle(annotated_frame, (x_min, y_min - text_height - 10),
    #                   (x_min + text_width, y_min), (0, 255, 0), -1)
    #     cv2.putText(annotated_frame, text, (x_min, y_min - 5), cv2.FONT_HERSHEY_SIMPLEX,
    #                 0.7, (0, 0, 0), 2)

    return detected_objects, annotated_frame
