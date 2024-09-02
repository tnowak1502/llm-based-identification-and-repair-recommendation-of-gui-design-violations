import sys
sys.path.append("./utils")

import json
from PIL import ImageDraw
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

comp_classes = json.load(open(sys.path[0] + "/data/comp_classes.json"))
MAX_X = 412
MAX_Y = 844

#recurses over json to extract relevant attributes
def reduce_json_metrics(dic, new_dic, parent_loc):
    new_dic["children"] = []
    dic["children"].reverse()
    for child in dic["children"]:
        x1 = int(child["x"] + parent_loc[0])
        x2 = int(x1 + child["width"])
        y1 = int(child["y"] + parent_loc[1])
        y2 = int(y1 + child["height"])

        if child["visible"]:
            if child.get("type") == "TEXT":
                if child["characters"] == "":
                    continue
            opaque = ""
            if child["opacity"] != 1:
                opaque = "X"

            fill = ""
            if child.get("fills") is not None:
                if child["fills"] != []:
                    if child["fills"][0]["visible"] and child["fills"][0]["type"] != "GRADIENT_LINEAR":
                        fill = "X"
                    if child["fills"][0]["opacity"] != 1:
                        opaque = "X"

            new_child = {"id": child["id"], "name": child["name"], "type": child["type"], "bounds": [x1, y1, x2, y2],
                         "fill": fill, "opaque": opaque}
            if child.get("children") is not None:
                if child["type"] != "GROUP":
                    reduce_json_metrics(child, new_child, (x1, y1))
                else:
                    reduce_json_metrics(child, new_child, parent_loc)
            new_dic["children"].append(new_child)

#checks if two rectangles overlap
def rectangles_overlap(R1, R2):
    x0_1, y0_1, x1_1, y1_1 = R1
    x0_2, y0_2, x1_2, y1_2 = R2
    return not (x1_1 <= x0_2 or x1_2 <= x0_1 or y1_1 <= y0_2 or y1_2 <= y0_1)

#checks if any components overlap with a newly added component
def check_overlaps(comps, new_comp):
    overlaps = []
    for comp in comps:
        if comp["opaque"] != "X":
            if rectangles_overlap(new_comp["bounds"], comp["bounds"]):
                overlaps.append(comp)
    return overlaps

#crops parts of R1 that are completely covered by R2
def crop_covered_rectangle(R1, R2):
    x0_1, y0_1, x1_1, y1_1 = R1
    x0_2, y0_2, x1_2, y1_2 = R2

    # Check if the top edge of R1 is covered by R2
    if y0_2 <= y0_1 < y1_2 and x0_2 <= x0_1 and x1_2 >= x1_1:
        y0_1 = y1_2

    # Check if the bottom edge of R1 is covered by R2
    if y0_2 < y1_1 <= y1_2 and x0_2 <= x0_1 and x1_2 >= x1_1:
        y1_1 = y0_2

    # Check if the left edge of R1 is covered by R2
    if x0_2 <= x0_1 < x1_2 and y0_2 <= y0_1 and y1_2 >= y1_1:
        x0_1 = x1_2

    # Check if the right edge of R1 is covered by R2
    if x0_2 < x1_1 <= x1_2 and y0_2 <= y0_1 and y1_2 >= y1_1:
        x1_1 = x0_2

    # Check if any dimension of R1 has collapsed
    if x0_1 >= x1_1 or y0_1 >= y1_1:
        return None  # R1 is completely covered by R2

    return [x0_1, y0_1, x1_1, y1_1]

#checks if any components overlap with a newly added component and crops it accordingly
def check_for_overlaps_and_crop(comps, new_comp):
    overlaps = check_overlaps(comps, new_comp)
    for comp in overlaps:
        new_comp["bounds"] = crop_covered_rectangle(new_comp["bounds"], comp["bounds"])
        if new_comp["bounds"] is None:
            break

#checks if bounds2 is located entirely within bounds1
def is_inside(bounds2, bounds1):
    if bounds2[0] >= bounds1[0]:
        if bounds2[2] <= bounds1[2]:
            if bounds2[1] >= bounds1[1]:
                if bounds2[3] <= bounds1[3]:
                    return True
    return False

#check if a component extends beyond the bounds of the screen and crop it
def check_out_of_bounds_and_crop(new_comp):
    bounds = new_comp["bounds"]
    if bounds[0] < 0:
        bounds[0] = 0
    if bounds[0] > MAX_X:
        return None

    if bounds[1] < 0:
        bounds[1] = 0
    if bounds[1] > MAX_Y:
        return None

    if bounds[2] > MAX_X:
        bounds[2] = MAX_X

    if bounds[3] > MAX_Y:
        bounds[3] = MAX_Y

    return bounds

