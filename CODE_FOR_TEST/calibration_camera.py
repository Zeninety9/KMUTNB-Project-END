import cv2 as cv
import numpy as np
import glob

# ขนาดช่องจริง (mm)
square_size = 60

# จำนวน inner corners = ช่อง - 1
pattern_size = (7, 7)

# เตรียม object points
objp = np.zeros((pattern_size[0] * pattern_size[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:pattern_size[0], 0:pattern_size[1]].T.reshape(-1, 2)
objp *= square_size

objpoints = []
imgpoints = []

# Path ต้องเป็นแบบนี้
images = glob.glob(r'D:\project-1\COED\CODE_FOR_TEST\Camera_img\*.jpg')

print("พบจำนวนภาพ:", len(images))

for fname in images:
    img = cv.imread(fname)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    ret, corners = cv.findChessboardCorners(gray, pattern_size)
    if ret:
        objpoints.append(objp)
        imgpoints.append(corners)

# Calibrate
ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

print("Camera matrix:\n", mtx)
print("Distortion:\n", dist)
