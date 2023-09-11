import cv2
import os
import re

# Path to the folder containing your frames
frames_folder = 'frameCapture'

# Get a list of all image files in the folder and filter by ".jpg" extension
image_files = [os.path.join(frames_folder, img) for img in os.listdir(frames_folder) if img.endswith(".jpg")]

# Function to extract the frame number from a filename
def extract_frame_number(filename):
    match = re.search(r'frame(\d+)', filename)
    if match:
        return int(match.group(1))
    return -1  # Or another suitable value if no frame number is found

# Sort the image files by frame number, using the custom function
image_files.sort(key=extract_frame_number)

# Read the first frame to get its dimensions
first_frame = cv2.imread(image_files[0])
frame_height, frame_width, _ = first_frame.shape

# Create a window for displaying frames and set its size to match the frame
cv2.namedWindow('Display Frames', cv2.WINDOW_NORMAL)
cv2.resizeWindow('Display Frames', frame_width, frame_height)

# Define the initial frame rate and delay
frame_rate = 30
delay = int(10000 / frame_rate)  # Delay in milliseconds

# Loop through the image files and display each frame
for image_file in image_files:
    frame = cv2.imread(image_file)
    cv2.imshow('Display Frames', frame)
    
    # Display the current frame for the specified delay
    key = cv2.waitKey(delay) & 0xFF
    
    # Press 'q' to exit the loop, 'd' to decrease frame rate, and 'i' to increase frame rate
    if key == ord('q'):
        break
    elif key == ord('d'):
        frame_rate -= 1
        delay = int(1000 / frame_rate)
    elif key == ord('i'):
        frame_rate += 1
        delay = int(1000 / frame_rate)

# Close the window and cleanup
cv2.destroyAllWindows()
