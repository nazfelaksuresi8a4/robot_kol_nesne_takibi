from ultralytics import YOLO
import matplotlib.pyplot as plt 
import cv2 as cv
import numpy as np  

#image-processing
capture = cv.VideoCapture(0)

#artifical-intelligence
model_path = 'new_model.pt'
model = YOLO(model_path)

x_servo,y_servo = 0,0

model_height,model_width = [480,640]    #->> height-width şeklinde verilmeli

def Mcapture(capture_ = capture):   #görüntü - matris dönüşümü fonksiyonu   -> matlike
    ret,frame = capture_.read()

    if ret:
        resized_matrix = cv.resize(frame,(model_height,model_width))
        color_transformed_image_matrix = cv.cvtColor(resized_matrix,cv.COLOR_BGR2RGB) 

        return color_transformed_image_matrix

    else:
        print('görüntü yakalama hatasi')
            
        return None
    

status = False

def U(Mat_i,model_ = model):   #nesne tespit fonksiyonu -> x,y,w,h
    model_results = model_(Mat_i)

    coordinate_tensors = {}
    objects_list = []

    for i in range(len(model_results)):
       objects_list.append(model_results[i])

    for coordinate_tensor in objects_list:
        for j,box in enumerate(coordinate_tensor.boxes):
            x,y,w,h = map(int,list(box.xywh[0]))

            coordinate_tensors[j] = {
                                    model.names[int(box.cls)] : [x,y,w,h]
                                    }

                                                            #eğer birden fazla nesne algılandıysa ilk nesneden başla ve ona ulaşana kadar diğerine geçme 
    
    if isinstance(Mat_i,str):
        return coordinate_tensors,cv.cvtColor(cv.resize(cv.imread(Mat_i),(model_height,model_width)),cv.COLOR_BGR2RGB)

    else:
        return coordinate_tensors,Mat_i

capture_2 = cv.VideoCapture(r"C:\Users\alper\Downloads\Cat Games The Red Bouncing Ball! (Cat TV).mp4")

def closed_loop():
    global capture_2,capture,model
    
    x_tolerance,y_tolerance = 10,10
    x_servo,y_servo = 0,0

    frame_ = Mcapture(capture_2)
    coordinates,_ = U(frame_,model)

    for key in coordinates:
        for class_ in coordinates[key]:
            stat_y,stat_x = False,False
            while True:
                frame_ = Mcapture(capture_2)
                coordinates,_ = U(frame_,model)

                H,W,C = frame_.shape
                Xnesne,Ynesne,Wnesne,Hnesne = coordinates[key][class_]      #ana formüldeki bölme işlemlerini yapmamıza gerek kalmadı. Çünkü yolo zaten nesnenin merkez koordinatları ve büyüklükkerini veriyor. Tekrar 2 ye bölersek sağ ve sol kenarları buluruz.

                dx = (Xnesne) - (W//2)
                dy = (Ynesne) - (H//2)

                dx,dy = dx + 1,dy + 1

                if dx < 0:
                    x_servo = -((1 / dx) * 180)

                if dx > 0:
                    x_servo = (1/dx) * 180

                if 1 <= dx < x_tolerance:
                    stat_x = True

                if dy < 0:
                    y_servo = -((1 / dy) * 180)

                if dy > 0:
                    y_servo = (1 / dy) * 180

                if 1 <= dy < y_tolerance:
                    stat_y = True

                if stat_x and stat_y:
                    break 

                else:
                    print(f'dx : {dx}  || dy: {dy}  || x-servo: {x_servo}  ||  y-servo: {y_servo}  || DXY : {((Xnesne + Ynesne) - ((W//2) + (H//2)))}' )

                    analyzed = cv.rectangle(frame_,(Xnesne - Wnesne//2,Ynesne - Hnesne//2),(Xnesne+Wnesne//2,Ynesne+Hnesne//2),(0,255,0),1)
                    analyzed = cv.circle(frame_,(Xnesne,Ynesne),10,(255,0,255),4)
                    analyzed = cv.circle(frame_,(W//2,H//2),10,(0,255,0),4)
                   

                    cv.imshow('window',cv.cvtColor(analyzed,cv.COLOR_BGR2RGB))
                    cv.waitKey(25)



closed_loop()
