import cv2
import os

# Parameters
frame_folder = 'yolov7\inference\detectImg\\frameGallery65\\result'  # Folder containing your frames (images)
output_path = 'yolov7\inference\detectImg\\frameGallery65\\result\\result2.mp4'  # Output video path
frame_rate = 5  # Desired frame rate for the output video (adjust as needed)
resize_factor = 0.7  # Resize factor (e.g., 0.7 for 30% smaller)
# Get the list of frames in the folder and sort them based on numerical order in filenames
frame_files = sorted([os.path.join(frame_folder, f) for f in os.listdir(frame_folder) if f.startswith('frame') and f.endswith('.jpg')], key=lambda x: int(''.join(filter(str.isdigit, x))))

# Check if any frames were found
if not frame_files:
    print("No frames found in the specified folder.")
    exit()

# Get the dimensions of the first frame to determine the video size
first_frame = cv2.imread(frame_files[0])
height, width, layers = first_frame.shape

# Calculate the new dimensions for resizing
new_width = int(width * resize_factor)
new_height = int(height * resize_factor)

# Define the codec and create a VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # You can change the codec as needed (e.g., 'XVID', 'MJPG')
out = cv2.VideoWriter(output_path, fourcc, frame_rate, (new_width, new_height))

# Iterate through the frames, resize them, and write to the video
for frame_file in frame_files:
    frame = cv2.imread(frame_file)
    resized_frame = cv2.resize(frame, (new_width, new_height))
    out.write(resized_frame)

# Release the VideoWriter
out.release()

print(f"Video saved to {output_path}")