#recurses over json file to extract components and groups
def extract_components_for_metrics(location, file):
    try:
        dic = json.load(open(location + "/" + file + ".json"))
    except:
        dic = json.load(open(location + "/" + file + ".json", encoding="utf-8"))
    reduced = {}
    reduce_json_metrics(dic, reduced, (0, 0))
    for child in reduced["children"]:
        if child["name"] == "Phone portrait":
            reduced = child
            break

    for child in reduced["children"]:
        if child["name"] != "Status bar" and child["name"] != "Navigation bars":
            # print(child["name"])
            extracted_comps, extracted_groups = recurse_and_get_comps(child)

    for group in extracted_groups:
        to_remove = []
        for comp_id in group["ui_comp_ids"]:
            comp = find_elem(extracted_comps, comp_id)
            if comp["bounds"] == group["bounds"] and not "Media" in comp["name"]:
                to_remove.append(comp)
        for rem in to_remove:
            group["ui_comp_ids"].remove(rem["id"])
            extracted_comps.remove(rem)

    to_remove = []
    for group in extracted_groups:
        if len(group["ui_comp_ids"]) <= 0:
            to_remove.append(group)

    for rem in to_remove:
        extracted_groups.remove(rem)
        check_for_overlaps_and_crop(extracted_comps, rem)
        if rem["bounds"] is not None:
            extracted_comps.append(rem)

    return extracted_comps, extracted_groups

#recurses over json to extract components and groups
def recurse_and_get_comps(dic):
    extracted_comps = [{"name": "Status bar", "bounds": [0, 0, 412, 40], "opaque": ""},
                       {"name": "Navigation bars", "bounds": [0, 844, 412, 892], "opaque": ""}]
    extracted_groups = []
    remove_later = []
    group_id_counter = 0
    comp_id_counter = 0

    def recurse(child, current_top_parent=None):
        full_comps = [*extracted_comps, *extracted_groups]
        nonlocal group_id_counter, comp_id_counter
        current_id = group_id_counter + comp_id_counter
        child["bounds"] = check_out_of_bounds_and_crop(child)
        if child["bounds"] is None:
            return
        else:

            is_comp = False
            for comp_type in comp_classes.keys():
                if comp_type not in ["common_button", "chip", "fab", "icon_button", "segmented_button", "divider",
                                     "checkbox", "radio_button", "text_field"]:
                    if child["name"].replace(" ", "-") in comp_classes[comp_type]:
                        """check_for_overlaps_and_crop(full_comps, child)
                        if child["bounds"] != None:
                            extracted_comps.append({"id": child["id"], "name": child["name"], "bounds": child["bounds"]})
                            if current_top_parent is not None:
                                current_top_parent["comp_ids"].append(child["id"])"""
                        if comp_type == "card" and child["type"] == "INSTANCE":
                            child["children"].reverse()
                        is_comp = True
                    elif "List item" in child["name"] \
                            or "Nav item" in child["name"] \
                            or "Section header" in child["name"] \
                            or "Tab " in child["name"] \
                            or "Bottom Sheet" in child["name"]:
                        is_comp = True
            is_top_parent = False

            if child.get("children") is not None:
                check_for_overlaps_and_crop(full_comps, child)
                if child["bounds"] is None:
                    return
                group_id_counter += 1
                if ((child["type"] == "FRAME" and child["fill"] != "") or is_comp) \
                        and current_top_parent is None and not child["name"] == "Carousel - Full screen":
                    if not child["name"] == "List" \
                            and not child["name"] == "Tabs" \
                            and not child["name"] == "Tab group" \
                            and not child["name"] == "Bottom sheet":
                        new_parent = {"id": current_id,
                                      "old_id": child["id"],
                                      "name": child["name"],
                                      "bounds": child["bounds"],
                                      "ui_comp_ids": [],
                                      "ui_comp_group_ids": [],
                                      "opaque": child["opaque"]}
                        is_top_parent = True
                        for subchild in child["children"]:
                            recurse(subchild, current_top_parent=new_parent)
                        extracted_groups.append(new_parent)

                if not is_top_parent and not child["name"] == "Carousel - Full screen":
                    if is_comp or child["type"] != "INSTANCE":
                        if child["bounds"] is None:
                            return
                        else:
                            for subchild in child["children"]:
                                recurse(subchild, current_top_parent=current_top_parent)

            if child["type"] != "GROUP" and not is_top_parent:
                if not ("state-layer" in child["name"] and (child["fill"] == "" or child["opaque"] == "X")) \
                        and not child["name"] == "List" \
                        and not child["name"] == "Tabs" \
                        and not child["name"] == "Tab group" \
                        and not child["name"] == "Bottom sheet" \
                        and not "List item" in child["name"] \
                        and not "Nav item" in child["name"] \
                        and not "Section header" in child["name"] \
                        and not "Tab " in child["name"] \
                        and not "Bottom Sheet" in child["name"]:
                    if child["bounds"] is None:
                        return
                    elif current_top_parent is not None and child["name"] == "Background" \
                            or current_top_parent is not None and "Item-text" in child["name"] \
                            or child["type"] == "FRAME" and child.get(
                        "children") is None and not is_comp and not "Item-" in child["name"] and not "Media" in child[
                        "name"] and not "Text content" in child["name"]:
                        return
                    else:
                        check_for_overlaps_and_crop(full_comps, child)
                        if child["bounds"] is None:
                            return
                        else:
                            comp_id_counter += 1
                            if child["type"] == "FRAME":
                                if child["fill"] != "":
                                    if child["opaque"] == "X":
                                        remove_later.append({"id": current_id,
                                                             "old_id": child["id"],
                                                             "name": child["name"],
                                                             "bounds": child["bounds"],
                                                             "opaque": child["opaque"]})
                                    extracted_comps.append({"id": current_id,
                                                            "old_id": child["id"],
                                                            "name": child["name"],
                                                            "bounds": child["bounds"],
                                                            "opaque": child["opaque"]})
                                    if current_top_parent is not None and not child["opaque"] == "X":
                                        current_top_parent["ui_comp_ids"].append(current_id)
                            else:
                                if child["opaque"] == "X":
                                    remove_later.append({"id": current_id,
                                                         "old_id": child["id"],
                                                         "name": child["name"],
                                                         "bounds": child["bounds"],
                                                         "opaque": child["opaque"]})
                                extracted_comps.append({"id": current_id,
                                                        "old_id": child["id"],
                                                        "name": child["name"],
                                                        "bounds": child["bounds"],
                                                        "opaque": child["opaque"]})
                                if current_top_parent is not None and not child["opaque"] == "X":
                                    current_top_parent["ui_comp_ids"].append(current_id)

    for child in dic["children"]:
        recurse(child)

    extracted_comps.remove({"name": "Status bar", "bounds": [0, 0, MAX_X, 40], "opaque": ""})
    extracted_comps.remove({"name": "Navigation bars", "bounds": [0, MAX_Y, MAX_X, 892], "opaque": ""})
    for c in remove_later:
        extracted_comps.remove(c)

    return extracted_comps, extracted_groups

