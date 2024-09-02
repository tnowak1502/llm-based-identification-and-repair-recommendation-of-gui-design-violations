import sys
sys.path.append("./utils")

import json
import re
from bs4 import BeautifulSoup
import bs4
from cssutils import parseStyle
import copy
from ast import literal_eval
import random

MAX_X = 412
MAX_Y = 892

comp_classes = json.load(open(sys.path[0] + "/data/comp_classes.json"))

def convert_color(color, alpha=None):
    red = int(color["r"] * 255)
    green = int(color["g"] * 255)
    blue = int(color["b"] * 255)
    if alpha is None:
        alpha = 255
    else:
        alpha *= 255
    if color.get("a") is not None:
        alpha = color.get("a") * 255
    alpha = int(alpha)

    red_hex = hex(red)
    green_hex = hex(green)
    blue_hex = hex(blue)
    alpha_hex = hex(alpha)

    red_hex_string = str(red_hex)[2:]
    if len(red_hex_string) == 1:
        red_hex_string = "0" + red_hex_string
    green_hex_string = str(green_hex)[2:]
    if len(green_hex_string) == 1:
        green_hex_string = "0" + green_hex_string
    blue_hex_string = str(blue_hex)[2:]
    if len(blue_hex_string) == 1:
        blue_hex_string = "0" + blue_hex_string
    alpha_hex_string = str(alpha_hex)[2:]
    if len(alpha_hex_string) == 1:
        alpha_hex_string = "0" + alpha_hex_string

    color_hex = red_hex_string + green_hex_string + blue_hex_string + alpha_hex_string

    return color_hex


