# Extract frames from webcam 
import cv2 
import os
import time
import imutils

def extract_frame():
    webCam = cv2.VideoCapture("test.mp4") # to read or open webcam,  0 means the default webcam
   

    # Check if webcam is opened correctly
    if not webCam.isOpened():
        print("Unable to open webcam")
        return
    
    frame_interval = 10  # Interval in seconds
    currentframe = 0 # what particular framw will be presented
    saveframe = 1

    if not os.path.exists('yolov7/inference/detectImg'):
        os.makedirs('yolov7/inference/detectImg')

    # Create loop 
    while True:
        success, frame = webCam.read() 
        # capture frame by frame information 
        # success = boolean variable: True/False

        if not success:
            print("failed to grab frame")
            break
        
        # Check if it's time to extract a frame
        if currentframe % (frame_interval * webCam.get(cv2.CAP_PROP_FPS)) == 0:
            # Process the frame
            # Save the frame to a file or perform any other desired operations
            cv2.imwrite('yolov7/inference/detectImg/frame' + str(saveframe) + '.jpg', frame)
            saveframe += 1
            
        # Increment frame count
        currentframe += 1

            #cv2.imshow("Output", frame) # show the web frame to the user
        

        resize = imutils.resize(frame, width=(int(frame.shape[1] / 2)), height=(int(frame.shape[0] / 2)))
        #cv2.imwrite('./data/frame' + str(currentframe) + '.jpg', frame) 
        # single . means at the current frame
        cv2.imshow("Output", resize) # show the web frame to the user
        

        #k = cv2.waitKey(1) # q

        #if k%256 == 27:
        #    print("Escape hit, closing the app")
        #    break

        if cv2.waitKey(1) &  0xFF == ord('q'):
            print("Escape hit, closing the app")
            break

        # Delay to match the desired frame rate
        time.sleep(1 / webCam.get(cv2.CAP_PROP_FPS))

    webCam.release()
    cv2.destroyAllWindows()

# Call the function to start frame extraction 
extract_frame()