#converts extracted components and groups into the format we need for metric calculation
def convert(comps, groups):
    gui = {"ui_comps": [], "ui_comp_groups": groups, "ungrouped_comps": []}
    for comp in comps:
        in_group = False
        for group in groups:
            if comp["id"] in group["ui_comp_ids"]:
                in_group = True
                break
        if in_group:
            gui["ui_comps"].append(comp)
        else:
            gui["ungrouped_comps"].append(comp)
    return gui

#returns an element by id
def find_elem(list, id, list2=None):
    for elem in list:
        if elem["id"]==id:
            return elem
    for elem in list2:
        if elem["id"]==id:
            return elem

#removes groups that are inside other groups
def check_groups_inside(gui):
    groups = gui["ui_comp_groups"]
    groups = list(sorted(groups, key=lambda x: (x["bounds"][2] - x["bounds"][0]) * (x["bounds"][1] - x["bounds"][3])))

    to_remove = []
    for i in range(len(groups)):
        group_1 = groups[i]
        for j in range(i+1, len(groups)):
            group_2 = groups[j]
            if not "Snackbar" in group_2["name"] and not "Navigation" in group_2["name"] and not "Dialog" in group_2["name"] and not "Menu" in group_2["name"] and not "FAB" in group_2["name"]:
                if not group_2 in to_remove:
                    if is_inside(group_2["bounds"], group_1["bounds"]):
                        for comp_id in group_2["ui_comp_ids"]:
                            group_1["ui_comp_ids"].append(comp_id)
                        to_remove.append(group_2)

    for remove in to_remove:
        gui["ui_comp_groups"].remove(remove)

#creates a list of empty spaces in a grid created by already existing component's y bounds
def calculate_empty_spaces_width(rectangles):
    # Fixed grid size
    width = MAX_X
    height = MAX_Y

    # Initialize the grid using numpy for faster operations
    grid = np.zeros((height, width), dtype=bool)

    # Mark the grid cells covered by rectangles
    for r in rectangles:
        grid[r[1]:r[3], r[0]:r[2]] = True

    # Collect all unique y boundaries
    y_coords = set([0, height])
    for r in rectangles:
        y_coords.update([r[1], r[3]])

    # Sort the y coordinates to define horizontal segments
    y_coords = sorted(y_coords)

    # Find empty spaces
    empty_rectangles = []

    # Traverse the grid by horizontal segments defined by the y coordinates
    for i in range(len(y_coords) - 1):
        y0, y1 = y_coords[i], y_coords[i + 1]

        # Within each horizontal segment, find vertical empty regions
        x_start = 0
        for r in sorted(rectangles, key=lambda x: x[0]):
            if r[1] <= y0 < r[3] or r[1] < y1 <= r[3]:  # Rectangle overlaps the horizontal segment
                x_end = r[0]
                if x_start < x_end:
                    empty_rectangles.append([x_start, y0, x_end, y1])
                x_start = r[2]
        if x_start < width:
            empty_rectangles.append([x_start, y0, width, y1])

    return empty_rectangles

