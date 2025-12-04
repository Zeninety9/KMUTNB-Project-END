import cv2 as cv
import numpy as np
from tkinter import*
from tkinter import ttk
import Open_camera
import ROBOT
root = Tk()
notebook = ttk.Notebook(root)
notebook.pack(fill="both",expand=True)

tab_vision = Frame(notebook,width=15,height=3)
notebook.add(tab_vision,text="Vision")

tab_ROBOT = Frame(notebook,width=15,height=3)
notebook.add(tab_ROBOT,text="ROBOT")

def on_release_J1(event):
    value = J1_robot.get()
    ROBOT.Joint_1(value)
    ROBOT.Forward_kinematic()
    root.after(50,ROBOT.send_to_esp32)

def on_release_J2(event):
    value = J2_robot.get()
    ROBOT.Joint_2(value)
    ROBOT.Forward_kinematic()
    root.after(50,ROBOT.send_to_esp32)

def on_release_J3(event):
    value = J3_robot.get()
    ROBOT.Joint_3(value)
    ROBOT.Forward_kinematic()
    root.after(50,ROBOT.send_to_esp32)

def on_release_J4(event):
    value = J4_robot.get()
    ROBOT.Joint_4(value)
    ROBOT.Forward_kinematic()
    root.after(50,ROBOT.send_to_esp32)

def on_release_J5(event):
    value = J5_robot.get()
    ROBOT.Joint_5(value)
    ROBOT.Forward_kinematic()
    root.after(50,ROBOT.send_to_esp32)


J1_robot= Scale(tab_ROBOT,from_=-20,to=150,orient=HORIZONTAL,label="Joint 1",length=500)
J1_robot.place(x=950,y=50)

J2_robot= Scale(tab_ROBOT,from_=-60,to=60,orient=HORIZONTAL,label="Joint 2",length=500)
J2_robot.place(x=950,y=120)

J3_robot= Scale(tab_ROBOT,from_=-90,to=90,orient=HORIZONTAL,label="Joint 3",length=500)
J3_robot.place(x=950,y=190)

J4_robot= Scale(tab_ROBOT,from_=-20,to=180,orient=HORIZONTAL,label="Joint 4",length=500)
J4_robot.place(x=950,y=260)

J5_robot= Scale(tab_ROBOT,from_=-90,to=90,orient=HORIZONTAL,label="Joint 5",length=500)
J5_robot.place(x=950,y=330)

J1_robot.bind("<ButtonRelease-1>",on_release_J1)
J2_robot.bind("<ButtonRelease-1>",on_release_J2)
J3_robot.bind("<ButtonRelease-1>",on_release_J3)
J4_robot.bind("<ButtonRelease-1>",on_release_J4)
J5_robot.bind("<ButtonRelease-1>",on_release_J5)


Button_run_ROBOT = Button(tab_ROBOT,text="เริ่มทำงาน",fg="white",bg="green",command=Open_camera.run_camera,width=15,height=3)
Button_run_ROBOT.place(x=50,y=750)
Button_STOP_ROBOT = Button(tab_ROBOT,text="หยุดการทำงาน",fg="white",bg="green",command=Open_camera.run_camera,width=15,height=3)
Button_STOP_ROBOT.place(x=180,y=750)
Button_HOME_ROBOT = Button(tab_ROBOT,text="บ้าน",fg="white",bg="green",command=Open_camera.run_camera,width=15,height=3)
Button_HOME_ROBOT.place(x=310,y=750)

frame_display = Frame(tab_vision,width=650,height=490,bg="black",highlightbackground="gray",highlightthickness=3)
frame_display.place(x=10,y=80)
label = Label(frame_display)
label.place(x=0,y=0)
frame_snapshot = Frame(tab_vision,width=650,height=490,bg="black",highlightbackground="gray",highlightthickness=3)
frame_snapshot.place(x=750,y=80)
label_snapshot = Label(frame_snapshot)
label_snapshot.place(x=0,y=0)
threshold_value = IntVar(value=128)
slider = Scale(tab_vision,from_=0,to=255,orient=HORIZONTAL,label="Threshold",variable=threshold_value,length=300,showvalue=0)
slider.place(x=380,y=608)


Open_camera.label = label
Open_camera.root = tab_vision
Open_camera.label_snapshot = label_snapshot
Open_camera.threshold_value = threshold_value


root.title("A compact robotic arm training system for automated workpiece arrangement with image processing")
##Name_title = Label(root,text="A compact robotic arm training system for automated workpiece arrangement with image processing",fg="black",font=1)
##Name_title.place(x=5,y=5) 




Buttin_run_cam = Button(tab_vision,text="เปิดใช้งานกล้อง",fg="white",bg="green",command=Open_camera.run_camera,width=15,height=3)
Buttin_run_cam.place(x=50,y=600)
Button_stop_cam = Button(tab_vision,text="ปิดใช้งานกล้อง",fg="white",bg="red",width=15,height=3,command=Open_camera.stop_camera)
Button_stop_cam.place(x=50,y=670)
Button_snap_cam = Button(tab_vision,text="จับภาพกล้อง",fg="black",bg="gray",width=15,height=3,command=Open_camera.snapshot)
Button_snap_cam.place(x=200,y=600)
Buttin_mask_snap = Button(tab_vision,text="ครอบคลุม",command=Open_camera.do_mask,width=15,height=3)
Buttin_mask_snap.place(x=200,y=670)
Button_reset_mask = Button(tab_vision,text="รีเซ็ตกล้อง",command=Open_camera.reset_mask,width=15,height=3)
Button_reset_mask.place(x=50,y=740)
Button_rotation = Button(tab_vision,text="ตรวจจับวัตถุ",command=Open_camera.btn_detect_rotation,width=15,height=3)
Button_rotation.place(x=200,y=740)
Entry_th = Entry(tab_vision,width=10,state="readonly")
Entry_th.place(x=690,y=628)
Entry_X = Entry(tab_vision,width=10,state="readonly")
Entry_X.place(x=900,y=660)
Entry_Y = Entry(tab_vision,width=10,state="readonly")
Entry_Y.place(x=900,y=692)
Entry_angle = Entry(tab_vision,width=10,state="readonly")
Entry_angle.place(x=900,y=628)
Open_camera.Entry_angle = Entry_angle
def on_threshold_change(*args):
    Open_camera.update_threshold_view()
    Entry_th.config(state="normal")
    Entry_th.delete(0,END)
    Entry_th.insert(0,str(threshold_value.get()))
    Entry_th.config(state="readonly")
threshold_value.trace_add("write",on_threshold_change)

def close_GUI ():
    try:
        Open_camera.stop_camera()
    except:
        pass

    try:
        if ROBOT.ser is not None:
            ROBOT.ser.close()
    
    except:
        pass

    root.destroy()

Button_exit = Button(root,text="ปิดโปรแกรม",command=close_GUI,width=15,height=3)
Button_exit.place(x=1430,y=0)




Entry_th.config(state="normal")
Entry_th.insert(0,str(threshold_value.get()))
Entry_th.configure(state="readonly")

ROBOT.Forward_kinematic()

root.attributes("-fullscreen",True)
root.mainloop()
