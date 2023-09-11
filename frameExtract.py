import cv2
import numpy as np
import os
import sys
from datetime import date
import datetime

today = str(date.today())

## Directory Manage
os.chdir("../yolov7") # direct to the yolov7 folder

current_path = os.path.dirname(os.path.abspath(__file__)) # ..\AiLibrary\yolov7
parent_path = os.path.dirname(current_path) # ..\AiLibrary
output_path = parent_path + "\Result\\"+ today
sys.path.append(current_path)
# import recordData

# ######To create csv file
# csvName = 'record.csv'
# fieldnames = ['Date', 'Time','Folder','frameNo', 'rightHand', 'leftHand', 'bookCoordinate', 'Action']
#         #Folder: Output1
#         #Date: 8-9-2023
#         #Time:
#         #frameNo: frame1
#         #rightHand:(0.00, 0.00),(0.00,0.00),(0.00,0.00),(0.00,0.00)
#         #leftHand:(0.00, 0.00),(0.00,0.00),(0.00,0.00),(0.00,0.00)
#         #bookCoordinate:(0.00, 0.00),(0.00,0.00),(0.00,0.00),(0.00,0.00)
#         #Action: [Reading, holding, pending]
# recordData.csvCreate(output_path,csvName, fieldnames)

# def chkFolder():
#     filename = 'output'
#     folder = recordData.chkAndCreateFolder(output_path, filename)
#     frameFolder = folder + '\\frameCapture\\'
#     try:
#         if not os.path.exists(frameFolder):
#             print(frameFolder)
#             os.makedirs(frameFolder)
            
#     except OSError:
#         print("Error: Creating Directory of Data")
        
#     return frameFolder 
    
# def writeCSV(file_path, date, time, folderName, frame):   
#     data = [date, time, folderName, frame, ' ', ' ', ' ', ' ']
    
#     recordData.csvCreate(file_path, csvName, data)

def frameExtract(input, output):
    print("Start extract frames from ", input)
    # Open the video file
    cap = cv2.VideoCapture(input)

    # Get the original video's frame rate (FPS)
    original_fps = int(cap.get(cv2.CAP_PROP_FPS))

    # Calculate the desired time interval between frames (0.25 seconds)
    desired_time_interval = 3  # in seconds = 0.25

    # Calculate the frame interval based on the desired time interval
    frame_interval = int(original_fps * desired_time_interval)

    # Initialize a frame counter
    frame_counter = 1

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        # Save the frame if it's the appropriate frame according to the frame interval
        if frame_counter % frame_interval == 0:
            # Apply noise reduction
            frame = cv2.fastNlMeansDenoisingColored(frame, None, 10, 10, 7, 21)

            # Increase contrast and brightness
            alpha = 1.5  # Contrast control
            beta = 30    # Brightness control
            frame = cv2.convertScaleAbs(frame, alpha=alpha, beta=beta)
            
            # Get the current time
            current_time = datetime.datetime.now().time()
            # Format the time as hh:mm:ss
            formatted_time = str(current_time.strftime("%H:%M:%S"))
            # Construct the output frame filename with the "frameX.jpg" format
            num = frame_counter // frame_interval
            frameNo = 'frame'+ str(num)
            #save data to csv file
            #filepath = os.path.dirname(os.path.dirname(os.path.dirname(output))) #C:\Users\X\AiLibrary\Result\2023-09-08
            foldername = os.path.basename(os.path.dirname(os.path.dirname(output))) #outputX
            print("output path:", output_path)
            
            #writeCSV(output_path,today, formatted_time, str(foldername), frameNo)
            
            output_frame_path = os.path.join(output, f'{frameNo}.jpg')
            cv2.imwrite(output_frame_path, frame)

        frame_counter += 1

    # Release the video capture object
    cap.release()

    # Print a message when done
    print(f"Frames extracted at {desired_time_interval} seconds interval to {output}.")

input_path = current_path + "\inference\\videos\library.mp4"
output_folder = output_path
frameExtract(input_path, output_folder)