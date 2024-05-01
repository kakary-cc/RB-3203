import numpy as np
import cv2

def calibrate_image(image_path, intrinsic_matrix, distortion_coefficients):
    # Load the image from the specified path
    image = cv2.imread(image_path)
    
    if image is None:
        print("Error: Could not load the image.")
        return

    # Get the image size
    h, w = image.shape[:2]

    # Get the new camera matrix based on the intrinsic matrix and distortion coefficients
    new_camera_matrix, _ = cv2.getOptimalNewCameraMatrix(intrinsic_matrix, distortion_coefficients, (w, h), 1, (w, h))

    # Undistort the image
    undistorted_image = cv2.undistort(image, intrinsic_matrix, distortion_coefficients, None, new_camera_matrix)

    # Display the original and undistorted images
    cv2.imshow('Original Image', image)
    cv2.imshow('Calibrated Image', undistorted_image)

    # Wait for a key press and then close the windows
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Example usage
# Define the camera intrinsic matrix and distortion coefficients
intrinsic_matrix = np.array([
    [ 92.,   0., 160.],
    [  0.,  92., 120.],
    [  0.,   0.,   1.]
])
#     [1000, 0, 640],  # Replace with the actual values of your camera's intrinsic matrix
#     [0, 1000, 360],
#     [0, 0, 1]
# ])
distortion_coefficients = np.array([0, 0, 0, 0, 0])  # Replace with actual distortion coefficients

# Replace 'path_to_your_image.jpg' with the path to the image you want to process
image_path = 'data/images/0.jpg'
calibrate_image(image_path, intrinsic_matrix, distortion_coefficients)