import numpy as np

#creates a list of empty spaces in a grid created by already existing component's x bounds
def calculate_empty_spaces_height(rectangles):
    # Fixed grid size
    width = MAX_X
    height = MAX_Y

    # Initialize the grid using numpy for faster operations
    grid = np.zeros((height, width), dtype=bool)

    # Mark the grid cells covered by rectangles
    for r in rectangles:
        grid[r[1]:r[3], r[0]:r[2]] = True

    # Collect all unique x and y boundaries
    x_coords = set([0, width])
    y_coords = set([0, height])
    for r in rectangles:
        x_coords.update([r[0], r[2]])
        y_coords.update([r[1], r[3]])

    # Sort the coordinates to define regions
    x_coords = sorted(x_coords)
    y_coords = sorted(y_coords)

    # Find empty spaces
    empty_rectangles = []

    # Traverse the grid by regions defined by the coordinates
    for i in range(len(x_coords) - 1):
        x0, x1 = x_coords[i], x_coords[i + 1]
        vertical_empty_ranges = []
        current_empty_range_start = None

        for j in range(len(y_coords) - 1):
            y0, y1 = y_coords[j], y_coords[j + 1]
            # Check if the current region is empty
            if not grid[y0:y1, x0:x1].any():
                if current_empty_range_start is None:
                    current_empty_range_start = y0
            else:
                if current_empty_range_start is not None:
                    vertical_empty_ranges.append((current_empty_range_start, y0))
                    current_empty_range_start = None

        if current_empty_range_start is not None:
            vertical_empty_ranges.append((current_empty_range_start, height))

        for y0, y1 in vertical_empty_ranges:
            empty_rectangles.append([x0, y0, x1, y1])

    return empty_rectangles

#checks if ungrouped components are contained by groups or other ungrouped components
def check_ungroupeds_inside(gui):
    comps = gui["ui_comps"]
    groups = gui["ui_comp_groups"]
    ungroupeds = gui["ungrouped_comps"]

    for group in groups:
        to_remove = []
        bounds = group["bounds"]
        for comp in ungroupeds:
            if is_inside(comp["bounds"], bounds):
                group["ui_comp_ids"].append(comp["id"])
                to_remove.append(comp)
        if len(to_remove) > 0:
            for remove in to_remove:
                ungroupeds.remove(remove)
                comps.append(remove)

    ungroupeds = list(
        sorted(ungroupeds, key=lambda x: (x["bounds"][2] - x["bounds"][0]) * (x["bounds"][1] - x["bounds"][3])))
    to_remove_group = []
    to_remove_comp = []
    for i in range(len(ungroupeds)):
        u_1 = ungroupeds[i]
        new_group = {"id": u_1["id"],
                     "name": u_1["name"],
                     "bounds": u_1["bounds"],
                     "ui_comp_ids": [],
                     "ui_comp_group_ids": [],
                     "opaque": u_1["opaque"]}

        for j in range(i + 1, len(ungroupeds)):
            u_2 = ungroupeds[j]
            if not u_2 in to_remove_comp:
                if is_inside(u_2["bounds"], u_1["bounds"]):
                    new_group["ui_comp_ids"].append(u_2["id"])
                    to_remove_comp.append(u_2)

        if len(new_group["ui_comp_ids"]) > 0:
            groups.append(new_group)
            to_remove_group.append(u_1)

    for r in to_remove_group:
        gui["ungrouped_comps"].remove(r)

    for r in to_remove_comp:
        gui["ungrouped_comps"].remove(r)
        comps.append(r)

#groups ungrouped components in the spaces not covered by other components
def group_ungrouped_comps(gui):
    max_id = 0
    comps = gui["ui_comps"]
    groups = gui["ui_comp_groups"]
    ungroupeds = gui["ungrouped_comps"]
    for c in comps:
        if max_id < c["id"]:
            max_id = c["id"]
    for c in groups:
        if max_id < c["id"]:
            max_id = c["id"]
    for c in ungroupeds:
        if max_id < c["id"]:
            max_id = c["id"]

    rectangles = []
    for group in groups:
        if group["name"].replace(" ", "-") not in comp_classes["dialog"] and group["name"].replace(" ", "-") not in comp_classes["snackbar"]:
            rectangles.append(group["bounds"])
    empty_spaces = calculate_empty_spaces_width(rectangles)
    current_id = max_id + 1
    for empty in empty_spaces:
        to_remove = []
        new_group = {"id": current_id,
                     "name": "ungrouped",
                     "bounds": empty,
                     "ui_comp_ids": [],
                     "ui_comp_group_ids": [],
                     "opaque": ""}
        for comp in ungroupeds:
            if is_inside(comp["bounds"], empty):
                new_group["ui_comp_ids"].append(comp["id"])
                to_remove.append(comp)
        if len(to_remove) > 0:
            groups.append(new_group)
            current_id += 1
            for remove in to_remove:
                ungroupeds.remove(remove)
                comps.append(remove)

    if len(ungroupeds) > 0:
        rectangles = []
        for group in groups:
            rectangles.append(group["bounds"])
        empty_spaces = calculate_empty_spaces_height(rectangles)
        current_id = max_id + 1
        for empty in empty_spaces:
            to_remove = []
            new_group = {"id": current_id,
                         "name": "ungrouped",
                         "bounds": empty,
                         "ui_comp_ids": [],
                         "ui_comp_group_ids": [],
                         "opaque": ""}
            for comp in ungroupeds:
                if is_inside(comp["bounds"], empty):
                    new_group["ui_comp_ids"].append(comp["id"])
                    to_remove.append(comp)
            if len(to_remove) > 0:
                groups.append(new_group)
                current_id += 1
                for remove in to_remove:
                    ungroupeds.remove(remove)
                    comps.append(remove)

