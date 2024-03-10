from tkinter import *
from PIL import ImageTk, Image
import tkinter.messagebox as tkMessageBox
import ctypes
from tkinter import filedialog
import cv2,os
import numpy as np
import cv2 as cv
import Person
import time

home = Tk()
home.title("Crowd Counter")
directory = "./"
img = Image.open(directory+"/images/home.png")
img = ImageTk.PhotoImage(img)
panel = Label(home, image=img)
panel.pack(side="top", fill="both", expand="yes")
user32 = ctypes.windll.user32
user32.SetProcessDPIAware()
[w, h] = [user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)]
lt = [w, h]
a = str(lt[0]//2-432)
b= str(lt[1]//2-243)
home.geometry("864x486+"+a+"+"+b)
home.resizable(0,0)
file = ''

def fileopen():
    global file
    try:
        file = filedialog.askopenfilename(initialdir=os.getcwd(), title="Select video", filetypes=( ("images", ".mp4"),("images", ".mkv"),("images", ".avi")))
    except:
        file = ''

def check():
    global file

    f = file
    if f!='':
      

                cnt_up   = 0
                cnt_down = 0

                cap = cv.VideoCapture(file)

                w = cap.get(3)
                h = cap.get(4)
                frameArea = h*w
                areaTH = frameArea/250



                line_up = int(2*(h/5))
                line_down   = int(3*(h/5))

                up_limit =   int(1*(h/5))
                down_limit = int(4*(h/5))

                line_down_color = (255,0,0)
                line_up_color = (0,0,255)
                pt1 =  [0, line_down];
                pt2 =  [w, line_down];
                pts_L1 = np.array([pt1,pt2], np.int32)
                pts_L1 = pts_L1.reshape((-1,1,2))
                pt3 =  [0, line_up];
                pt4 =  [w, line_up];
                pts_L2 = np.array([pt3,pt4], np.int32)
                pts_L2 = pts_L2.reshape((-1,1,2))

                pt5 =  [0, up_limit];
                pt6 =  [w, up_limit];
                pts_L3 = np.array([pt5,pt6], np.int32)
                pts_L3 = pts_L3.reshape((-1,1,2))
                pt7 =  [0, down_limit];
                pt8 =  [w, down_limit];
                pts_L4 = np.array([pt7,pt8], np.int32)
                pts_L4 = pts_L4.reshape((-1,1,2))

                fgbg = cv.createBackgroundSubtractorMOG2(detectShadows = True)


                kernelOp = np.ones((3,3),np.uint8)
                kernelOp2 = np.ones((5,5),np.uint8)
                kernelCl = np.ones((11,11),np.uint8)


                font = cv.FONT_HERSHEY_SIMPLEX
                persons = []
                max_p_age = 5
                pid = 1

                while(cap.isOpened()):

                    ret, frame = cap.read()
            
                    if ret!=True:
                        tkMessageBox.showinfo("Crowd Counter",f"Total Up : {cnt_up}\nTotal In : {cnt_down}")
                    for i in persons:
                        i.age_one() 
                    fgmask = fgbg.apply(frame)
                    fgmask2 = fgbg.apply(frame)


                    try:
                        ret,imBin= cv.threshold(fgmask,80,255,cv.THRESH_BINARY)
                        ret,imBin2 = cv.threshold(fgmask2,100,255,cv.THRESH_BINARY)

                        mask = cv.morphologyEx(imBin, cv.MORPH_OPEN, kernelOp)
                        mask2 = cv.morphologyEx(imBin2, cv.MORPH_OPEN, kernelOp)
                     
                        mask =  cv.morphologyEx(mask , cv.MORPH_CLOSE, kernelCl)
                        mask2 = cv.morphologyEx(mask2, cv.MORPH_CLOSE, kernelCl)
                    except:
      
                        tkMessageBox.showinfo("Crowd Counter",f"Total Up : {cnt_up}\nTotal In : {cnt_down}")
                        break

                    
                    contours0, hierarchy = cv.findContours(mask2,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE)
                    for cnt in contours0:
                        area = cv.contourArea(cnt)
                        if area > areaTH:

                            M = cv.moments(cnt)
                            cx = int(M['m10']/M['m00'])
                            cy = int(M['m01']/M['m00'])
                            x,y,w,h = cv.boundingRect(cnt)

                            new = True
                            if cy in range(up_limit,down_limit):
                                for i in persons:
                                    if abs(x-i.getX()) <= w and abs(y-i.getY()) <= h:
                                    
                                        new = False
                                        i.updateCoords(cx,cy)   
                                        if i.going_UP(line_down,line_up) == True:
                                            cnt_up += 1;
                                     
                                        elif i.going_DOWN(line_down,line_up) == True:
                                            cnt_down += 1;

                                        break
                                    if i.getState() == '1':
                                        if i.getDir() == 'down' and i.getY() > down_limit:
                                            i.setDone()
                                        elif i.getDir() == 'up' and i.getY() < up_limit:
                                            i.setDone()
                                    if i.timedOut():
                       
                                        index = persons.index(i)
                                        persons.pop(index)
                                        del i    
                                if new == True:
                                    p = Person.MyPerson(pid,cx,cy, max_p_age)
                                    persons.append(p)
                                    pid += 1     
                           
                            cv.circle(frame,(cx,cy), 5, (0,0,255), -1)
                            img = cv.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)            
                       

                    for i in persons:

                        cv.putText(frame, str(i.getId()),(i.getX(),i.getY()),font,0.3,i.getRGB(),1,cv.LINE_AA)

                    str_up = 'UP: '+ str(cnt_up)
                    str_down = 'DOWN: '+ str(cnt_down)
                    frame = cv.polylines(frame,[pts_L1],False,line_down_color,thickness=2)
                    frame = cv.polylines(frame,[pts_L2],False,line_up_color,thickness=2)
                    frame = cv.polylines(frame,[pts_L3],False,(255,255,255),thickness=1)
                    frame = cv.polylines(frame,[pts_L4],False,(255,255,255),thickness=1)
                    cv.putText(frame, str_up ,(10,40),font,0.5,(255,255,255),2,cv.LINE_AA)
                    cv.putText(frame, str_up ,(10,40),font,0.5,(0,0,255),1,cv.LINE_AA)
                    cv.putText(frame, str_down ,(10,90),font,0.5,(255,255,255),2,cv.LINE_AA)
                    cv.putText(frame, str_down ,(10,90),font,0.5,(255,0,0),1,cv.LINE_AA)

                    cv.imshow('Frame',frame)
                      
                    

                    k = cv.waitKey(30) & 0xff
                    if k == 27:
                        break

            
                cap.release()
                cv.destroyAllWindows()
                tkMessageBox.showinfo("Crowd Counter",f"Total Up : {cnt_up}\nTotal In : {cnt_down}")


  
    else:
        tkMessageBox.showinfo('Crowd Counter','Please Upload a file first.')   

photo = Image.open(directory+"images/1.png")
img3 = ImageTk.PhotoImage(photo)
b2=Button(home, highlightthickness = 0, bd = 0,activebackground="#e4e4e4", image = img3,command=fileopen)
b2.place(x=209,y=174)

photo = Image.open(directory+"images/2.png")
img2 = ImageTk.PhotoImage(photo)
b1=Button(home, highlightthickness = 0, bd = 0,activebackground="white", image = img2,command=check)
b1.place(x=420,y=238)

home.mainloop()
