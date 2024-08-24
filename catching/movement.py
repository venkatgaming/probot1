import requests
import threading
import pyautogui
import time
from utilities import *

stop_flag = threading.Event()

def is_connected():
    try:
        return requests.get("https://www.google.com", timeout=5).status_code == 200
    except requests.ConnectionError:
        return False

def login():
    click_image("images\\login.png")

def backgroundtasks(stop_event):
    while not stop_event.is_set():
        if locate_image(r"images\dont_learn_move.png"):
            click_image(r"images\yes1.PNG")
        elif locate_image(r"images\no.png"):
            click_image(r"images\no.png")
        if not is_connected():
            login()
        time.sleep(0.1)

try:
    thread = threading.Thread(target=backgroundtasks, args=(stop_flag,), daemon=True)
    thread.start()
    while True:
        time.sleep(1)
except (KeyboardInterrupt, SystemExit):
    stop_flag.set()
    thread.join()
    print("Script interrupted.")
except Exception as e:
    print(f"An error occurred: {e}")
