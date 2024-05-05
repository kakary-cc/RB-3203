# import necessary libraries and modules
# /home/parallels/anaconda3/envs/game/lib/python3.10/site-packages/vis_nav_game
from vis_nav_game import Player, Action, Phase
import pygame
import cv2
import sys
import math

import numpy as np
import os
import pickle
from sklearn.cluster import KMeans
from sklearn.neighbors import BallTree

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Define a class for a player controlled by keyboard input using pygame
class KeyboardPlayerPyGame(Player):
    def __init__(self):
        # Initialize class variables
        self.fpv = None  # First-person view image
        self.last_act = Action.IDLE  # Last action taken by the player
        self.screen = None  # Pygame screen
        self.keymap = None  # Mapping of keyboard keys to actions
        super(KeyboardPlayerPyGame, self).__init__()
        
        # Variables for saving data
        self.count = 0  # Counter for saving images
        self.save_dir = "data/images/"  # Directory to save images to

        self.rotationFlag = True
        # Default: Nav phase only
        self.generateDatabase = False
        self.generateCodebook = False
        if (len(sys.argv) > 1):
            print(sys.argv)
            if (sys.argv[1] == 'all'):
                self.generateDatabase = True
                self.generateCodebook = True
            elif (sys.argv[1] == 'exp'):
                self.generateDatabase = True
                self.generateCodebook = False
            else:
                print('Bad argument!')

        self.pre_nav_compute_finish = False

        # Initialize SIFT detector
        # SIFT stands for Scale-Invariant Feature Transform
        self.sift = cv2.SIFT_create()
        # Load pre-trained codebook for VLAD encoding
        # If you do not have this codebook comment the following line
        # You can explore the maze once and generate the codebook (refer line 181 onwards for more)
        self.codebook = pickle.load(open("codebook.pkl", "rb"))
        # Initialize database for storing VLAD descriptors of FPV
        self.database = []

        # Map drawing
        self.player_pos = [0, 0]
        self.player_angle = math.pi / 2
        self.player_xspeed = 2
        self.player_rspeed = 0.0427
        self.path = []
        self.arrow_points = [(0, -15), (10, 15), (0, 10), (-10, 15)]

    def reset(self):
        # Reset the player state
        self.fpv = None
        self.last_act = Action.IDLE
        self.screen = None

        # Initialize pygame
        pygame.init()

        # Define key mappings for actions
        self.keymap = {
            pygame.K_a: Action.LEFT,
            pygame.K_d: Action.RIGHT,
            pygame.K_w: Action.FORWARD,
            pygame.K_s: Action.BACKWARD,
            pygame.K_SPACE: Action.CHECKIN,
            pygame.K_ESCAPE: Action.QUIT
        }

    def act(self):
        """
        Handle player actions based on keyboard input
        """
        for event in pygame.event.get():
            #  Quit if user closes window or presses escape
            if event.type == pygame.QUIT:
                pygame.quit()
                self.last_act = Action.QUIT
                return Action.QUIT
            # Check if a key has been pressed
            if event.type == pygame.KEYDOWN:
                # Check if the pressed key is in the keymap
                if event.key in self.keymap:
                    # If yes, bitwise OR the current action with the new one
                    # This allows for multiple actions to be combined into a single action
                    self.last_act |= self.keymap[event.key]
                else:
                    # If a key is pressed that is not mapped to an action, then display target images
                    self.show_target_images()
            # Check if a key has been released
            if event.type == pygame.KEYUP:
                # Check if the released key is in the keymap
                if event.key in self.keymap:
                    # If yes, bitwise XOR the current action with the new one
                    # This allows for updating the accumulated actions to reflect the current sate of the keyboard inputs accurately
                    self.last_act ^= self.keymap[event.key]
                    # Change arrow direction
                else:
                    if event.key == pygame.K_LEFT:
                        self.player_angle += math.pi / 2
                    if event.key == pygame.K_RIGHT:
                        self.player_angle -= math.pi / 2

        return self.last_act

    def show_target_images(self):
        """
        Display front, right, back, and left views of target location in 2x2 grid manner
        """
        targets = self.get_target_images()

        # Return if the target is not set yet
        if targets is None or len(targets) <= 0:
            return

        # Create a 2x2 grid of the 4 views of target location
        hor1 = cv2.hconcat(targets[:2])
        hor2 = cv2.hconcat(targets[2:])
        concat_img = cv2.vconcat([hor1, hor2])

        w, h = concat_img.shape[:2]
        
        color = (0, 0, 0)

        concat_img = cv2.line(concat_img, (int(h/2), 0), (int(h/2), w), color, 2)
        concat_img = cv2.line(concat_img, (0, int(w/2)), (h, int(w/2)), color, 2)

        w_offset = 25
        h_offset = 10
        font = cv2.FONT_HERSHEY_SIMPLEX
        line = cv2.LINE_AA
        size = 0.75
        stroke = 1

        cv2.putText(concat_img, 'Front View', (h_offset, w_offset), font, size, color, stroke, line)
        cv2.putText(concat_img, 'Right View', (int(h/2) + h_offset, w_offset), font, size, color, stroke, line)
        cv2.putText(concat_img, 'Back View', (h_offset, int(w/2) + w_offset), font, size, color, stroke, line)
        cv2.putText(concat_img, 'Left View', (int(h/2) + h_offset, int(w/2) + w_offset), font, size, color, stroke, line)

        cv2.imshow(f'KeyboardPlayer:target_images', concat_img)
        cv2.waitKey(1)

    def set_target_images(self, images):
        """
        Set target images
        """
        super(KeyboardPlayerPyGame, self).set_target_images(images)
        self.show_target_images()

    def display_img_from_id(self, id, window_name):
        """
        Display image from database based on its ID using OpenCV
        """
        path = self.save_dir + str(id) + ".jpg"
        img = cv2.imread(path)
        try:
            cv2.imshow(window_name, img)
        except:
            print('error displaying image')
        cv2.waitKey(1)

    def display_imgs_from_ids(self, ids, window_name):
        imgs = []

        for image_id in ids:
            path = self.save_dir + str(image_id) + ".jpg"
            img = cv2.imread(path)
            if img is not None:
                imgs.append(img)
            else:
                print(f"Image ID {image_id} not found or could not be loaded.")

        if len(imgs) > 0:
            concat_img = cv2.hconcat(imgs)

            h = concat_img.shape[1] // len(imgs)
            w = concat_img.shape[0]
            color = (0, 0, 0)
            w_offset = 25
            h_offset = 10
            font = cv2.FONT_HERSHEY_SIMPLEX
            line = cv2.LINE_AA
            size = 0.75
            stroke = 1

            cv2.putText(concat_img, '#%s' % ids[0], (h_offset, w_offset), font, size, color, stroke, line)

            for i in range(1, len(imgs)):
                concat_img = cv2.line(concat_img, (i * h, 0), (i * h, w), color, 2)
                cv2.putText(concat_img, '#%s' % ids[i], (h_offset + i * h, w_offset), font, size, color, stroke, line)

            cv2.imshow(window_name, concat_img)
            cv2.waitKey(1)
        else:
            print("No valid images to display.")

    def compute_sift_features(self):
        """
        Compute SIFT features for images in the data directory
        """
        length = len(os.listdir(self.save_dir))
        sift_descriptors = list()
        for i in range(length):
            path = str(i) + ".jpg"
            img = cv2.imread(os.path.join(self.save_dir, path))
            # Pass the image to sift detector and get keypoints + descriptions
            # We only need the descriptors
            # These descriptors represent local features extracted from the image.
            _, des = self.sift.detectAndCompute(img, None)
            # Extend the sift_descriptors list with descriptors of the current image
            sift_descriptors.extend(des)
        return np.asarray(sift_descriptors)
    
    def get_VLAD(self, img):
        """
        Compute VLAD (Vector of Locally Aggregated Descriptors) descriptor for a given image
        """
        # We use a SIFT in combination with VLAD as a feature extractor as it offers several benefits
        # 1. SIFT features are invariant to scale and rotation changes in the image
        # 2. SIFT features are designed to capture local patterns which makes them more robust against noise
        # 3. VLAD aggregates local SIFT descriptors into a single compact representation for each image
        # 4. VLAD descriptors typically require less memory storage compared to storing the original set of SIFT
        # descriptors for each image. It is more practical for storing and retrieving large image databases efficicently.

        # Pass the image to sift detector and get keypoints + descriptions
        # Again we only need the descriptors
        _, des = self.sift.detectAndCompute(img, None)
        # We then predict the cluster labels using the pre-trained codebook
        # Each descriptor is assigned to a cluster, and the predicted cluster label is returned
        pred_labels = self.codebook.predict(des)
        # Get number of clusters that each descriptor belongs to
        centroids = self.codebook.cluster_centers_
        # Get the number of clusters from the codebook
        k = self.codebook.n_clusters
        VLAD_feature = np.zeros([k, des.shape[1]])

        # Loop over the clusters
        for i in range(k):
            # If the current cluster label matches the predicted one
            if np.sum(pred_labels == i) > 0:
                # Then, sum the residual vectors (difference between descriptors and cluster centroids)
                # for all the descriptors assigned to that clusters
                # axis=0 indicates summing along the rows (each row represents a descriptor)
                # This way we compute the VLAD vector for the current cluster i
                # This operation captures not only the presence of features but also their spatial distribution within the image
                VLAD_feature[i] = np.sum(des[pred_labels==i, :] - centroids[i], axis=0)
        VLAD_feature = VLAD_feature.flatten()
        # Apply power normalization to the VLAD feature vector
        # It takes the element-wise square root of the absolute values of the VLAD feature vector and then multiplies 
        # it by the element-wise sign of the VLAD feature vector
        # This makes the resulting descriptor robust to noice and variations in illumination which helps improve the 
        # robustness of VPR systems
        VLAD_feature = np.sign(VLAD_feature)*np.sqrt(np.abs(VLAD_feature))
        # Finally, the VLAD feature vector is normalized by dividing it by its L2 norm, ensuring that it has unit length
        VLAD_feature = VLAD_feature/np.linalg.norm(VLAD_feature)

        return VLAD_feature

    def get_neighbor(self, img):
        """
        Find the nearest neighbor in the database based on VLAD descriptor
        """
        # Get the VLAD feature of the image
        q_VLAD = self.get_VLAD(img).reshape(1, -1)
        # This function returns the index of the closest match of the provided VLAD feature from the database the tree was created
        # The '1' indicates the we want 1 nearest neighbor
        _, index = self.tree.query(q_VLAD, 1)
        return index[0][0]

    def pre_nav_compute(self):
        """
        Build BallTree for nearest neighbor search and find the goal ID
        """
        if not self.generateDatabase:
            [self.count, self.database] = pickle.load(open("database.pkl", "rb"))
        # If this function is called after the game has started
        if self.count > 0:

            if self.generateDatabase:
                pickle.dump([self.count, self.database], open("database.pkl", "wb"))
            else:
                [_, self.database] = pickle.load(open("database.pkl", "rb"))
                print("Loaded database from pickle")
                # tree = BallTree(self.database, leaf_size=60)
                # self.tree = tree

            if self.generateCodebook:
                print('Making codebook...', end="")
                # below 3 code lines to be run only once to generate the codebook
                # Compute sift features for images in the database
                sift_descriptors = self.compute_sift_features()

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

            # Build a BallTree for fast nearest neighbor search
            # We create this tree to efficiently perform nearest neighbor searches later on which will help us navigate and reach the target location
            
            # TODO: try tuning the leaf size for better performance
            tree = BallTree(self.database, leaf_size=60)
            self.tree = tree

            # Get the neighbor nearest to the choice of the target image and set it as goal
            targets = self.get_target_images()

            # while(not self.pre_nav_compute_finish):
            #     ...

            candidates = []
            for i in range(len(targets)):
                candidates.append(self.get_neighbor(targets[i]))
            self.display_imgs_from_ids(candidates, f'Candidates')
            choice = input("Select best match target [1-4]:")
            choice = int(choice) - 1
            self.goal = candidates[choice]
            cv2.destroyWindow(f'Candidates')
            print(f'Goal ID: {self.goal}')
            self.pre_nav_compute_finish = True

    def pre_navigation(self):
        """
        Computations to perform before entering navigation and after exiting exploration
        """
        super(KeyboardPlayerPyGame, self).pre_navigation()
        self.pre_nav_compute()
        if self.screen is not None:
            h, w, _ = self.fpv.shape
            self.player_pos = [400+w, 750]
            self.path = [self.player_pos[:]]
        
    def display_next_best_view(self):
        """
        Display the next best view based on the current first-person view
        """
        # TODO: could you write this function in a smarter way to not simply display the image that closely 
        # matches the current FPV but the image that can efficiently help you reach the target?

        # Get the neighbor of current FPV
        # In other words, get the image from the database that closely matches current FPV
        index = self.get_neighbor(self.fpv)
        # Display the image 5 frames ahead of the neighbor, so that next best view is not exactly same as current FPV
        # self.display_img_from_id(index+5, f'Next Best View')
        self.display_imgs_from_ids([index+2, index+5, self.goal], f'Next Best Views')
        # Display the next best view id along with the goal id to understand how close/far we are from the goal
        print(f'Next View ID: {index+2}, {index+5} || Goal ID: {self.goal}')

    def see(self, fpv):
        """
        Set the first-person view input
        """

        # Return if fpv is not available
        if fpv is None or len(fpv.shape) < 3:
            return

        self.fpv = fpv

        # If the pygame screen has not been initialized, initialize it with the size of the fpv image
        # This allows subsequent rendering of the first-person view image onto the pygame screen
        if self.screen is None:
            h, w, _ = fpv.shape
            self.screen = pygame.display.set_mode((w*2, h))
            self.screen = pygame.display.set_mode((800+w, 800))
            self.player_pos = [400+w, 750]
            self.path = [self.player_pos[:]]
            # Set speed to FPS
            # self.player_speed = self.get_state()[4]

        def convert_opencv_img_to_pygame(opencv_image):
            """
            Convert OpenCV images for Pygame.

            see https://blanktar.jp/blog/2016/01/pygame-draw-opencv-image.html
            """
            opencv_image = opencv_image[:, :, ::-1]  # BGR->RGB
            shape = opencv_image.shape[1::-1]  # (height,width,Number of colors) -> (width, height)
            pygame_image = pygame.image.frombuffer(opencv_image.tobytes(), shape, 'RGB')

            return pygame_image

        pygame.display.set_caption("KeyboardPlayer:fpv")

        # If game has started
        if self._state:
            
            self.screen.fill(WHITE)
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]:
                self.player_pos[0] += self.player_xspeed * math.cos(self.player_angle)
                self.player_pos[1] -= self.player_xspeed * math.sin(self.player_angle)
            if keys[pygame.K_s]:
                self.player_pos[0] -= self.player_xspeed * math.cos(self.player_angle)
                self.player_pos[1] += self.player_xspeed * math.sin(self.player_angle)
            # if keys[pygame.K_a]:
            #     self.player_angle += self.player_rspeed
            # if keys[pygame.K_d]:
            #     self.player_angle -= self.player_rspeed

            # If in exploration stage
            if self._state[1] == Phase.EXPLORATION:
                # TODO: could you employ any technique to strategically perform exploration instead of random exploration
                # to improve performance (reach target location faster)?

                # keys = pygame.key.get_pressed()
                if keys[pygame.K_q]:
                        print('stat: ', self.get_state()[4])
                        self.K = self.get_camera_intrinsic_matrix()
                        print(self.K)
                if self.generateDatabase:
                    # Only save FPV when moving
                    if keys[pygame.K_w] or keys[pygame.K_a] or keys[pygame.K_s] or keys[pygame.K_d]:
                        self.rotationFlag = not self.rotationFlag
                        if self.rotationFlag:
                            # Get full absolute save path
                            save_dir_full = os.path.join(os.getcwd(),self.save_dir)
                            save_path = save_dir_full + str(self.count) + ".jpg"
                            # Create path if it does not exist
                            if not os.path.isdir(save_dir_full):
                                os.mkdir(save_dir_full)
                            # Save current FPV
                            cv2.imwrite(save_path, fpv)

                            # Get VLAD embedding for current FPV and add it to the database
                            VLAD = self.get_VLAD(self.fpv)
                            self.database.append(VLAD)
                            self.count = self.count + 1
                else:
                    self.count = 1

            # If in navigation stage
            elif self._state[1] == Phase.NAVIGATION:
                # TODO: could you do something else, something smarter than simply getting the image closest to the current FPV?
                self.rotationFlag = not self.rotationFlag
                if self.rotationFlag:
                    if self.pre_nav_compute_finish:
                        self.display_next_best_view()
                # if self.run_pre_nav:
                #     self.display_next_best_view()
                # # Key the state of the keys
                # keys = pygame.key.get_pressed()
                # # If 'q' key is pressed, then display the next best view based on the current FPV
                # if keys[pygame.K_q]:
                #     self.display_next_best_view()

        # Display the first-person view image on the pygame screen
        rgb = convert_opencv_img_to_pygame(fpv)
        self.screen.blit(rgb, (0, 0))
        
        # Draw player
        rotated_arrow = [(p[0] * math.sin(self.player_angle) - p[1] * math.cos(self.player_angle),
                        p[0] * math.cos(self.player_angle) + p[1] * math.sin(self.player_angle))
                        for p in self.arrow_points]
        transformed_arrow = [(int(p[0] + self.player_pos[0]), int(p[1] + self.player_pos[1])) for p in rotated_arrow]
        pygame.draw.polygon(self.screen, BLACK, transformed_arrow)

        # Draw path
        self.path.append(self.player_pos[:])
        for i in range(len(self.path)-1):
            pygame.draw.line(self.screen, RED, self.path[i], self.path[i+1], 2)

        pygame.display.update()


if __name__ == "__main__":
    import vis_nav_game
    # Start the game with the KeyboardPlayerPyGame player
    vis_nav_game.play(the_player=KeyboardPlayerPyGame())
