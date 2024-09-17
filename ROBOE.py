import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

Pallet_x, Pallet_y = 100, 120
Pallet_size = Pallet_x * Pallet_y

grid = np.zeros((Pallet_x, Pallet_y), dtype=int)

boxes = {
    'D': (25, 22),
    'H': (40, 25),
    'I': (41, 36)
}

arrival_probs = {
    'D': 0.85,
    'H': 0.10,
    'I': 0.05
}

boxes_mapping = {
    'D': 1,
    'H': 2,
    'I': 3
}

box_colors = {
    'D': 'yellow',
    'H': 'blue',
    'I': 'purple'
}

def rotation(box):
    x, y = box
    return y, x

def arrival():
    prob = np.random.rand()
    probs = prob * 100
    if prob < arrival_probs['D']:
        box_type = 'D'
    elif prob < arrival_probs['D'] + arrival_probs['H']:
        box_type = 'H'
    else:
        box_type = 'I'
    return probs, box_type

def check_space(grid, box, current_x, current_y, buffer):
    x_box, y_box = box
    if (current_x + x_box + buffer > Pallet_x) or (current_y + y_box + buffer > Pallet_y):
        return False
    
    # Buffer zone
    start_x = max(current_x - buffer, 0) # clamping so it doesn't go outside of sides
    start_y = max(current_y - buffer, 0) 
    end_x = min(current_x + x_box + buffer, Pallet_x)
    end_y = min(current_y + y_box + buffer, Pallet_y)

    for i in range(start_x, end_x):
        for j in range(start_y, end_y):
            if grid[i][j] != 0:
                return False
    return True

def place(grid, box_type, box, current_x, current_y):
    x_box, y_box = box
    box_mapped = boxes_mapping[box_type]

    for i in range(x_box):
        for j in range(y_box):
            grid[current_x + i][current_y + j] = box_mapped

def find_best_placement(grid, box_type, buffer):
    box = boxes[box_type]
    best_placement = None
    best_remaining_space = Pallet_size

    for rotate in [False, True]:
        current_box = rotation(box) if rotate else box
        perimeter_positions = []

        # Edge Preference
        if current_box[0] > current_box[1]:
            # Vertical placements
            perimeter_positions += [(i, 0) for i in range(Pallet_x - current_box[0] + 1)]  # Top row
            perimeter_positions += [(i, Pallet_y - current_box[1]) for i in range(Pallet_x - current_box[0] + 1)]  # Bottom row
        else:
            # Horizontal
            perimeter_positions += [(0, j) for j in range(Pallet_y - current_box[1] + 1)]  # Left side
            perimeter_positions += [(Pallet_x - current_box[0], j) for j in range(Pallet_y - current_box[1] + 1)]  # Right side

        # Compute for all remaining perimeter positions
        for (i, j) in perimeter_positions:
            if check_space(grid, current_box, i, j, buffer):
                remaining_space = Pallet_size - ((current_box[0] * current_box[1]) + np.count_nonzero(grid))
                if remaining_space < best_remaining_space:
                    best_remaining_space = remaining_space
                    best_placement = (i, j, rotate)

    return best_placement

def find_inner_space_placement(grid, box_type, buffer):
    box = boxes[box_type]
    best_placement = None
    best_remaining_space = Pallet_size
    squeeze_attempts = 0

    for rotate in [False, True]:
        current_box = rotation(box) if rotate else box

        for i in range(Pallet_x - current_box[0] + 1):
            for j in range(Pallet_y - current_box[1] + 1):
                squeeze_attempts += 1
                if check_space(grid, current_box, i, j, buffer):
                    remaining_space = Pallet_size - ((current_box[0] * current_box[1]) + np.count_nonzero(grid))
                    if remaining_space < best_remaining_space:
                        best_remaining_space = remaining_space
                        best_placement = (i, j, rotate)

    return best_placement, squeeze_attempts

