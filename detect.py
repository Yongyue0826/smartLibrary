import argparse
import time
from pathlib import Path

import cv2
import torch
import torch.backends.cudnn as cudnn
from numpy import random
import numpy as np

from models.experimental import attempt_load
from utils.datasets import LoadStreams, LoadImages
from utils.general import check_img_size, check_requirements, check_imshow, non_max_suppression, apply_classifier, \
    scale_coords, xyxy2xywh, strip_optimizer, set_logging, increment_path
from utils.plots import plot_one_box
from utils.torch_utils import select_device, load_classifier, time_synchronized, TracedModel
from shapely.geometry import Polygon, Point

import sys
import os
import openpyxl
import imutils
import natsort
import csv

# retrieve current directory of openposeTest.py and add it into the model path 
openpose_test_dir = os.path.join(os.path.dirname(__file__), "..", "openpose", "examples", "tutorial_api_python")
sys.path.append(openpose_test_dir)


def get_latest_excel_file(base_directory):
    excel_version = 1
    latest_excel_file = None

    while True:
        excel_file_name = os.path.join(base_directory, f'keypoint_coordinates_v{excel_version}.xlsx')
        if not os.path.exists(excel_file_name):
            break
        latest_excel_file = excel_file_name
        excel_version += 1

    return latest_excel_file

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

def read_keypoints_from_excel(filename):
    keypoints_data = []

    base_directory = "inference/detectImg"
    latest_gallery_directory = get_latest_gallery_directory(base_directory)

     # Construct the path to the latest Excel file
    excel_file_path = os.path.join(latest_gallery_directory, 'keypoint_coordinates.xlsx')

    # Check if the Excel file exists
    if not os.path.exists(excel_file_path):
        return keypoints_data

    # Load the existing Excel file
    workbook = openpyxl.load_workbook(excel_file_path)
    sheet = workbook.active

    # Loop through all rows in the sheet
    for row in sheet.iter_rows(min_row=2, values_only=True):
        data = {
            'filename': row[0],
            'right_x1': row[1],
            'right_y1': row[2],
            'right_x2': row[3],
            'right_y2': row[4],
            'left_x1': row[5],
            'left_y1': row[6],
            'left_x2': row[7],
            'left_y2': row[8]
        }        
        keypoints_data.append(data)
        return keypoints_data

