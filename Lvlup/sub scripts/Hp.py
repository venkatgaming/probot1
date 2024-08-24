import cv2
import networkx as nx
import math
import time
import pyautogui
import json

def load_overlay(overlay_path):
    """Load the overlay image and convert it to a binary image."""
    overlay = cv2.imread(overlay_path)
    # Convert the overlay to grayscale
    overlay_gray = cv2.cvtColor(overlay, cv2.COLOR_BGR2GRAY)
    # Threshold the grayscale image to create a binary image
    _, overlay_bin = cv2.threshold(overlay_gray, 1, 255, cv2.THRESH_BINARY)
    return overlay_bin

def find_path(start, target, overlay):
    """Find the shortest path from start to target on the overlay."""
    # Create a graph from the overlay image
    graph = nx.grid_2d_graph(*overlay.shape[::-1])
    
    # Remove nodes corresponding to black pixels (obstacles) in the overlay
    for y, row in enumerate(overlay):
        for x, value in enumerate(row):
            if value == 0:
                graph.remove_node((x, y))
    
    # Find the shortest path using A*
    path = nx.astar_path(graph, start, target)
    return path

def calculate_distances(path_coords):
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

        if direction != prev_direction or i == len(path_coords) - 1:
            distance = math.sqrt(last_dx**2 + last_dy**2) / 3.74  # Assuming 15 units per pixel
            if distance >= 1:
                distances.append((prev_direction, int(distance)))
            prev_direction = direction
            last_dx, last_dy = dx, dy
        else:
            last_dx += dx
            last_dy += dy

    # Append a "stop" at the end of the path
    distances.append(("stop", 1))

    return distances

def save_distances_to_json(all_distances):
    """Save all distances to a single JSON file."""
    with open("all_distances.json", 'w') as f:
        json.dump(all_distances, f, indent=4)
    print("All distances saved to all_distances.json")

def movetoend_HP(path_grid, num):
    path = path_grid[num]
    for direction, distance in path:
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
            pass

# Example usage
if __name__ == "__main__":
    overlay_path = r"images/map.PNG"  # Replace with your overlay image path
    overlay = load_overlay(overlay_path)
    
    points = [(61, 153), (93, 153), (125, 153), (157, 153), (189, 153), 
              (189, 194), (157, 194), (125, 194), (93, 194), (61, 194)]
    
    all_distances = {}

    for idx, start in enumerate(points):
        print(start)
        target = (49, 173)  # Replace with your target coordinates
        path_coords = find_path(start, target, overlay)
        distances = calculate_distances(path_coords)
        all_distances[f"point_{idx+1}"] = distances

    save_distances_to_json(all_distances)
