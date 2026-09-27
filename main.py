#27.09.2026 04.20

import cv2 as cv 
import numpy as np 
import serial #servolar gelince entegre ediecek.

kernel = np.ones((8,8),np.uint8)

lower_red = np.array([0,120,70])
upper_red = np.array([10,255,255])

lower_red_2 = np.array([170,120,70])
upper_red_2 = np.array([180,255,255])

Nterm = 50

capture = cv.VideoCapture(0)

tolerance = 15

n = 180
measurement_dict = {}


def delta_analysis():
    global Nterm

    for servo_x in range(0,n):
            ret,frame = capture.read()

            h,w,c = frame.shape

            y_center,x_center = h // 2, w // 2

            frame = cv.circle(frame,(w//2,h//2),50,(0,255,0),1)

            if not ret:
                print('kamera okunamadi')

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

                    x_i,y_i = x//2,y//2

                    delta_x = max(x_center,x+w//2) - min(x_center,x+w//2)
                    delta_y = max(y_center,y+h//2) - min(y_center,y+h//2)

                    target_delta = max(delta_x,delta_y) - min(delta_x,delta_y)

                    measurement_dict[servo_x] = target_delta

                    frame = cv.circle(frame,(x+w//2,y+h//2),3,(255,0,255),5)

            cv.imshow('delta analysiws',frame)
            cv.waitKey(1)

    if measurement_dict:
        delta_deg_range_array = []
        values = list(sorted(measurement_dict.values()))[0:Nterm]
        inversed = {measurement_dict[key] : key for key in measurement_dict}

        for delta_i in values:
            value = inversed[delta_i]

            delta_deg_range_array.append(value)

        Nterm = Nterm - 1

        out =  {'servo_goto' : min(measurement_dict, key=measurement_dict.get),
                'min_delta' : min(measurement_dict.values()),
                'max_delta' : max(measurement_dict.values()),
                'delta_deg_range' : delta_deg_range_array}

        measurement_dict.clear()

        return out

    else:
         return 'herhangi bir görsel tespit edilemedi!'

while True:
     if Nterm <= 0:
          break

     outs = delta_analysis()

     #akışın temel amaç ve tanımı : servo her seferinde (min(delta_deg_range)) e gidecek ve onun min ve max arasından tekrar bir tarama yapacak bunu Nterm < 0 olana kadar yapacak kaba kuvvet taraması ile nesneye en yakın konuma x eksenini ortalayacak.

     print(outs)
