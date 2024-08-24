import tkinter as tk
from tkinter import ttk
import random
import time
from utilities import *
import sys

attack_offsets = [50 * 4, 50 * 3, 50 * 2, 50]
pokemon_loc = [36, 35 + 50, 36 + (50 * 2), 36 + (50 * 3), 36 + (50 * 4), 36 + (50 * 5)]
pyautogui.FAILSAFE = False
# Define functions
def on_checkbox_toggle(pokemon_index):
    if pokemon_checkboxes[pokemon_index].get():
        show_pokemon_ui(pokemon_index)
    else:
        hide_pokemon_ui(pokemon_index)

def show_pokemon_ui(pokemon_index):
    frame = pokemon_frames[pokemon_index]

    if ev_entries[pokemon_index] is None:
        ev_label = ttk.Label(frame, text="EV Target:")
        ev_label.grid(column=0, row=1, padx=10, pady=5, sticky="w")
    
        ev_entry = ttk.Entry(frame)
        ev_entry.grid(column=1, row=1, padx=10, pady=5, sticky="ew")
        ev_entries[pokemon_index] = ev_entry

        ttk.Label(frame, text="Attack Choices:").grid(
            column=0, row=2, padx=10, pady=5, sticky="w"
        )

        checkbox_vars[pokemon_index] = [tk.BooleanVar() for _ in range(4)]
        pp_entries[pokemon_index] = [ttk.Entry(frame) for _ in range(4)]
        attack_checkbuttons[pokemon_index] = []

        for j in range(4):
            checkbutton = ttk.Checkbutton(
                frame,
                text=f"Attack {j + 1}",
                variable=checkbox_vars[pokemon_index][j],
                command=lambda idx=pokemon_index, atk=j: on_attack_checkbox_toggle(
                    idx, atk
                ),
            )
            checkbutton.grid(column=0, row=3 + j, padx=10, pady=5, sticky="w")
            attack_checkbuttons[pokemon_index].append(checkbutton)
            pp_entries[pokemon_index][j].grid(
                column=1, row=3 + j, padx=10, pady=5, sticky="ew"
            )
            pp_entries[pokemon_index][j].config(
                state="disabled"
            )  # Disable PP entry fields initially
    frame.grid(row=1, column=pokemon_index, padx=10, pady=5, sticky="nsew")

def hide_pokemon_ui(pokemon_index):
    frame = pokemon_frames[pokemon_index]
    frame.grid_forget()

def on_attack_checkbox_toggle(pokemon_index, attack_index):
    state = "normal" if checkbox_vars[pokemon_index][attack_index].get() else "disabled"
    pp_entries[pokemon_index][attack_index].config(state=state)

def get_ui_inputs():
    pp_list = []
    ev_targets = []
    pokemon_selection = []

    for i in range(num_pokemons):
        if pokemon_checkboxes[i].get():
            ev_target = int(ev_entries[i].get()) if ev_entries[i].get() else 0
            ev_target = round_to_nearest_multiple(ev_target, 6)
            ev_targets.append(ev_target)
            
            attacks_pp = []
            for j in range(4):
                pp = int(pp_entries[i][j].get()) if pp_entries[i][j].get() else 0
                attacks_pp.append(pp)
            pp_list.append(attacks_pp)
            pokemon_selection.append(1)  # Pokémon is selected
        else:
            pokemon_selection.append(0)  # Pokémon is not selected

    return pp_list, ev_targets, pokemon_selection

def start_training():
    root.withdraw()  # Hide the window during training
    pp_list, ev_targets, pokemon_selection = get_ui_inputs()
    print(f"PP_List: {pp_list}")
    print(f"EV Targets: {ev_targets}")
    training_pokemon_indices = [i for i, x in enumerate(pokemon_selection) if x == 1]

    for p in training_pokemon_indices:
        if p > 0:
            time.sleep(3)
            select_pokemon(p)
        print(training_pokemon_indices.index(p))
        pp_1list = pp_list[training_pokemon_indices.index(p)]
        ev_target = ev_targets[training_pokemon_indices.index(p)]

        for i, subpp in enumerate(pp_1list):
            if subpp > 0:
                for _ in range(subpp):
                    if ev_target <= 0:
                        print("Pokémon EV trained")
                        break
                    ev_training(i)
                    ev_target -= 6

    root.deiconify()  # Show the window again after training

def select_pokemon(num):
    print(f"Selecting Pokémon: {num}")
    mouse_drag(86, pokemon_loc[num], 86, pokemon_loc[0])
    time.sleep(1)

def ev_training(attk):
    while True:
        keypress_("a", random.uniform(0.05, 0.2))
        keypress_("d", random.uniform(0.05, 0.2))
        if locate_image(r"images\vs.png"):
            click_image(r"images\fight.png")
            click_image(r"images\choose_move.png", 0, -attack_offsets[attk])
            while locate_image(r"images\vs.png"):
                pass
            break

def round_to_nearest_multiple(value, multiple):
    return int(round(value / multiple)) * multiple

# Tkinter UI setup
root = tk.Tk()
root.title("EV Training Bot")

num_pokemons = 6
ev_entries = [None] * num_pokemons
checkbox_vars = [[] for _ in range(num_pokemons)]
pp_entries = [[] for _ in range(num_pokemons)]
attack_checkbuttons = [[] for _ in range(num_pokemons)]
result_labels = []
pokemon_checkboxes = []
pokemon_frames = []

for i in range(num_pokemons):
    frame = ttk.Frame(root)
    pokemon_frames.append(frame)

    pokemon_check_var = tk.BooleanVar()
    pokemon_checkbox = ttk.Checkbutton(
        root,
        text=f"Enable Pokémon {i + 1}",
        variable=pokemon_check_var,
        command=lambda idx=i: on_checkbox_toggle(idx),
    )
    pokemon_checkbox.grid(row=0, column=i, padx=10, pady=5, sticky="w")
    pokemon_checkboxes.append(pokemon_check_var)

    frame.grid(row=1, column=i, padx=10, pady=5, sticky="nsew")

    result_label = ttk.Label(root, text="")
    result_label.grid(row=2, column=i, padx=10, pady=5, sticky="w")
    result_labels.append(result_label)

start_button = ttk.Button(root, text="Start Training", command=start_training)
start_button.grid(
    row=3, column=0, columnspan=num_pokemons, padx=10, pady=20, sticky="ew"
)

result_label = ttk.Label(root, text="")
result_label.grid(
    row=4, column=0, columnspan=num_pokemons, padx=10, pady=10, sticky="w"
)

for i in range(num_pokemons):
    root.grid_columnconfigure(i, weight=1)
root.grid_rowconfigure(3, weight=1)

root.mainloop()
