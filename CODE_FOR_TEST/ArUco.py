import cv2
import numpy as np
import time

# ====== Camera Intrinsics ======
camera_matrix = np.array([
    [832.88895938, 0, 306.51481521],
    [0, 834.55626376, 294.65123437],
    [0, 0, 1]
], dtype=np.float64)

dist_coeffs = np.array([
    -0.0537961683,
     1.25366942,
    -0.00317107611,
     0.00621690113,
    -5.87650125
], dtype=np.float64)

# ====== Load Camera ======
cap = cv2.VideoCapture(0)

aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
params = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(aruco_dict, params)

marker_length = 0.012  # meters

# ====== Trackbar Window ======
cv2.namedWindow("Threshold Control")
cv2.createTrackbar("THRESH", "Threshold Control", 205, 255, lambda x: None)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # ========= ใช้ threshold ก่อนตรวจจับ =========
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    th = cv2.getTrackbarPos("THRESH", "Threshold Control")
    _, th_img = cv2.threshold(gray, th, 255, cv2.THRESH_BINARY)

    # ส่งภาพ threshold ให้ detector ตรวจ
    corners, ids, rejected = detector.detectMarkers(th_img)

    if ids is not None:

        # วาดมาร์กเกอร์บน original frame
        cv2.aruco.drawDetectedMarkers(frame, corners, ids)

        for c in corners:

            # 1) วาดกรอบ Bounding Box
            box = c[0].astype(int)
            cv2.polylines(frame, [box], True, (0, 255, 0), 2)

            # 2) solvePnP
            obj_points = np.array([
                [-marker_length/2,  marker_length/2, 0],
                [ marker_length/2,  marker_length/2, 0],
                [ marker_length/2, -marker_length/2, 0],
                [-marker_length/2, -marker_length/2, 0]
            ], dtype=np.float32)

            img_points = c[0].astype(np.float32)

            success, rvec, tvec = cv2.solvePnP(
                obj_points,
                img_points,
                camera_matrix,
                dist_coeffs
            )

            if success:
                cv2.drawFrameAxes(frame, camera_matrix, dist_coeffs,
                                  rvec, tvec, 0.006)
                print("rvec:", rvec.flatten())
                print("tvec:", tvec.flatten())
                print("----------------------------------")
                
                # ====== หน่วงเพื่ออ่านค่า ======
                time.sleep(0.5)

    # แสดงภาพ Threshold และภาพจริง
    cv2.imshow("Threshold Image", th_img)
    cv2.imshow("ArUco Detection with Box", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
