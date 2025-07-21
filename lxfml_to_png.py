import xml.etree.ElementTree as ET
from PIL import Image
import os
import sys
import argparse
from collections import namedtuple


Brick = namedtuple('Brick', ['materials', 'itemNos'])
START_ROW = -16.3999996185302734375
ROW_DIFF = START_ROW - -15.6000003814697265625
START_COL = 12.3999996185302734375
COL_DIFF = START_COL - 11.59999942779541015625
colors2bricks = {}
materials2color = {}

def add_color(r, g, b, itemNos, materials):
    brick = Brick(materials, itemNos)
    colors2bricks[(r, g, b)] = brick
    materials2color[materials] = (r, g, b)

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

def parse_lxfml(file_path):
    print(f"Parsing {file_path}")
    tree = ET.parse(file_path)
    root = tree.getroot()
    bricks = root.find("Bricks")
    positions = []
    for brick in bricks.findall("Brick"):
        part = brick.find("Part")
        mat_attr = part.attrib["materials"]
        mat_id = int(mat_attr.split(',')[0])
        color = materials2color.get(mat_id, (0, 0, 0))
        bone = part.find("Bone")
        t_str = bone.attrib["transformation"]
        t_vals = list(map(float, t_str.split(",")))
        x, y = t_vals[9], t_vals[10]
        positions.append((x, y, color))

    return positions

def lxfml_to_image(file_path, output_path):
    bricks = parse_lxfml(file_path)
    grid_positions = []
    for x, y, color in bricks:
        j = round((START_ROW - x) / ROW_DIFF)
        i = round((START_COL - y) / COL_DIFF)
        grid_positions.append((i, j, color))
    min_i = min(pos[0] for pos in grid_positions)
    max_i = max(pos[0] for pos in grid_positions)
    min_j = min(pos[1] for pos in grid_positions)
    max_j = max(pos[1] for pos in grid_positions)
    width = max_j - min_j + 1
    height = max_i - min_i + 1
    print(f"Reconstructing image of size {width}x{height}")
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    pixels = image.load()
    for i, j, color in grid_positions:
        x = j - min_j
        y = i - min_i
        if 0 <= x < width and 0 <= y < height:
            pixels[x, y] = (*color, 255)
    image.save(output_path)
    print(f"Image saved to {output_path}")


if __name__ == "__main__":
    init_colors()
    parser = argparse.ArgumentParser(description="Convert an LXFML LEGO model back into a PNG image.")
    parser.add_argument("lxfml_files", metavar="LXFML", type=str, nargs="+", help="Path to the input LXFML file(s)")
    args = parser.parse_args()
    for lxfml_path in args.lxfml_files:
        if not os.path.isfile(lxfml_path):
            print(f"File not found: {lxfml_path}")
            continue
        if not lxfml_path.lower().endswith(".lxfml"):
            print(f"Skipping non-LXFML file: {lxfml_path}")
            continue
        output_image = os.path.splitext(lxfml_path)[0] + "_reconstructed.png"
        lxfml_to_image(lxfml_path, output_image)
