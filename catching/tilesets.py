import os
import time
import random
import pyautogui
import requests
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from utilities import *  # Ensure utilities.py contains necessary functions like locate_image, click_image, etc.
import traceback

# Initialize global variables
name_LIST = []
falseswipe_1 = 0
falseswipe21 = 0
movement_time = 0.2  # Default movement time
stop_flag = threading.Event()

def process_sync():
    if locate_image("images/vs.png"):
        pokemon_switch_location = wait_for_image("images/pokemon_swich.PNG")
        if pokemon_switch_location:
            click_image_by_coords(pokemon_switch_location)
            greloom_location = wait_for_image("images/poke_breloom.PNG")
            if greloom_location:
                click_image_by_coords(greloom_location)
                fight_location = wait_for_image("images/fight.PNG")
                if fight_location:
                    click_image_by_coords(fight_location)
                    false_swipe_location = wait_for_image("images/false_swipe.PNG")
                    if false_swipe_location:
                        click_image_by_coords(false_swipe_location)
                        global falseswipe_1, falseswipe21
                        falseswipe_1 -= 1
                        falseswipe21 += 1
                        while locate_image("images/vs.png"):
                            bag_location = wait_for_image("images/bag.PNG")
                            if bag_location:
                                click_image_by_coords(bag_location)
                                pokeball_location = wait_for_image("images/pokeball.PNG")
                                if pokeball_location:
                                    click_image_by_coords(pokeball_location)

def process_nonsync():
    fight_location = wait_for_image("images/fight.PNG")
    if fight_location:
        click_image_by_coords(fight_location)
        false_swipe_location = wait_for_image("images/false_swipe.PNG")
        if false_swipe_location:
            click_image_by_coords(false_swipe_location)
            global falseswipe_1, falseswipe21
            falseswipe_1 -= 1
            falseswipe21 += 1
            while locate_image("images/vs.png"):
                bag_location = wait_for_image("images/bag.PNG")
                if bag_location:
                    click_image_by_coords(bag_location)
                    pokeball_location = wait_for_image("images/pokeball.PNG")
                    if pokeball_location:
                        click_image_by_coords(pokeball_location)

def main():
    global name_LIST  # Declare it global to modify the global list
    capture = wait_for_image(r"images\\pokepoke.png")
    if capture:
        captured_image = capture_screen_around_point(
            capture[0] - 30, capture[1] + 60, 20, 20, 100
        )
        captured_image.save("pokename.png")
        try:
            closest_match = pokemon_name(
                r"pokename.png",
                similarity=0.8,
            )
        except Exception as e:
            print(e)
        print(closest_match)
        try:
            if any(pokemon.lower() == closest_match.lower() for pokemon in pokemon_list):
                if sync_var.get():
                    process_sync()
                else:
                    process_nonsync()
            else:
                click_image_by_coords(wait_for_image("images/run.PNG"))
        except:
            pass
    name_LIST.clear()

def recharge():
    global falseswipe_1, falseswipe
    if falseswipe_1 == 0:
        click_image_by_coords(wait_for_image("images/bag_1.PNG"))
        time.sleep(0.1)
        if click_image("images/search.PNG", offset_x=200):
            pyautogui.write("leppa berry")
        for _ in range(4):
            click_image_by_coords(wait_for_image("images/lapaBarry.PNG"))
            click_image_by_coords(wait_for_image("images/poke_smerigle.PNG"))
            click_image_by_coords(wait_for_image("images/FS.PNG"))
        click_image_by_coords(wait_for_image("images/wrong.PNG"))
        falseswipe_1 = falseswipe

def movement():
    global movement_time
    if falseswipe21 == 145:
        if os.name == "nt":  # Check if the OS is Windows
            os.system("shutdown /s /t 1")  # /s for shutdown, /t 1 for 1 second delay
    if keypress_var.get():
        chosen_sequence = random.choice([1, 2])  # 1 for Option 1, 2 for Option 2
        if chosen_sequence == 1:
            for _ in range(200):
                recharge()
                keypress_("a", movement_time)
                keypress_("d", movement_time)
                main()
        else:
            for _ in range(200):
                recharge()
                keypress_("w", movement_time)
                keypress_("s", movement_time)
                main()
    else:
        recharge()
        keypress_("a", movement_time)
        keypress_("d", movement_time)
        main()

def start_script():
    try:
        global pokemon_list, sync, falseswipe, keypress, falseswipe_1, movement_time
        pokemon_list = [pokemon.strip().lower() for pokemon in pokemon_entry.get().split(",")]
        sync = 1 if sync_var.get() else 2
        keypress = 1 if keypress_var.get() else 2  # Use .get() method here
        falseswipe = int(falseswipe_entry.get())
        falseswipe_1 = falseswipe

        # Get movement time from the textbox, use default if empty
        movement_time_str = movement_time_entry.get().strip()
        if movement_time_str == "":
            movement_time = 0.2
        else:
            try:
                movement_time = float(movement_time_str)
                if not (0 <= movement_time <= 1):
                    raise ValueError("Movement time must be between 0 and 1.")
            except ValueError:
                movement_time = 0.2
                messagebox.showwarning("Invalid Input", "Movement time must be a number between 0 and 1. Using default value of 0.2.")

        os.environ["OMP_NUM_THREADS"] = "1"  # Ensures each subprocess gets 1 CPU core
        while True:
            movement()
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
        traceback.print_exc()
        

