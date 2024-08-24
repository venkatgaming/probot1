import os
import time
import pydirectinput
import pyautogui
from PIL import ImageGrab, Image
import cv2
from colorama import Fore
import win32com.client
import json
import difflib
import numpy as np
from scipy import ndimage
import easyocr  # Import EasyOCR
import requests
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
pyautogui.FAILSAFE = False
reader = easyocr.Reader(["en"], gpu=False)

# Dynamically set the base path to the directory where the script is running
base_image_path = os.path.dirname(os.path.abspath(__file__))

def get_image_path(image_name):
    return os.path.join(base_image_path, "images", image_name)

def pokemon_name(image_path, similarity=0.8):
    closest_match = None

    def recognize_text(image_array):
        """Recognize text from the image using EasyOCR."""
        # Save the image array to a temporary file
        temp_path = os.path.join(base_image_path, "temp.png")
        Image.fromarray(image_array).save(temp_path)

        # Recognize text from the temporary file
        result = reader.readtext(temp_path, detail=1, paragraph=False)
        if result:
            return result[0][1].strip()  # Combine all recognized texts into one string
        return None

    def process_image(img_path):
        # Load the image
        img = Image.open(img_path).convert("RGBA")
        pixels = np.array(img)

        # Define the pixel colors
        white_pixel_range_min = np.array([200, 200, 200, 255])
        white_pixel_range_max = np.array([255, 255, 255, 255])
        blue_color = np.array([0, 0, 255, 255])
        white_color = np.array([255, 255, 255, 255])
        black_light_min = np.array([0, 0, 0, 255])
        black_light_max = np.array([50, 50, 50, 255])

        # Create masks for different conditions
        is_white = np.all(
            (pixels >= white_pixel_range_min) & (pixels <= white_pixel_range_max),
            axis=-1,
        )

        # Find connected components of white regions
        labels, num_features = ndimage.label(is_white)

        # Check if each component is enclosed
        enclosed = np.zeros(num_features, dtype=bool)
        for i in range(num_features):
            component = labels == (i + 1)
            # Check if the component is enclosed
            if (
                np.any(component[0, :])
                or np.any(component[-1, :])
                or np.any(component[:, 0])
                or np.any(component[:, -1])
            ):
                enclosed[i] = False
            else:
                enclosed[i] = True

        # Replace white pixels in enclosed regions with blue
        for i in range(num_features):
            if enclosed[i]:
                pixels[labels == (i + 1)] = blue_color

        # Replace all black and light black colors with white
        pixels[
            np.all((pixels >= black_light_min) & (pixels <= black_light_max), axis=-1)
        ] = white_color
        pixels[np.all(pixels == [0, 0, 0, 255], axis=-1)] = white_color

        # Replace any remaining colors except blue with white
        not_blue = ~np.all(pixels == blue_color, axis=-1)
        pixels[not_blue] = white_color

        # Convert the numpy array back to an image
        return pixels

    def find_closest_match(recognized_text, names_list, cutoff):
        """Find the closest Pokémon name match."""
        matches = difflib.get_close_matches(
            recognized_text, names_list, n=1, cutoff=cutoff
        )
        if matches:
            return matches[0]
        # In case no match is found above the cutoff, find the closest match without a cutoff
        closest_match = difflib.get_close_matches(
            recognized_text, names_list, n=1, cutoff=0
        )
        return closest_match[0] if closest_match else None

    def fetch_all_pokemon_names():
        """Fetch all Pokémon names from the PokeAPI."""
        pokemon_names = []
        url = "https://pokeapi.co/api/v2/pokemon?limit=10000"  # Adjust limit if needed

        while url:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                pokemon_names.extend(pokemon["name"] for pokemon in data["results"])
                url = data["next"]  # Get the URL for the next page
            else:
                print("Error fetching Pokémon data from PokeAPI")
                break

        return pokemon_names

    try:
        processed_img = process_image(image_path)
        recognized_text = recognize_text(processed_img)
        if recognized_text:
            pokemon_names = fetch_all_pokemon_names()
            closest_match = find_closest_match(
                recognized_text.lower(),
                [name.lower() for name in pokemon_names],
                similarity,
            )

            if closest_match:
                pass
            else:
                print("No close match found.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        return closest_match


# Initialize EasyOCR reader outside of multiprocessing to avoid redundant initialization

shell = win32com.client.Dispatch("WScript.Shell")


def locate_image(image, con=0.80):
    try:
        start = pyautogui.locateCenterOnScreen(
            image, region=(0, 0, 1920, 1080), grayscale=True, confidence=con
        )

        if start:
            return start
        else:
            return None
    except Exception as e:
        print(e)
        return None


def wait_for_image(image_path, timeout=60, confidence=0.8):
    start_time = time.time()
    try:
        while time.time() - start_time < timeout:
            location = pyautogui.locateCenterOnScreen(
                image_path,
                region=(0, 0, 1920, 1080),
                grayscale=True,
                confidence=confidence,
            )
            if location:
                return location
            else:
                return None
    except Exception as e:
        print(e)


def click_image_by_coords(coords):
    if coords is not None:
        x, y = coords
        Click_Location(x, y)


def focus_by_title(title):
    for window in pyautogui.getAllWindows():
        if window.title == title:
            print(f"Found window with title: {title}")
            shell.AppActivate(title)
            break
    else:
        print(f"Window with title '{title}' not found")


def click_image(image_path, offset_x=0, offset_y=0, wait=0, click=True):
    location = wait_for_image(image_path)
    if location and click:
        Click_Location(location[0] + offset_x, location[1] + offset_y, wait)
    return location


def Click_Location(x, y, wait=0):
    pydirectinput.moveTo(x, y)
    pydirectinput.mouseDown()
    time.sleep(wait)
    pydirectinput.mouseUp()


def Quit():
    print(Fore.GREEN + "Probot Closed\n")
    os._exit(os.EX_OK)


def fast_keypress(key, Time=0.1):
    import threading

    threading.Thread(target=keypress_, args=(key, Time)).start()


def keypress_(key, Time):
    pyautogui.keyDown(key)
    time.sleep(Time)
    pyautogui.keyUp(key)


def capture_screen_around_point(x, y, width, height, Right):
    # Calculate the region to capture
    left = x - width // 2
    top = y - height // 2
    right = x + (width + 1) // 2  # Adding 1 to ensure right is inclusive
    bottom = y + (height + 1) // 2  # Adding 1 to ensure bottom is inclusive

    # Capture the screen region
    image = ImageGrab.grab(bbox=(left, top, right + Right, bottom))

    return image


def detect_and_extract_text(image_path):
    try:
        # Read the image using OpenCV
        image = cv2.imread(image_path)

        # Preprocess the image (example: resize, grayscale conversion)
        resized_image = cv2.resize(
            image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC
        )
        grayscale_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY)

        # Use EasyOCR for text detection and extraction
        results = reader.readtext(grayscale_image)

        # Extracted text list
        extracted_text = [result[1] for result in results]

        return extracted_text

    except Exception as e:
        print(f"Error processing image {image_path}: {e}")
        return None


def movetoend(path_grid):
    for i in range(len(path_grid)):
        for n in range(int(path_grid[i][1])):
            if path_grid[i][0] == "right":
                pyautogui.keyDown("D")
                time.sleep(0.05)
                pyautogui.keyUp("D")
            if path_grid[i][0] == "left":
                pyautogui.keyDown("A")
                time.sleep(0.05)
                pyautogui.keyUp("A")
            if path_grid[i][0] == "down":
                pyautogui.keyDown("S")
                time.sleep(0.05)
                pyautogui.keyUp("S")
            if path_grid[i][0] == "up":
                pyautogui.keyDown("W")
                time.sleep(0.05)
                pyautogui.keyUp("W")
