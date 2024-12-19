import cv2
from extract import process_frame
from understand import process_scene, add_text_panel, PANEL_HEIGHT
from llm import process_llm, preprocess
from user_info import get_user_info, update_user_state

VIDEO_PATH = "/media/tang/Windows-Storage/HW/CV/Cv_Project/video1.mp4"
OUTPUT_PATH = "/media/tang/Windows-Storage/HW/CV/Cv_Project/video2.mp4"

ANNOTATED_DURATION = 5   # 5s annotated
CYCLE_DURATION = 10      # total cycle: 5s annotated, 5s original

cap = cv2.VideoCapture(VIDEO_PATH)
fps = cap.get(cv2.CAP_PROP_FPS)
if fps <= 0:
    fps = 30.0

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
out = cv2.VideoWriter(OUTPUT_PATH, fourcc, fps, (width, height + PANEL_HEIGHT))
frame_index = 0

current_combined_text = ""
was_in_annotated_period = False

last_scene_time = -1.0
collected_objects = []
collected_contexts = []  # store captions (context) each second

user_profile = get_user_info()  # load user profile at start
while True:
    ret, frame = cap.read()
    if not ret:
        break

    current_time = frame_index / fps
    cycle_pos = current_time % CYCLE_DURATION
    in_annotated_period = (cycle_pos < ANNOTATED_DURATION)

    # exit the annotated period
    if was_in_annotated_period and not in_annotated_period:
        if collected_objects and collected_contexts:
            # preprocess collected contexts
            final_context = preprocess(collected_contexts)

            # get LLM suggestion
            # llm_suggestion = process_llm(collected_objects, final_context)
            llm_suggestion = process_llm(collected_objects, collected_contexts)
            current_combined_text = f"{llm_suggestion}"

            print(f"\nTime {current_time:.2f}s\n"
                  f"Collected Objects: {collected_objects}\n"
                  f"Collected Contexts (captions): {collected_contexts}\n"
                  f"Final Context: {final_context}\n"
                  f"LLM Suggestion: {llm_suggestion}\n")

        # clear
        collected_objects.clear()
        collected_contexts.clear()
        last_scene_time = -1.0

    # enter the annotated period
    if in_annotated_period and not was_in_annotated_period:
        collected_objects.clear()
        collected_contexts.clear()
        last_scene_time = -1.0

    if in_annotated_period:
        detected_objects, ann_frame = process_frame(frame)
        scene_context = process_scene(frame)  # added line

        # collect unique objects
        for obj in detected_objects:
            label = obj['label']
            if label not in [o['label'] for o in collected_objects]:
                collected_objects.append(obj)

        # if 1s has passed since last scene processing
        if last_scene_time < 0 or (current_time - last_scene_time) >= 1.0:
            caption = process_scene(ann_frame)
            collected_contexts.append(caption)
            last_scene_time = current_time
        else:
            pass

        # no LLM suggestion
        final_frame = add_text_panel(ann_frame, current_combined_text)
        out.write(final_frame)
    else:
        # show last LLM suggestion
        final_frame = add_text_panel(frame, current_combined_text)
        out.write(final_frame)

    was_in_annotated_period = in_annotated_period
    frame_index += 1

cap.release()
out.release()
print("Finished. Output saved at:", OUTPUT_PATH)
