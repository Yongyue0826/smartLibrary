# From Python
# It requires OpenCV installed for Python
import sys
import cv2
import os
from sys import platform
import argparse
import numpy as np #new added
import openpyxl
from openpyxl import Workbook

# Function to write keypoints to Excel
def write_keypoints_to_excel(right_keypoint, left_keypoint):
    # Check if the Excel file exists
    if not os.path.exists('keypoint_coordinates.xlsx'):
        # Create a new Excel workbook if the file doesn't exist
        workbook = Workbook()
        # Write the header
        sheet = workbook.active
        sheet.cell(row=1, column=1, value="Filename")
        sheet.cell(row=1, column=2, value="Right x")
        sheet.cell(row=1, column=3, value="Right y")
        sheet.cell(row=1, column=4, value="Left x")
        sheet.cell(row=1, column=5, value="Left y")
    else:
        # Load the existing Excel file
        workbook = openpyxl.load_workbook('keypoint_coordinates.xlsx')
        sheet = workbook.active

    
    # Find the last row in the sheet
    last_row = sheet.max_row + 1

    # Extract the x-coordinate, y-coordinate, and confidence score of the keypoints
    right_x_coordinate = right_keypoint[0]
    right_y_coordinate = right_keypoint[1]
    right_confidence_score = right_keypoint[2]
    left_x_coordinate = left_keypoint[0]
    left_y_coordinate = left_keypoint[1]
    left_confidence_score = left_keypoint[2]

    # Write the keypoints to the Excel sheet
    sheet.cell(row=last_row, column=1, value= saved_filename)
    sheet.cell(row=last_row, column=2, value=right_x_coordinate)
    sheet.cell(row=last_row, column=3, value=right_y_coordinate)
    sheet.cell(row=last_row, column=4, value=left_x_coordinate)
    sheet.cell(row=last_row, column=5, value=left_y_coordinate)

    # Save the Excel file
    workbook.save('keypoint_coordinates.xlsx')

def get_latest_gallery_directory(base_path):
    # Find the latest gallery directory number
    i = 1
    latest_gallery = None
    while True:
        gallery_path = os.path.join(base_path, f'frameGallery{i}')
        if not os.path.exists(gallery_path):
            break
        latest_gallery = gallery_path
        i += 1
    return latest_gallery

def get_new_filename(base_path):
    i = 1
    while True:
        filename = os.path.join(base_path, f"frame{i}.jpg")
        if not os.path.exists(filename):
            return filename
        i += 1
        
try:
    # Import Openpose (Windows/Ubuntu/OSX)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    try:
        # Windows Import
        if platform == "win32":
            # Change these variables to point to the correct folder (Release/x64 etc.)
            sys.path.append(dir_path + '/../../build/python/openpose/Release');
            os.environ['PATH']  = os.environ['PATH'] + ';' + dir_path + '/../../build/x64/Release;' +  dir_path + '/../../build/bin;'
            import pyopenpose as op
        else:
            # Change these variables to point to the correct folder (Release/x64 etc.)
            sys.path.append('../../python');
            # If you run `make install` (default path is `/usr/local/python` for Ubuntu), you can also access the OpenPose/python module from there. This will install OpenPose and the python library at your desired installation path. Ensure that this is in your python path in order to use it.
            # sys.path.append('/usr/local/python')
            from openpose import pyopenpose as op
    except ImportError as e:
        print('Error: OpenPose library could not be found. Did you enable `BUILD_PYTHON` in CMake and have this Python script in the right folder?')
        raise e

    # Flags
    parser = argparse.ArgumentParser()
    parser.add_argument("--image_path", default="../media/COCO_val2014_000000000192.jpg", help="Process an image. Read all standard formats (jpg, png, bmp, etc.).")
    args = parser.parse_known_args()

    # Custom Params (refer to include/openpose/flags.hpp for more parameters)
    params = dict()
    params["model_folder"] = "../../models/"

    # Add others in path?
    for i in range(0, len(args[1])):
        curr_item = args[1][i]
        if i != len(args[1])-1: next_item = args[1][i+1]
        else: next_item = "1"
        if "--" in curr_item and "--" in next_item:
            key = curr_item.replace('-','')
            if key not in params:  params[key] = "1"
        elif "--" in curr_item and "--" not in next_item:
            key = curr_item.replace('-','')
            if key not in params: params[key] = next_item

    # Construct it from system arguments
    # op.init_argv(args[1])
    # oppython = op.OpenposePython()

    # Starting OpenPose
    opWrapper = op.WrapperPython()
    opWrapper.configure(params)
    opWrapper.start()

    # Process Image
    datum = op.Datum()
    imageToProcess = cv2.imread(args[0].image_path)
    datum.cvInputData = imageToProcess
    opWrapper.emplaceAndPop(op.VectorDatum([datum]))

    # Display Image
    print("Body keypoints: \n" + str(datum.poseKeypoints))
    #cv2.imshow("OpenPose 1.7.0 - Tutorial Python API", datum.cvOutputData)
    #cv2.waitKey(0)

    # Test
    # Index of the keypoint you want to extract (e.g., 0 for the first keypoint)
    right_keypoint_index = 4
    left_keypoint_index = 7

    # Extract the specified keypoint from the keypoints
    right_keypoint = datum.poseKeypoints[0][right_keypoint_index]
    left_keypoint = datum.poseKeypoints[0][left_keypoint_index]

    # Print the extracted values
    print("Right Keypoint coordinate: (", right_keypoint[0], ",", right_keypoint[1], ")")
    print("Left Keypoint coordinate: (", left_keypoint[0], ",", left_keypoint[1], ")")

    
    # # Save Image
    # base_directory = '../../../yolov7/inference/video'
    # latest_gallery_directory = get_latest_gallery_directory(base_directory)

    # folder_dir = latest_gallery_directory

    # saved_filename = os.path.basename()

    # result = cv2.imwrite(saved_path, datum.cvOutputData)

    # # Write keypoints to Excel
    # write_keypoints_to_excel(right_keypoint, left_keypoint)

    # if result:
    #     print("File saved successfully with file name:", saved_filename)
    # else:
    #     print("Error in saving file")

    # Save Image
    #saved_path = r"..\results\output.jpg"
    base_directory = '../../../yolov7/inference/detectImg'
    latest_gallery_directory = get_latest_gallery_directory(base_directory)

    folder_dir = latest_gallery_directory

    # Find the latest image number in the directory
    image_number = 1
    for image_file in os.listdir(folder_dir):
        if image_file.startswith("frame") and image_file.endswith(".jpg"):
            image_number += 1

    # Set the filename and path for saving the image
    saved_filename = f"frame{image_number}.jpg"
    saved_path = os.path.join(folder_dir, saved_filename)

    # Your existing code for saving the image
    result = cv2.imwrite(saved_path, datum.cvOutputData)

    # Write keypoints to Excel
    write_keypoints_to_excel(right_keypoint, left_keypoint)

    if result==True:
        print("File saved successfully with file name:", saved_filename)
    else:
        print("Error in saving file")

except Exception as e:
    print(e)
    sys.exit(-1)





# C:\Users\60115\.conda\envs\ailib\aiLibrary\openpose\examples\tutorial_api_python\openposeTest.py
# C:\Users\60115\.conda\envs\ailib\aiLibrary\yolov7\detect.py