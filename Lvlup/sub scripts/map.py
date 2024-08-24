from battle import *
import networkx as nx
import math
from utilities import *

def load_overlay(overlay_path):
    """Load the overlay image and convert it to a binary image."""
    overlay = cv2.imread(overlay_path)
    # Convert the overlay to grayscale
    overlay_gray = cv2.cvtColor(overlay, cv2.COLOR_BGR2GRAY)
    # Threshold the grayscale image to create a binary image
    _, overlay_bin = cv2.threshold(overlay_gray, 1, 255, cv2.THRESH_BINARY)

    return overlay_bin

def find_path(start, waypoints, overlay):
    """Find the path that connects all waypoints starting from the start point."""
    # Create a graph from the overlay image
    graph = nx.grid_2d_graph(*overlay.shape[::-1])
    # Remove nodes corresponding to black pixels (obstacles) in the overlay
    for y, row in enumerate(overlay):
        for x, value in enumerate(row):
            if value == 0:
                graph.remove_node((x, y))
    
    # Initialize path_coords with the start point
    path_coords = [start]
    
    # Append paths from start to each waypoint
    for waypoint in waypoints:
        path = nx.astar_path(graph, path_coords[-1], waypoint)
        path_coords.extend(path[1:])  # Exclude the first point (already in path_coords)

    return path_coords

def calculate_distances(path_coords, waypoints):
    """Calculate the distances traveled in each direction along the path, including stops at waypoints."""
    distances = []
    prev_coord = path_coords[0]
    prev_direction = None
    last_dx, last_dy = 0, 0

    for i in range(1, len(path_coords)):
        coord = path_coords[i]
        prev_coord = path_coords[i-1]
        dx = coord[0] - prev_coord[0]
        dy = coord[1] - prev_coord[1]
        if dx == 0 and dy == 0:
            continue

        if abs(dx) > abs(dy):
            if dx > 0:
                direction = "right"
            else:
                direction = "left"
        else:
            if dy > 0:
                direction = "down"
            else:
                direction = "up"

        if prev_direction is None:
            prev_direction = direction

        if direction != prev_direction or i == len(path_coords) - 1 or coord in waypoints:
            distance = math.sqrt(last_dx**2 + last_dy**2) / 3.74  # Assuming 15 units per pixel
            if distance >= 1:
                print(distance)
                distances.append((prev_direction, int(distance)))
            else:
                distances.append(("stop", 1))
            prev_direction = direction
            last_dx, last_dy = dx, dy

        else:
            last_dx += dx
            last_dy += dy

    return distances

def remove_consecutive_stops(distances):
    """Remove consecutive 'stop' commands from the distances list."""
    cleaned_distances = []
    last_command = None

    for command in distances:
        if command == ("stop", 1) and last_command == ("stop", 1):
            continue
        cleaned_distances.append(command)
        last_command = command

    return cleaned_distances

def draw_path(map_img, path_coords):
    """Draw the path on a copy of the map image."""
    map_img = cv2.imread(map_img)
    for i in range(len(path_coords) - 1):  
        cv2.line(map_img,
                 tuple(path_coords[i]), tuple(path_coords[i + 1]), (255, 255, 255), thickness=1)
    return map_img

def is_task_complete():
    pokemon_battle_strategy()

def perform_task():
    """Perform a task at a waypoint by clicking on a specific button and waiting for completion."""
    # Wait for the task to complete
    is_task_complete()
def movetoend(path_grid):
    for i in range(len(path_grid)):
        direction, distance = path_grid[i]
        if direction in ["right", "left", "down", "up"]:
            for _ in range(distance):
                if direction == "right":
                    pyautogui.keyDown("D")
                    time.sleep(0.05)
                    pyautogui.keyUp("D")
                elif direction == "left":
                    pyautogui.keyDown("A")
                    time.sleep(0.05)
                    pyautogui.keyUp("A")
                elif direction == "down":
                    pyautogui.keyDown("S")
                    time.sleep(0.05)
                    pyautogui.keyUp("S")
                elif direction == "up":
                    pyautogui.keyDown("W")
                    time.sleep(0.05)
                    pyautogui.keyUp("W")
        elif direction == "stop":
            perform_task()
            # Wait until the task is complete before proceeding
            while not is_task_complete():
                time.sleep(0.5)

def path_main():
    start = (20, 173)
    # Define waypoints
    waypoints = [(61, 153), (93, 153), (125, 153), (157, 153), (189, 153), 
                 (189, 194), (157, 194), (125, 194), (93, 194), (61, 194)]
    
    # Load the overlay image
    overlay = load_overlay('images/map.PNG')
    path_coords = None
    path_coords = find_path(start, waypoints, overlay)
    distances = calculate_distances(path_coords, waypoints)
    distances = remove_consecutive_stops(distances)  # Remove consecutive stops
    print(distances)
    return distances, path_coords

# Run the path planning and movement
json_file = 'distances.json'
if os.path.exists(json_file):
    with open(json_file, 'r') as file:
        data = json.load(file)
        movetoend(data)
else:
    with open(json_file, 'w') as f:
        path_distances, path_coords = path_main()
        f.truncate(0)
        json.dump(path_distances, f)

# Save path_coords[0] to a JSON file