def toggle_advanced_settings():
    """Show or hide advanced settings based on the checkbox state."""
    if advanced_settings_var.get():
        # Show advanced settings
        movement_time_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        movement_time_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
    else:
        # Hide advanced settings
        movement_time_label.grid_forget()
        movement_time_entry.grid_forget()

def validate_float(value):
    """Validate that the input is a float and within the range [0, 1]."""
    try:
        f = float(value)
        return 0 <= f <= 1
    except ValueError:
        if value == "":
            return True
        return False

def validate_numeric(char):
    """Validate that the input is numeric."""
    if char.replace('.', '', 1).isdigit() or char == "":
        return True
    return False

def is_connected():
    try:
        return requests.get("https://www.google.com", timeout=3).status_code == 200
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

# Create the main window
root = tk.Tk()
root.title("Pokémon Catching Bot")

# Create the Notebook (tabbed interface)
notebook = ttk.Notebook(root)
notebook.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

# Create the Main tab
main_tab = ttk.Frame(notebook)
notebook.add(main_tab, text="Main")

# Create the Advanced Settings tab
advanced_settings_tab = ttk.Frame(notebook)
notebook.add(advanced_settings_tab, text="Advanced Settings")

# Create the Instructions tab
instructions_tab = ttk.Frame(notebook)
notebook.add(instructions_tab, text="Instructions")

# Layout for the Main tab
pokemon_label = tk.Label(main_tab, text="Pokémon Names (comma-separated):")
pokemon_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
pokemon_entry = tk.Entry(main_tab, width=50)
pokemon_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

falseswipe_label = tk.Label(main_tab, text="Falseswipe PP:")
falseswipe_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
falseswipe_entry = tk.Entry(main_tab, validate="key")
falseswipe_entry['validatecommand'] = (falseswipe_entry.register(validate_numeric), "%S")
falseswipe_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

sync_var = tk.BooleanVar()
sync_check = tk.Checkbutton(main_tab, text="Sync Mode", variable=sync_var)
sync_check.grid(row=2, column=0, padx=10, pady=5, sticky="w")

keypress_var = tk.BooleanVar()
keypress_check = tk.Checkbutton(main_tab, text="Random Keypress", variable=keypress_var)
keypress_check.grid(row=3, column=0, padx=10, pady=5, sticky="w")

start_button = tk.Button(main_tab, text="Start Script", command=lambda: threading.Thread(target=start_script, daemon=True).start())
start_button.grid(row=4, column=0, columnspan=2, pady=10)

# Layout for the Advanced Settings tab
advanced_settings_var = tk.BooleanVar()
advanced_settings_check = tk.Checkbutton(advanced_settings_tab, text="Show Advanced Settings", variable=advanced_settings_var, command=toggle_advanced_settings)
advanced_settings_check.grid(row=0, column=0, padx=10, pady=5, sticky="w")

movement_time_label = tk.Label(advanced_settings_tab, text="Movement Time (0 to 1):")
movement_time_entry = tk.Entry(advanced_settings_tab, validate="key")
movement_time_entry['validatecommand'] = (movement_time_entry.register(validate_float), "%S")

# Set the default visibility of advanced settings
toggle_advanced_settings()

# Layout for the Instructions tab
instructions_label = tk.Label(instructions_tab, text="", justify=tk.LEFT)
instructions_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
instructions_text = (
        "How to Use the Pokémon Catching Bot:\n\n"
        "1. Pokémon Names:\n"
        "- Enter the names of the Pokémon you want to catch, separated by commas.\n"
        "- Example: 'natu, bulbasaur, charmander'.\n\n"
        "2. Falseswipe PP:\n"
        "- Enter the number of PP (Power Points) available for the move 'False Swipe'.\n"
        "- This is used to weaken the Pokémon without knocking it out.\n\n"
        "3. Sync Option:\n"
        "- Check this option if you want the script to synchronize with specific Pokémon events.\n"
        "- If unchecked, it will use a different method.\n\n"
        "4. Keypress Option:\n"
        "- Check this option for random movement during the script's execution.\n"
        "- If unchecked, the movement will follow a standard pattern.\n\n"
        "5. Start Script:\n"
        "- Once all options are set, click 'Start Script' to begin.\n"
        "- The script will continue to run until manually stopped or an error occurs."
    )
instructions_label.config(text=instructions_text)

# Create a stop event for background tasks
stop_event = threading.Event()
background_thread = threading.Thread(target=backgroundtasks, args=(stop_event,), daemon=True)
background_thread.start()

# Run the application
root.mainloop()

# Stop the background tasks when the main window is closed
stop_event.set()
background_thread.join()
