import tkinter as tk
from tkinter import messagebox
import threading
import time
import json
import os
import pyautogui
import tempfile
from utilities import *
from moves import *
from pywinauto import Application, findwindows


def focus_window_by_name(window_title):
    try:
        # Attempt to connect to the window by its title
        app = Application().connect(title_re=window_title)
        # Set focus to the window
        app.top_window().set_focus()
        print(f"Focused on window with title containing: {window_title}")
    except findwindows.WindowNotFoundError:
        print(f"Window with title containing '{window_title}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


# Global variables
pp_count = {"crunch": 24, "earthquake": 16, "waterfall": 24, "ice-fang": 24}
Stops = 0
train = None
mega = None


def backgroundtasks():
    while True:
        A = locate_image(r"images\dont_learn_move.png")

        if A: 
            Click_Location(A[0], A[1])
            click_image(r"images\yes1.PNG")
        B = locate_image(r"images\no.png")
        if B:
            Click_Location(B[0], B[1])
        time.sleep(1)  # Add a small delay to prevent busy-waiting
        if not A and not B:
            break



def pokemon_battle_strategy():
    gyarados_moves = ["crunch", "earthquake", "waterfall", "ice-fang"]

    def find_poke_w():
        capture = wait_for_image(r"images\pokepoke.png")
        if capture:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
                captured_image = capture_screen_around_point(
                    capture[0] - 30, capture[1] + 60, 20, 20, 100
                )
                captured_image.save(temp_file.name)
                opponent_name = pokemon_name(temp_file.name)
            return opponent_name
        else:
            print("Image pokepoke.png not found")
            return None

    def choose_move(gyarados_moves, opponent_name):
        global pp_count
        attacker_level = 100
        attacker_stats = {"attack": 348, "special-attack": 130}
        gyarados_name = "gyarados"

        best_move = asyncio.run(
            find_best_move_for_pokemon(
                gyarados_name,
                gyarados_moves,
                opponent_name,
                attacker_level,
                attacker_stats,
            )
        )
        if pp_count[best_move] == 0:
            for move in gyarados_moves:
                if pp_count[move] > 0:
                    best_move = move
                    break
        pp_count[best_move] -= 1
        return best_move

    def main():
        global mega, train
        print(mega)
        i = 0
        if locate_image(r"images\vs.png"):
            while True:
                capture = locate_image(r"images\vs.png")
                if capture:
                    name = find_poke_w()
                    if i == 0:
                        click_image(r"images\fight.png")
                        if mega == 1:
                            click_image(r"images\megaevlove.png")
                        i += 1
                    else:
                        click_imageNT(r"images\fight.png")
                    try:
                        best_move = choose_move(gyarados_moves, name)
                        click_imageNT(f"attks\\{best_move}.png")
                    except Exception as e:
                        print(e)
                    time.sleep(6)
                    if Check_hp() == 0:
                        break
                    name = None
                else:
                    for _ in range(train + 1):
                        time.sleep(0.8)
                        keypress_("space", 0.1)
                    time.sleep(1)
                    break

    main()


def movetoend(path_grid):
    if os.path.exists(path_grid):
        with open(path_grid, "r") as file:
            path_grid = json.load(file)
    for direction, distance in path_grid:
        if direction in ["right", "left", "down", "up"]:
            for _ in range(distance):
                move_direction(direction)
                time.sleep(0.01)
        elif direction == "stop":
            global Stops
            Stops += 1
            for _ in range(2):
                keypress_("space", 0.01)
                time.sleep(2)
            pokemon_battle_strategy()
            backgroundtasks( )


def movetoend_HP(path_grid, num, path_r=0):
    if os.path.exists(path_grid):
        with open(path_grid, "r") as file:
            path_grid = json.load(file)
            
    key = f"point_{num}"  # Convert the integer to the corresponding string key
    if key not in path_grid:
        raise KeyError(f"Key {key} not found in path_grid")

    path = path_grid[key]

    if path_r == 1:
        # Reverse the path and directions
        path = [
            (reverse_direction(direction), distance)
            for direction, distance in path[::-1]
        ]

    for direction, distance in path:
        if direction in ["right", "left", "down", "up"]:
            for _ in range(distance):
                move_direction(direction)
        elif direction == "stop" and path_r == 0:
            pyautogui.keyDown("W")
            time.sleep(0.01)
            pyautogui.keyUp("W")
            for _ in range(2):
                time.sleep(0.6)
                keypress_("space", 0.1)
            click_image(r"images\yes3.png")
            time.sleep(1)
            for _ in range(2):
                time.sleep(0.6)
                keypress_("space", 0.1)
            break


def move_direction(direction):
    if direction == "right":
        pyautogui.keyDown("D")
        direction = "D"
    elif direction == "left":
        pyautogui.keyDown("A")
        direction = "A"
    elif direction == "down":
        pyautogui.keyDown("S")
        direction = "S"
    elif direction == "up":
        pyautogui.keyDown("W")
        direction = "W"
    time.sleep(0.01)
    pyautogui.keyUp(direction)


def reverse_direction(direction):
    reverse_map = {"right": "left", "left": "right", "up": "down", "down": "up"}
    return reverse_map.get(direction, direction)


def Check_hp():
    capture = wait_for_image(r"images\gyarados_name.PNG")
    if capture:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
            captured_image = capture_screen_around_point(
                capture[0] + 53, capture[1] + 50, 20, 20, 30
            )
            captured_image.save(temp_file.name)

        class HPChecker:
            def __init__(self, hp_string):
                self.current_hp, self.full_hp = self.parse_hp(hp_string)

            def parse_hp(self, hp_string):
                current_hp, full_hp = map(int, hp_string.split("/"))
                return current_hp, full_hp

            def check_hp(self):
                if self.current_hp == 0:
                    self.execute_task()
                else:
                    print("HP is above 30%.")
                return self.current_hp  # Add return statement here

            def execute_task(self):
                print("HP is below 30%! Executing task...")
                click_image(r"images\surrender.png")
                click_image(r"images\yes1.png")
                time.sleep(5)
                global Stops, pp_count
                movetoend_HP(r"distances\all_distances.json", Stops, 0)
                movetoend_HP(r"distances\all_distances.json", Stops, 1)
                pp_count = {
                    "crunch": 24,
                    "earthquake": 16,
                    "waterfall": 24,
                    "ice-fang": 24,
                }
                if Stops == 12:
                    Stops = 0
                return self.current_hp

            def display_hp(self):
                print(f"HP: {self.current_hp}/{self.full_hp}")

        hp_string = recognize_text_hp(temp_file.name)  # Example current HP and max HP
        hp_checker = HPChecker(hp_string)
        hp_checker.display_hp()
        current_hp = hp_checker.check_hp()  # Get the returned current_hp value
        return current_hp


def start_automation():
    try:
        focus_window_by_name("PROClient")
        global mega, train
        mega = 1 if mega_checkbox_var.get() else 0
        train = int(train_entry.get())
        if train <= 0:
            raise ValueError("Number of Pokémon to train must be greater than 0.")
        movetoend(r"distances\distances.json")
    except ValueError as e:
        messagebox.showerror("Error", str(e))
    except Exception as e:
        messagebox.showerror("Error", str(e))


def stop_automation():
    messagebox.showinfo("Info", "Automation stopped!")


# Setup UI
root = tk.Tk()
root.title("Pokémon Automation")

# Mega Evolution checkbox
mega_checkbox_var = tk.BooleanVar()
mega_checkbox = tk.Checkbutton(
    root, text="Enable Mega Evolution", variable=mega_checkbox_var
)
mega_checkbox.pack(pady=5)

# Number of Pokémon to train entry
tk.Label(root, text="Number of Pokémon to train:").pack(pady=5)
train_entry = tk.Entry(root)
train_entry.pack(pady=5)

# Start button
start_button = tk.Button(root, text="Start Automation", command=start_automation)
start_button.pack(pady=5)

# Stop button
stop_button = tk.Button(root, text="Stop Automation", command=stop_automation)
stop_button.pack(pady=5)

# Run the GUI loop
root.mainloop()
