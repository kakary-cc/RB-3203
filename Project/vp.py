import cv2
import numpy as np
import matplotlib.pyplot as plt

def detect_vanishing_point(image_path):
    
    image = cv2.imread(image_path)
    blurred = cv2.GaussianBlur(image, (21, 21), 0)
    edges = cv2.Canny(blurred, threshold1=100, threshold2=200)

    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 0)
    
    cartesian_lines = []

    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
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
    
    # Check if the vanishing point is at infinity
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
    
    # Finding intersection using determinant
    d = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    
    if d == 0:
        # Parallel lines
        return None

    # x and y coordinates of intersection
    xi = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / d
    yi = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / d
    
    return int(xi), int(yi)

for i in range(100):
    detect_vanishing_point('data/images/'+str(i)+'.jpg')