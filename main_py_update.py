import cv2 as cv 
import numpy as np 
import serial #servolar gelince entegre ediecek.

kernel = np.ones((8,8),np.uint8)

lower_red = np.array([0,120,70])
upper_red = np.array([10,255,255])

lower_red_2 = np.array([170,120,70])
upper_red_2 = np.array([180,255,255])

Nterm = 50
delta_target_x,delta_target_y = 0,0


capture = cv.VideoCapture(0)

tolerance = 15

n = 180


def delta_analysis():
    global Nterm,tolerance

    for servo_x in range(0,n):
            ret,frame = capture.read()

            if  ret:
                h,w,c = frame.shape

                y_center,x_center = h // 2, w // 2

                frame = cv.circle(frame,(w//2,h//2),1,(0,255,0),1)

                hsv_frame = cv.cvtColor(frame,cv.COLOR_BGR2HSV)

                mask_1 = cv.inRange(hsv_frame,lower_red,upper_red)
                mask_2 = cv.inRange(hsv_frame,lower_red_2,upper_red_2)
                
                mask = mask_1 + mask_2

                mask = cv.medianBlur(mask,7)

                mask = cv.morphologyEx(mask,cv.MORPH_OPEN,kernel)
                mask = cv.morphologyEx(mask,cv.MORPH_CLOSE,kernel)

                contours,_ = cv.findContours(mask,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE)

                masked_image = cv.bitwise_and(frame,frame,mask=mask) 

                if len(contours) > 0:
                    largest_contour = max(contours,key=cv.contourArea)
                    if cv.contourArea(largest_contour) > 400:
                        x,y,w,h = cv.boundingRect(largest_contour)

                        delta_x = x - (x_center)
                        delta_y = y - (y_center)

                        if delta_x < 0:
                             print('sol')

                        elif delta_x > 0:
                             print('sag')

                        if delta_x > 0 and delta_x < tolerance:
                             print('kal')


                        print('x : {}  ||  y: {}'.format(delta_x,delta_y))

                        frame = cv.circle(frame,(x+w//2,y+h//2),1,(255,0,255),5)

                cv.imshow('delta analysiws',frame)
                cv.waitKey(1)




while True:
    outs = delta_analysis()

