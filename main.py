import streamlit as st
import tempfile
import cv2
import numpy as np
from extract import process_frame
from understand import process_scene, add_text_panel, PANEL_HEIGHT
from llm import process_llm, preprocess
from user_info import get_user_info, update_user_state

ANNOTATED_DURATION = 5
CYCLE_DURATION = 10

st.title("🎥 Video Processing Demo")

# Layout: Upload on the left, instructions or results on right
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### Upload a Video!")
uploaded_file = col1.file_uploader("Select a video file", type=["mp4", "mov", "avi", "mkv"])

if uploaded_file is not None:
    # Write uploaded file to a temp file
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded_file.read())
    tfile_path = tfile.name
    tfile.close()

    # Display input video
    col1.markdown("#### Input Video")
    col1.video(tfile_path)

    if col1.button("Process Video"):
        VIDEO_PATH = tfile_path
        OUTPUT_PATH = "output_video.mp4"

        user_profile = get_user_info()  # load user profile at start

        cap = cv2.VideoCapture(VIDEO_PATH)
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0:
            fps = 30.0

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(OUTPUT_PATH, fourcc, fps, (width, height + PANEL_HEIGHT))

        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        total_duration = frame_count / fps if frame_count > 0 else 0

        frame_index = 0
        current_combined_text = ""
        was_in_annotated_period = False
        last_scene_time = -1.0
        collected_objects = []
        collected_contexts = []

        # We'll use a progress bar to indicate how many annotated segments completed
        total_segments = int(total_duration // ANNOTATED_DURATION) if total_duration > 0 else 1
        segments_completed = 0

        # Update status on right column
        with col2:
            st.markdown("### Processing Status")
            status_text = st.empty()
            progress_bar = st.progress(0)
            status_text.write("Processing...")

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
                    llm_suggestion = process_llm(collected_objects, final_context)

                    current_combined_text = f"{llm_suggestion}"

                    # Debug info to console
                    print(f"\nTime {current_time:.2f}s\n"
                          f"Collected Objects: {collected_objects}\n"
                          f"Collected Contexts (captions): {collected_contexts}\n"
                          f"Final Context: {final_context}\n"
                          f"LLM Suggestion: {llm_suggestion}\n")

                    # Update progress bar and status
                    segments_completed += 1
                    progress_fraction = segments_completed / total_segments
                    progress_bar.progress(min(int(progress_fraction * 100), 100))
                    status_text.write(
                        f"Processed {segments_completed * ANNOTATED_DURATION:.0f}s out of ~{total_duration:.0f}s")

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
                scene_context = process_scene(frame)  # optional line if you want context

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

                final_frame = add_text_panel(ann_frame, current_combined_text)
                out.write(final_frame)
            else:
                final_frame = add_text_panel(frame, current_combined_text)
                out.write(final_frame)

            was_in_annotated_period = in_annotated_period
            frame_index += 1

        cap.release()
        out.release()

        # Mark processing as complete
        with col2:
            status_text.write("Processing complete!")
            st.markdown("#### Output Video")
            with open(OUTPUT_PATH, "rb") as f:
                out_video_bytes = f.read()
            st.video(out_video_bytes)
            st.success("Finished. Output saved at: output_video.mp4")