# Read the shelf data from the CSV file with an optional maximum limit
def read_shelf_data(file_path):
    with open(file_path, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        
        # Initialize lists to store names and coordinates
        max_shelf = 3
        shelf_names = []
        shelf_polygons = []
        
        for row in reader:
            if max_shelf is not None and len(shelf_polygons) >= max_shelf:
                break  # Stop processing if the maximum number of coordinates is reached
            
            shelf_name = row['name']
            shelf_coords = []
            
            # Extract 'x' and 'y' coordinates dynamically
            for i in range(1, 10):  # Adjust the range as needed for the maximum expected coordinates
                key_x = f'x{i}'
                key_y = f'y{i}'
                
                # Check if both 'x' and 'y' keys exist in the row and are not None
                if key_x in row and key_y in row and row[key_x] is not None and row[key_y] is not None:
                    shelf_coords.append((float(row[key_x]), float(row[key_y])))
                else:
                    break  # Stop processing if either 'x' or 'y' is missing or invalid
            
            # Create a Polygon object only if there are valid coordinates
            if shelf_coords:
                shelf_names.append(shelf_name)
                shelf_polygons.append(Polygon(shelf_coords))
    
    return shelf_names, shelf_polygons

def detect(save_img=False):

    source, weights, view_img, save_txt, imgsz, trace = opt.source, opt.weights, opt.view_img, opt.save_txt, opt.img_size, not opt.no_trace
    save_img = not opt.nosave and not source.endswith('.txt')  # save inference images
    webcam = source.isnumeric() or source.endswith('.txt') or source.lower().startswith(
        ('rtsp://', 'rtmp://', 'http://', 'https://'))

    # Directories
    #save_dir = Path(increment_path(Path(opt.project) / opt.name, exist_ok=opt.exist_ok))  # increment run
    #(save_dir / 'labels' if save_txt else save_dir).mkdir(parents=True, exist_ok=True)  # make dir
    yolo_base_directory = "inference/detectImg"
    yolo_latest_gallery_directory = get_latest_gallery_directory(yolo_base_directory)
    result_directory_path = os.path.join(yolo_latest_gallery_directory, "result")

    if not yolo_latest_gallery_directory:
        print("No gallery directory found.")
        return

    save_dir = Path(result_directory_path)
    if save_txt:
         (save_dir / 'labels').mkdir(exist_ok=True)
    
    # save_dir = Path("runs/detect")
    # if not save_dir.exists():
    #     save_dir.mkdir(parents=True)
    # if save_txt:
    #     (save_dir / 'labels').mkdir(exist_ok=True)

    # Initialize
    set_logging()
    device = select_device(opt.device)
    half = device.type != 'cpu'  # half precision only supported on CUDA

    # Load model
    model = attempt_load(weights, map_location=device)  # load FP32 model
    stride = int(model.stride.max())  # model stride
    imgsz = check_img_size(imgsz, s=stride)  # check img_size

    if trace:
        model = TracedModel(model, device, opt.img_size)

    if half:
        model.half()  # to FP16

    # Second-stage classifier
    classify = False
    if classify:
        modelc = load_classifier(name='resnet101', n=2)  # initialize
        modelc.load_state_dict(torch.load('weights/resnet101.pt', map_location=device)['model']).to(device).eval()

    # Set Dataloader
    vid_path, vid_writer = None, None
    if webcam:
        view_img = check_imshow()
        cudnn.benchmark = True  # set True to speed up constant image size inference
        dataset = LoadStreams(source, img_size=imgsz, stride=stride)
    else:
        dataset = LoadImages(source, img_size=imgsz, stride=stride)

    # Get names and colors
    names = model.module.names if hasattr(model, 'module') else model.names
    colors = [[random.randint(0, 255) for _ in range(3)] for _ in names]

    # Load shelf names and bookshelf coordinates from the CSV file
    shelf_names, bookshelf_coords = read_shelf_data('bookshelf_config.csv')

    # Create Polygon objects for the bookshelf regions
    bookshelf_polygons = [Polygon(coords) for coords in bookshelf_coords]
    
    # Run inference
    if device.type != 'cpu':
        model(torch.zeros(1, 3, imgsz, imgsz).to(device).type_as(next(model.parameters())))  # run once
    old_img_w = old_img_h = imgsz
    old_img_b = 1

    t0 = time.time()
    # Sort the files by name before processing
    file_list = natsort.natsorted(dataset, key=lambda x: x[0])

    for path, img, im0s, vid_cap in file_list:
        img = torch.from_numpy(img).to(device)
        img = img.half() if half else img.float()  # uint8 to fp16/32
        img /= 255.0  # 0 - 255 to 0.0 - 1.0
        if img.ndimension() == 3:
            img = img.unsqueeze(0)

        # Warmup
        if device.type != 'cpu' and (old_img_b != img.shape[0] or old_img_h != img.shape[2] or old_img_w != img.shape[3]):
            old_img_b = img.shape[0]
            old_img_h = img.shape[2]
            old_img_w = img.shape[3]
            for i in range(3):
                model(img, augment=opt.augment)[0]

        # Inference
        t1 = time_synchronized()
        with torch.no_grad():   # Calculating gradients would cause a GPU memory leak
            pred = model(img, augment=opt.augment)[0]
        t2 = time_synchronized()

        # Apply NMS
        pred = non_max_suppression(pred, opt.conf_thres, opt.iou_thres, classes=opt.classes, agnostic=opt.agnostic_nms)
        t3 = time_synchronized()

        # Apply Classifier
        if classify:
            pred = apply_classifier(pred, modelc, img, im0s)

        # Process detections
        for i, det in enumerate(pred):  # detections per image
            if webcam:  # batch_size >= 1
                p, s, im0, frame = path[i], '%g: ' % i, im0s[i].copy(), dataset.count
            else:
                p, s, im0, frame = path, '', im0s, getattr(dataset, 'frame', 0)

            p = Path(p)  # to Path
            save_path = str(save_dir / p.name)  # img.jpg
            txt_path = str(save_dir / 'labels' / p.stem) + ('' if dataset.mode == 'image' else f'_{frame}')  # img.txt
            gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]  # normalization gain whwh

            # Draw bookshelf polygons on the image
            for shelf_polygon in bookshelf_polygons:
                shelf_points = shelf_polygon.exterior.coords  # Get the polygon points
                shelf_points = [(int(x), int(y)) for x, y in shelf_points]  # Convert to integer coordinates
                cv2.polylines(im0, [np.array(shelf_points)], isClosed=True, color=(0, 255, 0), thickness=2)  # Draw polygon

            if len(det):
                # Rescale boxes from img_size to im0 size
                det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()

                # Print results
                for c in det[:, -1].unique():
                    n = (det[:, -1] == c).sum()  # detections per class
                    s += f"{n} {names[int(c)]}{'s' * (n > 1)}, "  # add to string

                #Test
                # Get the filename of the current image
                image_filename = os.path.basename(path)
                print(f"Processing image: {image_filename}")
                # Read keypoints data from Excel for the current image filename
                keypoints_data = read_keypoints_from_excel(image_filename)

                # Test
                if keypoints_data:
                # Loop through the keypoints data for the current image
                    for data in keypoints_data:
                        right_buffer_x1= data['right_x1']
                        right_buffer_y1 = data['right_y1']
                        right_buffer_x2 = data['right_x2']
                        right_buffer_y2 = data['right_y2']
                        left_buffer_x1 = data['left_x1']
                        left_buffer_y1 = data['left_y1']
                        left_buffer_x2 = data['left_x2']
                        left_buffer_y2 = data['left_y2']

                # Write results
                for *xyxy, conf, cls in reversed(det):
                    if save_txt:  # Write to file
                        xywh = (xyxy2xywh(torch.tensor(xyxy).view(1, 4)) / gn).view(-1).tolist()  # normalized xywh
                        line = (cls, *xywh, conf) if opt.save_conf else (cls, *xywh)  # label format
                        with open(txt_path + '.txt', 'a') as f:
                            f.write(('%g ' * len(line)).rstrip() % line + '\n')

                    if save_img or view_img:  # Add bbox to image
                        label = f'{names[int(cls)]} {conf:.2f}'
                        plot_one_box(xyxy, im0, label=label, color=colors[int(cls)], line_thickness=2)

                    # cls.item() == 73.0 means that it is a book
                    if cls.item() == 73.0:
                        # Extract bounding box coordinates
                        x1, y1, x2, y2 = xyxy[0], xyxy[1], xyxy[2], xyxy[3]

                        # Print the bounding box coordinates and confidence score
                        print(f"Bounding Box Coordinates: ({x1}, {y1}), ({x2}, {y2}), {conf.item()}")

                        # Dictionary to store buffer coordinates for left and right keypoints
                        buffers = {
                            'left': {'x1': left_buffer_x1, 'y1': left_buffer_y1, 'x2': left_buffer_x2, 'y2': left_buffer_y2},
                            'right': {'x1': right_buffer_x1, 'y1': right_buffer_y1, 'x2': right_buffer_x2, 'y2': right_buffer_y2}
                        }

                        # Load shelf names and bookshelf coordinates from the CSV file
                        shelf_names, bookshelf_coords = read_shelf_data('bookshelf_config.csv')

                        # Create Polygon objects for the bookshelf regions
                        bookshelf_polygons = [Polygon(coords) for coords in bookshelf_coords]

                        # Compare each buffer with the YOLO bounding box
                        for keypoint_name, buffer_coords in buffers.items():
                            buffer_x1, buffer_y1, buffer_x2, buffer_y2 = buffer_coords['x1'], buffer_coords['y1'], buffer_coords['x2'], buffer_coords['y2']
                            if (x1 <= buffer_x1 <= x2 and y1 <= buffer_y1 <= y2) or \
                                (x1 <= buffer_x2 <= x2 and y1 <= buffer_y1 <= y2) or \
                                (x1 <= buffer_x1 <= x2 and y1 <= buffer_y2 <= y2) or \
                                (x1 <= buffer_x2 <= x2 and y1 <= buffer_y2 <= y2):
                                print(f"The {keypoint_name} keypoint is inside the bounding box.")
                                cv2.putText(im0, "Holding book", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,(0, 0, 0))
                                cv2.imshow("Detected image", im0)
                                #cv2.waitKey(0)

                                # Create a Point object for the center of the book's bounding box
                                book_center = Point((x1 + x2) / 2, (y1 + y2) / 2)

                                # Check if the book's center point is inside any bookshelf polygon
                                for i, bookshelf_polygon in enumerate(bookshelf_polygons):
                                    if bookshelf_polygon.contains(book_center):
                                        print(f"The book is inside {shelf_names[i]}.")
                                        cv2.putText(im0, f"From {shelf_names[i]}", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0))
                                        break  # Exit the loop if the book is inside a bookshelf

                                else:
                                    print("The book is outside any bookshelf.")
                                    cv2.putText(im0, "Book outside bookshelves", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0))
                            else:
                                print(f"The {keypoint_name} keypoint is outside the bounding box.")

                    # else:
                    #     print("There is no book in the image.")

            # Print time (inference + NMS)
            print(f'{s}Done. ({(1E3 * (t2 - t1)):.1f}ms) Inference, ({(1E3 * (t3 - t2)):.1f}ms) NMS')    

            # Stream results
            if view_img:
                cv2.imshow(str(p), im0)
                cv2.waitKey(1)  # 1 millisecond

            # Save results (image with detections)
            if save_img:
                if dataset.mode == 'image':
                    cv2.imwrite(save_path, im0)
                    print(f" The image with the result is saved in: {save_path}")
                else:  # 'video' or 'stream'
                    if vid_path != save_path:  # new video
                        vid_path = save_path
                        if isinstance(vid_writer, cv2.VideoWriter):
                            vid_writer.release()  # release previous video writer
                        if vid_cap:  # video
                            fps = vid_cap.get(cv2.CAP_PROP_FPS)
                            w = int(vid_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                            h = int(vid_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                        else:  # stream
                            fps, w, h = 30, im0.shape[1], im0.shape[0]
                            save_path += '.mp4'
                        vid_writer = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))
                    vid_writer.write(im0)

    if save_txt or save_img:
        s = f"\n{len(list(save_dir.glob('labels/*.txt')))} labels saved to {save_dir / 'labels'}" if save_txt else ''
        #print(f"Results saved to {save_dir}{s}")

    print(f'Done. ({time.time() - t0:.3f}s)')
    print("\n")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--weights', nargs='+', type=str, default='yolov7-e6e.pt', help='model.pt path(s)')
    parser.add_argument('--source', type=str, default='inference/detectImg/output', help='source')  # file/folder, 0 for webcam
    parser.add_argument('--img-size', type=int, default=640, help='inference size (pixels)')
    parser.add_argument('--conf-thres', type=float, default=0.25, help='object confidence threshold')
    parser.add_argument('--iou-thres', type=float, default=0.45, help='IOU threshold for NMS')
    parser.add_argument('--device', default='', help='cuda device, i.e. 0 or 0,1,2,3 or cpu')
    parser.add_argument('--view-img', action='store_true', help='display results')
    parser.add_argument('--save-txt', action='store_true', help='save results to *.txt')
    parser.add_argument('--save-conf', action='store_true', help='save confidences in --save-txt labels')
    parser.add_argument('--nosave', action='store_true', help='do not save images/videos')
    parser.add_argument('--classes', nargs='+', type=int, help='filter by class: --class 0, or --class 0 2 3')
    parser.add_argument('--agnostic-nms', action='store_true', help='class-agnostic NMS')
    parser.add_argument('--augment', action='store_true', help='augmented inference')
    parser.add_argument('--update', action='store_true', help='update all models')
    parser.add_argument('--project', default='runs/detect', help='save results to project/name')
    parser.add_argument('--name', default='exp', help='save results to project/name')
    parser.add_argument('--exist-ok', action='store_true', help='existing project/name ok, do not increment')
    parser.add_argument('--no-trace', action='store_true', help='don`t trace model')
    opt = parser.parse_args()
    print(opt)
    #check_requirements(exclude=('pycocotools', 'thop'))

    with torch.no_grad():
        if opt.update:  # update all models (to fix SourceChangeWarning)
            for opt.weights in ['yolov7-e6e.pt']:
                detect()
                strip_optimizer(opt.weights)
        else:
            detect()