def extract_stats(dic, parent_is_group=False, parent_bounds=None):
    stats = {}
    stats["type"] = dic["type"]
    stats["name"] = dic["name"]
    stats["id"] = dic["id"]

    width = dic["width"]
    height = dic["height"]

    if not parent_is_group:
        stats["bounds"] = [dic["x"], dic["y"], dic["x"] + width, dic["y"] + height]
    else:
        stats["bounds"] = [dic["x"] - parent_bounds[0],
                           dic["y"] - parent_bounds[1],
                           dic["x"] - parent_bounds[0] + dic["width"],
                           dic["y"] - parent_bounds[1] + dic["height"]]

    stats["cornerRadius"] = ""
    stats["fill"] = ""
    stats["fillOpacity"] = ""
    stats["opacity"] = ""
    stats["strokeAlign"] = ""
    stats["strokeWeight"] = ""
    stats["strokeTopWeight"] = ""
    stats["strokeBottomWeight"] = ""
    stats["strokeLeftWeight"] = ""
    stats["strokeRightWeight"] = ""

    if dic.get("opacity") is not None:
        stats["opacity"] = dic["opacity"]

    # else:
    if dic["type"] == "TEXT":
        stats["font"] = dic["fontName"]["family"]
        stats["fontStyle"] = dic["fontName"]["style"]
        stats["fontSize"] = dic["fontSize"]
        stats["fontSpacing"] = dic["letterSpacing"]["value"]
        stats["cornerRadius"] = ""
        stats["text"] = dic["characters"]
        stats["lineHeight"] = dic["lineHeight"]["value"]
        stats["textAlignVertical"] = dic["textAlignVertical"]
        stats["textAlignHorizontal"] = dic["textAlignHorizontal"]

    else:
        if dic.get("type") == "ELLIPSE" or dic.get("name") == "Monogram":
            stats["cornerRadius"] = 100
        elif dic.get("cornerRadius") is not None:
            stats["cornerRadius"] = dic["cornerRadius"]
            if stats["cornerRadius"] == "MIXED":
                stats["topLeftRadius"] = dic["topLeftRadius"]
                stats["topRightRadius"] = dic["topRightRadius"]
                stats["bottomRightRadius"] = dic["bottomRightRadius"]
                stats["bottomLeftRadius"] = dic["bottomLeftRadius"]

    if dic.get("type") == "VECTOR":
        paths = []
        for path in dic["vectorPaths"]:
            paths.append(path["data"])
        stats["paths"] = paths

    stats["fill"] = ""
    stats["fillOpacity"] = ""
    if dic.get("fills") is not None:
        if dic["fills"] != []:
            if dic["fills"][0]["visible"] and dic["fills"][0]["type"] != "GRADIENT_LINEAR":
                stats["fillOpacity"] = dic["fills"][0]["opacity"]
                if dic["fills"][0]["type"] != "IMAGE":
                    stats["fill"] = convert_color(dic["fills"][0]["color"], dic["fills"][0].get("opacity"))
                elif dic["fills"][0]["type"] == "IMAGE":
                    stats["fill"] = "IMAGE"

    if dic.get("strokes") is not None:
        if dic["strokes"] != []:
            stats["strokeColor"] = convert_color(dic["strokes"][0]["color"], dic["strokes"][0].get("opacity"))
            stats["strokeOpacity"] = dic["strokes"][0]["opacity"]
            stats["strokeAlign"] = dic["strokeAlign"]

            if dic.get("strokeTopWeight") is not None:
                stats["strokeTopWeight"] = dic["strokeTopWeight"]
            if dic.get("strokeBottomWeight") is not None:
                stats["strokeBottomWeight"] = dic["strokeBottomWeight"]
            if dic.get("strokeLeftWeight") is not None:
                stats["strokeLeftWeight"] = dic["strokeLeftWeight"]
            if dic.get("strokeRightWeight") is not None:
                stats["strokeRightWeight"] = dic["strokeRightWeight"]
            if dic.get("strokeWeight") is not None:
                stats["strokeWeight"] = dic["strokeWeight"]

    if dic.get("effects") is not None:
        if dic["effects"] != []:
            stats["shadowColor"] = convert_color(dic["effects"][0]["color"], dic["effects"][0].get("opacity"))
            stats["shadowRadius"] = dic["effects"][0]["radius"]
            stats["shadowOffsetX"] = dic["effects"][0]["offset"]["x"]
            stats["shadowOffsetY"] = dic["effects"][0]["offset"]["y"]

    if dic.get("componentProperties") is not None:
        if dic["componentProperties"].get("Configuration") is not None:
            stats["config"] = dic["componentProperties"]["Configuration"]["value"]
            if dic["componentProperties"].get("# of lines") is not None:
                stats["config"] += " " +  dic["componentProperties"]["# of lines"]["value"]
            if dic["componentProperties"].get("Style") is not None:
                stats["config"] += " " + dic["componentProperties"]["Style"]["value"]
            if dic["componentProperties"].get("Selected") is not None:
                if dic["componentProperties"]["Selected"]["value"] == "true":
                    stats["config"] += " selected"
                else:
                    stats["config"] += " unselected"
        elif dic["componentProperties"].get("Size") is not None:
            stats["config"] = dic["componentProperties"]["Size"]["value"]
        elif dic["componentProperties"].get("Style") is not None:
            stats["config"] = dic["componentProperties"]["Style"]["value"]
        elif dic["componentProperties"].get("Type") is not None:
            stats["config"] = dic["componentProperties"]["Type"]["value"]
        elif dic["componentProperties"].get("Condition") is not None:
            stats["config"] = dic["componentProperties"]["Condition"]["value"]
        elif dic["componentProperties"].get("Selected") is not None:
            if dic["componentProperties"]["Selected"]["value"] == "true":
                stats["config"] = "selected"
            else:
                stats["config"] = "unselected"

    return stats


def is_inside(bounds2, bounds1):
    if bounds2[0] >= bounds1[0]:
        if bounds2[2] <= bounds1[2]:
            if bounds2[1] >= bounds1[1]:
                if bounds2[3] <= bounds1[3]:
                    return True
    return False


