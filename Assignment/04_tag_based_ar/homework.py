import cv2
import cv2.aruco
import numpy as np
from matplotlib import pyplot as plt

print(cv2.__version__)

aruco_dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_1000)
aruco_parameters = cv2.aruco.DetectorParameters()
mtx = np.array([[478.55988546,   0.,         321.25310519],
       [  0.,         638.8870619,  239.04702389],
       [  0.,           0.,           1.        ]])
dist = np.array([[-1.52941504e-01,  1.22326731e+00, -1.11054377e-03,  6.90654893e-03,
  -2.45749295e+00]])

def draw_box(source):
    source = cv2.resize(source, (640, 480))
    gray = cv2.cvtColor(source, cv2.COLOR_RGB2GRAY)
    res = cv2.aruco.detectMarkers(gray, aruco_dictionary, parameters = aruco_parameters)
    if res[1] is not None:
        print(f'Corners: {res[0]}')
        print(f'ID: {res[1]}')
        rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(res[0][0], 1, mtx, dist)
        # axis_drawn = cv2.drawFrameAxes(source, mtx, dist, rvecs, tvecs, 1)
        # cv2.imshow('ar_box', axis_drawn)
        axis = np.float32([[-0.5, -0.5, 0], [-0.5, 0.5, 0], [0.5, 0.5, 0], [0.5, -0.5, 0],
                   [-0.5, -0.5, 1], [-0.5, 0.5, 1], [0.5, 0.5, 1],[0.5, -0.5, 1]])
        imgpts, jac = cv2.projectPoints(axis, np.float32(rvecs), np.float32(tvecs), mtx, dist)
        imgpts = np.int32(imgpts).reshape(-1, 2)
        side2 = source.copy()
        side3 = source.copy()
        side4 = source.copy()
        side5 = source.copy()
        side6 = source.copy()
        side2 = cv2.drawContours(side2, [imgpts[4:]], -1, (255, 0, 0), -2)
        # right side vertical to the marker
        side3 = cv2.drawContours(side3, [np.array(
            [imgpts[0], imgpts[1], imgpts[5],
            imgpts[4]])], -1, (255, 0, 0), -2)
        # left side vertical to the marker
        side4 = cv2.drawContours(side4, [np.array(
            [imgpts[2], imgpts[3], imgpts[7],
            imgpts[6]])], -1, (255, 0, 0), -2)
        # front side vertical to the marker
        side5 = cv2.drawContours(side5, [np.array(
            [imgpts[1], imgpts[2], imgpts[6],
            imgpts[5]])], -1, (255, 0, 0), -2)
        # back side vertical to the marker
        side6 = cv2.drawContours(side6, [np.array(
            [imgpts[0], imgpts[3], imgpts[7],
            imgpts[4]])], -1, (255, 0, 0), -2)

        # now we put everything together.
        source = cv2.addWeighted(side2, 0.1, source, 0.9, 0)
        source = cv2.addWeighted(side3, 0.1, source, 0.9, 0)
        source = cv2.addWeighted(side4, 0.1, source, 0.9, 0)
        source = cv2.addWeighted(side5, 0.1, source, 0.9, 0)
        source = cv2.addWeighted(side6, 0.1, source, 0.9, 0)
        source = cv2.drawContours(source, [imgpts[:4]], -1, (255, 0, 0), 2)
        for i, j in zip(range(4), range(4, 8)): # this is basically putting the five side of this cube together
            source = cv2.line(source, tuple(imgpts[i]), tuple(imgpts[j]), (255, 0, 0), 2)
        source = cv2.drawContours(source, [imgpts[4:]], -1, (255, 0, 0), 2)
        cv2.imshow('ar_box', source)
    else:
        print('no marker found')
        cv2.imshow('ar_box', source)

cap = cv2.VideoCapture(0)
# ret, frame = cap.read()
# draw_box(frame)
# cv2.waitKey(0)
while True:
    ret, frame = cap.read()
    if not ret:
        break
    draw_box(frame)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
cv2.waitKey(1)
