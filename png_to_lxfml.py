from PIL import Image
import math
import os
import sys
from collections import namedtuple
import argparse

Brick = namedtuple('Brick', ['materials', 'itemNos'])
START_ROW = -16.3999996185302734375
ROW_DIFF = START_ROW - -15.6000003814697265625
START_COL = 12.3999996185302734375
COL_DIFF = START_COL - 11.59999942779541015625
colors2bricks = {}

def add_color(r, g, b, itemNos, materials):
    colors2bricks[(r, g, b)] = Brick(materials, itemNos)

def init_colors():
    add_color(21, 32, 40, 300526, 26)
    add_color(101, 101, 101, 4211098, 199)
    add_color(112, 3, 16, 4209383, 154)
    add_color(94, 51, 0, 4211242, 192)
    add_color(132, 120, 78, 300505, 5)
    add_color(145, 82, 10, 4122456, 38)
    add_color(170, 128, 80, 4569624, 312)
    add_color(214, 124, 0, 4173805, 106)
    add_color(252, 204, 0, 300524, 24)
    add_color(13, 70, 18, 4521915, 141)
    add_color(115, 144, 124, 4155050, 151)
    add_color(34, 135, 19, 300528, 28)
    add_color(171, 206, 0, 4122446, 119)
    add_color(112, 197, 232, 4619652, 322)
    add_color(25, 50, 94, 4255413, 140)
    add_color(23, 66, 130, 300523, 23)
    add_color(117, 151, 207, 4179830, 102)
    add_color(114, 131, 158, 4169428, 135)
    add_color(152, 152, 152, 4211389, 194)
    add_color(255, 255, 255, 300501, 1)

def nearest_color(r, g, b):
    min_dist = float('inf')
    nearest = None
    for color in colors2bricks:
        dist = math.sqrt(sum((a - b) ** 2 for a, b in zip((r, g, b), color)))
        if dist < min_dist:
            min_dist = dist
            nearest = color
    return nearest

def brick_string(refID, brick, x, y):
    return f"""<Brick refID="{refID}" designID="3005" itemNos="{brick.itemNos}">
<Part refID="{refID}" designID="3005" materials="{brick.materials},0" decoration="0">
<Bone refID="{refID + 1}" transformation="1,0,0,0,0,-1,0,1,0,{x},{y},0"></Bone>
</Part>
</Brick>"""

def header():
    return """<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
<LXFML versionMajor="5" versionMinor="0" name="Name">
<Meta>
<Application name="LEGO Digital Designer" versionMajor="4" versionMinor="3"/>
<Brand name="LDD"/>
<BrickSet version="835.4"/>
</Meta>
<Cameras>
<Camera refID="1" fieldOfView="80" distance="82.5515899658203125" transformation="0.06752951443195343,0,-0.9977173209190369,-0.30479493737220764,0.9521945714950562,-0.020629746839404106,0.9500210285186768,0.30549225211143494,0.06430123746395111,66.0257339477539,25.787870407104492,17.708168029785156"/>
</Cameras>
<Bricks cameraRef="1">"""

def footer():
    return """</Bricks>
<GroupSystems>
<GroupSystem>
</GroupSystem>
</GroupSystems>
<BuildingInstructions>
</BuildingInstructions>
</LXFML>"""

def convert(image_path):
    print(f"Processing image: {image_path}")
    image = Image.open(image_path).convert("RGBA")
    width, height = image.size
    print(f"Image size: {width}x{height}")
    pixels = list(image.getdata())
    output_file = image_path + ".lxfml"
    bottom_row = None
    for i in reversed(range(height)):
        for j in range(width):
            r, g, b, a = pixels[i * width + j]
            if a > 0:
                bottom_row = i
                break
        if bottom_row is not None:
            break

    if bottom_row is None:
        print("No visible pixels found!")
        return

    vertical_offset = (height - 1 - bottom_row) * COL_DIFF
    with open(output_file, "w") as f:
        f.write(header() + "\n")
        refID = 0
        for i in range(height):
            print(f"Processing row {i+1}/{height} ({100*(i+1)//height}%)")
            for j in range(width):
                r, g, b, a = pixels[i * width + j]
                if a == 0:
                    continue
                nearest = nearest_color(r, g, b)
                brick = colors2bricks[nearest]
                x = START_ROW - j * ROW_DIFF  # horizontal
                y = (height - 1 - i) * COL_DIFF - vertical_offset  # vertical
                f.write(brick_string(refID, brick, x, y) + "\n")
                refID += 1
        f.write(footer())
    print(f"Written to {output_file}\nDone!")

if __name__ == "__main__":
    init_colors()
    parser = argparse.ArgumentParser(
        description="Convert a PNG image to an LXFML LEGO model file."
    )
    parser.add_argument(
        "images",
        metavar="IMAGE",
        type=str,
        nargs="+",
        help="Path to the input PNG file(s)",
    )
    args = parser.parse_args()
    for image_path in args.images:
        if not os.path.isfile(image_path):
            print(f"File not found: {image_path}")
            continue
        if not image_path.lower().endswith(".png"):
            print(f"Skipping non-PNG file: {image_path}")
            continue
        convert(image_path)