#calculates the element smallness metric
def elem_smallness(gui):
    group_infos = []
    ui_comps = gui["ui_comps"]
    ungrouped_comps = gui["ungrouped_comps"]
    groups = gui["ui_comp_groups"]
    measured_comps = []
    for group in groups:
        if group["id"] != -1:
            widths = []
            heights = []
            group_bounds = group["bounds"]
            group_width = abs(group_bounds[0] - group_bounds[2])
            group_height = abs(group_bounds[1] - group_bounds[3])
            group_area = group_width*group_height
            comp_ids = group["ui_comp_ids"]
            for id in comp_ids:
                elem = find_elem(ui_comps, id, groups)
                bounds = elem["bounds"]
                width = abs(bounds[0] - bounds[2])
                height = abs(bounds[1] - bounds[3])
                if not (group_width == width and group_height == height):
                    widths.append(width)
                    heights.append(height)
                measured_comps.append(id)
            mean_width = np.mean(np.array(widths))
            mean_height = np.mean(np.array(heights))
            group_infos.append({"id": group["id"], "area": group_area, "mean_height": mean_height, "mean_width": mean_width})
    for comp in ungrouped_comps:
        if comp["id"] not in measured_comps:
            bounds = comp["bounds"]
            width = abs(bounds[0] - bounds[2])
            height = abs(bounds[1] - bounds[3])
            area = width*height
            measured_comps.append(comp["id"])
            group_infos.append({"id": comp["id"], "area": area, "mean_height": height, "mean_width": width})
    width_strich = 0
    height_strich = 0
    area_strich = 0
    for group in group_infos:
        if not np.isnan(group["mean_width"]) and not np.isnan(group["mean_height"]):
            area_strich += group["area"]
            width_strich += group["area"] * group["mean_width"]
            height_strich += group["area"] * group["mean_height"]
    if area_strich == 0:
        area_strich = MAX_X*MAX_Y
    width_strich = 1/area_strich*width_strich
    height_strich = 1/area_strich*height_strich
    if width_strich != 0 and height_strich != 0:
        smallness = ((1 - width_strich/MAX_X) + (1 - height_strich/MAX_Y))/2
    else:
        smallness = 0
    return smallness

#finds the right and bottom neighbors of a component
def find_neighbors(comp, comps):
    rights = [{"id": "", "bounds": "", "dist": 2000}]
    bots = [{"id": "", "bounds": "", "dist": 2000}]
    bounds = comp["bounds"]
    for other_comp in comps:
        if other_comp != comp:
            bounds2 = other_comp["bounds"]
            if lines_up_hor(bounds, bounds2):
                dist = bounds2[2] - bounds[2]
                if dist >= 0 or rectangles_overlap(bounds, bounds2):
                    if dist < rights[0]["dist"]:
                        rights = [{"id": "", "bounds": "", "dist": 2000}]
                        rights[0]["id"] = other_comp["id"]
                        rights[0]["bounds"] = other_comp["bounds"]
                        rights[0]["dist"] = dist
                    elif dist == rights[0]["dist"]:
                        new_right = {"id": other_comp["id"], "bounds": other_comp["bounds"], "dist": dist}
                        rights.append(new_right)

            if lines_up_vert(bounds, bounds2):
                dist = bounds2[3] - bounds[3]
                if dist >= 0 or rectangles_overlap(bounds, bounds2):
                    if dist < bots[0]["dist"]:
                        bots = [{"id": "", "bounds": "", "dist": 2000}]
                        bots[0]["id"] = other_comp["id"]
                        bots[0]["bounds"] = other_comp["bounds"]
                        bots[0]["dist"] = dist
                    elif dist == bots[0]["dist"]:
                        new_bot = {"id": other_comp["id"], "bounds": other_comp["bounds"], "dist": dist}
                        bots.append(new_bot)

    return rights, bots