def transform_abs_bounds(absBounds, top_bounds):
    ret = []
    absBoundsCopy = {}
    absBoundsCopy["x"] = absBounds["x"]
    absBoundsCopy["y"] = absBounds["y"]
    absBoundsCopy["width"] = absBounds["width"]
    absBoundsCopy["height"] = absBounds["height"]

    if top_bounds["x"] < 0:
        absBoundsCopy["x"] += -top_bounds["x"]
    if top_bounds["y"] < 0:
        absBoundsCopy["y"] += -top_bounds["y"]
    ret.append(absBoundsCopy["x"])
    ret.append(absBoundsCopy["y"])
    ret.append(absBoundsCopy["x"] + absBoundsCopy["width"])
    ret.append(absBoundsCopy["y"] + absBoundsCopy["height"])
    return ret


def reduce_json(dic, new_dic, top_bounds=None):
    new_dic["children"] = []
    if dic["name"].replace(" ", "-") in comp_classes["card"]:
        dic["children"] = list(sorted(dic["children"], key=lambda x: x["name"].lower() == "background", reverse=True))
    for child in dic["children"]:
        if child["visible"]:
            if child.get("type") == "TEXT":
                if child["characters"] == "":
                    continue
            if dic["type"] == "GROUP":
                stats = extract_stats(child, parent_is_group=True, parent_bounds=[dic["x"], dic["y"]])
            else:
                stats = extract_stats(child)
            new_child = {"name": child["name"], **stats}
            if child.get("children") is not None:
                reduce_json(child, new_child, top_bounds)
            new_dic["children"].append(new_child)

def parse_divider(child):
    name = child["name"]
    ret = "class = '" + child["name"].replace(" ", "-") + "' id = '" + child["id"] + "' "
    ret += "style='margin: 0px; "

    position = "absolute"
    left = child["bounds"][0]
    width = child["bounds"][2] - child["bounds"][0]
    height = child["bounds"][3] - child["bounds"][1]

    ret += " position: " + position + "; left: " + str(left) + "px; width: " + str(
        width) + "px; height: " + str(height) + "px; "

    ret += "opacity: " + str(child["opacity"]) + "; "
    strokeColor = "#" + child["strokeColor"].upper()
    ret += "color: " + strokeColor + ";'>"
    return ret


