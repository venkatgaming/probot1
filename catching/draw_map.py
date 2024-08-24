import matplotlib.pyplot as plt
import os
import cv2
import numpy as np


def detect_and_draw_tile(tile_img, map_img):
    # Check if the input image has multiple channels
    if len(tile_img.shape) == 3 and tile_img.shape[2] == 3:
        # Convert the image to grayscale
        tile_gray = cv2.cvtColor(tile_img, cv2.COLOR_BGR2GRAY)
    else:
        tile_gray = tile_img

    # Convert the map image to grayscale
    map_gray = cv2.cvtColor(map_img, cv2.COLOR_BGR2GRAY)

    # Get the dimensions of the tile image
    tile_height, tile_width = tile_gray.shape

    # Calculate the threshold for matching the tiles
    threshold = 0.95

    # Detect the tiles in the map image
    res = cv2.matchTemplate(map_gray, tile_gray, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)
    
    # Get the coordinates of the top-left corner of each tile
    tile_coords = []
    for pt in zip(*loc[::-1]):
        x, y = pt[0] + tile_width // 2, pt[1] + tile_height // 2
        tile_coords.append((x, y))
    
    return tile_coords




def read_img_files_from_dir(dir_path):
    # Get a list of all files in the directory
    file_list = os.listdir(dir_path)

    # Create an empty list to store the image files
    img_list = []

    # Loop through each file in the directory
    for file_name in file_list:
        # Check if the file is an image file
        if file_name.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif")):
            # If the file is an image file, append its full path to the image list
            img_path = os.path.join(dir_path, file_name)
            img_list.append(img_path)

    # Return the list of image files
    return img_list

def detect_all_tiles_in_dir(tile_dirs, map_img, colors):
    # Create a black overlay image for drawing the tiles
    # map_img = cv2.imread(map_img)
    map_img = cv2.imread(map_img)
    print(map_img.shape)
    overlay = np.zeros_like(map_img, dtype=np.uint8)
    overlay.fill(0) 
    # overlay.fill(0)  # Fill the overlay with black

    for i, tile_dir in enumerate(tile_dirs):
        # Get the color to use for drawing the tiles in this directory
        color = colors[i]

        # Get a list of all the tile images in the directory
        tile_imgs = []
        for file_name in os.listdir(tile_dir):
            if file_name.endswith('.png') or file_name.endswith('.jpg'):
                tile_img = cv2.imread(os.path.join(tile_dir, file_name), cv2.IMREAD_GRAYSCALE)
                tile_imgs.append(tile_img)

        # Detect and draw each tile image on the overlay
        for tile_img in tile_imgs:
            tile_loc = detect_and_draw_tile(tile_img, map_img)
            if tile_loc:
                for i in range(len(tile_loc)):
                    x = tile_loc[i][0]
                    y = tile_loc[i][1]
                    cv2.rectangle(overlay, (x-8, y-8), (x+8, y+8), color, thickness=-1)

    return overlay



# Define the directory path, map image path, and threshold value
map_img_path = "map.png"
tile_dirs = ['img/tiles/FireRed/land/','img/tiles/FireRed/build/', 'img/tiles/FireRed/water/', 'img/tiles/FireRed/grass/']
colors = [(255, 255, 255), (138, 90, 32), (255, 0, 0), (0, 255, 0)]
output_img = detect_all_tiles_in_dir(tile_dirs, map_img_path, colors)

cv2.imwrite("overlay.png", output_img)
# cv2.waitKey(0)