#calculates the alignment metric
def alignment(gui):
    group_infos = []
    ui_comps = gui["ui_comps"]
    groups = gui["ui_comp_groups"]
    for group in groups:
        if len(group["ui_comp_group_ids"]) == 0:
            hor_alignments = 0
            vert_alignments = 0
            cent_alignments = 0
            poss_alignments = 0
            group_bounds = group["bounds"]
            group_width = abs(group_bounds[0] - group_bounds[2])
            group_height = abs(group_bounds[1] - group_bounds[3])
            group_area = group_width * group_height
            comp_ids = group["ui_comp_ids"]
            grp_comps = []
            for id in comp_ids:
                grp_comps.append(find_elem(ui_comps, id))
            grp_comps = list(sorted(grp_comps, key=lambda x: (x["bounds"][0], x["bounds"][1])))
            for comp in grp_comps:
                rights, bots = find_neighbors(comp, grp_comps)
                for right in rights:
                    if right["id"] != "":
                        poss_alignments += 2
                        if right["bounds"][1] == comp["bounds"][1] or right["bounds"][3] == comp["bounds"][3]:
                            vert_alignments += 1
                        if np.round((right["bounds"][1] + right["bounds"][3]) / 2) - np.round(
                                (comp["bounds"][1] + comp["bounds"][3]) / 2) <= 2:
                            cent_alignments += 1
                for bot in bots:
                    if bot["id"] != "":
                        poss_alignments += 2
                        if bot["bounds"][0] == comp["bounds"][0] or bot["bounds"][2] == comp["bounds"][2]:
                            hor_alignments += 1
                        if np.round((bot["bounds"][0] + bot["bounds"][2]) / 2) - np.round(
                                (comp["bounds"][0] + comp["bounds"][2]) / 2) <= 2:
                            cent_alignments += 1

            group_infos.append({"id": group["id"], "area": group_area, "hor_alignments": hor_alignments,
                                "vert_alignments": vert_alignments,
                                "cent_alignments": cent_alignments, "poss_alignments": poss_alignments})
    hor_alignments_strich = 0
    vert_alignments_strich = 0
    cent_alignments_strich = 0
    area_strich = 0
    total_poss_alignments = 0
    for group in group_infos:
        if group["poss_alignments"] != 0 and group["area"] != 0:
            area_strich += group["area"]
            total_poss_alignments += group["poss_alignments"]
            hor_alignments_strich += (group["area"] * (group["hor_alignments"] / group["poss_alignments"]))
            vert_alignments_strich += (group["area"] * (group["vert_alignments"] / group["poss_alignments"]))
            cent_alignments_strich += (group["area"] * (group["cent_alignments"] / group["poss_alignments"]))
    if area_strich == 0:
        area_strich = MAX_X * MAX_X
    hor_alignments_strich = 1 / area_strich * hor_alignments_strich
    vert_alignments_strich = 1 / area_strich * vert_alignments_strich
    cent_alignments_strich = 1 / area_strich * cent_alignments_strich
    if total_poss_alignments != 0:
        M = 1 - (hor_alignments_strich + vert_alignments_strich + cent_alignments_strich)
    else:
        M = 0
    return M

#calculates the density metric
def density(gui):
    standard_total_area = MAX_X*MAX_Y
    areas = 0
    total_area = 0
    ui_comps = gui["ui_comps"]
    ungrouped_comps = gui["ungrouped_comps"]
    groups = gui["ui_comp_groups"]
    for group in groups:
        group_bounds = group["bounds"]
        group_width = abs(group_bounds[0] - group_bounds[2])
        group_height = abs(group_bounds[1] - group_bounds[3])
        group_area = group_width*group_height
        total_area += group_area
    for u_comp in ungrouped_comps:
        u_comp_bounds = u_comp["bounds"]
        u_comp_width = abs(u_comp_bounds[0] - u_comp_bounds[2])
        u_comp_height = abs(u_comp_bounds[1] - u_comp_bounds[3])
        u_comp_area = u_comp_width*u_comp_height
        areas += u_comp_area
        total_area += u_comp_area
    for comp in ui_comps:
        comp_bounds = comp["bounds"]
        comp_width = abs(comp_bounds[0] - comp_bounds[2])
        comp_height = abs(comp_bounds[1] - comp_bounds[3])
        comp_area = comp_width*comp_height
        areas += comp_area
    if total_area < standard_total_area:
        total_area = standard_total_area
    D = 1/total_area*areas
    return D

#checks if two components line up vertically
def lines_up_vert(bounds1, bounds2):
    if bounds1[0] < bounds2[2] and bounds1[2] > bounds2[0]:
        return True
    return False

#checks if two components line up horizontally
def lines_up_hor(bounds1, bounds2):
    if bounds1[1] < bounds2[3] and bounds1[3] > bounds2[1]:
        return True
    return False