def parse_child(child):
    if "divider" in child["name"].lower() and child.get("children") is None:
        return parse_divider(child)
    name = child["name"]
    ret = "class = '" + child["name"].replace(" ", "-") + "' id = '" + child["id"] + "' "

    position = "absolute"
    top = child["bounds"][1]
    left = child["bounds"][0]
    width = child["bounds"][2] - child["bounds"][0]
    height = child["bounds"][3] - child["bounds"][1]

    if child["type"] == "TEXT":
        width += 1

    if child.get("config") is not None:
        ret += "config='" + child.get("config") + "' "

    ret += "style='position: " + position + "; top: " + str(top) + "px; left: " + str(left) + "px; width: " + str(
        width) + "px; height: " + str(height) + "px; "

    if child["type"] == "FRAME" or child["type"] == "INSTANCE":
        if not child["name"].replace(" ", "-") in comp_classes["bottom_sheet"] and \
        not child["name"].replace(" ", "-") in comp_classes["text_field"] and \
        not child["name"].replace(" ", "-") in comp_classes["slider"] and \
        not "Track-and-handle" in child["name"].replace(" ", "-") and \
        not "icon-container" in child["name"].replace(" ", "-"):
            ret += "overflow: hidden; "

    if child["opacity"] != "":
        ret += "opacity: " + str(child["opacity"]) + "; "

    if child["type"] != "TEXT":
        if child["fill"] != "":
            if child["fill"] != "IMAGE":
                fill = "#" + child["fill"].upper()
                ret += "background-color: " + fill + "; "
            else:
                ret += "background-image: url(\"../Code/image_fill.jpg\"); background-size: cover; "

        if child.get("cornerRadius") is not None:
            if child["cornerRadius"] != "":
                if child["cornerRadius"] == "MIXED":
                    topLeftRadius = child["topLeftRadius"]
                    topRightRadius = child["topRightRadius"]
                    bottomRightRadius = child["bottomRightRadius"]
                    bottomLeftRadius = child["bottomLeftRadius"]

                    ret += "border-radius: " + str(topLeftRadius) + "px " + str(topRightRadius) + "px " + str(
                        bottomRightRadius) + "px " + \
                           str(bottomLeftRadius) + "px; "
                else:
                    cornerRadius = child["cornerRadius"]
                    ret += "border-radius: " + str(cornerRadius) + "px; "

        if child.get("strokeColor") is not None:
            strokeColor = "#" + child["strokeColor"].upper()

            if child.get("strokeWeight") is not None:
                if child["strokeTopWeight"] == child["strokeBottomWeight"] == child["strokeLeftWeight"] == child[
                    "strokeRightWeight"]:
                    if child["strokeAlign"] == "INSIDE":
                        ret += "box-shadow: inset 0px 0px 0px " + str(child["strokeTopWeight"]) + "px " + strokeColor[:-2] + "; "
                    else:
                        ret += "border: " + str(child["strokeTopWeight"]) + "px " + strokeColor + " solid; "
                else:
                    if child["strokeTopWeight"] != 0:
                        ret += "border-top: " + str(child["strokeTopWeight"]) + "px " + strokeColor + " solid; "
                    if child["strokeBottomWeight"] != 0:
                        ret += "border-bottom: " + str(child["strokeBottomWeight"]) + "px " + strokeColor + " solid; "
                    if child["strokeLeftWeight"] != 0:
                        ret += "border-left: " + str(child["strokeLeftWeight"]) + "px " + strokeColor + " solid; "
                    if child["strokeRightWeight"] != 0:
                        ret += "border-right: " + str(child["strokeRightWeight"]) + "px " + strokeColor + " solid; "

        if child.get("shadowColor") is not None:
            shadowColor = "#" + child["shadowColor"].upper()
            shadowOffsetX = child["shadowOffsetX"]
            shadowOffsetY = child["shadowOffsetY"]
            shadowRadius = child["shadowRadius"]

            ret += "filter: drop-shadow(" + str(shadowOffsetX) + "px " + str(shadowOffsetY) + "px " + str(
                shadowRadius) + "px " + shadowColor + "); "

        ret += "'>"

    else:
        font = child["font"]
        fontStyle = child["fontStyle"]
        fontSize = child["fontSize"]
        fontSpacing = child["fontSpacing"]
        lineHeight = child["lineHeight"]
        textAlignHorizontal = child["textAlignHorizontal"]
        textAlignVertical = child["textAlignVertical"]
        characters = child["text"]
        fontWeight = "400"
        if fontStyle == "Bold":
            fontWeight = "700"
        elif fontStyle == "Medium":
            fontWeight = "500"
        fill = child["fill"].upper()
        ret += "display: flex; white-space: pre-line; "
        ret += "font-family: " + font + "; font-size: " + str(fontSize) + "px; font-weight: " + fontWeight + \
               "; letter-spacing: " + str(fontSpacing) + "px; color: " + "#" + fill + "; line-height: " + str(
            lineHeight) + "px; " + \
               "justify-content: " + textAlignHorizontal.lower() + "; align-items: " + textAlignVertical.lower() + ";'>" + characters

    return ret


