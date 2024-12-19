import cv2
import numpy as np
from PIL import Image
from transformers import pipeline

scene_understanding_pipeline = pipeline("image-to-text", model="nlpconnect/vit-gpt2-image-captioning")

MAX_LINES = 10  # text lines allowed in the panel
PANEL_PADDING = 20
FONT = cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE = 0.7
THICKNESS = 2

(line_width, line_height), _ = cv2.getTextSize("Test", FONT, FONT_SCALE, THICKNESS)
PANEL_HEIGHT = line_height * MAX_LINES + PANEL_PADDING  # fixed panel height

def process_scene(frame):
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(rgb_frame)
    captions = scene_understanding_pipeline(pil_image)
    caption = captions[0]['generated_text'] if captions else "No description available"
    return caption

def add_text_panel(frame, text):
    frame_h, frame_w, _ = frame.shape
    max_text_width = int(frame_w * 0.8)

    # split text by newline to handle multiple lines
    raw_lines = text.split('\n')
    lines = []
    for line in raw_lines:
        words = line.split()
        if not words:
            lines.append("")
            continue
        current_line = words[0]
        for w in words[1:]:
            test_line = current_line + " " + w
            (tw, th), _ = cv2.getTextSize(test_line, FONT, FONT_SCALE, THICKNESS)
            if tw > max_text_width:
                lines.append(current_line)
                current_line = w
            else:
                current_line = test_line
        lines.append(current_line)

    if len(lines) > MAX_LINES:
        lines = lines[:MAX_LINES]

    panel = np.zeros((PANEL_HEIGHT, frame_w, 3), dtype=np.uint8)
    y_offset = PANEL_PADDING // 2 + line_height
    for line in lines:
        (lw, lh), _ = cv2.getTextSize(line, FONT, FONT_SCALE, THICKNESS)
        x_offset = 20
        cv2.putText(panel, line, (x_offset, y_offset), FONT, FONT_SCALE, (255, 255, 255), THICKNESS, cv2.LINE_AA)
        y_offset += lh + 10

    combined = np.vstack((frame, panel))
    return combined