#calculates the imbalance metric
def imbalance(gui):
    ui_comps = gui["ui_comps"]
    groups = gui["ui_comp_groups"]
    group_infos = []
    for group in groups:
        if len(group["ui_comp_ids"]) < 1:
            continue
        group_bounds = group["bounds"]
        group_width = abs(group_bounds[0] - group_bounds[2])
        group_height = abs(group_bounds[1] - group_bounds[3])
        group_area = group_width * group_height
        sub_bounds = [(group["id"], group_bounds)]
        comp_ids = group["ui_comp_ids"]
        for id in comp_ids:
            elem = find_elem(ui_comps, id, groups)
            bounds = elem["bounds"]
            sub_bounds.append((id, bounds))
        sorted_bounds = sorted(sub_bounds, key=lambda x: x[1][0])
        hor_margins = []
        vert_margins = []
        for id, bounds in sorted_bounds:
            if id == group["id"]:
                continue
            else:
                nearest_left = bounds[0] - sorted(sub_bounds, key=lambda x: bounds[0] - x[1][2] if \
                    lines_up_hor(bounds, x[1]) and bounds[0] >= x[1][2] else 3000)[0][1][2]
                if nearest_left < 0:
                    nearest_left = bounds[0] - \
                                   sorted(sub_bounds, key=lambda x: bounds[0] - x[1][0] if \
                                       lines_up_hor(bounds, x[1]) and bounds[0] >= x[1][0] and x[0] != id else 3000)[0][
                                       1][0]

                nearest_right = sorted(sub_bounds, key=lambda x: x[1][0] - bounds[2] if \
                    lines_up_hor(bounds, x[1]) and x[1][0] >= bounds[2] else 3000)[0][1][0] - bounds[2]
                if nearest_right < 0:
                    nearest_right = sorted(sub_bounds, key=lambda x: x[1][2] - bounds[2] if \
                        lines_up_hor(bounds, x[1]) and x[1][2] >= bounds[2] and x[0] != id else 3000)[0][1][2] - \
                                    bounds[2]

                nearest_top = bounds[1] - sorted(sub_bounds, key=lambda x: bounds[1] - x[1][3] if \
                    lines_up_vert(bounds, x[1]) and bounds[1] >= x[1][3] else 3000)[0][1][3]
                if nearest_top < 0:
                    nearest_top = bounds[1] - \
                                  sorted(sub_bounds, key=lambda x: bounds[1] - x[1][1] if \
                                      lines_up_vert(bounds, x[1]) and bounds[1] >= x[1][1] and x[0] != id else 3000)[0][
                                      1][1]

                nearest_bot = sorted(sub_bounds, key=lambda x: x[1][1] - bounds[3] if \
                    lines_up_vert(bounds, x[1]) and x[1][1] >= bounds[3] else 3000)[0][1][1] - bounds[3]
                if nearest_bot < 0:
                    nearest_bot = sorted(sub_bounds, key=lambda x: x[1][3] - bounds[3] if \
                        lines_up_vert(bounds, x[1]) and x[1][3] >= bounds[3] and x[0] != id else 3000)[0][1][3] - \
                                  bounds[3]

                hor_margins.append(nearest_left)
                hor_margins.append(nearest_right)
                vert_margins.append(nearest_top)
                vert_margins.append(nearest_bot)

        hor_margins = np.array(hor_margins)
        vert_margins = np.array(vert_margins)
        max_hor_marg = np.max(hor_margins)
        max_vert_marg = np.max(vert_margins)
        balh = 0
        if max_hor_marg != 0:
            i = 0
            total_hor_margs = 0
            while i + 1 < len(hor_margins):
                total_hor_margs += hor_margins[i] + hor_margins[i + 1]
                i += 2
            avg_hor_marg = 1 / len(comp_ids) * total_hor_margs
            balh = avg_hor_marg / (2 * max_hor_marg)
        else:
            balh = 1
        balv = 0
        if max_vert_marg != 0:
            i = 0
            total_vert_margs = 0
            while i + 1 < len(vert_margins):
                total_vert_margs += vert_margins[i] + vert_margins[i + 1]
                i += 2
            avg_vert_marg = 1 / len(comp_ids) * total_vert_margs
            balv = avg_vert_marg / (2 * max_vert_marg)
        else:
            balv = 1
        group_infos.append({"id": group["id"], "area": group_area, "balh": balh, "balv": balv})

    if len(group_infos) > 0:
        balh_strich = 0
        balv_strich = 0
        area_strich = 0
        for group in group_infos:
            if group["area"] != 0:
                area_strich += group["area"]
                balh_strich += group["area"] * group["balh"]
                balv_strich += group["area"] * group["balv"]
        if area_strich == 0:
            area_strich = MAX_X * MAX_Y
        balh_strich = 1 / area_strich * balh_strich
        balv_strich = 1 / area_strich * balv_strich
        B = 1 - (balh_strich + balv_strich) / 2
    else:
        B = 0
    return B

#counts the amount of components
def count_elems(gui):
    count = len(gui["ungrouped_comps"])
    for group in gui["ui_comp_groups"]:
        count += len(group["ui_comp_ids"])
    return count

