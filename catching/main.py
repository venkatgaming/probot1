import os
import random
import pyautogui
import threading
import traceback
from utilities import *
import socket

stop_flag = threading.Event()
falseswipe21 = 0
falseswipe_1 = 0
pokemon_list = []
sync = 1
keypress = 2
Sp = 1
attack_offsets = [50 * 4, 50 * 3, 50 * 2, 50]

def login():
    click_image(r"images\\login.png")
    click_image(wait_for_image(r"images\\bicycle.png"))


def is_connected():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        return True
    except OSError:
        return False


def dbackgroundtasks(stop_event):
    while not stop_event.is_set():
        A = locate_image(r"images\dont_learn_move.png")
        if A:
            Click_Location(A[0], A[1])
            click_image(r"images\\yes1.PNG")
        A = locate_image(r"images\\no.png")
        if A:
            Click_Location(A[0], A[1])
        elif is_connected == False:
            login()
        time.sleep(0.1)

def process_sync():
    if locate_image("images\\vs.png"):
        pokemon_switch_location = wait_for_image("images\\pokemon_swich.PNG")
        if pokemon_switch_location:
            click_image_by_coords(pokemon_switch_location)
            greloom_location = wait_for_image("images\\poke_smerigle.PNG")
            if greloom_location:
                click_image_by_coords(greloom_location)
                fight_location = wait_for_image("images\\fight.PNG")
                if fight_location:
                    click_image_by_coords(fight_location)
                    if Sp == 1:
                        click_image(r"images\choose_move.png", 0, -attack_offsets[0])
                    elif Sp == 2:
                        click_image(r"images\choose_move.png", 0, -attack_offsets[1])
                    global falseswipe_1, falseswipe21
                    falseswipe_1 -= 1
                    falseswipe21 += 1
                    while locate_image("images\\vs.png"):
                        bag_location = wait_for_image("images\\bag.PNG")
                        if bag_location:
                            click_image_by_coords(bag_location)
                            pokeball_location = wait_for_image("images\\pokeball.PNG")
                            if pokeball_location:
                                click_image_by_coords(pokeball_location)



def process_nonsync():
    fight_location = wait_for_image("images\\fight.PNG")
    if fight_location:
        click_image_by_coords(fight_location)
        if Sp == 1:
            click_image(r"images\choose_move.png", 0, -attack_offsets[0])
        elif Sp == 2:
            click_image(r"images\choose_move.png", 0, -attack_offsets[1])
        global falseswipe_1, falseswipe21
        falseswipe_1 -= 1
        falseswipe21 += 1
        while locate_image("images\\vs.png"):
            bag_location = wait_for_image("images\\bag.PNG")
            if bag_location:
                click_image_by_coords(bag_location)
                pokeball_location = wait_for_image("images\\pokeball.PNG")
                if pokeball_location:
                    click_image_by_coords(pokeball_location)


def main():
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
            if any(
                pokemon.lower() == closest_match.lower() for pokemon in pokemon_list
            ):
                if sync == 1:
                    process_sync()
                elif sync == 2:
                    process_nonsync()
            else:
                click_image_by_coords(wait_for_image("images\\run.PNG"))
        except Exception as e:
            print(f"Error during processing: {e}")
            traceback.print_exc()


def recharge():
    global falseswipe_1, falseswipe
    if falseswipe_1 == 0:
        click_image_by_coords(wait_for_image("images\\bag_1.PNG"))
        time.sleep(0.1)
        if click_image("images\\search.PNG", offset_x=200):
            pyautogui.write("leppa berry")
        for _ in range(4):
            click_image_by_coords(wait_for_image("images\\lapaBarry.PNG"))
            click_image_by_coords(wait_for_image("images\\poke_breloom.PNG"))
            if Sp == 1:
                click_image_by_coords(wait_for_image("images\\FS.PNG"))
            elif Sp == 2:
                click_image_by_coords(wait_for_image("images\\spore.png"))
        click_image_by_coords(wait_for_image("images\\wrong.PNG"))
        falseswipe_1 = falseswipe


def movement():
    if falseswipe21 == 145:
        if os.name == "nt":  # Check if the OS is Windows
            os.system("shutdown /s /t 1")  # /s for shutdown, /t 1 for 1 second delay
    if keypress == 1:
        chosen_sequence = random.choice([1, 2])  # 1 for Option 1, 2 for Option 2
        if chosen_sequence == 1:
            for _ in range(200):
                recharge()
                keypress_("a", 0.4)
                keypress_("d", 0.4)
                main()
        else:
            for _ in range(200):
                recharge()
                keypress_("w", 0.2)
                keypress_("s", 0.2)
                main()
    elif keypress == 2:
        recharge()
        keypress_("a", random.uniform(0.2, 0.2))
        keypress_("d", random.uniform(0.2, 0.2))
        main()


try:
    if __name__ == "__main__":
        input_img = input("Enter the pokemons you want to catch (e.g., natu, blub): ")
        Sp = int(input("1 for falseswipe true, 2 for spore:") or 1)
        pokemon_list = [pokemon.strip().lower() for pokemon in input_img.split(",")]
        print(pokemon_list)
        sync = int(input("1 for sync true, 2 for false: "))
        falseswipe = int(input("Enter falseswipe pp: ") or 40)
        keypress = int(
            input("1 for random movement true, 2 for normal movement: ") or 2
        )
        falseswipe_1 = falseswipe
        os.environ["OMP_NUM_THREADS"] = "1"  # Ensures each subprocess gets 1 CPU core

        # Start background tasks in a separate thread
        thread = threading.Thread(target=dbackgroundtasks, args=(stop_flag,))
        thread.daemon = True  # Ensure the thread exits when the main program exits
        thread.start()
        while True:
            movement()

except KeyboardInterrupt:
    print("Script interrupted.")
except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()
finally:
    stop_flag.set()
    thread.join()
