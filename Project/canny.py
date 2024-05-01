import cv2

def detect_edges(image_path):
    image = cv2.imread(image_path)
    blurred = cv2.GaussianBlur(image, (21, 21), 0)
    edges = cv2.Canny(blurred, threshold1=100, threshold2=200)

    cv2.imshow('Original Image', image)
    cv2.imshow('Edge-detected Image', edges)

    cv2.waitKey(0)
    cv2.destroyAllWindows()

for i in range(100):
    detect_edges('data/images/'+str(i)+'.jpg')