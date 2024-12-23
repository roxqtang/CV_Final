# Earth Online
CV Final Project 2024 Fall

## Project Description
To bring a Flow State experience to the users, we propose a system that can automatically detect the user's state and provide appropriate feedback.
## Project Implementation
We used Vision Models to detect the user's state and Large Language Models to analyze the user's state and provide appropriate feedback.
## Testing with your own video
1. Download the video you want to test.
2. in main.py, change the VIDEO_PATH to the path of your video. And OUTPUT_PATH to the path where you want to save the analyzed video. \
MAKE SURE IT IS IN MP4 FORMAT! 
For example, 
```
VIDEO_PATH = "/Users/yourname/Desktop/test.mp4"
OUTPUT_PATH = "/Users/yourname/Desktop/test_output.mp4"
```
3. Run the `main.py` file.
```
python main.py
```
4. The video will be processed and the results will be saved in the OUTPUT_PATH.