#draws bounding boxes and ids onto an image
def draw_on_image(gui, img, empty_spaces=[]):
    comps = gui["ui_comps"]
    groups = gui["ui_comp_groups"]
    ungroupeds = gui["ungrouped_comps"]
    draw = ImageDraw.Draw(img)
    top_offset = 8
    left_offset = 8
    for comp in comps:
        bounds = comp["bounds"]
        x0 = bounds[0] + left_offset
        y0 = bounds[1] + top_offset
        x1 = bounds[2] + top_offset
        y1 = bounds[3] + top_offset
        draw.rectangle([x0, y0, x1, y1], outline="#ff000055", width=4)
        draw.text([x0, y0], str(comp["id"]), font_size=20, fill="#ff000055")

    for group in groups:
        bounds = group["bounds"]
        x0 = bounds[0] + top_offset
        y0 = bounds[1] + top_offset
        x1 = bounds[2] + top_offset
        y1 = bounds[3] + top_offset
        draw.rectangle([x0, y0, x1, y1], outline="#00ff0055", width=4)
        draw.text([x0, y0], str(group["id"]), font_size=20, fill="#00ff0055")

    for comp in ungroupeds:
        bounds = comp["bounds"]
        x0 = bounds[0] + left_offset
        y0 = bounds[1] + top_offset
        x1 = bounds[2] + left_offset
        y1 = bounds[3] + top_offset
        draw.rectangle([x0, y0, x1, y1], outline="#40E0D055", width=4)
        draw.text([x0, y0], str(comp["id"]), font_size=20, fill="#40E0D055")

    for bounds in empty_spaces:
        x0 = bounds[0] + left_offset
        y0 = bounds[1] + top_offset
        x1 = bounds[2] + left_offset
        y1 = bounds[3] + top_offset
        draw.rectangle([x0, y0, x1, y1], outline="#00000000", width=4)

#calculates all metrics, creates textual and visual report
def calc_metrics_and_show(location, filename, destination):
    report = ""
    comps, groups = extract_components_for_metrics(location, filename)
    gui = convert(comps, groups)
    check_ungroupeds_inside(gui)
    group_ungrouped_comps(gui)
    row = {}

    row["smallness"] = elem_smallness(gui)
    row["misalignment"] = alignment(gui)
    row["imbalance"] = imbalance(gui)
    row["density"] = density(gui)
    row["elems"] = count_elems(gui)
    row["groups"] = len(gui["ui_comp_groups"])
    row["ungroupeds"] = len(gui["ungrouped_comps"])

    titles = {"smallness": "Element Smallness", "misalignment": "Misalignment", "imbalance": "Imbalance",
              "density": "Density", "elems": "Number of elements",
              "groups": "Number of groups", "ungroupeds": "Number of ungrouped elements"}

    tips = {"smallness": "To reduce this value, consider increasing the size of some of the smaller elements in your UI.\n",
            "misalignment": "To reduce this value, check how many of the elements in your UI are aligned along their edges or centers.\n",
            "imbalance": "To reduce this value, consider spreading out the elements in your UI a bit more evenly.\n",
            "density": "To reduce this value, consider removing some elements from your UI or making some of them smaller.\n"}

    stats = pd.read_csv(sys.path[0] + "../../metrics_enrico_and_figma.csv")

    metrics = list(row.keys())

    fig, axs = plt.subplots(2, 4, figsize=(35, 15))

    for i in range(len(metrics)):
        axs[int(i / 4), i % 4].hist(stats[metrics[i]])

        axs[int(i / 4), i % 4].axvline(row[metrics[i]], color="red")
        axs[int(i/4), i%4].set_title(titles[metrics[i]] + ": " + "{:.2f}".format(row[metrics[i]]))
        if i < 4:
            axs[int(i / 4), i % 4].set_xticks(np.arange(0, 1.2, 0.2))
            mean = np.mean(np.array(stats[metrics[i]]))
            std = np.std(np.array(stats[metrics[i]]))
            axs[int(i / 4), i % 4].axvspan(mean-std, mean+std, color='red', alpha=0.25)
            axs[int(i / 4), i % 4].legend(["Your design", "Standard deviation area", "Distribution"])
            report += titles[metrics[i]] + ": Your design has a value of " + "{:.2f}".format(row[metrics[i]])
            if row[metrics[i]] > mean + std:
                report += ", which is more than one standard deviation higher than the mean value of this metric. "
                report += tips[metrics[i]]
            elif row[metrics[i]] < mean - std:
                report += ", which is more than one standard deviation lower than the mean value of this metric. This is not an issue.\n"
            else:
                report += ", which is inside the standard deviation area for this metric.\n"

    plt.savefig(destination + "/" + filename + "_analyzed.png", bbox_inches='tight')
    plt.close()
    with open(destination + "/" + filename + "_metric_report.txt", "w") as f:
        f.write(report)
        f.close()