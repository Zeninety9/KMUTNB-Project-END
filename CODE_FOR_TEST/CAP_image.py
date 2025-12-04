import cv2 as cv
import os

# สร้างโฟลเดอร์สำหรับเก็บภาพคาลิเบรตถ้ายังไม่มี
save_path = "D:\project-1\COED\CODE_FOR_TEST"
if not os.path.exists(save_path):
    os.makedirs(save_path)

cap = cv.VideoCapture(0)   # ถ้ามีหลายกล้อง เปลี่ยนเป็น 1, 2, 3 ได้

img_count = 1

print("กด SPACE เพื่อบันทึกภาพ")
print("กด ESC เพื่อออก")

while True:
    ret, frame = cap.read()
    if not ret:
        print("ไม่สามารถเปิดกล้องได้")
        break

    cv.imshow("Camera", frame)

    key = cv.waitKey(1) & 0xFF
    
    # กด SPACE เพื่อเซฟรูป
    if key == 32:  
        filename = f"{save_path}/calib_{img_count}.jpg"
        cv.imwrite(filename, frame)
        print(f"บันทึกภาพ: {filename}")
        img_count += 1

    # กด ESC เพื่อออก
    elif key == 27:
        break

cap.release()
cv.destroyAllWindows()