def main():
    arrangement_size = 0

    total_squeeze_attempts = 0
    num_boxes_placed = 0
    total_attempts = 0  

    inner_squeeze_attempts = 0
    inner_num_boxes_placed = 0
    num_boxes_attempted = 0 
    placement_order = []

    # Perimeter filling
    while True:
        fits = False
        probs, box_type = arrival()
        num_boxes_attempted += 1  
        print(f"{box_type}, {round(probs)}%")

        perimeter_buffer = 0
        best_placement = find_best_placement(grid, box_type, buffer=perimeter_buffer)
        if best_placement is not None:
            i, j, rotate = best_placement
            current_box = rotation(boxes[box_type]) if rotate else boxes[box_type]
            place(grid, box_type, current_box, i, j)
            arrangement_size += (current_box[0] * current_box[1])
            fits = True
            num_boxes_placed += 1

            placement_order.append((box_type, i, j, current_box[0], current_box[1]))
            print(f"Placed box on perimeter: {box_type} at ({i}, {j}), rotation: {'Yes' if rotate else 'No'}")
        else:
            print(f"Failed to place box on perimeter: {box_type}.")
            break

    # Inner filling
    while True:
        fits = False
        probs, box_type = arrival()
        num_boxes_attempted += 1  
        print(f"{box_type}, {round(probs)}%")

        inner_space_buffer = 3
        inner_space_placement, squeeze_attempts = find_inner_space_placement(grid, box_type, buffer=inner_space_buffer)
        total_attempts += squeeze_attempts  
        inner_squeeze_attempts += squeeze_attempts  

        if inner_space_placement is not None:
            i, j, rotate = inner_space_placement
            current_box = rotation(boxes[box_type]) if rotate else boxes[box_type]
            place(grid, box_type, current_box, i, j)
            arrangement_size += (current_box[0] * current_box[1])
            fits = True
            num_boxes_placed += 1
            inner_num_boxes_placed += 1

            placement_order.append((box_type, i, j, current_box[0], current_box[1]))
            print(f"Placed box in inner space: {box_type} at ({i}, {j}), rotation: {'Yes' if rotate else 'No'}")
        else:
            print(f"Failed to place box in inner space: {box_type}. Breaking loop.")
            break

    load_factor = arrangement_size / Pallet_size
    average_squeeze_attempts = inner_squeeze_attempts / inner_num_boxes_placed if inner_num_boxes_placed > 0 else 0
    success_rate = num_boxes_placed / num_boxes_attempted if num_boxes_attempted > 0 else 0
    placement_efficiency = total_attempts / num_boxes_placed if num_boxes_placed > 0 else 0

    print(f"\nNumber of Boxes: {num_boxes_placed}")
    print(f"Number of Inner boxes: {inner_num_boxes_placed}")
    print(f"\nLoad Factor: {load_factor * 100:.2f}%")
    print(f"Average Attempts to Squeeze a Box: {average_squeeze_attempts:.2f}")
    print(f"\nSuccess Rate: {success_rate * 100:.2f}%")

    return load_factor, grid, average_squeeze_attempts, placement_order, success_rate, placement_efficiency

load_factor, grid, average_squeeze_attempts, placement_order, success_rate, placement_efficiency = main()

def print_final_grid(grid, placement_order):
    fig, ax = plt.subplots(figsize=(12, 10))

    for idx, (box_type, x, y, height, width) in enumerate(placement_order, 1):
        color = box_colors[box_type]        
        rect = patches.Rectangle((y, x), width, height, linewidth=1, edgecolor='black', facecolor=color, alpha=0.6)
        ax.add_patch(rect)
        ax.text(y + width / 2, x + height / 2, str(idx), color='black', fontsize=10, ha='center', va='center', fontweight='bold')

    ax.set_xlim(0, Pallet_y)
    ax.set_ylim(Pallet_x, 0)
    ax.set_aspect('equal')
    ax.set_xticks(np.arange(0, Pallet_y + 1, 10))
    ax.set_yticks(np.arange(0, Pallet_x + 1, 10))
    plt.grid(True)
    plt.show()

# Visualize the final grid
print_final_grid(grid, placement_order)