def parse_vector(child, layer):
    name = child["name"]
    position = "absolute"
    top = child["bounds"][1]
    left = child["bounds"][0]
    width = child["bounds"][2] - child["bounds"][0]
    height = child["bounds"][3] - child["bounds"][1]
    fill = "#" + child["fill"].upper()
    paths = child["paths"]
    wrap_start = "<div class='" + name.replace(" ", "-") + "' id='" + child[
        "id"] + "' style='position: " + position + "; top: " + str(top) + "px; left: " + str(
        left) + "px; width: " + str(
        width) + "px; height: " + str(height) + "px;'>"
    svg_start = "<svg height = '" + str(height) + "px' width = '" + str(
        width) + "px' xmlns = 'http://www.w3.org/2000/svg'>"
    vectors = []
    for path in paths:
        vectors.append("<path d='" + path + "' style='fill: " + fill + ";'/>")

    ret = wrap_start + "\n"
    for i in range(layer + 1):
        ret += "  "
    ret += svg_start + "\n"
    for vector in vectors:
        for i in range(layer + 2):
            ret += "  "
        ret += vector + "\n"
    for i in range(layer + 1):
        ret += "  "
    ret += "</svg>"

    return ret

def json_to_html(dic, filename):
    split = filename.split("\\")
    filename = split[len(split)-1]
    html = [
        "<html lang='de'>\n  <head><title>" + filename + "</title></head>\n  <body>"]  # \n    <div class="AndroidSmall2' style='width: 360px; height: 640px; position: relative; background: white'>"]

    def append_child(child, layer, html):
        html.append("\n")
        for i in range(layer):
            html.append("  ")
        if child["type"] == "VECTOR":
            html.append(parse_vector(child, layer))
        else:
            if "divider" in child["name"].lower():
                if child.get("children") is not None:
                    html.append("<div ")
                else:
                    html.append("<hr ")
            else:
                html.append("<div ")
            html.append(parse_child(child))
        if child.get("children") is not None:
            for sub_child in child["children"]:
                append_child(sub_child, layer + 1, html)
        html.append("\n")
        for i in range(layer):
            html += "  "
        if "divider" in child["name"].lower():
            html.append("")
            if child.get("children") is not None:
                html.append("</div>")
        else:
            html.append("</div>")

    for child in dic["children"]:
        append_child(child, 2, html)
    # html.append("\n    </div>\n  </body>\n</html>")
    html.append("\n  </body>\n</html>")

    ret = ""
    for substring in html:
        ret += substring
    return ret


def extract_comp(soup, comp_type, comp_classes):
    classes = comp_classes[comp_type]
    comps = []
    for class_ in classes:
        comps.extend(soup.find_all("div", attrs={"class": class_}))
        comps.extend(soup.find_all("button", attrs={"class": class_}))
    return comps


def extract_comp_containers(soup, comp_type, containers, comp_classes):
    classes = comp_classes[comp_type]
    for child in soup.children:
        if type(child) == bs4.element.Tag:
            if (class_ := child.get("class")) is not None:
                if str(class_[0]) in classes:
                    containers.append(soup)
                    continue
            extract_comp_containers(child, comp_type, containers, comp_classes)


def extract_frames(soup, frames):
    for child in soup.children:
        if type(child) == bs4.element.Tag:
            if (class_ := str(child.get("class"))) is not None:
                if "frame" in class_.lower():
                    frames.append(child)
                    continue
            extract_frames(child, frames)


def create_html_file(data_path, file, write=True):
    try:
        j = json.load(open(data_path + file + ".json", "r"))
    except:
        j = json.load(open(data_path + file + ".json", "r", encoding="utf-8"))
    stats = extract_stats(j)
    top_bounds = j["absoluteRenderBounds"]
    new_j = {"name": j["name"], **stats}
    reduce_json(j, new_j, top_bounds)
    parsed = json_to_html(new_j, file)
    if write:
        html_file = open(data_path + file + ".html", "w")
        html_file.write(parsed)
        html_file.close()
    return parsed


def get_soup(data_path, file):
    try:
        html_file = open(data_path + file + ".html", "r", encoding="utf-8")
        str = html_file.read().replace("’", "'")
    except:
        html_file = open(data_path + file + ".html", "r")
        str = html_file.read().replace("’", "'")
    soup = BeautifulSoup(str, 'lxml')
    return soup

def extract_answers(response):
    json_start = response.find("{")
    json_end = response.rfind("}")
    json_string = response[json_start:json_end+1]
    dic = literal_eval(json_string)
    return dic
