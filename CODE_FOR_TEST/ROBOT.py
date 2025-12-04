import numpy as np
import serial 

try :
    ser = serial.Serial('COM9',38400,timeout=1)
except:
    ser = None

joint_values = [0,0,0,0,0]

def send_to_esp32():
    global joint_values,ser

    if ser is None:
        return
    try:
        msg = "{},{},{},{},{}\n".format(
            joint_values[0],
            joint_values[1],
            joint_values[2],
            joint_values[3],
            joint_values[4]
        )
        ser.write(msg.encode())

    except :
        pass


def Joint_1(value):
    global joint_values
    joint_values[0] = float(value)
    

def Joint_2(value):
    global joint_values
    joint_values[1] = float(value)
    

def Joint_3(value):
    global joint_values
    joint_values[2] = float(value)
    

def Joint_4(value):
    global joint_values
    joint_values[3] = float(value)
    

def Joint_5(value):
    global joint_values
    joint_values[4] = int(value)
    


def Forward_kinematic():
    J1,J2,J3,J4,J5 = joint_values
    
    RZ_J1 = np.array([ [np.cos(np.radians(J1)),-np.sin(np.radians(J1)), 0, 0],
                       [np.sin(np.radians(J1)), np.cos(np.radians(J1)), 0, 0],
                       [0, 0, 1, 0],
                       [0, 0, 0, 1]])
    
    TZ_J1_TO_J2 = np.array([[1, 0, 0, 0],
                            [0, 1, 0, 0],
                            [0, 0, 1, 133.5],
                            [0, 0, 0, 1]])
    
    RX1 = np.array([[1, 0, 0, 0],
                    [0, np.cos(np.radians(90)), -np.sin(np.radians(90)), 0],
                    [0, np.sin(np.radians(90)), np.cos(np.radians(90)), 0],
                    [0, 0, 0, 1]])
    
    RZ1 = np.array([[np.cos(np.radians(90)),-np.sin(np.radians(90)), 0, 0],
                    [np.sin(np.radians(90)), np.cos(np.radians(90)), 0, 0],
                    [0, 0, 1, 0],
                    [0, 0, 0, 1]])

    RZ_J2 = np.array([[np.cos(np.radians(J2)),-np.sin(np.radians(J2)), 0, 0],
                    [np.sin(np.radians(J2)), np.cos(np.radians(J2)), 0, 0],
                    [0, 0, 1, 0],
                    [0, 0, 0, 1]])

    TX2 = np.array([[1, 0, 0, 120.5],
                    [0, 1, 0, 0],
                    [0, 0, 1, 0],
                    [0, 0, 0, 1]])

    RX2 = np.array([[1, 0, 0, 0],
                    [0, np.cos(np.radians(180)), -np.sin(np.radians(180)), 0],
                    [0, np.sin(np.radians(180)), np.cos(np.radians(180)), 0],
                    [0, 0, 0, 1]])

    RZ_J3 = np.array([[np.cos(np.radians(J3)),-np.sin(np.radians(J3)), 0, 0],
                      [np.sin(np.radians(J3)), np.cos(np.radians(J3)), 0, 0],
                      [0, 0, 1, 0],
                      [0, 0, 0, 1]])

    TX3 = np.array([[1, 0, 0, 101],
                    [0, 1, 0, 0],
                    [0, 0, 1, 0],
                    [0, 0, 0, 1]])

    RX3 = np.array([[1, 0, 0, 0],
                    [0, np.cos(np.radians(180)), -np.sin(np.radians(180)), 0],
                    [0, np.sin(np.radians(180)), np.cos(np.radians(180)), 0],
                    [0, 0, 0, 1]])

    RZ_J4 = np.array([[np.cos(np.radians(J4)),-np.sin(np.radians(J4)), 0, 0],
                      [np.sin(np.radians(J4)), np.cos(np.radians(J4)), 0, 0],
                      [0, 0, 1, 0],
                      [0, 0, 0, 1]])

    RX4 = np.array([[1, 0, 0, 0],
                    [0, np.cos(np.radians(90)), -np.sin(np.radians(90)), 0],
                    [0, np.sin(np.radians(90)), np.cos(np.radians(90)), 0],
                    [0, 0, 0, 1]])

    TZ4 = np.array([[1, 0, 0, 0],
                    [0, 1, 0, 0],
                    [0, 0, 1, 75.84],
                    [0, 0, 0, 1]])

    RZ_J5 = np.array([[np.cos(np.radians(J5)),-np.sin(np.radians(J5)), 0, 0],
                      [np.sin(np.radians(J5)), np.cos(np.radians(J5)), 0, 0],
                      [0, 0, 1, 0],
                      [0, 0, 0, 1]])

    TZ5 = np.array([[1, 0, 0, 0],
                    [0, 1, 0, 0],
                    [0, 0, 1, 86.5],
                    [0, 0, 0, 1]])


    
    ROBOT = [RZ_J1,TZ_J1_TO_J2,RX1,RZ1,RZ_J2,TX2,RX2,RZ_J3,TX3,RX3,RZ_J4,RX4,TZ4,RZ_J5,TZ5]
    T = np.eye(4)   
    for M in ROBOT:
        T = T @ M 

    T_rounded = np.round(T, 2)

    # ====== แสดงผลลัพธ์ ======
    print("ผลลัพธ์เมทริกซ์ Transformation สุดท้าย (2 ตำแหน่ง):\n", T_rounded)
    print("ตำแหน่ง Tool (x, y, z):", T_rounded[:3, 3])
    T_rounded = np.round(T, 2)
    X_AXIS = T[0,3]
    Y_AXIS = T[1,3]
    Z_AXIS = T[2,3]
 

    return X_AXIS,Y_AXIS,Z_AXIS
