import cv2
import numpy as np
import matplotlib.pyplot as plt

def detect_vanishing_point(image_path):
    
    # image = cv2.imread(image_path)
    # height, width, _ = image.shape
    # blurred = cv2.GaussianBlur(image, (21, 21), 0)
    # cv2.line(blurred, (50, height // 5), (width - 50, height // 5), color=(0, 0, 0), thickness=1)

    # edges = cv2.Canny(blurred, threshold1=100, threshold2=200)

    image = cv2.imread(image_path)
    height, width, _ = image.shape
    image = image[:, 100:width-100]

    blur = cv2.medianBlur(image, 7)
    gray = cv2.cvtColor(blur, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,11,3)

    canny = cv2.Canny(thresh, 120, 255, 1)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
    opening = cv2.morphologyEx(canny, cv2.MORPH_CLOSE, kernel)
    dilate = cv2.dilate(opening, kernel, iterations=2)
    canny = cv2.Canny(dilate, 120, 255, 1)

    cv2.imshow('image', canny)
    cv2.waitKey(0)

    lines = cv2.HoughLinesP(canny, 1, np.pi / 180, 20)
    
    cartesian_lines = []

    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(image, (x1, y1), (x2, y2), (0, 255, 0), 1)
            cartesian_lines.append(((x1, y1), (x2, y2)))
    
    if lines is None:
        print("No lines detected.")
        return
 
    intersections = []
    for i in range(len(cartesian_lines)):
        for j in range(i+1, len(cartesian_lines)):
            intersection = line_intersection(cartesian_lines[i], cartesian_lines[j])
            if intersection is not None:
                intersections.append(intersection)
                cv2.circle(image, intersection, 5, (0, 0, 0), -1)
    
    if len(intersections) == 0:
        print("Vanishing point is at infinity. The wall is parallel to the camera.")
        plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        plt.show()
    else:
        print("Vanishing point detected.")
        plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        plt.show()

def line_intersection(line1, line2):
    (x1, y1), (x2, y2) = line1
    (x3, y3), (x4, y4) = line2
    
    d = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    
    if d == 0:
        return None

    xi = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / d
    yi = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / d
    
    return int(xi), int(yi)

for i in range(100):
    detect_vanishing_point('data/images/' + str(i) + '.jpg')