import cv2
import os

def get_next_gallery_directory(base_path):
    # Find the last gallery directory number and increment it
    i = 1
    while True:
        gallery_path = os.path.join(base_path, f'frameGallery{i}')
        if not os.path.exists(gallery_path):
            return gallery_path
        i += 1

video = cv2.VideoCapture("yolov7/inference/video/library.mp4")

try:
    base_directory = 'yolov7/inference/video'
    gallery_directory = get_next_gallery_directory(base_directory)
    os.makedirs(gallery_directory)

except OSError:
    print("Error: Creating Directory of Data")

desired_time_interval = 2  # Set the desired time interval in seconds (e.g., 2 seconds)
fps = video.get(cv2.CAP_PROP_FPS)
frame_interval = int(fps * desired_time_interval)
current_frame = 0

while True:
    ret, frame = video.read()
    if ret:
        if current_frame % frame_interval == 0:
            name = os.path.join(gallery_directory, f'frame{current_frame}.jpg')
            print("Creating..." + name)

            cv2.imwrite(name, frame)

        current_frame += 1
    else:
        break

video.release()
cv2.destroyAllWindows()