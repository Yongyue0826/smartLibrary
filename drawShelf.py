import cv2
import numpy as np

old_img = cv2.imread('yolov7/inference/video/frameGallery1/frame0.jpg')

new_img = cv2.polylines(img=old_img, pts=[np.array([[471,-1],[138,331],[138,373],[539,225],[537,0]], dtype=np.int32)], isClosed=True, color=(0,255,0), thickness=3)
new_img = cv2.polylines(img=old_img, pts=[np.array([[139,377],[137,423],[539,549],[534,237]], dtype=np.int32)], isClosed=True, color=(255,0,0), thickness=3)
#new_img = cv2.circle(img=old_img, center=(0,0), radius=30, color=(0,255,0), thickness=-1)

cv2.imshow('new_img', new_img)
cv2.waitKey(0)
cv2.destroyAllWindows()

#137,330,139,377,534,237,536,3,461,2 Shelf2
#135,377,135,423,539,549,535,238 Shelf3