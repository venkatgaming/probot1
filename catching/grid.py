from PIL import Image, ImageDraw

# Load image
img = Image.open('map.PNG')
draw = ImageDraw.Draw(img)

# Define grid parameters
grid_size = 4
width, height = img.size

# Draw grid lines and circles
for x in range(0, width, grid_size):
    draw.line((x, 0, x, height), fill=(255, 255, 0))
    for y in range(0, height, grid_size):
        draw.line((0, y, width, y), fill=(255, 255, 0))
        draw.ellipse(
            (x + grid_size // 2 - 1, y + grid_size // 2 - 1, x + grid_size // 2 + 1, y + grid_size // 2 + 1),
            fill=(0, 0, 0),
            outline=(0, 0, 0)
        )

# Save image
img.save('GridImage.png')
