import cv2 as cv
import numpy as np
import tkinter as tk 
from PIL import Image,ImageTk

cap = None
camera_on = False
label = None
root = None
label_snapshot = None
threshold_value = None
snap_image = None
mask_window = None
canvas = None
snap_thresh = None
roi_mask = None
Entry_angle = None

def run_camera():
    global cap,camera_on
    if not camera_on:
        cap = cv.VideoCapture(0)
        camera_on = True
        update_frame()
        

def stop_camera():
    global cap,camera_on,label
    camera_on = False
    if cap is not None:
        cap.release()
        cap = None
    if label is not None:   
        label.config(image='')

def update_frame():
    global cap,camera_on,label
    if camera_on and cap is not None:
        ret,frame = cap.read()
        if ret:
            frame = cv.cvtColor(frame,cv.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)

            label.imgtk = imgtk
            label.config(image=imgtk)

        root.after(20,update_frame)

def snapshot():
    global cap,label_snapshot,snap_image

    if cap is None:
        return
    
    ret,frame = cap.read()
    if ret:
        snap_image = frame.copy()
        update_threshold_view()

def update_threshold_view():
    global snap_image,label_snapshot,threshold_value,snap_thresh

    if snap_image is None:
        return

    gray = cv.cvtColor(snap_image,cv.COLOR_BGR2GRAY)
    t = threshold_value.get()
    _,snap_thresh = cv.threshold(gray,t,255,cv.THRESH_BINARY)

    if roi_mask is not None:
        display = cv.bitwise_and(snap_thresh,snap_thresh,mask=roi_mask)
    else:
        display = snap_thresh


    thresh_rgb = cv.cvtColor(display,cv.COLOR_GRAY2RGB)
    img = Image.fromarray(thresh_rgb)
    imgtk = ImageTk.PhotoImage(image=img)

    label_snapshot.imgtk = imgtk
    label_snapshot.configure(image=imgtk)

def on_mouse_up(event):
    global roi_start,roi_end,drawing,mask_image,threshold_value,mask_window,canvas,snap_thresh,roi_mask
    drawing = False

    if snap_image is None:
        return

    if snap_thresh is None:
        return
    
    roi_end = (event.x,event.y)

    h,w = snap_thresh.shape[:2]
    mask = np.zeros((h,w),dtype = np.uint8)
    x1,y1 = roi_start
    x2,y2 = roi_end

    x1,x2 = sorted([x1,x2])
    y1,y2 = sorted([y1,y2])

    mask[y1:y2,x1:x2] = 255
    

    roi_mask = mask.copy()

    masked_binary = cv.bitwise_and(snap_thresh,snap_thresh,mask=mask)
    
    confirm_mask(masked_binary)
    
    if mask_window is not None:
        mask_window.destroy()
        mask_window = None
        

def on_mouse_down(event):
    global roi_start,drawing
    roi_start = (event.x,event.y)
    drawing =True

def on_mouse_move(event):
    global roi_start,roi_end,drawing,mask_image,canvas
    if drawing:
        roi_end = (event.x,event.y)
        canvas.delete("rect")
        canvas.create_rectangle(roi_start[0],roi_start[1],roi_end[0],roi_end[1],outline="red",width=2,tag="rect")

def do_mask():
    global canvas,mask_window,snap_thresh
    if snap_thresh is None:
        return
    
    mask_image = snap_thresh.copy()
    mask_window = tk.Toplevel()
    mask_window.title("เลือกบริเวณพื้นที่สนใจ")

    canvas = tk.Canvas(mask_window,width=mask_image.shape[1],height=mask_image.shape[0])
    canvas.pack()

    img = Image.fromarray(cv.cvtColor(mask_image,cv.COLOR_GRAY2RGB))
    imgtk = ImageTk.PhotoImage(image=img)
    canvas.imgtk = imgtk
    canvas.create_image(0,0,anchor="nw",image=imgtk)
    
    canvas.bind("<Button-1>",on_mouse_down)
    canvas.bind("<B1-Motion>",on_mouse_move)
    canvas.bind("<ButtonRelease-1>",on_mouse_up)

def confirm_mask(masked_binary_image):
    global label_snapshot
    masked_rgb = cv.cvtColor(masked_binary_image,cv.COLOR_GRAY2RGB)
    img = Image.fromarray(masked_rgb)
    imgtk = ImageTk.PhotoImage(image=img)
    label_snapshot.imgtk = imgtk
    label_snapshot.configure(image=imgtk)

def reset_mask():
    global roi_mask,snap_thresh,label_snapshot
    roi_mask = None
    if snap_thresh is not None:
        thresh_rgb = cv.cvtColor(snap_thresh,cv.COLOR_GRAY2RGB)
        img = Image.fromarray(thresh_rgb)
        imgtk = ImageTk.PhotoImage(image=img)
        label_snapshot.imgtk = imgtk
        label_snapshot.configure(image=imgtk)

def detect_rotation_angle(input_img):

    if len(input_img.shape) == 2:
        bw = input_img.copy()
        img = cv.cvtColor(input_img,cv.COLOR_GRAY2BGR)
        gray = input_img.copy()

    else:
        img = input_img.copy()
        gray = cv.cvtColor(input,cv.COLOR_BGR2GRAY)
        _,bw = cv.threshold(gray,50,255,cv.THRESH_BINARY)

    contours,_ = cv.findContours(bw,cv.RETR_LIST,cv.CHAIN_APPROX_NONE)

    for c in contours :
        area = cv.contourArea(c)
        if area < 3700 or area > 10000:
            continue

        rect = cv.minAreaRect(c)
        box = cv.boxPoints(rect)
        box = box.astype(int)

        center = (int(rect[0][0]),int(rect[0][1]))
        width = int(rect[1][0])
        height = int(rect[1][1])
        angle = int(rect[2])

        if width < height:
            angle = 90 - angle
        else:
            angle = -angle
        
        #label = f"Roatation Angle : {angle} degrees"
        #cv.rectangle(img,(center[0]-40,center[1]-30),(center[0]+200,center[1]+10),(255,255,255),-1)
        #cv.putText(img,label,(center[0]-30,center[1]),cv.FONT_HERSHEY_SIMPLEX,0.7,(0,0,0),1)

        detected_angle = angle

        cv.drawContours(img,[box],0,(0,0,255),2)
        return img,detected_angle

def btn_detect_rotation():
    global snap_thresh,label_snapshot,roi_mask,Entry_angle

    if snap_thresh is None:
        return
    
    if roi_mask is None:
        binary = snap_thresh

    else:
        binary = cv.bitwise_and(snap_thresh,snap_thresh,mask=roi_mask)

    result,angle = detect_rotation_angle(binary)
    if angle is not None:
        Entry_angle.config(state="normal")
        Entry_angle.delete(0,tk.END)
        Entry_angle.insert(0,str(angle))
        Entry_angle.config(state="readonly")

    if result is not None:
        result_rgb = cv.cvtColor(result,cv.COLOR_BGR2RGB)
        img = Image.fromarray(result_rgb)
        imgtk = ImageTk.PhotoImage(image=img)
        label_snapshot.imgtk = imgtk
        label_snapshot.configure(image=imgtk)





