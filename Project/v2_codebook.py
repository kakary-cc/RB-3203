import cv2
import numpy as np
import os
import pickle
from sklearn.cluster import KMeans
from sklearn.neighbors import BallTree

# textures_dir = "data/textures/"
textures_dir = "data/images/"
sift = cv2.SIFT_create()


def compute_sift_features():
    length = len(os.listdir(textures_dir))
    sift_descriptors = list()
    for i in range(length):
        # path = "pattern_" + str(i+1) + ".png"
        path = str(i) + ".jpg"
        print(os.path.join(textures_dir, path))
        img = cv2.imread(os.path.join(textures_dir, path))
        img = cv2.resize(img, (320, 240))
        # Pass the image to sift detector and get keypoints + descriptions
        # We only need the descriptors
        # These descriptors represent local features extracted from the image.
        _, des = sift.detectAndCompute(img, None)
        # Extend the sift_descriptors list with descriptors of the current image
        sift_descriptors.extend(des)
    return np.asarray(sift_descriptors)


def pre_nav_compute():
    print('Making codebook...', end="")
    # below 3 code lines to be run only once to generate the codebook
    # Compute sift features for images in the database
    sift_descriptors = compute_sift_features()

    # KMeans clustering algorithm is used to create a visual vocabulary, also known as a codebook,
    # from the computed SIFT descriptors.
    # n_clusters = 64: Specifies the number of clusters (visual words) to be created in the codebook. In this case, 64 clusters are being used.
    # init='k-means++': This specifies the method for initializing centroids. 'k-means++' is a smart initialization technique that selects initial 
    # cluster centers in a way that speeds up convergence.
    # n_init=10: Specifies the number of times the KMeans algorithm will be run with different initial centroid seeds. The final result will be 
    # the best output of n_init consecutive runs in terms of inertia (sum of squared distances).
    # The fit() method of KMeans pis then called with sift_descriptors as input data. 
    # This fits the KMeans model to the SIFT descriptors, clustering them into n_clusters clusters based on their feature vectors

    # TODO: try tuning the function parameters for better performance
    codebook = KMeans(n_clusters = 64, init='k-means++', n_init=10, verbose=1).fit(sift_descriptors)
    pickle.dump(codebook, open("codebook.pkl", "wb"))
    print('Finish')


# img = cv2.imread('data/textures/pattern_1.png')
# img = cv2.resize(img, (320, 240))
# cv2.imshow("demo", img)
# cv2.waitKey(0)
pre_nav_compute()