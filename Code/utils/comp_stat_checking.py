import sys
sys.path.append("./utils")

from json_to_html_utils import *
import re
import logging
import cssutils
from html2image import Html2Image
from bs4.element import Tag
cssutils.log.setLevel(logging.CRITICAL)

DEVICE_WIDTH = 412
DEVICE_HEIGHT = 892
comp_stats = json.load(open(sys.path[0] + "/data/comp_stats.json"))

def full_measurement_check(location, filename, destination, comp_classes, screenshot=False):
    soup = get_soup(location, filename)
    report = ""
    for comp_type in comp_classes.keys():
        if len(extract_comp(soup, comp_type, comp_classes)) > 0:
            comps = extract_comp(soup, comp_type, comp_classes)
            report += check_comp_issues(comp_type, comps, soup)
    print(report)
    with open(destination + "/" + filename + "_measurement_report.txt", "w") as f:
        f.write(report)
        f.close()
    with open(destination + "/" + filename + "_marked.html", "w", encoding="utf-8") as f:
        f.write(str(soup))
        f.close()
    if screenshot:
        for div in soup.find_all("div"):
            new_style = div["style"]
            if new_style.find("background-image: url(\"../Code/image_fill.jpg\");") > 0:
                div["style"] = new_style.replace(
                    "background-image: url(\"../Code/image_fill.jpg\");",
                    "background-color: #D9D9D9 !important;")
        hti = Html2Image(size=(428, 1008), output_path=destination + "/")
        hti.screenshot(html_str=str(soup),
                       save_as=filename + "_marked.png")

#calls a checking method based on the configuration of each component
def check_comp_issues(comp_type, comps, soup):
    ret = ""
    for comp in comps:
        if comp.get("config") is not None:
            if comp_type == "top_app_bar":
                if comp["config"] == "small-centered":
                    ret += check_top_app_bar_center_aligned([comp], comp_stats, soup)
                elif comp["config"] == "small":
                    ret += check_top_app_bar_small([comp], comp_stats, soup)
                elif comp["config"] == "medium":
                    ret += check_top_app_bar_medium([comp], comp_stats, soup)
                elif comp["config"] == "large":
                    ret += check_top_app_bar_large([comp], comp_stats, soup)
            elif comp_type == "badge":
                if comp["config"] == "Small":
                    ret += check_badge([comp], comp_stats, soup)
                elif comp["config"] == "Large":
                    ret += check_badge_large([comp], comp_stats, soup)
            elif comp_type == "common_button":
                if comp["config"] == "Outlined":
                    ret += check_button_outlined([comp], comp_stats, soup)
                else:
                    ret += check_button_elevated_tonal_filled_text([comp], comp_stats, soup)
            elif comp_type == "icon_button":
                if comp["config"] == "Outlined":
                    ret += check_icon_button_outlined([comp], comp_stats, soup)
                else:
                    ret += check_icon_button([comp], comp_stats, soup)
            elif comp_type == "carousel":
                if comp["config"] == "Uncontained":
                    ret += check_carousel_uncontained([comp], comp_stats, soup)
                else:
                    ret += check_carousel_multi_browse_hero([comp], comp_stats, soup)
            elif comp_type == "checkbox":
                if comp["config"] == "Selected":
                    ret += check_checkbox([comp], comp_stats, soup)
                else:
                    ret += check_checkbox_unselected([comp], comp_stats, soup)
            elif comp_type == "snackbar":
                if "longer action" in comp["config"]:
                    ret += check_snackbar_longer_action([comp], comp_stats, soup)
                elif "One line" in comp["config"]:
                    ret += check_snackbar_one_line([comp], comp_stats, soup)
                else:
                    ret += check_snackbar_two_line([comp], comp_stats, soup)
            elif comp_type == "switch":
                if comp["config"] == "selected":
                    ret += check_switch_selected([comp], comp_stats, soup)
                else:
                    ret += check_switch_unselected([comp], comp_stats, soup)
            elif comp_type == "tab":
                if comp["config"] == "Primary":
                    ret += check_tabs_primary([comp], comp_stats, soup)
                else:
                    ret += check_tabs_secondary([comp], comp_stats, soup)
            elif comp_type == "text_field":
                if comp["config"] == "Filled":
                    ret += check_text_field_filled([comp], comp_stats, soup)
                else:
                    ret += check_text_field_outlined([comp], comp_stats, soup)
        if comp_type == "bottom_app_bar":
            ret += check_bottom_app_bar([comp], comp_stats, soup)
        elif comp_type == "fab":
            class_ = comp["class"][0]
            if class_ == "FAB" or class_ == "FAB-dark":
                ret += check_FAB([comp], comp_stats, soup)
            elif class_ == "Small-FAB" or class_ == "Small-FAB-dark":
                ret += check_FAB_small([comp], comp_stats, soup)
            elif class_ == "Large-FAB" or class_ == "Large-FAB-dark":
                ret += check_FAB_large([comp], comp_stats, soup)
            elif class_ == "Extended-FAB" or class_ == "Extended-FAB-dark":
                ret += check_FAB_extended([comp], comp_stats, soup)
        elif comp_type == "chip":
            class_ = comp["class"][0]
            if class_ == "Input-chip" or class_ == "Input-chip-dark":
                ret += check_chip_input([comp], comp_stats, soup)
            else:
                ret += check_chip_filter_assistive_suggestion([comp], comp_stats, soup)
        elif comp_type == "segmented_button":
            ret += check_segmented_button([comp], comp_stats, soup)
        elif comp_type == "card":
            ret += check_card([comp], comp_stats, soup)
        elif comp_type == "dialog":
            ret += check_dialog([comp], comp_stats, soup)
        elif comp_type == "divider":
            ret += check_divider([comp], comp_stats, soup)
        elif comp_type == "list":
            ret += check_list([comp], comp_stats, soup)
        elif comp_type == "menu":
            ret += check_menu([comp], comp_stats, soup)
        elif comp_type == "navigation_bar":
            ret += check_navigation_bar([comp], comp_stats, soup)
        elif comp_type == "navigation_drawer":
            ret += check_navigation_drawer([comp], comp_stats, soup)
        elif comp_type == "radio_button":
            ret += check_radio_button([comp], comp_stats, soup)
        elif comp_type == "search":
            class_ = comp["class"][0]
            if class_ == "Search-bar" or class_ == "Search-bar-dark":
                ret += check_search_bar([comp], comp_stats, soup)
            elif class_ == "Search-view-full-screen" or class_ == "Search-view-full-screen-dark":
                ret += check_search_view_full_screen([comp], comp_stats, soup)
            else:
                ret += check_search_view_docked([comp], comp_stats, soup)
        elif comp_type == "bottom_sheet":
            ret += check_bottom_sheet([comp], comp_stats, soup)
    return ret


def check_width(style, width):
    if int(float(style["width"].replace("px", ""))) == int(width):
        return True
    return False


def check_height(style, height):
    if int(float(style["height"].replace("px", ""))) == int(height):
        return True
    return False


def check_corner_radius(style, corner_radius):
    if int(float(style["border-radius"].replace("px", ""))) == corner_radius:
        return True
    return False


def check_top_padding(comp, padding):
    for child in comp.children:
        if type(child) == Tag:
            style = parseStyle(child["style"])
            top = float(style["top"].replace("px", ""))
            if round(top) < padding:
                return False
    return True


def check_bottom_padding(comp, padding):
    comp_height = int(parseStyle(comp["style"])["height"].replace("px", ""))
    for child in comp.children:
        if type(child) == Tag:
            style = parseStyle(child["style"])
            bottom = comp_height - (float(style["top"].replace("px", "")) + float(style["height"].replace("px", "")))
            if round(bottom) < padding:
                return False
    return True


def check_left_padding(comp, padding):
    for child in comp.children:
        if type(child) == Tag:
            style = parseStyle(child["style"])
            left = float(style["left"].replace("px", ""))
            if round(left) < padding:
                return False
    return True


def check_right_padding(comp, padding):
    comp_width = float(parseStyle(comp["style"])["width"].replace("px", ""))
    for child in comp.children:
        if type(child) == Tag:
            style = parseStyle(child["style"])
            right = comp_width - (float(style["left"].replace("px", "")) + float(style["width"].replace("px", "")))
            if round(right) < padding:
                return False
    return True


def check_padding_between(comp, padding):
    filtered_children = []
    for child in comp.children:
        if type(child) == Tag:
            filtered_children.append(child)
    sorted_children = sorted(filtered_children, key=lambda x: float(parseStyle(x["style"])["left"].replace("px", "")))
    for i in range(len(sorted_children) - 1):
        child = sorted_children[i]
        style = parseStyle(child["style"])
        right = float(style["left"].replace("px", "")) + float(style["width"].replace("px", ""))
        other_child = sorted_children[i + 1]
        other_style = parseStyle(other_child["style"])
        if round(float(other_style["left"].replace("px", "")) - right) != padding:
            return False
    return True


def check_padding_between_vert(comp, padding):
    filtered_children = []
    for child in comp.children:
        if type(child) == Tag:
            filtered_children.append(child)
    sorted_children = sorted(filtered_children, key=lambda x: float(parseStyle(x["style"])["top"].replace("px", "")))
    for i in range(len(sorted_children) - 1):
        child = sorted_children[i]
        style = parseStyle(child["style"])
        bottom = float(style["top"].replace("px", "")) + float(style["height"].replace("px", ""))
        other_child = sorted_children[i + 1]
        other_style = parseStyle(other_child["style"])
        if round(float(other_style["top"].replace("px", "")) - bottom) != padding:
            return False
    return True


def check_icon_size(comp, size):
    for child in comp.children:
        if type(child) == Tag:
            state_layer = child.find("div", attrs={"class": "state-layer"})
            icon_height = int(parseStyle(state_layer.contents[1]["style"])["height"].replace("px", ""))
            icon_width = int(parseStyle(state_layer.contents[1]["style"])["width"].replace("px", ""))
            if icon_height != size or icon_width != size:
                return False
    return True


def check_icon_state_layer_size(comp, size):
    for child in comp.children:
        if type(child) == Tag:
            state_layer = child.find("div", attrs={"class": "state-layer"})
            height = int(parseStyle(state_layer["style"])["height"].replace("px", ""))
            width = int(parseStyle(state_layer["style"])["width"].replace("px", ""))
            if height != size or width != size:
                return False
    return True


def check_icon_target_size(comp, size):
    for child in comp.children:
        if type(child) == Tag:
            height = int(parseStyle(child["style"])["height"].replace("px", ""))
            width = int(parseStyle(child["style"])["width"].replace("px", ""))
            if height != size or width != size:
                return False
    return True


def check_text_size(comp, size):
    style = parseStyle(comp["style"])
    text_size = int(style["font-size"].replace("px", ""))
    if text_size != size:
        return False
    return True


def check_text_weight(comp, weight):
    style = parseStyle(comp["style"])
    text_weight = int(style["font-weight"].replace("px", ""))
    if text_weight != weight:
        return False
    return True


def check_badge_pos(comp, pos_top, pos_left):
    style = parseStyle(comp["style"])
    top = int(style["top"].replace("px", ""))
    left = int(style["left"].replace("px", ""))
    if top != pos_top or left != pos_left:
        return False
    return True


def check_outline(style, outline):
    try:
        comp_outline_str = style["border"]
        px_loc = comp_outline_str.find("px")
        comp_outline = int(comp_outline_str[:px_loc])
        if comp_outline != outline:
            return False
        return True
    except:
        comp_outline_str = style["box-shadow"]
        vals = comp_outline_str.split(" ")
        comp_outline = 0
        for val in vals:
            if "px" in val:
                comp_outline = int(val.replace("px", ""))
        if outline != comp_outline:
            return False
        return True

def check_centered_hor(comp):
    comp_width = float(parseStyle(comp["style"])["width"].replace("px", ""))
    for child in comp.children:
        if type(child) == Tag:
            style = parseStyle(child["style"])
            left = float(style["left"].replace("px", ""))
            right = comp_width - (float(style["left"].replace("px", "")) + float(style["width"].replace("px", "")))
            if round(left) != round(right):
                return False
    return True

def check_centered_vert(comp):
    comp_height = float(parseStyle(comp["style"])["height"].replace("px", ""))
    for child in comp.children:
        if type(child) == Tag:
            style = parseStyle(child["style"])
            top = float(style["top"].replace("px", ""))
            bot = comp_height - (float(style["top"].replace("px", "")) + float(style["height"].replace("px", "")))
            if round(top) != round(bot):
                return False
    return True

def check_text_align(comp, align):
    style = parseStyle(comp["style"])
    if style["justify-content"] != align:
        return False
    return True

def check_bottom_app_bar(comps, comp_stats, soup):
    comp_name = "bottom app bar"
    stats = comp_stats["bottom_app_bar"]
    ret = ""
    for comp in comps:
        id = comp["id"]
        comp_str = "the " + comp_name + " with id " + id

        style = parseStyle(comp["style"])
        icons = comp.find_all("div", attrs={"class": "leading-icon"})[0]

        width = stats["width"]
        if width == "device":
            width = DEVICE_WIDTH
        if not check_width(style, width):
            ret += comp_str.capitalize().capitalize() + " needs to have its width changed to " + str(width) + ".\n"

        height = stats["height"]
        if height == "device":
            height = DEVICE_HEIGHT
        if not check_height(style, height):
            ret += comp_str.capitalize().capitalize() + " needs to have its height changed to " + str(height) + ".\n"

        corner_radius = stats["corner_radius"]
        if not check_corner_radius(style, corner_radius):
            ret += comp_str.capitalize().capitalize() + " needs to have its corner radius changed to " + str(corner_radius) + ".\n"

        top_padding = stats["top_padding"]
        if not check_top_padding(comp, top_padding):
            ret += "Ensure that every direct child of " + comp_str + " has a top value of at least " + str(
                top_padding) + ".\n"

        bottom_padding = stats["bottom_padding"]
        if not check_bottom_padding(comp, bottom_padding):
            ret += "Ensure that every direct child of " + comp_str + " has a distance to the " + comp_name + "'s bottom of at least " + str(
                bottom_padding) + ".\n"

        left_padding = stats["left_padding"]
        if not check_left_padding(comp, left_padding):
            ret += "Ensure that every direct child of " + comp_str + " has a left value of at least " + str(
                left_padding) + ".\n"

        right_padding = stats["right_padding"]
        if not check_right_padding(comp, right_padding):
            ret += "Ensure that every direct child of " + comp_str + " has a distance to the " + comp_name + "'s right side of at least " + str(
                right_padding) + ".\n"

        padding_between = stats["padding_between"]
        if not check_padding_between(icons, padding_between):
            ret += "Ensure that the distance between every icon in " + comp_str + " is equal to exactly " + str(
                padding_between) + ".\n"

        icon_size = stats["icon_size"]
        if not check_icon_size(icons, icon_size):
            ret += "Ensure that every icon in " + comp_str + "'s leading icon section has a height and width of " + str(
                icon_size) + ".\n"

        icon_state_layer_size = stats["icon_state_layer_size"]
        if not check_icon_state_layer_size(icons, icon_state_layer_size):
            ret += "Ensure that every icon's state layer in " + comp_str + "'s leading icon section has a height and width of " + str(
                icon_state_layer_size) + ".\n"

        icon_target_size = stats["icon_target_size"]
        if not check_icon_target_size(icons, icon_target_size):
            ret += "Ensure that every icon's click target in " + comp_str + "'s leading icon section has a height and width of " + str(
                icon_target_size) + ".\n"

        if ret != "":
            comp.parent.append(soup.new_tag(name = "div",
                                              attrs = {"class": "Mark-" + comp["class"][0],
                                                     "style": "position: " + style["position"] +
                                                              "; left: " + style["left"] +
                                                              "; top: " + style["top"] +
                                                              "; height: " + style["height"] +
                                                              "; width: " + style["width"] +
                                                              "; box-shadow: inset 0px 0px 0px 4px red;",
                                                       "name": "Mark-" + comp["class"][0]}))

    return ret


def check_top_app_bar_center_aligned(comps, comp_stats, soup):
    comp_name = "top app bar"
    stats = comp_stats["top_app_bar_center_aligned"]
    ret = ""
    for comp in comps:
        id = comp["id"]
        comp_str = "the " + comp_name + " with id " + id

        style = parseStyle(comp["style"])
        leading_icons = comp.find_all("div", attrs={"class": "leading-icon"})[0]
        try:
            trailing_icons = comp.find_all("div", attrs={"class": "trailing-icon"})[0]
        except:
            trailing_icons = None

        width = stats["width"]
        if width == "device":
            width = DEVICE_WIDTH
        if not check_width(style, width):
            ret += comp_str.capitalize().capitalize() + " needs to have its width changed to " + str(width) + ".\n"

        height = stats["height"]
        if height == "device":
            height = DEVICE_HEIGHT
        if not check_height(style, height):
            ret += comp_str.capitalize().capitalize() + " needs to have its height changed to " + str(height) + ".\n"

        corner_radius = stats["corner_radius"]
        if not check_corner_radius(style, corner_radius):
            ret += comp_str.capitalize().capitalize() + " needs to have its corner radius changed to " + str(
                corner_radius) + ".\n"

        left_padding = stats["left_padding"]
        if not check_left_padding(comp, left_padding):
            ret += "Ensure that every direct child of " + comp_str + " has a left value of at least " + str(
                left_padding) + ".\n"

        right_padding = stats["right_padding"]
        if not check_right_padding(comp, right_padding):
            ret += "Ensure that every direct child of " + comp_str + " has a distance to the " + comp_name + "'s right side of at least " + str(
                right_padding) + ".\n"

        padding_between = stats["padding_between"]
        if not check_padding_between(comp, padding_between):
            ret += "Ensure that the distance between every child of " + comp_str + " is equal to at least " + str(
                padding_between) + ".\n"

        if len(comp.find_all("div", attrs={"class": "headline"})) > 0:
            headline = comp.find_all("div", attrs={"class": "headline"})[0]
            text_size = stats["text_size"]
            if not check_text_size(headline, text_size):
                ret += "The text in the headline section of " + comp_str + " needs to have its size changed to " + str(
                    text_size) + ".\n"

            text_weight = stats["text_weight"]
            if not check_text_weight(headline, text_weight):
                ret += "The text in the headline section of " + comp_str + " needs to have its weight changed to " + str(
                    text_weight) + ".\n"

            align = stats["text_alignment"]
            if not check_text_align(headline, align):
                ret += "Ensure that the text in " + comp_str + "'s headline section is centered horizontally.\n"

        icon_size = stats["icon_size"]
        if not check_icon_size(leading_icons, icon_size):
            ret += "Ensure that every icon in " + comp_str + "'s leading icon section has a height and width of " + str(
                icon_size) + ".\n"

        icon_state_layer_size = stats["icon_state_layer_size"]
        if not check_icon_state_layer_size(leading_icons, icon_state_layer_size):
            ret += "Ensure that every icon's state layer in " + comp_str + "'s leading icon section has a height and width of " + str(
                icon_state_layer_size) + ".\n"

        icon_target_size = stats["icon_target_size"]
        leading_icons_style = parseStyle(leading_icons["style"])
        if not check_height(leading_icons_style, icon_target_size) or not check_width(leading_icons_style, icon_target_size):
            ret += "Ensure that every icon's click target in " + comp_str + "'s leading icon section has a height and width of " + str(
                icon_target_size) + ".\n"

        if trailing_icons is not None:
            if not check_icon_size(trailing_icons, icon_size):
                ret += "Ensure that every icon in " + comp_str + "'s trailing icon section has a height and width of " + str(
                    icon_size) + ".\n"

            if not check_icon_state_layer_size(trailing_icons, icon_state_layer_size):
                ret += "Ensure that every icon's state layer in " + comp_str + "'s trailing icon section has a height and width of " + str(
                    icon_state_layer_size) + ".\n"

            if len(trailing_icons.contents) > 3:
                if not check_icon_target_size(trailing_icons, icon_target_size):
                    ret += "Ensure that every icon's click target in " + comp_str + "'s trailing icon section has a height and width of " + str(
                        icon_target_size) + ".\n"
            else:
                trailing_icons_style = parseStyle(trailing_icons["style"])
                if not check_height(trailing_icons_style, icon_target_size) or not check_width(trailing_icons_style,
                                                                                               icon_target_size):
                    ret += "Ensure that every icon's click target in " + comp_str + "'s trailing icon section has a height and width of " + str(
                        icon_target_size) + ".\n"

        if not check_centered_vert(comp):
            ret += "Ensure that everything contained in " + comp_str + " is vertically centered.\n"

        if ret != "":
            comp.parent.append(soup.new_tag(name = "div",
                                              attrs = {"class": "Mark-" + comp["class"][0],
                                                     "style": "position: " + style["position"] +
                                                              "; left: " + style["left"] +
                                                              "; top: " + style["top"] +
                                                              "; height: " + style["height"] +
                                                              "; width: " + style["width"] +
                                                              "; box-shadow: inset 0px 0px 0px 4px red;",
                                                       "name": "Mark-" + comp["class"][0]}))

    return ret


def check_top_app_bar_small(comps, comp_stats, soup):
    comp_name = "top app bar"
    stats = comp_stats["top_app_bar_small"]
    ret = ""
    for comp in comps:
        id = comp["id"]
        comp_str = "the " + comp_name + " with id " + id

        style = parseStyle(comp["style"])
        trailing_icons = comp.find_all("div", attrs={"class": "trailing-icon"})[0]

        width = stats["width"]
        if width == "device":
            width = DEVICE_WIDTH
        if not check_width(style, width):
            ret += comp_str.capitalize().capitalize() + " needs to have its width changed to " + str(width) + ".\n"

        height = stats["height"]
        if height == "device":
            height = DEVICE_HEIGHT
        if not check_height(style, height):
            ret += comp_str.capitalize().capitalize() + " needs to have its height changed to " + str(height) + ".\n"

        corner_radius = stats["corner_radius"]
        if not check_corner_radius(style, corner_radius):
            ret += comp_str.capitalize().capitalize() + " needs to have its corner radius changed to " + str(
                corner_radius) + ".\n"

        left_padding = stats["left_padding"]
        if not check_left_padding(comp, left_padding):
            ret += "Ensure that every direct child of " + comp_str + " has a left value of at least " + str(
                left_padding) + ".\n"

        right_padding = stats["right_padding"]
        if not check_right_padding(comp, right_padding):
            ret += "Ensure that every direct child of " + comp_str + " has a distance to the " + comp_name + "'s right side of at least " + str(
                right_padding) + ".\n"

        padding_between = stats["padding_between"]
        if not check_padding_between(comp, padding_between):
            ret += "Ensure that the distance between every direct child in " + comp_str + " is equal to at least " + str(
                padding_between) + ".\n"

        if len(comp.find_all("div", attrs={"class": "headline"})) > 0:
            headline = comp.find_all("div", attrs={"class": "headline"})[0]
            text_size = stats["text_size"]
            if not check_text_size(headline, text_size):
                ret += "The text in the headline section of " + comp_str + " needs to have its size changed to " + str(
                    text_size) + ".\n"

            text_weight = stats["text_weight"]
            if not check_text_weight(headline, text_weight):
                ret += "The text in the headline section of " + comp_str + " needs to have its weight changed to " + str(
                    text_weight) + ".\n"

            align = stats["text_alignment"]
            if not check_text_align(headline, align):
                ret += "Ensure that the text in " + comp_str + "'s headline section is aligned to the left.\n"

        padding_icons = stats["padding_icons"]
        if not check_padding_between(trailing_icons, padding_icons):
            ret += "Ensure that the distance between every trailing icon in " + comp_str + " is equal to " + str(
                padding_icons) + ".\n"

        icon_size = stats["icon_size"]
        icon_state_layer_size = stats["icon_state_layer_size"]
        icon_target_size = stats["icon_target_size"]
        if len(comp.find_all("div", attrs={"class": "leading-icon"})) > 0:
            leading_icons = comp.find_all("div", attrs={"class": "leading-icon"})[0]
            leading_icons_style = parseStyle(leading_icons["style"])
            if not check_icon_size(leading_icons, icon_size):
                ret += "Ensure that every icon in " + comp_str + "'s leading icon section has a height and width of " + str(
                    icon_size) + ".\n"

            if not check_icon_state_layer_size(leading_icons, icon_state_layer_size):
                ret += "Ensure that every icon's state layer in " + comp_str + "'s leading icon section has a height and width of " + str(
                    icon_state_layer_size) + ".\n"

            if not check_height(leading_icons_style, icon_target_size) or not check_width(leading_icons_style, icon_target_size):
                ret += "Ensure that every icon's click target in " + comp_str + "'s leading icon section has a height and width of " + str(
                    icon_target_size) + ".\n"

        if not check_icon_size(trailing_icons, icon_size):
            ret += "Ensure that every icon in " + comp_str + "'s trailing icon section has a height and width of " + str(
                icon_size) + ".\n"

        if not check_icon_state_layer_size(trailing_icons, icon_state_layer_size):
            ret += "Ensure that every icon's state layer in " + comp_str + "'s trailing icon section has a height and width of " + str(
                icon_state_layer_size) + ".\n"

        if not check_icon_target_size(trailing_icons, icon_target_size):
            ret += "Ensure that every icon's click target in " + comp_str + "'s trailing icon section has a height and width of " + str(
                icon_target_size) + ".\n"

        if not check_centered_vert(comp):
            ret += "Ensure that everything contained in " + comp_str + " is vertically centered.\n"

        if ret != "":
            comp.parent.append(soup.new_tag(name = "div",
                                              attrs = {"class": "Mark-" + comp["class"][0],
                                                     "style": "position: " + style["position"] +
                                                              "; left: " + style["left"] +
                                                              "; top: " + style["top"] +
                                                              "; height: " + style["height"] +
                                                              "; width: " + style["width"] +
                                                              "; box-shadow: inset 0px 0px 0px 4px red;",
                                                       "name": "Mark-" + comp["class"][0]}))

    return ret


def check_top_app_bar_medium(comps, comp_stats, soup):
    comp_name = "top app bar"
    stats = comp_stats["top_app_bar_medium"]
    ret = ""
    for comp in comps:
        id = comp["id"]
        comp_str = "the " + comp_name + " with id " + id

        style = parseStyle(comp["style"])
        leading_icons = comp.find_all("div", attrs={"class": "leading-icon"})[0]
        trailing_icons = comp.find_all("div", attrs={"class": "trailing-icon"})[0]

        width = stats["width"]
        if width == "device":
            width = DEVICE_WIDTH
        if not check_width(style, width):
            ret += comp_str.capitalize().capitalize() + " needs to have its width changed to " + str(width) + ".\n"

        height = stats["height"]
        if height == "device":
            height = DEVICE_HEIGHT
        if not check_height(style, height):
            ret += comp_str.capitalize().capitalize() + " needs to have its height changed to " + str(height) + ".\n"

        corner_radius = stats["corner_radius"]
        if not check_corner_radius(style, corner_radius):
            ret += comp_str.capitalize().capitalize() + " needs to have its corner radius changed to " + str(
                corner_radius) + ".\n"

        left_padding = stats["left_padding"]
        if not check_left_padding(comp, left_padding):
            ret += "Ensure that every direct child of " + comp_str + " has a left value of at least " + str(
                left_padding) + ".\n"

        right_padding = stats["right_padding"]
        if not check_right_padding(comp, right_padding):
            ret += "Ensure that every direct child of " + comp_str + " has a distance to the " + comp_name + "'s right side of at least " + str(
                right_padding) + ".\n"

        padding_between_vert = stats["padding_between_vert"]
        if not check_padding_between_vert(comp, padding_between_vert):
            ret += "Ensure that the vertical distance between every direct child of " + comp_str + " is equal to at least " + str(
                padding_between_vert) + ".\n"

        if len(comp.find_all("div", attrs={"class": "headline"})) > 0:
            headline = comp.find_all("div", attrs={"class": "headline"})[1]
            text_size = stats["text_size"]
            if not check_text_size(headline, text_size):
                ret += "The text in the headline section of " + comp_str + " needs to have its size changed to " + str(
                    text_size) + ".\n"

            text_weight = stats["text_weight"]
            if not check_text_weight(headline, text_weight):
                ret += "The text in the headline section of " + comp_str + " needs to have its weight changed to " + str(
                    text_weight) + ".\n"

            left_padding_text = stats["left_padding_text"]
            if not check_left_padding(headline, left_padding_text):
                ret += "Ensure that the text in the headline section of " + comp_str + " has a distance to the left of exactly " + str(
                    left_padding_text) + ".\n"

            right_padding_text = stats["right_padding_text"]
            if not check_right_padding(headline, right_padding_text):
                ret += "Ensure that the text in the headline section of " + comp_str + " has a distance to the right of at least " + str(
                    right_padding_text) + ".\n"

            align = stats["text_alignment"]
            if not check_text_align(headline, align):
                ret += "Ensure that the text in " + comp_str + "'s headline section is aligned to the left.\n"

        padding_icons = stats["padding_icons"]
        if not check_padding_between(trailing_icons, padding_icons):
            ret += "Ensure that the distance between every trailing icon in " + comp_str + " is equal to " + str(
                padding_icons) + ".\n"
        if not check_padding_between(leading_icons, padding_icons):
            ret += "Ensure that the distance between every leading icon in " + comp_str + " is equal to " + str(
                padding_icons) + ".\n"

        icon_size = stats["icon_size"]
        if not check_icon_size(leading_icons, icon_size):
            ret += "Ensure that every icon in " + comp_str + "'s leading icon section has a height and width of " + str(
                icon_size) + ".\n"
        if not check_icon_size(trailing_icons, icon_size):
            ret += "Ensure that every icon in " + comp_str + "'s trailing icon section has a height and width of " + str(
                icon_size) + ".\n"

        icon_state_layer_size = stats["icon_state_layer_size"]
        if not check_icon_state_layer_size(leading_icons, icon_state_layer_size):
            ret += "Ensure that every icon's state layer in " + comp_str + "'s leading icon section has a height and width of " + str(
                icon_state_layer_size) + ".\n"
        if not check_icon_state_layer_size(trailing_icons, icon_state_layer_size):
            ret += "Ensure that every icon's state layer in " + comp_str + "'s trailing icon section has a height and width of " + str(
                icon_state_layer_size) + ".\n"

        icon_target_size = stats["icon_target_size"]
        leading_icons_style = parseStyle(leading_icons["style"])
        if not check_height(leading_icons_style, icon_target_size) or not check_width(leading_icons_style, icon_target_size):
            ret += "Ensure that every icon's click target in " + comp_str + "'s leading icon section has a height and width of " + str(
                icon_target_size) + ".\n"
        if not check_icon_target_size(trailing_icons, icon_target_size):
            ret += "Ensure that every icon's click target in " + comp_str + "'s trailing icon section has a height and width of " + str(
                icon_target_size) + ".\n"

        if not check_centered_vert(comp):
            ret += "Ensure that everything contained in each direct child of " + comp_str + " is vertically centered.\n"

        if ret != "":
            comp.parent.append(soup.new_tag(name = "div",
                                              attrs = {"class": "Mark-" + comp["class"][0],
                                                     "style": "position: " + style["position"] +
                                                              "; left: " + style["left"] +
                                                              "; top: " + style["top"] +
                                                              "; height: " + style["height"] +
                                                              "; width: " + style["width"] +
                                                              "; box-shadow: inset 0px 0px 0px 4px red;",
                                                       "name": "Mark-" + comp["class"][0]}))

    return ret


def check_top_app_bar_large(comps, comp_stats, soup):
    comp_name = "top app bar"
    stats = comp_stats["top_app_bar_large"]
    ret = ""
    for comp in comps:
        id = comp["id"]
        comp_str = "the " + comp_name + " with id " + id

        style = parseStyle(comp["style"])
        leading_icons = comp.find_all("div", attrs={"class": "leading-icon"})[0]
        trailing_icons = comp.find_all("div", attrs={"class": "trailing-icon"})[0]

        width = stats["width"]
        if width == "device":
            width = DEVICE_WIDTH
        if not check_width(style, width):
            ret += comp_str.capitalize().capitalize() + " needs to have its width changed to " + str(width) + ".\n"

        height = stats["height"]
        if height == "device":
            height = DEVICE_HEIGHT
        if not check_height(style, height):
            ret += comp_str.capitalize().capitalize() + " needs to have its height changed to " + str(height) + ".\n"

        corner_radius = stats["corner_radius"]
        if not check_corner_radius(style, corner_radius):
            ret += comp_str.capitalize().capitalize() + " needs to have its corner radius changed to " + str(
                corner_radius) + ".\n"

        left_padding = stats["left_padding"]
        if not check_left_padding(comp, left_padding):
            ret += "Ensure that every direct child of " + comp_str + " has a left value of at least " + str(
                left_padding) + ".\n"

        right_padding = stats["right_padding"]
        if not check_right_padding(comp, right_padding):
            ret += "Ensure that every direct child of " + comp_str + " has a distance to the " + comp_name + "'s right side of at least " + str(
                right_padding) + ".\n"

        padding_between_vert = stats["padding_between_vert"]
        if not check_padding_between(comp, padding_between_vert):
            ret += "Ensure that the vertical distance between every direct child of " + comp_str + " is equal to exactly " + str(
                padding_between_vert) + ".\n"

        if len(comp.find_all("div", attrs={"class": "headline"})) > 0:
            headline = comp.find_all("div", attrs={"class": "headline"})[1]
            text_size = stats["text_size"]
            if not check_text_size(headline, text_size):
                ret += "The text in the headline section of " + comp_str + " needs to have its size changed to " + str(
                    text_size) + ".\n"

            text_weight = stats["text_weight"]
            if not check_text_weight(headline, text_weight):
                ret += "The text in the headline section of " + comp_str + " needs to have its weight changed to " + str(
                    text_weight) + ".\n"

            left_padding_text = stats["left_padding_text"]
            if not check_left_padding(headline, left_padding_text):
                ret += "Ensure that the text in the headline section of " + comp_str + " has a distance to the left of exactly " + str(
                    left_padding_text) + ".\n"

            right_padding_text = stats["right_padding_text"]
            if not check_right_padding(headline, right_padding_text):
                ret += "Ensure that the text in the headline section of " + comp_str + " has a distance to the right of at least " + str(
                    right_padding_text) + ".\n"

            align = stats["text_alignment"]
            if not check_text_align(headline, align):
                ret += "Ensure that the text in " + comp_str + "'s headline section is aligned to the left.\n"

        padding_icons = stats["padding_icons"]
        if not check_padding_between(trailing_icons, padding_icons):
            ret += "Ensure that the distance between every trailing icon in " + comp_str + " is equal to " + str(
                padding_icons) + ".\n"
        if not check_padding_between(leading_icons, padding_icons):
            ret += "Ensure that the distance between every leading icon in " + comp_str + " is equal to " + str(
                padding_icons) + ".\n"

        icon_size = stats["icon_size"]
        if not check_icon_size(leading_icons, icon_size):
            ret += "Ensure that every icon in " + comp_str + "'s leading icon section has a height and width of " + str(
                icon_size) + ".\n"
        if not check_icon_size(trailing_icons, icon_size):
            ret += "Ensure that every icon in " + comp_str + "'s trailing icon section has a height and width of " + str(
                icon_size) + ".\n"

        icon_state_layer_size = stats["icon_state_layer_size"]
        if not check_icon_state_layer_size(leading_icons, icon_state_layer_size):
            ret += "Ensure that every icon's state layer in " + comp_str + "'s leading icon section has a height and width of " + str(
                icon_state_layer_size) + ".\n"
        if not check_icon_state_layer_size(trailing_icons, icon_state_layer_size):
            ret += "Ensure that every icon's state layer in " + comp_str + "'s trailing icon section has a height and width of " + str(
                icon_state_layer_size) + ".\n"

        icon_target_size = stats["icon_target_size"]
        leading_icons_style = parseStyle(leading_icons["style"])
        if not check_height(leading_icons_style, icon_target_size) or check_width(leading_icons_style, icon_target_size):
            ret += "Ensure that every icon's click target in " + comp_str + "'s leading icon section has a height and width of " + str(
                icon_target_size) + ".\n"
        if not check_icon_target_size(trailing_icons, icon_target_size):
            ret += "Ensure that every icon's click target in " + comp_str + "'s trailing icon section has a height and width of " + str(
                icon_target_size) + ".\n"

        for child in comp.children:
            if type(child) == Tag:
                if not check_centered_vert(child):
                    ret += "Ensure that everything contained in each direct child of " + comp_str + " is vertically centered.\n"
                    break

        if ret != "":
            comp.parent.append(soup.new_tag(name = "div",
                                              attrs = {"class": "Mark-" + comp["class"][0],
                                                     "style": "position: " + style["position"] +
                                                              "; left: " + style["left"] +
                                                              "; top: " + style["top"] +
                                                              "; height: " + style["height"] +
                                                              "; width: " + style["width"] +
                                                              "; box-shadow: inset 0px 0px 0px 4px red;",
                                                       "name": "Mark-" + comp["class"][0]}))

    return ret


def check_badge(comps, comp_stats, soup):
    comp_name = "badge"
    stats = comp_stats["badge"]
    ret = ""

    for comp in comps:
        id = comp["id"]
        comp_str = "the " + comp_name + " with id " + id
        style = parseStyle(comp["style"])

        width = stats["width"]
        if not check_width(style, width):
            ret += comp_str.capitalize().capitalize() + " needs to have its width changed to " + str(width) + ".\n"

        height = stats["height"]
        if not check_height(style, height):
            ret += comp_str.capitalize().capitalize() + " needs to have its height changed to " + str(height) + ".\n"

        corner_radius = stats["corner_radius"]
        if not check_corner_radius(style, corner_radius):
            ret += comp_str.capitalize().capitalize() + " needs to have its corner radius changed to " + str(corner_radius) + ".\n"

        if len(comp.find_all("div", attrs={"class": "Spacer"})) <= 0:
            pos_top = stats["pos_top"]
            pos_left = stats["pos_left"]
            if not check_badge_pos(comp, pos_top, pos_left):
                ret += comp_str.capitalize().capitalize() + " needs to be repositioned so that its top value is equal to " + str(
                    pos_top) + " and its left value is equal to " + str(pos_left) + ".\n"

        if ret != "":
            comp.parent.append(soup.new_tag(name = "div",
                                              attrs = {"class": "Mark-" + comp["class"][0],
                                                     "style": "position: " + style["position"] +
                                                              "; left: " + style["left"] +
                                                              "; top: " + style["top"] +
                                                              "; height: " + style["height"] +
                                                              "; width: " + style["width"] +
                                                              "; box-shadow: inset 0px 0px 0px 4px red;",
                                                       "name": "Mark-" + comp["class"][0]}))

    return ret


def check_badge_large(comps, comp_stats, soup):
    comp_name = "badge"
    stats = comp_stats["badge_large"]
    ret = ""

    for comp in comps:
        id = comp["id"]
        comp_str = "the " + comp_name + " with id " + id
        style = parseStyle(comp["style"])

        height = stats["height"]
        if not check_height(style, height):
            ret += comp_str.capitalize().capitalize() + " needs to have its height changed to " + str(height) + ".\n"

        corner_radius = stats["corner_radius"]
        if not check_corner_radius(style, corner_radius):
            ret += comp_str.capitalize().capitalize() + " needs to have its corner radius changed to " + str(corner_radius) + ".\n"

        text = comp.find_all("div", attrs={"class": "Badge-label"})[0]
        text_size = stats["text_size"]
        if not check_text_size(text, text_size):
            ret += "The size of the label text of " + comp_str + " needs to have its size changed to " + str(
                text_size) + ".\n"

        text_weight = stats["text_weight"]
        if not check_text_weight(text, text_weight):
            ret += "The weight of the label text of " + comp_str + " needs to have its size changed to " + str(
                text_weight) + ".\n"

        align = stats["text_alignment"]
        if not check_text_align(text, align):
            ret += "Make sure the text in " + comp_str + " is centered both vertically and horizontally.\n"

        if len(comp.find_all("div", attrs={"class": "Spacer"})) <= 0:
            pos_top = stats["pos_top"]
            pos_left = stats["pos_left"]
            if not check_badge_pos(comp, pos_top, pos_left):
                ret += comp_str.capitalize().capitalize() + " needs to be repositioned so that its top value is equal to " + str(
                    pos_top) + " and its left value is equal to " + str(pos_left) + ".\n"

        if ret != "":
            comp.parent.append(soup.new_tag(name = "div",
                                              attrs = {"class": "Mark-" + comp["class"][0],
                                                     "style": "position: " + style["position"] +
                                                              "; left: " + style["left"] +
                                                              "; top: " + style["top"] +
                                                              "; height: " + style["height"] +
                                                              "; width: " + style["width"] +
                                                              "; box-shadow: inset 0px 0px 0px 4px red;",
                                                       "name": "Mark-" + comp["class"][0]}))

    return ret


def check_button_elevated_tonal_filled_text(comps, comp_stats, soup):
    comp_name = "button"
    stats = comp_stats["button_elevated_tonal_filled_text"]
    ret = ""

    for comp in comps:
        id = comp["id"]
        comp_str = "the " + comp_name + " with id " + id
        style = parseStyle(comp["style"])
        state_layer = comp.find_all("div", attrs={"class": "state-layer"})[0]
        label_text = comp.find_all("div", attrs={"class": "label-text"})[0]

        height = stats["height"]
        if not check_height(style, height):
            ret += comp_str.capitalize().capitalize() + " needs to have its height changed to " + str(height) + ".\n"

        corner_radius = stats["corner_radius"]
        if not check_corner_radius(style, corner_radius):
            ret += "The corner radius of " + comp_str + " needs to be changed to " + str(corner_radius) + ".\n"

        top_padding = stats["top_padding"]
        if not check_top_padding(state_layer, top_padding):
            ret += "Ensure that every direct child of " + comp_str + "'s state layer has a top value of at least " + str(
                top_padding) + ".\n"

        bottom_padding = stats["bottom_padding"]
        if not check_bottom_padding(state_layer, bottom_padding):
            ret += "Ensure that every direct child of " + comp_str + "'s state layer has a distance to the " + comp_name + "'s bottom of at least " + str(
                bottom_padding) + ".\n"

        if len(comp.find_all("div", attrs={"class": "icon"})) > 0:
            left_padding = stats["left_padding_icon"]
        else:
            left_padding = stats["left_padding"]
        if not check_left_padding(state_layer, left_padding):
            ret += "Ensure that every direct child of " + comp_str + "'s state layer has a left value of at least " + str(
                left_padding) + ".\n"

        right_padding = stats["right_padding"]
        if not check_right_padding(state_layer, right_padding):
            ret += "Ensure that every direct child of " + comp_str + "'s state layer has a distance to the " + comp_name + "'s right side of at least " + str(
                right_padding) + ".\n"

        padding_between = stats["padding_between"]
        if not check_padding_between(state_layer, padding_between):
            ret += "Ensure that the distance between every child of " + comp_str + "'s state layer is equal to exactly " + str(
                padding_between) + ".\n"

        text_size = stats["text_size"]
        if not check_text_size(label_text, text_size):
            ret += "The label text of " + comp_str + " needs to have its size changed to " + str(text_size) + ".\n"

        text_weight = stats["text_weight"]
        if not check_text_weight(label_text, text_weight):
            ret += "The label text of " + comp_str + " needs to have its weight changed to " + str(text_weight) + ".\n"

        align = stats["text_alignment"]
        if not check_text_align(label_text, align):
            ret += "Ensure that the label text of " + comp_str + "is centered both horizontally and vertically.\n"

        if len(comp.find_all("div", attrs={"class": "icon"})) > 0:
            icon = comp.find_all("div", attrs={"class": "icon"})[0]
            icon_style = parseStyle(icon["style"])
            icon_size = stats["icon_size"]

            if not check_height(icon_style, icon_size):
                ret += "The icon in " + comp_str + " needs to have its height changed to " + str(icon_size) + ".\n"

            if not check_width(icon_style, icon_size):
                ret += "The icon in " + comp_str + " needs to have its width changed to " + str(icon_size) + ".\n"

        if not check_centered_vert(comp):
            ret += "Ensure that every child of " + comp_str + " is vertically centered.\n"

        if ret != "":
            comp.parent.append(soup.new_tag(name = "div",
                                              attrs = {"class": "Mark-" + comp["class"][0],
                                                     "style": "position: " + style["position"] +
                                                              "; left: " + style["left"] +
                                                              "; top: " + style["top"] +
                                                              "; height: " + style["height"] +
                                                              "; width: " + style["width"] +
                                                              "; box-shadow: inset 0px 0px 0px 4px red;",
                                                       "name": "Mark-" + comp["class"][0]}))

    return ret


def check_button_outlined(comps, comp_stats, soup):
    comp_name = "button"
    stats = comp_stats["button_outlined"]
    ret = ""

    for comp in comps:
        id = comp["id"]
        comp_str = "the " + comp_name + " with id " + id
        style = parseStyle(comp["style"])
        state_layer = comp.find_all("div", attrs={"class": "state-layer"})[0]
        label_text = comp.find_all("div", attrs={"class": "label-text"})[0]

        height = stats["height"]
        if not check_height(style, height):
            ret += comp_str.capitalize().capitalize() + " needs to have its height changed to " + str(height) + ".\n"

        corner_radius = stats["corner_radius"]
        if not check_corner_radius(style, corner_radius):
            ret += "The corner radius of " + comp_str + " needs to be changed to " + str(corner_radius) + ".\n"

        top_padding = stats["top_padding"]
        if not check_top_padding(state_layer, top_padding):
            ret += "Ensure that every direct child of " + comp_str + "'s state layer has a top value of at least " + str(
                top_padding) + ".\n"

        bottom_padding = stats["bottom_padding"]
        if not check_bottom_padding(state_layer, bottom_padding):
            ret += "Ensure that every direct child of " + comp_str + "'s state layer has a distance to the " + comp_name + "'s bottom of at least " + str(
                bottom_padding) + ".\n"

        if len(comp.find_all("div", attrs={"class": "icon"})) > 0:
            left_padding = stats["left_padding_icon"]
        else:
            left_padding = stats["left_padding"]
        if not check_left_padding(state_layer, left_padding):
            ret += "Ensure that every direct child of " + comp_str + "'s state layer has a left value of at least " + str(
                left_padding) + ".\n"

        right_padding = stats["right_padding"]
        if not check_right_padding(state_layer, right_padding):
            ret += "Ensure that every direct child of " + comp_str + "'s state layer has a distance to the " + comp_name + "'s right side of at least " + str(
                right_padding) + ".\n"

        padding_between = stats["padding_between"]
        if not check_padding_between(state_layer, padding_between):
            ret += "Ensure that the distance between every child of " + comp_str + "'s state layer is equal to exactly " + str(
                padding_between) + ".\n"

        text_size = stats["text_size"]
        if not check_text_size(label_text, text_size):
            ret += "The label text of " + comp_str + " needs to have its size changed to " + str(text_size) + ".\n"

        text_weight = stats["text_weight"]
        if not check_text_weight(label_text, text_weight):
            ret += "The label text of " + comp_str + " needs to have its weight changed to " + str(text_weight) + ".\n"

        align = stats["text_alignment"]
        if not check_text_align(label_text, align):
            ret += "Ensure that the label text of " + comp_str + "is centered both horizontally and vertically.\n"

        if len(comp.find_all("div", attrs={"class": "icon"})) > 0:
            icon = comp.find_all("div", attrs={"class": "icon"})[0]
            icon_style = parseStyle(icon["style"])
            icon_size = stats["icon_size"]

            if not check_height(icon_style, icon_size):
                ret += "The icon in " + comp_str + " needs to have its height changed to " + str(icon_size) + ".\n"

            if not check_width(icon_style, icon_size):
                ret += "The icon in " + comp_str + " needs to have its width changed to " + str(icon_size) + ".\n"

        outline = stats["outline"]
        if not check_outline(style, outline):
            ret += comp_str.capitalize().capitalize() + " needs to have the size of its outline changed to " + str(outline)

        if not check_centered_vert(comp):
            ret += "Ensure that every child of " + comp_str + " is vertically centered.\n"

        if ret != "":
            comp.parent.append(soup.new_tag(name = "div",
                                              attrs = {"class": "Mark-" + comp["class"][0],
                                                     "style": "position: " + style["position"] +
                                                              "; left: " + style["left"] +
                                                              "; top: " + style["top"] +
                                                              "; height: " + style["height"] +
                                                              "; width: " + style["width"] +
                                                              "; box-shadow: inset 0px 0px 0px 4px red;",
                                                       "name": "Mark-" + comp["class"][0]}))

    return ret


def check_FAB(comps, comp_stats, soup):
    comp_name = "FAB"
    stats = comp_stats["FAB"]
    ret = ""

    for comp in comps:
        id = comp["id"]
        comp_str = "the " + comp_name + " with id " + id
        style = parseStyle(comp["style"])
        icon = comp.find_all("div", attrs={"class": "icon"})[0]
        icon_style = parseStyle(icon["style"])

        height = stats["height"]
        if not check_height(style, height):
            ret += comp_str.capitalize().capitalize() + " needs to have its height changed to " + str(height) + ".\n"

        width = stats["width"]
        if not check_width(style, width):
            ret += comp_str.capitalize().capitalize() + " needs to have its width changed to " + str(width) + ".\n"

        corner_radius = stats["corner_radius"]
        if not check_corner_radius(style, corner_radius):
            ret += comp_str.capitalize().capitalize() + " needs to have its corner radius changed to " + str(corner_radius) + ".\n"

        icon_size = stats["icon_size"]
        if not check_height(icon_style, icon_size):
            ret += "The icon in " + comp_str + " needs to have its height changed to " + str(icon_size) + ".\n"

        if not check_width(icon_style, icon_size):
            ret += "The icon in " + comp_str + " needs to have its width changed to " + str(icon_size) + ".\n"

        if not check_centered_hor(comp):
            ret += "Ensure that every child of " + comp_str + " is centered horizontally.\n"

        if not check_centered_vert(comp):
            ret += "Ensure that every child of " + comp_str + " is centered vertically.\n"

        device_bottom_padding = stats["device_bottom_padding"]
        device_right_padding = stats["device_right_padding"]
        ret += "Ensure that " + comp_str + " is positioned with a distance of " + str(
            device_right_padding) + " to the right side of the screen.\n"
        ret += "Ensure that " + comp_str + " is positioned with a distance of " + str(
            device_bottom_padding) + " to either the bottom of the screen or, if present, to any other elements positioned at the bottom of the screen like a navigation bar or a bottom sheet.\n"

        if ret != "":
            comp.parent.append(soup.new_tag(name = "div",
                                              attrs = {"class": "Mark-" + comp["class"][0],
                                                     "style": "position: " + style["position"] +
                                                              "; left: " + style["left"] +
                                                              "; top: " + style["top"] +
                                                              "; height: " + style["height"] +
                                                              "; width: " + style["width"] +
                                                              "; box-shadow: inset 0px 0px 0px 4px red;",
                                                       "name": "Mark-" + comp["class"][0]}))

    return ret


def check_FAB_small(comps, comp_stats, soup):
    comp_name = "FAB"
    stats = comp_stats["FAB_small"]
    ret = ""

    for comp in comps:
        id = comp["id"]
        comp_str = "the " + comp_name + " with id " + id
        style = parseStyle(comp["style"])
        icon = comp.find_all("div", attrs={"class": "icon"})[0]
        icon_style = parseStyle(icon["style"])

        height = stats["height"]
        if not check_height(style, height):
            ret += comp_str.capitalize().capitalize() + " needs to have its height changed to " + str(height) + ".\n"

        width = stats["width"]
        if not check_width(style, width):
            ret += comp_str.capitalize().capitalize() + " needs to have its width changed to " + str(width) + ".\n"

        corner_radius = stats["corner_radius"]
        if not check_corner_radius(style, corner_radius):
            ret += comp_str.capitalize().capitalize() + " needs to have its corner radius changed to " + str(corner_radius) + ".\n"

        icon_size = stats["icon_size"]
        if not check_height(icon_style, icon_size):
            ret += "The icon in " + comp_str + " needs to have its height changed to " + str(icon_size) + ".\n"

        if not check_width(icon_style, icon_size):
            ret += "The icon in " + comp_str + " needs to have its width changed to " + str(icon_size) + ".\n"

        if not check_centered_hor(comp):
            ret += "Ensure that every child of " + comp_str + " is centered horizontally.\n"

        if not check_centered_vert(comp):
            ret += "Ensure that every child of " + comp_str + " is centered vertically.\n"

        device_right_padding = stats["device_right_padding"]
        FAB_padding = stats["FAB_padding"]
        FAB_small_padding = stats["FAB_small_padding"]
        ret += "Ensure that " + comp_str + " is positioned with a distance of " + str(
            device_right_padding) + " to the right side of the screen.\n"
        ret += "Ensure that " + comp_str + " is positioned with a vertical distance of at least " + str(
            FAB_padding) + " to a large, extended, or normal FAB on the screen.\n"
        ret += "Ensure that " + comp_str + " is positioned with a vertical distance of at least " + str(
            FAB_small_padding) + " to any other small FABs on the screen.\n"

        if ret != "":
            comp.parent.append(soup.new_tag(name = "div",
                                              attrs = {"class": "Mark-" + comp["class"][0],
                                                     "style": "position: " + style["position"] +
                                                              "; left: " + style["left"] +
                                                              "; top: " + style["top"] +
                                                              "; height: " + style["height"] +
                                                              "; width: " + style["width"] +
                                                              "; box-shadow: inset 0px 0px 0px 4px red;",
                                                       "name": "Mark-" + comp["class"][0]}))

    return ret


def check_FAB_large(comps, comp_stats, soup):
    comp_name = "FAB"
    stats = comp_stats["FAB_large"]
    ret = ""

    for comp in comps:
        id = comp["id"]
        comp_str = "the " + comp_name + " with id " + id
        style = parseStyle(comp["style"])
        icon = comp.find_all("div", attrs={"class": "icon"})[0]
        icon_style = parseStyle(icon["style"])

        height = stats["height"]
        if not check_height(style, height):
            ret += comp_str.capitalize().capitalize() + " needs to have its height changed to " + str(height) + ".\n"

        width = stats["width"]
        if not check_width(style, width):
            ret += comp_str.capitalize().capitalize() + " needs to have its width changed to " + str(width) + ".\n"

        corner_radius = stats["corner_radius"]
        if not check_corner_radius(style, corner_radius):
            ret += comp_str.capitalize().capitalize() + " needs to have its corner radius changed to " + str(corner_radius) + ".\n"

        icon_size = stats["icon_size"]
        if not check_height(icon_style, icon_size):
            ret += "The icon in " + comp_str + " needs to have its height changed to " + str(icon_size) + ".\n"

        if not check_width(icon_style, icon_size):
            ret += "The icon in " + comp_str + " needs to have its width changed to " + str(icon_size) + ".\n"

        if not check_centered_hor(comp):
            ret += "Ensure that every child of " + comp_str + " is centered horizontally.\n"

        if not check_centered_vert(comp):
            ret += "Ensure that every child of " + comp_str + " is centered vertically.\n"

        device_bottom_padding = stats["device_bottom_padding"]
        device_right_padding = stats["device_right_padding"]
        ret += "Ensure that " + comp_str + " is positioned with a distance of " + str(
            device_right_padding) + " to the right side of the screen.\n"
        ret += "Ensure that " + comp_str + " is positioned with a distance of " + str(
            device_bottom_padding) + " to either the bottom of the screen or, if present, to any other elements positioned at the bottom of the screen like a navigation bar or a bottom sheet.\n"

        if ret != "":
            comp.parent.append(soup.new_tag(name = "div",
                                              attrs = {"class": "Mark-" + comp["class"][0],
                                                     "style": "position: " + style["position"] +
                                                              "; left: " + style["left"] +
                                                              "; top: " + style["top"] +
                                                              "; height: " + style["height"] +
                                                              "; width: " + style["width"] +
                                                              "; box-shadow: inset 0px 0px 0px 4px red;",
                                                       "name": "Mark-" + comp["class"][0]}))

    return ret


def check_FAB_extended(comps, comp_stats, soup):
    comp_name = "FAB"
    stats = comp_stats["FAB_extended"]
    ret = ""

    for comp in comps:
        id = comp["id"]
        comp_str = "the " + comp_name + " with id " + id
        style = parseStyle(comp["style"])
        state_layer = comp.find_all("div", attrs={"class": "state-layer"})[0]
        label_text = comp.find_all("div", attrs={"class": "label-text"})[0]

        height = stats["height"]
        if not check_height(style, height):
            ret += comp_str.capitalize().capitalize() + " needs to have its height changed to " + str(height) + ".\n"

        width = stats["width"]
        if not check_width(style, width):
            ret += comp_str.capitalize().capitalize() + " needs to have its width changed to " + str(width) + ".\n"

        corner_radius = stats["corner_radius"]
        if not check_corner_radius(style, corner_radius):
            ret += comp_str.capitalize().capitalize() + " needs to have its corner radius changed to " + str(corner_radius) + ".\n"

        if len(comp.find_all("div", attrs={"class": "icon"})) > 0:
            icon = comp.find_all("div", attrs={"class": "icon"})[0]
            icon_style = parseStyle(icon["style"])
            icon_size = stats["icon_size"]
            if not check_height(icon_style, icon_size):
                ret += "The icon in " + comp_str + " needs to have its height changed to " + str(icon_size) + ".\n"

            if not check_width(icon_style, icon_size):
                ret += "The icon in " + comp_str + " needs to have its width changed to " + str(icon_size) + ".\n"

        text_size = stats["text_size"]
        if not check_text_size(label_text, text_size):
            ret += "The label text of " + comp_str + " needs to have its size changed to " + str(text_size) + ".\n"

        text_weight = stats["text_weight"]
        if not check_text_weight(label_text, text_weight):
            ret += "The label text of " + comp_str + " needs to have its weight changed to " + str(text_weight) + ".\n"

        align = stats["text_alignment"]
        if not check_text_align(label_text, align):
            ret += "Ensure that the label text of " + comp_str + "is centered both horizontally and vertically.\n"

        top_padding = stats["top_padding"]
        if not check_top_padding(state_layer, top_padding):
            ret += "Ensure that every direct child of " + comp_str + " has a top value of at least " + str(
                top_padding) + ".\n"

        bottom_padding = stats["bottom_padding"]
        if not check_bottom_padding(state_layer, bottom_padding):
            ret += "Ensure that every direct child of " + comp_str + " has a distance to the " + comp_name + "'s bottom of at least " + str(
                bottom_padding) + ".\n"

        if len(comp.find_all("div", attrs={"class": "icon"})) > 0:
            left_padding = stats["left_padding_icon"]
        else:
            left_padding = stats["left_padding"]
        if not check_left_padding(state_layer, left_padding):
            ret += "Ensure that every direct child of " + comp_str + " has a left value of at least " + str(
                left_padding) + ".\n"

        right_padding = stats["right_padding"]
        if not check_right_padding(state_layer, right_padding):
            ret += "Ensure that every direct child of " + comp_str + " has a distance to the " + comp_name + "'s right side of at least " + str(
                right_padding) + ".\n"

        padding_between = stats["padding_between"]
        if not check_padding_between(state_layer, padding_between):
            ret += "Ensure that the distance between every child of " + comp_str + " is equal to exactly " + str(
                padding_between) + ".\n"

        if not check_centered_hor(comp):
            ret += "Ensure that every child of " + comp_str + " is centered horizontally.\n"

        if not check_centered_vert(comp):
            ret += "Ensure that every child of " + comp_str + " is centered vertically.\n"

        device_bottom_padding = stats["device_bottom_padding"]
        device_right_padding = stats["device_right_padding"]
        ret += "Ensure that " + comp_str + " is positioned with a distance of " + str(
            device_right_padding) + " to the right side of the screen.\n"
        ret += "Ensure that " + comp_str + " is positioned with a distance of " + str(
            device_bottom_padding) + " to either the bottom of the screen or, if present, to any other elements positioned at the bottom of the screen like a navigation bar or a bottom sheet.\n"

        if ret != "":
            comp.parent.append(soup.new_tag(name = "div",
                                              attrs = {"class": "Mark-" + comp["class"][0],
                                                     "style": "position: " + style["position"] +
                                                              "; left: " + style["left"] +
                                                              "; top: " + style["top"] +
                                                              "; height: " + style["height"] +
                                                              "; width: " + style["width"] +
                                                              "; box-shadow: inset 0px 0px 0px 4px red;",
                                                       "name": "Mark-" + comp["class"][0]}))

    return ret


def check_icon_button(comps, comp_stats, soup):
    comp_name = "icon button"
    stats = comp_stats["icon_button"]
    ret = ""

    for comp in comps:
        id = comp["id"]
        comp_str = "the " + comp_name + " with id " + id
        container_style = parseStyle(comp.find_all("div", attrs={"class": "container"})[0]["style"])
        style = parseStyle(comp["style"])

        width = stats["width"]
        if not check_width(container_style, width):
            ret += "The container in " + comp_str + " needs to have its width changed to " + str(width) + ".\n"

        height = stats["height"]
        if not check_height(container_style, height):
            ret += "The container in " + comp_str + " needs to have its height changed to " + str(height) + ".\n"

        corner_radius = stats["corner_radius"]
        if not check_corner_radius(container_style, corner_radius):
            ret += "The container in " + comp_str + " needs to have its corner radius changed to " + str(
                corner_radius) + ".\n"

        icon_size = stats["icon_size"]
        if not check_icon_size(comp, icon_size):
            ret += "The icon in " + comp_str + " needs to have its height and width changed to " + str(
                icon_size) + ".\n"

        target_size = stats["target_size"]
        if not check_width(style, target_size) or not check_height(style, target_size):
            ret += comp_str.capitalize().capitalize() + " needs to have its size changed to " + str(target_size) + ".\n"

        if ret != "":
            comp.parent.append(soup.new_tag(name = "div",
                                              attrs = {"class": "Mark-" + comp["class"][0],
                                                     "style": "position: " + style["position"] +
                                                              "; left: " + style["left"] +
                                                              "; top: " + style["top"] +
                                                              "; height: " + style["height"] +
                                                              "; width: " + style["width"] +
                                                              "; box-shadow: inset 0px 0px 0px 4px red;",
                                                       "name": "Mark-" + comp["class"][0]}))

    return ret


def check_icon_button_outlined(comps, comp_stats, soup):
    comp_name = "icon button"
    stats = comp_stats["icon_button"]
    ret = ""

    for comp in comps:
        id = comp["id"]
        comp_str = "the " + comp_name + " with id " + id
        container_style = parseStyle(comp.find_all("div", attrs={"class": "container"})[0]["style"])
        style = parseStyle(comp["style"])

        width = stats["width"]
        if not check_width(container_style, width):
            ret += "The container in " + comp_str + " needs to have its width changed to " + str(width) + ".\n"

        height = stats["height"]
        if not check_height(container_style, height):
            ret += "The container in " + comp_str + " needs to have its height changed to " + str(height) + ".\n"

        corner_radius = stats["corner_radius"]
        if not check_corner_radius(container_style, corner_radius):
            ret += "The container in " + comp_str + " needs to have its corner radius changed to " + str(
                corner_radius) + ".\n"

        icon_size = stats["icon_size"]
        if not check_icon_size(comp, icon_size):
            ret += "The icon in " + comp_str + " needs to have its height and width changed to " + str(
                icon_size) + ".\n"

        target_size = stats["target_size"]
        if not check_width(style, target_size) or check_height(style, target_size):
            ret += comp_str.capitalize().capitalize() + " needs to have its size changed to " + str(target_size) + ".\n"

        outline = stats["outline"]
        if not check_outline(style, outline):
            ret += comp_str.capitalize().capitalize() + " needs to have its outline size changed to " + str(outline) + ".\n"

        if ret != "":
            comp.parent.append(soup.new_tag(name = "div",
                                              attrs = {"class": "Mark-" + comp["class"][0],
                                                     "style": "position: " + style["position"] +
                                                              "; left: " + style["left"] +
                                                              "; top: " + style["top"] +
                                                              "; height: " + style["height"] +
                                                              "; width: " + style["width"] +
                                                              "; box-shadow: inset 0px 0px 0px 4px red;",
                                                       "name": "Mark-" + comp["class"][0]}))

    return ret


def check_segmented_button(comps, comp_stats, soup):
    comp_name = "segmented button"
    stats = comp_stats["segmented_button"]
    ret = ""

    for comp in comps:
        id = comp["id"]
        comp_str = "the " + comp_name + " with id " + id
        style = parseStyle(comp["style"])

        height = stats["target_size"]
        if not check_height(style, height):
            ret += comp_str.capitalize().capitalize() + " needs to have its height changed to " + str(height) + ".\n"

        largest_segment = comp.contents[1]
        largest_segment_style = parseStyle(largest_segment["style"])
        largest_segment_width = largest_segment_style["width"]
        width = 0
        for child in comp.children:
            if type(child) == Tag:
                child_style = parseStyle(child["style"])
                child_width = child_style["width"]
                if int(float(child_width.replace("px", ""))) > int(float(largest_segment_width.replace("px", ""))):
                    largest_segment = child
                    largest_segment_width = child_width
                    largest_segment_style = child_style

        width = int(float(largest_segment_width.replace("px", ""))) * (len(comp.contents) - 2)
        if not check_width(style, width):
            ret += comp_str.capitalize().capitalize() + " needs to have its width changed to " + str(width) + ".\n"

        left_padding = stats["left_padding"]
        right_padding = stats["right_padding"]
        padding_between = stats["padding_between"]
        outline = stats["outline"]
        text_size = stats["text_size"]
        text_weight = stats["text_weight"]
        container_height = stats["height"]
        icon_size = stats["icon_size"]
        for child in comp.children:
            if type(child) == Tag:
                child_style = parseStyle(child["style"])
                child_width = child_style["width"]
                child_id = child["id"]
                container = child.find_all("div", attrs={"class": "container"})[0]
                container_style = parseStyle(container["style"])

                child_str = "the segment with id " + child_id + " that is a child of " + comp_str

                if int(float(child_width.replace("px", ""))) < int(float(largest_segment_width.replace("px", ""))):
                    ret += child_str + " needs to have its width changed to " + largest_segment_width + ".\n"

                if not check_height(container_style, container_height):
                    ret += child_str + " needs to have its height changed to " + str(container_height) + ".\n"

                if not check_left_padding(container, left_padding):
                    ret += "Ensure that every direct child of " + child_str + "'s container element has a left value of at least " + str(
                        left_padding) + ".\n"

                if not check_right_padding(container, right_padding):
                    ret += "Ensure that every direct child of " + child_str + "'s container element has a distance to " + child_str + "'s right side of at least " + str(
                        right_padding) + ".\n"

                if not check_padding_between(container, padding_between):
                    ret += "Ensure that the distance between every direct child in " + child_str + "'s container element is equal to exactly " + str(
                        padding_between) + ".\n"

                if not check_outline(child_style, outline):
                    ret += child_str + "'s container element needs to have its outline width changed to " + str(
                        outline) + ".\n"

                if len(child.find_all("div", attrs={"class": "label-text"})) > 0:
                    label_text = child.find_all("div", attrs={"class": "label-text"})[0]
                    if not check_text_size(label_text, text_size):
                        ret += "The label text of " + child_str + " needs to have its size changed to " + str(
                            text_size) + ".\n"

                    if not check_text_weight(label_text, text_weight):
                        ret += "The label text of " + child_str + " needs to have its weight changed to " + str(
                            text_weight) + ".\n"

                icons = []
                if len(child.find_all("div", attrs={"class": "Icon"})) > 0:
                    icons = child.find_all("div", attrs={"class": "Icon"})
                elif len(child.find_all("div", attrs={"class": "Selected icon"})) > 0:
                    icons = child.find_all("div", attrs={"class": "Selected icon"})
                for icon in icons:
                    icon_style = parseStyle(icon["style"])
                    if not check_width(icon_style, icon_size) or not check_height(icon_style, icon_size):
                        ret += "The icon in " + child_str + " needs to have its height and width set to " + str(
                            icon_size) + ".\n"

        corner_radius = stats["corner_radius"]
        start_segment = comp.find_all("div", attrs={"class": "Segment-start"})[0]
        end_segment = comp.find_all("div", attrs={"class": "Segment-end"})[0]
        start_segment_style = parseStyle(start_segment["style"])
        end_segment_style = parseStyle(end_segment["style"])
        if not start_segment_style["border-radius"] == "100px 0px 0px 100px":
            ret += "The border radius style of " + comp_str + "'s start segment should be changed to 100px 0px 0px 100px.\n"

        if not end_segment_style["border-radius"] == "0px 100px 100px 0px":
            ret += "The border radius style of " + comp_str + "'s end segment should be changed to 0px 100px 100px 0px.\n"

        if ret != "":
            comp.parent.append(soup.new_tag(name = "div",
                                              attrs = {"class": "Mark-" + comp["class"][0],
                                                     "style": "position: " + style["position"] +
                                                              "; left: " + style["left"] +
                                                              "; top: " + style["top"] +
                                                              "; height: " + style["height"] +
                                                              "; width: " + style["width"] +
                                                              "; box-shadow: inset 0px 0px 0px 4px red;",
                                                       "name": "Mark-" + comp["class"][0]}))

    return ret


def check_card(comps, comp_stats, soup):
    comp_name = "card"
    stats = comp_stats["card"]
    ret = ""

    for comp in comps:
        id = comp["id"]
        comp_str = "the " + comp_name + " with id " + id
        style = parseStyle(comp["style"])
        background = comp.find_all("div", attrs={"class": "Background"})[0]
        background_style = parseStyle(background["style"])

        corner_radius = stats["corner_radius"]
        if not check_corner_radius(style, corner_radius):
            ret += comp_str.capitalize().capitalize() + " needs to have its corner radius changed to " + str(corner_radius) + ".\n"

        outline = stats["outline"]
        if background_style["border"] != "":
            if not check_outline(background_style, outline):
                ret += comp_str.capitalize().capitalize() + "'s background needs to have its border width changed to " + str(outline) + ".\n"

        texts = comp.find_all("div", attrs={"class": re.compile("Title|subhead|Header|Subhead|Supporting-text")})
        align = stats["text_alignment"]
        for text in texts:
            if not check_text_align(text, align):
                ret += "Make sure the text in " + comp_str + " is aligned to the left.\n"

        if ret != "":
            comp.parent.append(soup.new_tag(name = "div",
                                              attrs = {"class": "Mark-" + comp["class"][0],
                                                     "style": "position: " + style["position"] +
                                                              "; left: " + style["left"] +
                                                              "; top: " + style["top"] +
                                                              "; height: " + style["height"] +
                                                              "; width: " + style["width"] +
                                                              "; box-shadow: inset 0px 0px 0px 4px red;",
                                                       "name": "Mark-" + comp["class"][0]}))

    return ret


def check_carousel_multi_browse_hero(comps, comp_stats, soup):
    comp_name = "carousel"
    stats = comp_stats["carousel_multi_browse_hero"]
    ret = ""

    for comp in comps:
        id = comp["id"]
        comp_str = "the " + comp_name + " with id " + id
        style = parseStyle(comp["style"])
        last_item = comp.find_all("div", attrs={"class": "Item-Last"})[0]
        last_item_style = parseStyle(last_item["style"])

        left_padding = stats["left_padding"]
        if not check_left_padding(comp, left_padding):
            ret += "Ensure that every direct child of " + comp_str + " has a left value of at least " + str(
                left_padding) + ".\n"

        right_padding = stats["right_padding"]
        if not check_right_padding(comp, right_padding):
            ret += "Ensure that every direct child of " + comp_str + " has a distance to the " + comp_name + "'s right side of at least " + str(
                right_padding) + ".\n"

        top_padding = stats["top_padding"]
        if not check_left_padding(comp, top_padding):
            ret += "Ensure that every direct child of " + comp_str + " has a top value of at least " + str(
                top_padding) + ".\n"

        bottom_padding = stats["bottom_padding"]
        if not check_right_padding(comp, bottom_padding):
            ret += "Ensure that every direct child of " + comp_str + " has a distance to the " + comp_name + "'s bottom of at least " + str(
                bottom_padding) + ".\n"

        padding_between = stats["padding_between"]
        if not check_padding_between(comp, padding_between):
            ret += "Ensure that the distance between every direct child in " + comp_str + " is equal to exactly " + str(
                padding_between) + ".\n"

        small_item_width_min = stats["small_item_width_min"]
        small_item_width_max = stats["small_item_width_max"]
        last_item_width = int(last_item_style["width"].replace("px", ""))
        if last_item_width < small_item_width_min or last_item_width > small_item_width_max:
            ret += "The smallest item in " + comp_str + " needs to have its width changed to be between " + str(
                small_item_width_min) + " and " + str(small_item_width_max) + ".\n"

        if ret != "":
            comp.parent.append(soup.new_tag(name = "div",
                                              attrs = {"class": "Mark-" + comp["class"][0],
                                                     "style": "position: " + style["position"] +
                                                              "; left: " + style["left"] +
                                                              "; top: " + style["top"] +
                                                              "; height: " + style["height"] +
                                                              "; width: " + style["width"] +
                                                              "; box-shadow: inset 0px 0px 0px 4px red;",
                                                       "name": "Mark-" + comp["class"][0]}))

    return ret


def check_carousel_uncontained(comps, comp_stats, soup):
    comp_name = "carousel"
    stats = comp_stats["carousel_uncontained"]
    ret = ""

    for comp in comps:
        id = comp["id"]
        comp_str = "the " + comp_name + " with id " + id
        style = parseStyle(comp["style"])

        left_padding = stats["left_padding"]
        if not check_left_padding(comp, left_padding):
            ret += "Ensure that every direct child of " + comp_str + " has a left value of at least " + str(
                left_padding) + ".\n"

        top_padding = stats["top_padding"]
        if not check_left_padding(comp, top_padding):
            ret += "Ensure that every direct child of " + comp_str + " has a top value of at least " + str(
                top_padding) + ".\n"

        bottom_padding = stats["bottom_padding"]
        if not check_right_padding(comp, bottom_padding):
            ret += "Ensure that every direct child of " + comp_str + " has a distance to the " + comp_name + "'s bottom of at least " + str(
                bottom_padding) + ".\n"

        padding_between = stats["padding_between"]
        if not check_padding_between(comp, padding_between):
            ret += "Ensure that the distance between every direct child in " + comp_str + " is equal to exactly " + str(
                padding_between) + ".\n"

        if ret != "":
            comp.parent.append(soup.new_tag(name = "div",
                                              attrs = {"class": "Mark-" + comp["class"][0],
                                                     "style": "position: " + style["position"] +
                                                              "; left: " + style["left"] +
                                                              "; top: " + style["top"] +
                                                              "; height: " + style["height"] +
                                                              "; width: " + style["width"] +
                                                              "; box-shadow: inset 0px 0px 0px 4px red;",
                                                       "name": "Mark-" + comp["class"][0]}))

    return ret


def check_checkbox(comps, comp_stats, soup):
    comp_name = "checkbox"
    stats = comp_stats["checkbox"]
    ret = ""

    for comp in comps:
        id = comp["id"]
        comp_str = "the " + comp_name + " with id " + id
        style = parseStyle(comp["style"])
        container = comp.find_all("div", attrs={"class": "container"})[0]
        container_style = parseStyle(container["style"])
        state_layer = comp.find_all("div", attrs={"class": "state-layer"})[0]
        state_layer_style = parseStyle(state_layer["style"])

        target_size = stats["target_size"]
        if not check_width(style, target_size) or not check_height(style, target_size):
            ret += comp_str.capitalize().capitalize() + " needs to have it's width and height changed to " + str(target_size) + ".\n"

        width = stats["width"]
        if not check_width(container_style, width):
            ret += comp_str.capitalize().capitalize() + "'s container element needs to have its width changed to " + str(width) + ".\n"

        height = stats["height"]
        if not check_width(container_style, height):
            ret += comp_str.capitalize().capitalize() + "'s container element needs to have its height changed to " + str(height) + ".\n"

        corner_radius = stats["corner_radius"]
        if not check_corner_radius(container_style, corner_radius):
            ret += comp_str.capitalize().capitalize() + "'s container element needs to have its corner radius changed to " + str(
                corner_radius) + ".\n"

        state_layer_size = stats["state_layer_size"]
        if not check_width(state_layer_style, state_layer_size) or not check_height(state_layer_style,
                                                                                    state_layer_size):
            ret += comp_str.capitalize().capitalize() + "'s state layer element needs to have its height and width changed to " + str(
                state_layer_size) + ".\n"

        if ret != "":
            comp.parent.append(soup.new_tag(name = "div",
                                              attrs = {"class": "Mark-" + comp["class"][0],
                                                     "style": "position: " + style["position"] +
                                                              "; left: " + style["left"] +
                                                              "; top: " + style["top"] +
                                                              "; height: " + style["height"] +
                                                              "; width: " + style["width"] +
                                                              "; box-shadow: inset 0px 0px 0px 4px red;",
                                                       "name": "Mark-" + comp["class"][0]}))

    return ret


def check_checkbox_unselected(comps, comp_stats, soup):
    comp_name = "unselected checkbox"
    stats = comp_stats["checkbox_unselected"]
    ret = ""

    for comp in comps:
        id = comp["id"]
        comp_str = "the " + comp_name + " with id " + id
        style = parseStyle(comp["style"])
        container = comp.find_all("div", attrs={"class": "container"})[0]
        container_style = parseStyle(container["style"])
        state_layer = comp.find_all("div", attrs={"class": "state-layer"})[0]
        state_layer_style = parseStyle(state_layer["style"])

        target_size = stats["target_size"]
        if not check_width(style, target_size) or not check_height(style, target_size):
            ret += comp_str.capitalize().capitalize() + " needs to have it's width and height changed to " + str(target_size) + ".\n"

        width = stats["width"]
        if not check_width(container_style, width):
            ret += comp_str.capitalize().capitalize() + "'s container element needs to have its width changed to " + str(width) + ".\n"

        height = stats["height"]
        if not check_width(container_style, height):
            ret += comp_str.capitalize().capitalize() + "'s container element needs to have its height changed to " + str(height) + ".\n"

        corner_radius = stats["corner_radius"]
        if not check_corner_radius(container_style, corner_radius):
            ret += comp_str.capitalize().capitalize() + "'s container element needs to have its corner radius changed to " + str(
                corner_radius) + ".\n"

        outline = stats["outline"]
        if not check_outline(container_style, outline):
            ret += comp_str.capitalize().capitalize() + "'s container element needs to have its border width changed to " + str(outline) + ".\n"

        state_layer_size = stats["state_layer_size"]
        if not check_width(state_layer_style, state_layer_size) or not check_height(state_layer_style,
                                                                                    state_layer_size):
            ret += comp_str.capitalize().capitalize() + "'s state layer element needs to have its height and width changed to " + str(
                state_layer_size) + ".\n"

        if ret != "":
            comp.parent.append(soup.new_tag(name = "div",
                                              attrs = {"class": "Mark-" + comp["class"][0],
                                                     "style": "position: " + style["position"] +
                                                              "; left: " + style["left"] +
                                                              "; top: " + style["top"] +
                                                              "; height: " + style["height"] +
                                                              "; width: " + style["width"] +
                                                              "; box-shadow: inset 0px 0px 0px 4px red;",
                                                       "name": "Mark-" + comp["class"][0]}))

    return ret


def check_chip_filter_assistive_suggestion(comps, comp_stats, soup):
    comp_name = "chip"
    stats = comp_stats["chip_filter_assistive_suggestion"]
    ret = ""

    for comp in comps:
        id = comp["id"]
        comp_str = "the " + comp_name + " with id " + id
        style = parseStyle(comp["style"])
        state_layer = comp.find_all("div", attrs={"class": re.compile("state-layers?")})[0]
        label_text = comp.find_all("div", attrs={"class": "label-text"})[0]

        height = stats["height"]
        if not check_height(style, height):
            ret += comp_str.capitalize().capitalize() + " needs to have its height changed to " + str(height) + ".\n"

        corner_radius = stats["corner_radius"]
        if not check_corner_radius(style, corner_radius):
            ret += comp_str.capitalize().capitalize() + " needs to have its corner radius changed to " + str(corner_radius) + ".\n"

        if not "selected" in comp["config"]:
            outline = stats["outline"]
            if not check_outline(style, outline):
                ret += comp_str.capitalize().capitalize() + " needs to have its outline changed to " + str(outline) + ".\n"

        padding_between = stats["padding_between"]
        if not check_padding_between(state_layer, padding_between):
            ret += "Ensure that the distance between every child of " + comp_str + "'s state layer is equal to " + str(
                padding_between) + ".\n"

        text_size = stats["text_size"]
        if not check_text_size(label_text, text_size):
            ret += "The label text in " + comp_str + " needs to have its size changed to " + str(text_size) + ".\n"

        text_weight = stats["text_weight"]
        if not check_text_weight(label_text, text_weight):
            ret += "The label text in " + comp_str + " needs to have its weight changed to " * str(text_weight) + ".\n"

        icon_size = stats["icon_size"]
        if len(comp.find_all("div", attrs={"class": "Leading-icon"})) > 0:
            leading_icon = comp.find_all("div", attrs={"class": "Leading-icon"})[0]
            leading_icon_style = parseStyle(leading_icon["style"])

            if not check_width(leading_icon_style, icon_size) or not check_height(leading_icon_style, icon_size):
                ret += comp_str.capitalize().capitalize() + "'s leading icon needs to have its size changed to " + str(icon_size) + ".\n"

            left_padding_icon = stats["left_padding_icon"]
            if not check_left_padding(state_layer, left_padding_icon):
                ret += "Ensure that every direct child of " + comp_str + "'s state layer has a left value of at least " + str(
                    left_padding_icon) + ".\n"
        else:
            left_padding = stats["left_padding"]
            if not check_left_padding(state_layer, left_padding):
                ret += "Ensure that every direct child of " + comp_str + "'s state layer has a left value of at least " + str(
                    left_padding) + ".\n"

        if len(comp.find_all("div", attrs={"class": "Trailing-icon"})) > 0:
            trailing_icon = comp.find_all("div", attrs={"class": "Trailing-icon"})[0]
            trailing_icon_style = parseStyle(trailing_icon["style"])

            if not check_width(trailing_icon_style, icon_size) or not check_height(trailing_icon_style, icon_size):
                ret += comp_str.capitalize().capitalize() + "'s trailing icon needs to have its size changed to " + str(icon_size) + ".\n"

            right_padding_icon = stats["right_padding_icon"]
            if not check_right_padding(state_layer, right_padding_icon):
                ret += "Ensure that every direct child of " + comp_str + "'s state layer has a distance to the " + comp_name + "'s right side of at least " + str(
                    right_padding_icon) + ".\n"
        else:
            right_padding = stats["right_padding"]
            if not check_right_padding(state_layer, right_padding):
                ret += "Ensure that every direct child of " + comp_str + "'s state layer has a distance to the " + comp_name + "'s right side of at least " + str(
                    right_padding) + ".\n"

        if ret != "":
            comp.parent.append(soup.new_tag(name = "div",
                                              attrs = {"class": "Mark-" + comp["class"][0],
                                                     "style": "position: " + style["position"] +
                                                              "; left: " + style["left"] +
                                                              "; top: " + style["top"] +
                                                              "; height: " + style["height"] +
                                                              "; width: " + style["width"] +
                                                              "; box-shadow: inset 0px 0px 0px 4px red;",
                                                       "name": "Mark-" + comp["class"][0]}))

    return ret


def check_chip_input(comps, comp_stats, soup):
    comp_name = "chip"
    stats = comp_stats["chip_input"]
    ret = ""

    for comp in comps:
        id = comp["id"]
        comp_str = "the " + comp_name + " with id " + id
        style = parseStyle(comp["style"])
        state_layer = comp.find_all("div", attrs={"class": "state-layer"})
        label_text = comp.find_all("div", attrs={"class": "label-text"})

        height = stats["height"]
        if not check_height(style, height):
            ret += comp_str.capitalize().capitalize() + " needs to have its height changed to " + height + ".\n"

        corner_radius = stats["corner_radius"]
        if not check_corner_radius(style, corner_radius):
            ret += comp_str.capitalize().capitalize() + " needs to have its corner radius changed to " + corner_radius + ".\n"

        outline = stats["outline"]
        if not check_outline(style, outline):
            ret += comp_str.capitalize().capitalize() + " needs to have its outline changed to " + outline + ".\n"

        padding_between = stats["padding_between"]
        if not check_padding_between(state_layer, padding_between):
            ret += "Ensure that the distance between every child of " + comp_str + "'s state layer is equal to " + str(
                padding_between) + ".\n"

        text_size = stats["text_size"]
        if not check_text_size(label_text, text_size):
            ret += "The label text in " + comp_str + " needs to have its size changed to " + str(text_size) + ".\n"

        text_weight = stats["text_weight"]
        if not check_text_weight(label_text, text_weight):
            ret += "The label text in " + comp_str + " needs to have its weight changed to " * str(text_weight) + ".\n"

        icon_size = stats["icon_size"]
        if len(comp.find_all("div", attrs={"class": "Icon"})) > 0:
            leading_icon = comp.find_all("div", attrs={"class": "Icon"})[0]
            leading_icon_style = parseStyle(leading_icon["style"])

            if not check_width(leading_icon_style, icon_size) or not check_height(leading_icon_style, icon_size):
                ret += comp_str.capitalize().capitalize() + "'s leading icon needs to have its size changed to " + str(icon_size) + ".\n"

            left_padding_icon = stats["left_padding_icon"]
            if not check_left_padding(state_layer, left_padding_icon):
                ret += "Ensure that every direct child of " + comp_str + "'s state layer has a left value of at least " + str(
                    left_padding_icon) + ".\n"

        elif len(comp.find_all("div", attrs={"class": "User-images/User-Images"})) > 0:
            avatar = comp.find_all("div", attrs={"class": "User-images/User-Images"})[0]
            avatar_size = stats["avatar_size"]
            avatar_shape = stats["avatar_shape"]
            avatar_style = parseStyle(avatar["style"])

            left_padding_avatar = stats["left_padding_avatar"]
            if not check_left_padding(state_layer, left_padding_avatar):
                ret += "Ensure that every direct child of " + comp_str + "'s state layer has a left value of at least " + str(
                    left_padding_avatar) + ".\n"

            if not check_width(avatar_style, avatar_size) or not check_height(avatar_style, avatar_size):
                ret += comp_str.capitalize().capitalize() + "'s avatar needs to have its width and height changed to " + str(avatar_size) + ".\n"

            if not check_corner_radius(avatar_style, avatar_shape):
                ret += comp_str.capitalize().capitalize() + "'s avatar needs to have its border radius changed to " + str(avatar_shape) + ".\n"

        else:
            left_padding = stats["left_padding"]
            if not check_left_padding(state_layer, left_padding):
                ret += "Ensure that every direct child of " + comp_str + "'s state layer has a left value of at least " + str(
                    left_padding) + ".\n"

        if len(comp.find_all("div", attrs={"class": "trailing-icon"})) > 0:
            trailing_icon = comp.find_all("div", attrs={"class": "trailing-icon"})[0]
            trailing_icon_style = parseStyle(trailing_icon["style"])

            if not check_width(trailing_icon_style, icon_size) or not check_height(trailing_icon_style, icon_size):
                ret += comp_str.capitalize().capitalize() + "'s trailing icon needs to have its size changed to " + str(icon_size) + ".\n"

            right_padding_icon = stats["right_padding_icon"]
            if not check_right_padding(comp, right_padding_icon):
                ret += "Ensure that every direct child of " + comp_str + "'s state layer has a distance to the " + comp_name + "'s right side of at least " + str(
                    right_padding_icon) + ".\n"
        else:
            right_padding = stats["right_padding"]
            if not check_right_padding(comp, right_padding):
                ret += "Ensure that every direct child of " + comp_str + "'s state layer has a distance to the " + comp_name + "'s right side of at least " + str(
                    right_padding) + ".\n"

        if ret != "":
            comp.parent.append(soup.new_tag(name = "div",
                                              attrs = {"class": "Mark-" + comp["class"][0],
                                                     "style": "position: " + style["position"] +
                                                              "; left: " + style["left"] +
                                                              "; top: " + style["top"] +
                                                              "; height: " + style["height"] +
                                                              "; width: " + style["width"] +
                                                              "; box-shadow: inset 0px 0px 0px 4px red;",
                                                       "name": "Mark-" + comp["class"][0]}))

    return ret


def check_dialog(comps, comp_stats, soup):
    comp_name = "dialog"
    stats = comp_stats["dialog_basic"]
    ret = ""

    for comp in comps:
        id = comp["id"]
        comp_str = "the " + comp_name + " with id " + id
        style = parseStyle(comp["style"])
        text_section = comp.find_all("div", attrs={"class": "Title-&-Description-"})[0]
        action_section = comp.find_all("div", attrs={"class": "Actions"})[0]
        title = comp.find_all("div", attrs={"class": "headline"})[0]
        button_labels = comp.find_all("div", attrs={"class": "label-text"})

        width_min = stats["width_min"]
        width_max = stats["width_max"]
        if int(style["width"].replace("px", "")) < width_min or int(style["width"].replace("px", "")) > width_max:
            ret += comp_str.capitalize().capitalize() + " needs to have its width changed to a value between " + str(width_min) + " and " + str(
                width_max) + ".\n"

        corner_radius = stats["corner_radius"]
        if not check_corner_radius(style, corner_radius):
            ret += comp_str.capitalize().capitalize() + " needs to have its corner radius changed to " + str(corner_radius) + ".\n"

        top_padding = stats["top_padding"]
        if not check_top_padding(text_section, top_padding):
            ret += "Ensure that every child of " + comp_str + "'s title and description section has a top value of at least " + str(
                top_padding) + ".\n"

        left_padding = stats["left_padding"]
        if not check_left_padding(text_section, left_padding):
            ret += "Ensure that every child of " + comp_str + "'s title and description section has a left value of at least " + str(
                left_padding) + ".\n"

        right_padding = stats["right_padding"]
        if not check_right_padding(text_section, right_padding):
            ret += "Ensure that every child of " + comp_str + "'s title and description section has a distance to the right of at least " + str(
                right_padding) + ".\n"

        padding_body_vert = stats["padding_body_vert"]
        if not check_padding_between_vert(text_section, padding_body_vert):
            ret += "Ensure that the vertical distance between every child of " + comp_str + "'s title and description section is equal to " + str(
                padding_body_vert) + ".\n"

        if not check_top_padding(action_section, top_padding):
            ret += "Ensure that every child of " + comp_str + "'s action section has a top value of at least " + ".\n"

        left_padding_buttons = stats["left_padding_buttons"]
        if not check_left_padding(action_section, left_padding_buttons):
            ret += "Ensure that every child of " + comp_str + "'s action section has a left value of at least " + str(
                left_padding_buttons) + ".\n"

        right_padding_buttons = stats["right_padding_buttons"]
        if not check_right_padding(action_section, right_padding_buttons):
            ret += "Ensure that every child of " + comp_str + "'s action section has a distance to the right of at least " + str(
                right_padding_buttons) + ".\n"

        bottom_padding_actions = stats["bottom_padding_actions"]
        if not check_bottom_padding(action_section, bottom_padding_actions):
            ret += "Ensure that every child of " + comp_str + "'s action section has a distance to the bottom of at least " + str(
                bottom_padding_actions) + ".\n"

        padding_between_buttons = stats["padding_between_buttons"]
        if not check_padding_between(action_section, padding_between_buttons):
            ret += "Ensure that the distance between every child of " + comp_str + "'s action section is equal to " + str(
                padding_between_buttons) + ".\n"

        icon_size = stats["icon_size"]
        align = stats["title_alignment"]
        if len(comp.find_all("div", attrs={"class": "Icon"})) > 0:
            icon = comp.find_all("div", attrs={"class": "Icon"})[0]
            icon_style = parseStyle(icon["style"])
            align = stats["title_alignment_icon"]

            if not check_width(icon_style, icon_size) or not check_height(icon_style, icon_size):
                ret += "The icon in " + comp_str + " needs to have its height and weight set to " + str(
                    icon_size) + ".\n"

        divider_height = stats["divider_height"]
        top_padding_divider = stats["top_padding_divider"]
        if len(comp.find_all("div", attrs={"class": "divider"})) > 0:
            divider_section = comp.find_all("div", attrs={"class": "divider"})[0]
            divider = divider_section.find_all("div", attrs={"class": "horizontal/full-width"})[0]
            divider_style = parseStyle(divider["style"])

            if not check_top_padding(divider_section, top_padding_divider):
                ret += "The distance of the divider in " + comp_str + " to the top of its containing section needs to be changed to " + str(
                    top_padding_divider) + ".\n"

            if not check_height(divider_style, divider_height):
                ret += "The height of the divider in " + comp_str + " needs to be changed to " + str(
                    divider_height) + ".\n"

        text_size_title = stats["text_size_title"]
        if not check_text_size(title, text_size_title):
            ret += "The size of " + comp_str + "'s title needs to be changed to " + str(text_size_title) + ".\n"

        text_weight_title = stats["text_weight_title"]
        if not check_text_weight(title, text_weight_title):
            ret += "The weight of " + comp_str + "'s title needs to be changed to " + str(text_weight_title) + ".\n"

        if not check_text_align(title, align):
            ret += "Ensure that " + comp_str + "'s title is aligned to the " + align + ".\n"

        if len(comp.find_all("div", attrs={"class": "supporting_text"})) > 0:
            body = comp.find_all("div", attrs={"class": "supporting_text"})[0]
            text_size_body = stats["text_size_body"]
            if not check_text_size(body, text_size_body):
                ret += "The size of " + comp_str + "'s body needs to be changed to " + str(text_size_body) + ".\n"

            text_weight_body = stats["text_weight_body"]
            if not check_text_weight(body, text_weight_body):
                ret += "The weight of " + comp_str + "'s body needs to be changed to " + str(text_weight_body) + ".\n"

        text_size_buttons = stats["text_size_buttons"]
        text_weight_buttons = stats["text_weight_buttons"]
        for label in button_labels:
            label_id = label["id"]
            label_str = "the label text with id " + label_id + " in " + comp_str
            if not check_text_size(label, text_size_buttons):
                ret += "The size of " + label_str + " needs to be changed to " + str(text_size_buttons) + ".\n"

            if not check_text_weight(label, text_weight_buttons):
                ret += "The size of " + label_str + " needs to be changed to " + str(text_weight_buttons) + ".\n"

        if ret != "":
            comp.parent.append(soup.new_tag(name = "div",
                                              attrs = {"class": "Mark-" + comp["class"][0],
                                                     "style": "position: " + style["position"] +
                                                              "; left: " + style["left"] +
                                                              "; top: " + style["top"] +
                                                              "; height: " + style["height"] +
                                                              "; width: " + style["width"] +
                                                              "; box-shadow: inset 0px 0px 0px 4px red;",
                                                       "name": "Mark-" + comp["class"][0]}))

    return ret


def check_divider(comps, comp_stats, soup):
    comp_name = "divider"
    stats = comp_stats["divider"]
    ret = ""

    for comp in comps:
        id = comp["id"]
        comp_str = "the " + comp_name + " with id " + id
        style = parseStyle(comp["style"])

        height = stats["height"]
        if not check_height(style, height):
            ret += comp_str.capitalize().capitalize() + "'s height needs to be set to " + str(height) + ".\n"

        if len(comp.find_all("div", attrs={"class": "Subheader"})) > 0:
            subhead = comp.find_all("div", attrs={"class": "Subheader"})[0]
            subhead_style = parseStyle(subhead["style"])

            if int(subhead_style["top"].replace("px", "")) != 5:
                ret += "The subheader in " + comp_str + " needs to have its top value set to 5.\n"

        if ret != "":
            comp.parent.append(soup.new_tag(name = "div",
                                              attrs = {"class": "Mark-" + comp["class"][0],
                                                     "style": "position: " + style["position"] +
                                                              "; left: " + style["left"] +
                                                              "; top: " + style["top"] +
                                                              "; height: " + style["height"] +
                                                              "; width: " + style["width"] +
                                                              "; box-shadow: inset 0px 0px 0px 4px red;",
                                                       "name": "Mark-" + comp["class"][0]}))

    return ret


def check_list_item_one_line(comps, comp_stats, soup):
    comp_name = "list item"
    stats = comp_stats["list_item_one_line"]
    ret = ""

    for comp in comps:
        id = comp["id"]
        comp_str = "the " + comp_name + " with id " + id
        style = parseStyle(comp["style"])
        state_layer = comp.find_all("div", attrs={"class": "state-layer"})[0]
        headline = comp.find_all("div", attrs={"class": "Headline"})[0]

        padding_left = stats["padding_left"]
        if not check_left_padding(state_layer, padding_left):
            ret += "Ensure that every direct child of " + comp_str + "'s state layer has a left value of at least " + str(
                padding_left) + " and the leftmost child has a left value " + str(padding_left) + ".\n"

        padding_right = stats["padding_right"]
        if not check_right_padding(state_layer, padding_right):
            ret += "Ensure that every direct child of " + comp_str + "'s state layer has a distance to the right of at least " + str(
                padding_right) + ".\n"

        padding_between = stats["padding_between"]
        if not check_padding_between(state_layer, padding_between):
            ret += "Ensure that the distance between every direct child of " + comp_str + " is equal to " + str(
                padding_between) + ".\n"

        label_text_size = stats["label_text_size"]
        if not check_text_size(headline, label_text_size):
            ret += "The headline of " + comp_str + " needs to have its size changed to " + str(label_text_size) + ".\n"

        label_text_weight = stats["label_text_weight"]
        if not check_text_weight(headline, label_text_weight):
            ret += "The headline of " + comp_str + " needs to have its weight changed to " + str(
                label_text_weight) + ".\n"

        if len(comp.find_all("div", attrs={"class": "Building-Blocks/image-Thumbnail"})) > 0:
            image = comp.find_all("div", attrs={"class": "Building-Blocks/image-Thumbnail"})[0]
            image_style = parseStyle(image["style"])

            image_size = stats["image_size"]
            if not check_height(image_style, image_size) or not check_width(image_size, image_style):
                ret += "The image in " + comp_str + " needs to have its height and width changed to " + str(
                    image_size) + ".\n"

            ret += "The label text in " + comp_str + " should be vertically centered.\n"

            height = stats["height_image"]
            padding_top = stats["padding_top"]
            padding_bottom = stats["padding_bottom"]

        elif len(comp.find_all("div", attrs={"class": "Building-Blocks/video-Thumbnail"})) > 0:
            video = comp.find_all("div", attrs={"class": "Building-Blocks/video-Thumbnail"})[0]
            video_style = parseStyle(video["style"])

            video_height = stats["video_height"]
            if not check_height(video_style, video_height):
                ret += "The video thumbnail in " + comp_str + " needs to have its height changed to " + str(
                    video_height) + ".\n"

            video_width = stats["video_width"]
            if not check_width(video_style, video_width):
                ret += "The video thumbnail in " + comp_str + " needs to have its width changed to " + str(
                    video_width) + ".\n"

            ret += "The content and trailing sections in " + comp_str + " should be aligned to the top of their container.\n"
            height = stats["height_video"]
            padding_top = stats["padding_top_video"]
            padding_bottom = stats["padding_bottom_video"]

        else:
            if not check_centered_vert(comp):
                ret += "The contents of " + comp_str + " should be vertically centered.\n"
            height = stats["height"]
            padding_top = stats["padding_top"]
            padding_bottom = stats["padding_bottom"]

        if not check_height(style, height):
            ret += comp_str.capitalize().capitalize() + " needs to have its height changed to " + str(height) + ".\n"

        if not check_top_padding(state_layer, padding_top):
            ret += "Ensure that every direct child of " + comp_str + "'s state layer has a top value of at least " + ".\n"

        if not check_bottom_padding(state_layer, padding_bottom):
            ret += "Ensure that every direct child of " + comp_str + "'s state layer has a distance to the bottom of at least " + str(
                padding_bottom) + ".\n"

        if len(comp.find_all("div", attrs={"class": re.compile("^Icon")})) > 0:
            for icon in comp.find_all("div", attrs={"class": re.compile("^Icon")}):
                icon_style = parseStyle(icon["style"])
                icon_id = icon["id"]

                icon_size = stats["icon_size"]
                if not check_height(icon_style, icon_size) or not check_width(icon_style, icon_size):
                    ret += "The icon with id " + icon_id + " in " + comp_str + " needs to have its height and width changed to " + str(
                        icon_size) + ".\n"

        if len(comp.find_all("div", attrs={"class": "Building-Blocks/Monogram"})) > 0:
            monogram = comp.find_all("div", attrs={"class": "Building-Blocks/Monogram"})[0]
            monogram_style = parseStyle(monogram["style"])
            initial = monogram.find_all("div", attrs={"class": "Initial"})[0]

            monogram_size = stats["monogram_size"]
            if not check_height(monogram_style, monogram_size) or not check_width(monogram_style, monogram_size):
                ret += "The monogram in " + comp_str + " needs to have its height and width changed to " + str(
                    monogram_size) + ".\n"

            monogram_text_size = stats["monogram_text_size"]
            if not check_text_size(initial, monogram_text_size):
                ret += "The initial on the monogram in " + comp_str + " needs to have its size changed to " + str(
                    monogram_text_size) + ".\n"

            monogram_text_weight = stats["monogram_text_weight"]
            if not check_text_weight(initial, monogram_text_weight):
                ret += "The initial on the monogram in " + comp_str + " needs to have its weight changed to " + str(
                    monogram_text_weight) + ".\n"

        if len(comp.find_all("div", attrs={"class": "Overline"})) > 0:
            overline = comp.find_all("div", attrs={"class": "Overline"})[0]

            overline_text_size = stats["overline_text_size"]
            if not check_text_size(overline, overline_text_size):
                ret += "The overline in " + comp_str + " needs to have its size changed to " + str(
                    overline_text_size) + ".\n"

            overline_text_weight = stats["overline_text_weight"]
            if not check_text_weight(overline, overline_text_weight):
                ret += "The overline in " + comp_str + " needs to have its weight changed to " + str(
                    overline_text_weight) + ".\n"

        if len(comp.find_all("div", attrs={"class": "Trailing-supporting-text"})) > 0:
            trailing_supporting_text = comp.find_all("div", attrs={"class": "Trailing-supporting-text"})[0]

            trailing_supporting_text_size = stats["trailing_supporting_text_size"]
            if not check_text_size(trailing_supporting_text, trailing_supporting_text_size):
                ret += "The trailing supporting text in " + comp_str + " needs to have its size changed to " + str(
                    trailing_supporting_text_size) + ".\n"

            trailing_supporting_text_weight = stats["trailing_supporting_text_weight"]
            if not check_text_weight(trailing_supporting_text, trailing_supporting_text_weight):
                ret += "The trailing supporting text in " + comp_str + " needs to have its weight changed to " + str(
                    trailing_supporting_text_weight) + ".\n"

        if ret != "":
            comp.parent.append(soup.new_tag(name = "div",
                                              attrs = {"class": "Mark-" + comp["class"][0],
                                                     "style": "position: " + style["position"] +
                                                              "; left: " + style["left"] +
                                                              "; top: " + style["top"] +
                                                              "; height: " + style["height"] +
                                                              "; width: " + style["width"] +
                                                              "; box-shadow: inset 0px 0px 0px 4px red;",
                                                       "name": "Mark-" + comp["class"][0]}))

    return ret


def check_list_item_two_line(comps, comp_stats, soup):
    comp_name = "list item"
    stats = comp_stats["list_item_two_line"]
    ret = ""

    for comp in comps:
        id = comp["id"]
        comp_str = "the " + comp_name + " with id " + id
        style = parseStyle(comp["style"])
        state_layer = comp.find_all("div", attrs={"class": "state-layer"})[0]
        headline = comp.find_all("div", attrs={"class": "Headline"})[0]

        padding_left = stats["padding_left"]
        if not check_left_padding(state_layer, padding_left):
            ret += "Ensure that every direct child of " + comp_str + "'s state layer has a left value of at least " + str(
                padding_left) + ".\n"

        padding_right = stats["padding_right"]
        if not check_right_padding(state_layer, padding_right):
            ret += "Ensure that every direct child of " + comp_str + "'s state layer has a distance to the right of at least " + str(
                padding_right) + ".\n"

        padding_between = stats["padding_between"]
        if not check_padding_between(state_layer, padding_between):
            ret += "Ensure that the distance between every direct child of " + comp_str + " is equal to " + str(
                padding_between) + ".\n"

        label_text_size = stats["label_text_size"]
        if not check_text_size(headline, label_text_size):
            ret += "The headline of " + comp_str + " needs to have its size changed to " + str(label_text_size) + ".\n"

        label_text_weight = stats["label_text_weight"]
        if not check_text_weight(headline, label_text_weight):
            ret += "The headline of " + comp_str + " needs to have its weight changed to " + str(
                label_text_weight) + ".\n"

        if len(comp.find_all("div", attrs={"class": "Building-Blocks/image-Thumbnail"})) > 0:
            image = comp.find_all("div", attrs={"class": "Building-Blocks/image-Thumbnail"})[0]
            image_style = parseStyle(image["style"])

            image_size = stats["image_size"]
            if not check_height(image_style, image_size) or not check_width(image_size, image_style):
                ret += "The image in " + comp_str + " needs to have its height and width changed to " + str(
                    image_size) + ".\n"

            ret += "The label text in " + comp_str + " should be vertically centered.\n"

            height = stats["height_image"]
            padding_top = stats["padding_top"]
            padding_bottom = stats["padding_bottom"]

        elif len(comp.find_all("div", attrs={"class": "Building-Blocks/video-Thumbnail"})) > 0:
            video = comp.find_all("div", attrs={"class": "Building-Blocks/video-Thumbnail"})[0]
            video_style = parseStyle(video["style"])

            video_height = stats["video_height"]
            if not check_height(video_style, video_height):
                ret += "The video thumbnail in " + comp_str + " needs to have its height changed to " + str(
                    video_height) + ".\n"

            video_width = stats["video_width"]
            if not check_width(video_style, video_width):
                ret += "The video thumbnail in " + comp_str + " needs to have its width changed to " + str(
                    video_width) + ".\n"

            ret += "The content and trailing sections in " + comp_str + " should be aligned to the top of their container.\n"
            height = stats["height_video"]
            padding_top = stats["padding_top_video"]
            padding_bottom = stats["padding_bottom_video"]

        else:
            if not check_centered_vert(comp):
                ret += "The contents of " + comp_str + " should be vertically centered.\n"
            height = stats["height"]
            padding_top = stats["padding_top"]
            padding_bottom = stats["padding_bottom"]

        if not check_height(style, height):
            ret += comp_str.capitalize().capitalize() + " needs to have its height changed to " + str(height) + ".\n"

        if not check_top_padding(state_layer, padding_top):
            ret += "Ensure that every direct child of " + comp_str + "'s state layer has a top value of at least " + str(
                padding_top) + ".\n"

        if not check_bottom_padding(state_layer, padding_bottom):
            ret += "Ensure that every direct child of " + comp_str + "'s state layer has a distance to the bottom of at least " + str(
                padding_bottom) + ".\n"

        if len(comp.find_all("div", attrs={"class": re.compile("^Icon")})) > 0:
            for icon in comp.find_all("div", attrs={"class": re.compile("^Icon")}):
                icon_style = parseStyle(icon["style"])
                icon_id = icon["id"]

                icon_size = stats["icon_size"]
                if not check_height(icon_style, icon_size) or not check_width(icon_style, icon_size):
                    ret += "The icon with id " + icon_id + " in " + comp_str + " needs to have its height and width changed to " + str(
                        icon_size) + ".\n"

        if len(comp.find_all("div", attrs={"class": "Building-Blocks/Monogram"})) > 0:
            monogram = comp.find_all("div", attrs={"class": "Building-Blocks/Monogram"})[0]
            monogram_style = parseStyle(monogram["style"])
            initial = monogram.find_all("div", attrs={"class": "Initial"})[0]

            monogram_size = stats["monogram_size"]
            if not check_height(monogram_style, monogram_size) or not check_width(monogram_style, monogram_size):
                ret += "The monogram in " + comp_str + " needs to have its height and width changed to " + str(
                    monogram_size) + ".\n"

            monogram_text_size = stats["monogram_text_size"]
            if not check_text_size(initial, monogram_text_size):
                ret += "The initial on the monogram in " + comp_str + " needs to have its size changed to " + str(
                    monogram_text_size) + ".\n"

            monogram_text_weight = stats["monogram_text_weight"]
            if not check_text_weight(initial, monogram_text_weight):
                ret += "The initial on the monogram in " + comp_str + " needs to have its weight changed to " + str(
                    monogram_text_weight) + ".\n"

        if len(comp.find_all("div", attrs={"class": "Overline"})) > 0:
            overline = comp.find_all("div", attrs={"class": "Overline"})[0]

            overline_text_size = stats["overline_text_size"]
            if not check_text_size(overline, overline_text_size):
                ret += "The overline in " + comp_str + " needs to have its size changed to " + str(
                    overline_text_size) + ".\n"

            overline_text_weight = stats["overline_text_weight"]
            if not check_text_weight(overline, overline_text_weight):
                ret += "The overline in " + comp_str + " needs to have its weight changed to " + str(
                    overline_text_weight) + ".\n"

        if len(comp.find_all("div", attrs={"class": "Trailing-supporting-text"})) > 0:
            trailing_supporting_text = comp.find_all("div", attrs={"class": "Trailing-supporting-text"})[0]

            trailing_supporting_text_size = stats["trailing_supporting_text_size"]
            if not check_text_size(trailing_supporting_text, trailing_supporting_text_size):
                ret += "The trailing supporting text in " + comp_str + " needs to have its size changed to " + str(
                    trailing_supporting_text_size) + ".\n"

            trailing_supporting_text_weight = stats["trailing_supporting_text_weight"]
            if not check_text_weight(trailing_supporting_text, trailing_supporting_text_weight):
                ret += "The trailing supporting text in " + comp_str + " needs to have its weight changed to " + str(
                    trailing_supporting_text_weight) + ".\n"

        if len(comp.find_all("div", attrs={"class": "Supporting-text"})) > 0:
            supporting_text = comp.find_all("div", attrs={"class": "Supporting-text"})[0]

            supporting_text_size = stats["supporting_text_size"]
            if not check_text_size(supporting_text, supporting_text_size):
                ret += "The supporting text in " + comp_str + " needs to have its size changed to " + str(
                    supporting_text_size) + ".\n"

            suppporting_text_weight = stats["suppporting_text_weight"]
            if not check_text_weight(supporting_text, suppporting_text_weight):
                ret += "The supporting text in " + comp_str + " needs to have its weight changed to " + str(
                    suppporting_text_weight) + ".\n"

        if ret != "":
            comp.parent.append(soup.new_tag(name = "div",
                                              attrs = {"class": "Mark-" + comp["class"][0],
                                                     "style": "position: " + style["position"] +
                                                              "; left: " + style["left"] +
                                                              "; top: " + style["top"] +
                                                              "; height: " + style["height"] +
                                                              "; width: " + style["width"] +
                                                              "; box-shadow: inset 0px 0px 0px 4px red;",
                                                       "name": "Mark-" + comp["class"][0]}))

    return ret


def check_list_item_three_line(comps, comp_stats, soup):
    comp_name = "list item"
    stats = comp_stats["list_item_three_line"]
    ret = ""

    for comp in comps:
        id = comp["id"]
        comp_str = "the " + comp_name + " with id " + id
        style = parseStyle(comp["style"])
        state_layer = comp.find_all("div", attrs={"class": "state-layer"})[0]
        headline = comp.find_all("div", attrs={"class": "Headline"})[0]

        padding_left = stats["padding_left"]
        if not check_left_padding(state_layer, padding_left):
            ret += "Ensure that every direct child of " + comp_str + "'s state layer has a left value of at least " + str(
                padding_left) + ".\n"

        padding_right = stats["padding_right"]
        if not check_right_padding(state_layer, padding_right):
            ret += "Ensure that every direct child of " + comp_str + "'s state layer has a distance to the right of at least " + str(
                padding_right) + ".\n"

        padding_between = stats["padding_between"]
        if not check_padding_between(state_layer, padding_between):
            ret += "Ensure that the distance between every direct child of " + comp_str + " is equal to " + str(
                padding_between) + ".\n"

        label_text_size = stats["label_text_size"]
        if not check_text_size(headline, label_text_size):
            ret += "The headline of " + comp_str + " needs to have its size changed to " + str(label_text_size) + ".\n"

        label_text_weight = stats["label_text_weight"]
        if not check_text_weight(headline, label_text_weight):
            ret += "The headline of " + comp_str + " needs to have its weight changed to " + str(
                label_text_weight) + ".\n"

        if len(comp.find_all("div", attrs={"class": "Building-Blocks/image-Thumbnail"})) > 0:
            image = comp.find_all("div", attrs={"class": "Building-Blocks/image-Thumbnail"})[0]
            image_style = parseStyle(image["style"])

            image_size = stats["image_size"]
            if not check_height(image_style, image_size) or not check_width(image_size, image_style):
                ret += "The image in " + comp_str + " needs to have its height and width changed to " + str(
                    image_size) + ".\n"

        elif len(comp.find_all("div", attrs={"class": "Building-Blocks/video-Thumbnail"})) > 0:
            video = comp.find_all("div", attrs={"class": "Building-Blocks/video-Thumbnail"})[0]
            video_style = parseStyle(video["style"])

            video_height = stats["video_height"]
            if not check_height(video_style, video_height):
                ret += "The video thumbnail in " + comp_str + " needs to have its height changed to " + str(
                    video_height) + ".\n"

            video_width = stats["video_width"]
            if not check_width(video_style, video_width):
                ret += "The video thumbnail in " + comp_str + " needs to have its width changed to " + str(
                    video_width) + ".\n"

        ret += "The content and trailing sections in " + comp_str + " should be aligned to the top of their container.\n"

        height = stats["height"]
        if not check_height(style, height):
            ret += comp_str.capitalize().capitalize() + " needs to have its height changed to " + str(height) + ".\n"

        padding_top = stats["padding_top"]
        if not check_top_padding(state_layer, padding_top):
            ret += "Ensure that every direct child of " + comp_str + "'s state layer has a top value of at least " + str(
                padding_top) + ".\n"

        padding_bottom = stats["padding_bottom"]
        if not check_bottom_padding(state_layer, padding_bottom):
            ret += "Ensure that every direct child of " + comp_str + "'s state layer has a distance to the bottom of at least " + str(
                padding_bottom) + ".\n"

        if len(comp.find_all("div", attrs={"class": re.compile("^Icon")})) > 0:
            for icon in comp.find_all("div", attrs={"class": re.compile("^Icon")}):
                icon_style = parseStyle(icon["style"])
                icon_id = icon["id"]

                icon_size = stats["icon_size"]
                if not check_height(icon_style, icon_size) or not check_width(icon_style, icon_size):
                    ret += "The icon with id " + icon_id + " in " + comp_str + " needs to have its height and width changed to " + str(
                        icon_size) + ".\n"

        if len(comp.find_all("div", attrs={"class": "Building-Blocks/Monogram"})) > 0:
            monogram = comp.find_all("div", attrs={"class": "Building-Blocks/Monogram"})[0]
            monogram_style = parseStyle(monogram["style"])
            initial = monogram.find_all("div", attrs={"class": "Initial"})[0]

            monogram_size = stats["monogram_size"]
            if not check_height(monogram_style, monogram_size) or not check_width(monogram_style, monogram_size):
                ret += "The monogram in " + comp_str + " needs to have its height and width changed to " + str(
                    monogram_size) + ".\n"

            monogram_text_size = stats["monogram_text_size"]
            if not check_text_size(initial, monogram_text_size):
                ret += "The initial on the monogram in " + comp_str + " needs to have its size changed to " + str(
                    monogram_text_size) + ".\n"

            monogram_text_weight = stats["monogram_text_weight"]
            if not check_text_weight(initial, monogram_text_weight):
                ret += "The initial on the monogram in " + comp_str + " needs to have its weight changed to " + str(
                    monogram_text_weight) + ".\n"

        if len(comp.find_all("div", attrs={"class": "Overline"})) > 0:
            overline = comp.find_all("div", attrs={"class": "Overline"})[0]

            overline_text_size = stats["overline_text_size"]
            if not check_text_size(overline, overline_text_size):
                ret += "The overline in " + comp_str + " needs to have its size changed to " + str(
                    overline_text_size) + ".\n"

            overline_text_weight = stats["overline_text_weight"]
            if not check_text_weight(overline, overline_text_weight):
                ret += "The overline in " + comp_str + " needs to have its weight changed to " + str(
                    overline_text_weight) + ".\n"

        if len(comp.find_all("div", attrs={"class": "Trailing-supporting-text"})) > 0:
            trailing_supporting_text = comp.find_all("div", attrs={"class": "Trailing-supporting-text"})[0]

            trailing_supporting_text_size = stats["trailing_supporting_text_size"]
            if not check_text_size(trailing_supporting_text, trailing_supporting_text_size):
                ret += "The trailing supporting text in " + comp_str + " needs to have its size changed to " + str(
                    trailing_supporting_text_size) + ".\n"

            trailing_supporting_text_weight = stats["trailing_supporting_text_weight"]
            if not check_text_weight(trailing_supporting_text, trailing_supporting_text_weight):
                ret += "The trailing supporting text in " + comp_str + " needs to have its weight changed to " + str(
                    trailing_supporting_text_weight) + ".\n"

        if len(comp.find_all("div", attrs={"class": "Supporting-text"})) > 0:
            supporting_text = comp.find_all("div", attrs={"class": "Supporting-text"})[0]

            supporting_text_size = stats["supporting_text_size"]
            if not check_text_size(supporting_text, supporting_text_size):
                ret += "The supporting text in " + comp_str + " needs to have its size changed to " + str(
                    supporting_text_size) + ".\n"

            suppporting_text_weight = stats["suppporting_text_weight"]
            if not check_text_weight(supporting_text, suppporting_text_weight):
                ret += "The supporting text in " + comp_str + " needs to have its weight changed to " + str(
                    suppporting_text_weight) + ".\n"

        if ret != "":
            comp.parent.append(soup.new_tag(name = "div",
                                              attrs = {"class": "Mark-" + comp["class"][0],
                                                     "style": "position: " + style["position"] +
                                                              "; left: " + style["left"] +
                                                              "; top: " + style["top"] +
                                                              "; height: " + style["height"] +
                                                              "; width: " + style["width"] +
                                                              "; box-shadow: inset 0px 0px 0px 4px red;",
                                                       "name": "Mark-" + comp["class"][0]}))

    return ret


def check_list(comps, comp_stats, soup):
    ret = ""
    for comp in comps:
        list_items = comp.find_all("div", attrs={"class": re.compile("List item")})
        for list_item in list_items:
            if list_item["config"] == "1-line":
                ret += check_list_item_one_line([list_item], comp_stats) + ".\n"
            if list_item["config"] == "2-line":
                ret += check_list_item_two_line([list_item], comp_stats) + ".\n"
            if list_item["config"] == "3-line":
                ret += check_list_item_three_line([list_item], comp_stats) + ".\n"
    return ret


def check_menu(comps, comp_stats, soup):
    comp_name = "menu"
    stats = comp_stats["menu"]
    ret = ""

    for comp in comps:
        id = comp["id"]
        comp_str = "the " + comp_name + " with id " + id
        style = parseStyle(comp["style"])

        min_width = stats["min_width"]
        max_width = stats["max_width"]
        if not check_width(style, min_width) or not check_width(style, max_width):
            ret += comp_str.capitalize().capitalize() + " needs to have its width changed to a value between " + str(min_width) +\
            " and " + str(max_width) + ".\n"

        corner_radius = stats["corner_radius"]
        if not check_corner_radius(style, corner_radius):
            ret += comp_str.capitalize().capitalize() + " needs to have its corner radius changed to " + str(corner_radius) + ".\n"

        top_padding = stats["top_padding"]
        if not check_top_padding(comp, top_padding):
            ret += "Ensure that every direct child of " + comp_str + " has a top value of at least " + str(
                top_padding) + ".\n"

        bottom_padding = stats["bottom_padding"]
        if not check_bottom_padding(comp, bottom_padding):
            ret += "Ensure that every direct child of " + comp_str + " has a distance to the bottom of at least " + str(
                bottom_padding) + ".\n"

        items = comp.find_all("div", attrs={"class": re.compile("^Menu-list-item")})
        for item in items:
            id = item["id"]
            item_str = "the menu item with id " + id
            item_style = parseStyle(item["style"])
            state_layer = item.find_all("div", attrs={"class": "state-layer"})[0]
            label_text = item.find_all("div", attrs={"class": "Label-text"})[0]

            left_padding = stats["left_padding"]
            if not check_left_padding(state_layer, left_padding):
                ret += "Ensure that every direct child of " + item_str + " has a left value of at least " + str(
                    left_padding) + ".\n"

            right_padding = stats["right_padding"]
            if not check_right_padding(state_layer, right_padding):
                ret += "Ensure that every direct child of " + item_str + " has a distance to the right of at least " + str(
                    right_padding) + ".\n"

            top_padding = stats["top_padding"]
            if not check_top_padding(state_layer, top_padding):
                ret += "Ensure that every direct child of " + item_str + " has a top value of at least " + str(
                    top_padding) + ".\n"

            bottom_padding = stats["bottom_padding"]
            if not check_bottom_padding(state_layer, bottom_padding):
                ret += "Ensure that every direct child of " + item_str + " has a distance to the bottom of at least " + str(
                    bottom_padding) + ".\n"

            item_height = stats["item_height"]
            if not check_height(item_style, item_height):
                ret += item_str + " needs to have its height changed to " + str(item_height) + ".\n"

            for icon in comp.find_all("div", attrs={"class": "icon"}):
                icon_style = parseStyle(icon["style"])

                icon_size = stats["icon_size"]
                if not check_height(icon_style, icon_size) or not check_width(icon_style, icon_size):
                    ret += "The icon in " + item_str + " needs to have its height and width changed to " + str(
                        icon_size) + ".\n"

            text_size = stats["text_size"]
            if not check_text_size(label_text, text_size):
                ret += "The label text of " + item_str + " needs to have its size changed to " + str(text_size) + ".\n"

            text_weight = stats["text_weight"]
            if not check_text_weight(label_text, text_weight):
                ret += "The label text of " + item_str + " needs to have its weight changed to " + str(
                    text_weight) + ".\n"

            if len(item.find_all("div", attrs={"class": "Supporting-text"})) > 0:
                supporting_text = item.find_all("div", attrs={"class": "Supporting-text"})[0]

                supporting_text_size = stats["supporting_text_size"]
                if not check_text_size(supporting_text, supporting_text_size):
                    ret += "The supporting text of " + item_str + " needs to have its size changed to " + str(
                        supporting_text_size) + ".\n"

                supporting_text_weight = stats["supporting_text_weight"]
                if not check_text_weight(supporting_text, supporting_text_weight):
                    ret += "The supporting text of " + item_str + " needs to have its weight changed to " + str(
                        supporting_text_weight) + ".\n"

            if len(item.find_all("div", attrs={"class": "Divider"})) > 0:
                divider = item.find_all("div", attrs={"class": "Divider"})[0]

                divider_padding = stats["divider_padding"]
                if not check_top_padding(divider, divider_padding) or not check_bottom_padding(divider,
                                                                                               divider_padding):
                    ret += "Ensure that the divider in " + item_str + " has a distance to the top and bottom of its container that is equal to " + str(
                        divider_padding) + ".\n"

        if ret != "":
            comp.parent.append(soup.new_tag(name = "div",
                                              attrs = {"class": "Mark-" + comp["class"][0],
                                                     "style": "position: " + style["position"] +
                                                              "; left: " + style["left"] +
                                                              "; top: " + style["top"] +
                                                              "; height: " + style["height"] +
                                                              "; width: " + style["width"] +
                                                              "; box-shadow: inset 0px 0px 0px 4px red;",
                                                       "name": "Mark-" + comp["class"][0]}))

    return ret


def check_navigation_bar(comps, comp_stats, soup):
    comp_name = "navigation bar"
    stats = comp_stats["navigation_bar"]
    ret = ""

    for comp in comps:
        id = comp["id"]
        comp_str = "the " + comp_name + " with id " + id
        style = parseStyle(comp["style"])

        width = stats["width"]
        if width == "device":
            width = DEVICE_WIDTH
        if not check_width(style, width):
            ret += comp_str.capitalize().capitalize() + " needs to have its width set to " + str(width) + ".\n"

        height = stats["height"]
        if not check_height(style, height):
            ret += comp_str.capitalize().capitalize() + " needs to have its height set to " + str(height) + ".\n"

        corner_radius = stats["corner_radius"]
        if not check_corner_radius(style, corner_radius):
            ret += comp_str.capitalize().capitalize() + " needs to have its corner radius set to " + str(corner_radius) + ".\n"

        left_padding = stats["left_padding"]
        if not check_left_padding(comp, left_padding):
            ret += "Ensure that every direct child of " + comp_str + " has a left value of at least " + str(
                left_padding) + ".\n"

        right_padding = stats["right_padding"]
        if not check_right_padding(comp, right_padding):
            ret += "Ensure that every direct child of " + comp_str + " has a distance to the right of at least " + str(
                right_padding) + ".\n"

        top_padding = stats["top_padding"]
        if not check_top_padding(comp, top_padding):
            ret += "Ensure that every direct child of " + comp_str + " has a top value of " + str(
                top_padding) + ".\n"

        segments = comp.find_all("div", attrs={"class": re.compile("^Segment")})
        num_segments = len(segments)
        segment_width = (width - (16 + (num_segments - 1) * 8))/num_segments
        for segment in segments:
            segment_style = parseStyle(segment["style"])
            segment_str = "the segment with id " + segment["id"] + " in " + comp_str
            icon = segment.find_all("div", attrs={"class": "Icon"})[0]
            icon_style = parseStyle(icon["style"])
            icon_container = segment.find_all("div", attrs={"class": "icon-container"})[0]
            icon_container_style = parseStyle(icon_container["style"])

            if not check_width(segment_style, segment_width):
                ret += segment_str + " needs to have its width changed to " + str(segment_width) + ".\n"

            top_padding = stats["top_padding"]
            if not check_top_padding(segment, top_padding):
                ret += "Ensure that every direct child of " + segment_str + " has a top value of at least " + str(
                    top_padding) + ".\n"

            bottom_padding = stats["bottom_padding"]
            if not check_bottom_padding(segment, bottom_padding):
                ret += "Ensure that every direct child of " + segment_str + " has a distance to the bottom of at least " + str(
                    bottom_padding) + ".\n"

            padding_between_vert = stats["padding_between_vert"]
            if not check_padding_between_vert(segment, padding_between_vert):
                ret += "Ensure that the vertical distance between every direct child of " + segment_str + " is equal to " + str(
                    padding_between_vert) + ".\n"

            icon_size = stats["icon_size"]
            if not check_height(icon_style, icon_size) or not check_width(icon_style, icon_size):
                ret += "The icon in " + segment_str + " needs to have its height and width set to " + str(
                    icon_size) + ".\n"

            label_text_weight = stats["label_text_weight"]
            if "background-color" in icon_container["style"]:
                label_text_weight = stats["label_text_weight_active"]
                active_indicator_height = stats["active_indicator_height"]
                if not check_height(icon_container_style, active_indicator_height):
                    ret += "The icon container in " + segment_str + " needs to have its height changed to " + str(
                        active_indicator_height) + ".\n"

                active_indicator_width = stats["active_indicator_width"]
                if not check_width(icon_container_style, active_indicator_width):
                    ret += "The icon container in " + segment_str + " needs to have its width changed to " + str(
                        active_indicator_width) + ".\n"

                active_indicator_corner_radius = stats["active_indicator_corner_radius"]
                if not check_corner_radius(icon_container_style, active_indicator_corner_radius):
                    ret += "The icon container in " + segment_str + " needs to have its corner radius changed to " + str(
                        active_indicator_corner_radius) + ".\n"

            if len(segment.find_all("div", attrs={"class": "label-text"})) > 0:
                label_text = segment.find_all("div", attrs={"class": "label-text"})[0]
                label_text_size = stats["label_text_size"]
                if not check_text_size(label_text, label_text_size):
                    ret += "The label text of " + segment_str + " needs to have its size set to " + str(
                        label_text_size) + ".\n"


                if not check_text_weight(label_text, label_text_weight):
                    ret += "The label text of " + segment_str + " needs to have its weight set to " + str(
                        label_text_weight) + ".\n"

        if ret != "":
            comp.parent.append(soup.new_tag(name = "div",
                                              attrs = {"class": "Mark-" + comp["class"][0],
                                                     "style": "position: " + style["position"] +
                                                              "; left: " + style["left"] +
                                                              "; top: " + style["top"] +
                                                              "; height: " + style["height"] +
                                                              "; width: " + style["width"] +
                                                              "; box-shadow: inset 0px 0px 0px 4px red;",
                                                       "name": "Mark-" + comp["class"][0]}))

    return ret


def check_navigation_drawer(comps, comp_stats, soup):
    comp_name = "navigation drawer"
    stats = comp_stats["navigation_drawer"]
    ret = ""

    for comp in comps:
        id = comp["id"]
        comp_str = "the " + comp_name + " with id " + id
        style = parseStyle(comp["style"])

        height = stats["height"]
        if height == "device":
            height = DEVICE_HEIGHT
        if not check_height(style, height):
            ret += comp_str.capitalize().capitalize() + " needs to have its height set to " + str(height) + ".\n"

        width = stats["width"]
        if not check_width(style, width):
            ret += comp_str.capitalize().capitalize() + " needs to have its width set to " + str(width) + ".\n"

        left_padding = stats["left_padding"]
        if not check_left_padding(comp, left_padding):
            ret += "Ensure that the left value of every direct child of " + comp_str + " is at least " + str(
                left_padding) + ".\n"

        right_padding = stats["right_padding"]
        if not check_right_padding(comp, right_padding):
            ret += "Ensure that every direct child of " + comp_str + " has a distance to the right of at least " + str(
                right_padding) + ".\n"

        for item in comp.contents:
            if type(item) == Tag:
                if "Divider" in item["class"]:
                    item_str = "the item with id " + item["id"] + " in " + comp_str
                    divider_padding = stats["divider_padding"]
                    if not check_left_padding(item, divider_padding):
                        ret += "Ensure that the divider in " + item_str + " has a left value of " + str(
                            divider_padding) + ".\n"

                    if not check_right_padding(item, divider_padding):
                        ret += "Ensure that the divider in " + item_str + " has a distance to the right of " + str(
                            divider_padding) + ".\n"

                else:
                    if len(item.find_all("div", attrs={"class": "state-layer"})) > 0:
                        state_layer = item.find_all("div", attrs={"class": "state-layer"})[0]
                        state_layer_style = parseStyle(state_layer["style"])
                        item_str = "the item with id " + item["id"] + " in " + comp_str + "'s state layer"

                        item_height = stats["item_height"]
                        if not check_height(state_layer_style, item_height):
                            ret += item_str + " needs to have its height changed to " + str(item_height) + ".\n"

                        left_padding_item = stats["left_padding_item"]
                        if not check_left_padding(state_layer, left_padding_item):
                            ret += "Ensure that the left value of every direct child of " + item_str + " is at least " + str(
                                left_padding_item) + ".\n"

                        right_padding_item = stats["right_padding_item"]
                        if not check_right_padding(state_layer, right_padding_item):
                            ret += "Ensure that every direct child of " + item_str + " has a distance to the right of at least " + str(
                                right_padding_item) + ".\n"

                        padding_between = stats["padding_between"]
                        if not check_padding_between(state_layer, padding_between):
                            ret += "Ensure that the distance between every direct child of " + item_str + " is equal to " + str(
                                padding_between) + ".\n"

                    text_size = stats["text_size"]
                    text_weight = stats["text_weight"]

                    if len(item.find_all("div", attrs={"class": "Icon"})) > 0:
                        icon = item.find_all("div", attrs={"class": "Icon"})[0]
                        icon_style = parseStyle(icon["style"])

                        icon_size = stats["icon_size"]
                        if not check_height(icon_style, icon_size) or not check_width(icon_style, icon_size):
                            ret += "The icon in " + item_str + " needs to have its height and width set to " + str(
                                icon_size) + ".\n"

                    if item["class"] == "Headline":
                        text = item.find_all("div", attrs={"class": "Title"})[0]

                        if not check_text_size(text, text_size):
                            ret += "The title text in " + item_str + " needs to have its size changed to " + str(
                                text_size) + ".\n"

                        if not check_text_weight(text, text_weight):
                            ret += "The title text in " + item_str + " needs to have its weight changed to " + str(
                                text_weight) + ".\n"

                    elif "Section-header" in item["class"]:
                        text = item.find_all("div", attrs={"class": "Label"})[0]

                        if not check_text_size(text, text_size):
                            ret += "The label text in " + item_str + " needs to have its size changed to " + str(
                                text_size) + ".\n"

                        if not check_text_weight(text, text_weight):
                            ret += "The label text in " + item_str + " needs to have its weight changed to " + str(
                                text_weight) + ".\n"

                    elif "Nav-item" in item["class"]:
                        text = item.find_all("div", attrs={"class": "Label"})[0]

                        if not check_text_size(text, text_size):
                            ret += "The label text in " + item_str + " needs to have its size changed to " + str(
                                text_size) + ".\n"

                        if not check_text_weight(text, text_weight):
                            ret += "The label text in " + item_str + " needs to have its weight changed to " + str(
                                text_weight) + ".\n"

                        if len(item.find_all("div", attrs={"class": "Badge-label-text"})) > 0:
                            badge_text = item.find_all("div", attrs={"class": "Badge-label-text"})

                            if not check_text_size(badge_text, text_size):
                                ret += "The badge label text in " + item_str + " needs to have its size changed to " + str(
                                    text_size) + ".\n"

                            if not check_text_weight(badge_text, text_weight):
                                ret += "The badge label text in " + item_str + " needs to have its weight changed to " + str(
                                    text_weight) + ".\n"

        if ret != "":
            comp.parent.append(soup.new_tag(name = "div",
                                              attrs = {"class": "Mark-" + comp["class"][0],
                                                     "style": "position: " + style["position"] +
                                                              "; left: " + style["left"] +
                                                              "; top: " + style["top"] +
                                                              "; height: " + style["height"] +
                                                              "; width: " + style["width"] +
                                                              "; box-shadow: inset 0px 0px 0px 4px red;",
                                                       "name": "Mark-" + comp["class"][0]}))

    return ret


def check_radio_button(comps, comp_stats, soup):
    comp_name = "radio button"
    stats = comp_stats["radio_button"]
    ret = ""

    for comp in comps:
        id = comp["id"]
        comp_str = "the " + comp_name + " with id " + id
        style = parseStyle(comp["style"])
        state_layer = comp.find_all("div", attrs={"class": "state-layer"})[0]
        state_layer_style = parseStyle(state_layer["style"])
        icon = state_layer.div.div
        icon_style = parseStyle(icon["style"])

        if not "element" in comp.parent["class"][0]:
            target_size = stats["target_size"]
            if not check_height(style, target_size) or not check_width(style, target_size):
                ret += comp_str.capitalize().capitalize() + " needs to have its height and width set to " + str(target_size) + ".\n"

        state_layer_size = stats["state_layer_size"]
        if not check_height(state_layer_style, state_layer_size) or not check_width(state_layer_style,
                                                                                    state_layer_size):
            ret += comp_str.capitalize().capitalize() + "'s state layer needs to have its height and width set to " + str(
                state_layer_size) + ".\n"

        icon_size = stats["icon_size"]
        if not check_height(icon_style, icon_size) or not check_width(icon_style, icon_size):
            ret += comp_str.capitalize().capitalize() + "'s lowest level icon needs to have its height and width set to " + str(icon_size) + ".\n"

        if ret != "":
            comp.parent.append(soup.new_tag(name = "div",
                                              attrs = {"class": "Mark-" + comp["class"][0],
                                                     "style": "position: " + style["position"] +
                                                              "; left: " + style["left"] +
                                                              "; top: " + style["top"] +
                                                              "; height: " + style["height"] +
                                                              "; width: " + style["width"] +
                                                              "; box-shadow: inset 0px 0px 0px 4px red;",
                                                       "name": "Mark-" + comp["class"][0]}))

    return ret


def check_search_bar(comps, comp_stats, soup):
    comp_name = "search bar"
    stats = comp_stats["search_bar"]
    ret = ""

    for comp in comps:
        id = comp["id"]
        comp_str = "the " + comp_name + " with id " + id
        style = parseStyle(comp["style"])


        min_width = stats["min_width"]
        max_width = stats["max_width"]
        width = int(style["width"].replace("px", ""))
        if width < min_width or width > max_width:
            ret += comp_str.capitalize().capitalize() + " needs to have its width set to a value between " + str(min_width) + " and " + str(
                max_width) + ".\n"

        height = stats["height"]
        if not check_height(style, height):
            ret += comp_str.capitalize().capitalize() + " needs to have its height set to " + str(height) + ".\n"

        if len(comp.find_all("div", attrs={"class": "state-layer"})) > 0:
            state_layer = comp.find_all("div", attrs={"class": "state-layer"})[0]
            left_padding = stats["left_padding"]
            if not check_left_padding(state_layer, left_padding):
                ret += "Ensure that every direct child of " + comp_str + "'s state layer has a left value of at least " + str(
                    left_padding) + ".\n "

            right_padding = stats["right_padding"]
            if not check_right_padding(state_layer, right_padding):
                ret += "Ensure that every direct child of " + comp_str + "'s state layer has a distance to the right of at least " + str(
                    right_padding) + ".\n"

            padding_between = stats["padding_between"]
            if not check_padding_between(state_layer, padding_between):
                ret += "Ensure that the distance between every direct child of " + comp_str + "'s state layer is equal to " + str(
                    padding_between) + ".\n"

        corner_radius = stats["corner_radius"]
        if not check_corner_radius(style, corner_radius):
            ret += comp_str.capitalize().capitalize() + " needs to have its corner radius set to " + str(corner_radius) + ".\n"

        icon_size = stats["icon_size"]
        icons = comp.find_all("div", attrs={"class": "Icon"})
        for icon in icons:
            icon_style = parseStyle(icon["style"])
            icon_str = "the icon with id " + icon["id"] + " in " + comp_str
            if not check_height(icon_style, icon_size) or not check_width(icon_style, icon_size):
                ret += icon_str + " needs to have its height and width set to " + str(icon_size) + ".\n"

        avatar_size = stats["avatar_size"]
        if len(comp.find_all("div", attrs={"class": "Avatar"})) > 0:
            avatar = comp.find_all("div", attrs={"class": "Avatar"})[0]
            avatar_style = parseStyle(avatar["style"])
            if not check_width(avatar_style, avatar_size) or not check_height(avatar_style, avatar_size):
                ret += "The avatar in " + comp_str + " needs to have its height and width set to " + str(
                    avatar_size) + ".\n"

        text = comp.find_all("div", attrs={"class": "supporting-text"})[0]
        text_size = stats["text_size"]
        if not check_text_size(text, text_size):
            ret += "The text in " + comp_str + " needs to have its size set to " + str(text_size) + ".\n"

        text_weight = stats["text_weight"]
        if not check_text_weight(text, text_weight):
            ret += "The text in " + comp_str + " needs to have its weight set to " + str(text_weight) + ".\n"

        if ret != "":
            comp.parent.append(soup.new_tag(name = "div",
                                              attrs = {"class": "Mark-" + comp["class"][0],
                                                     "style": "position: " + style["position"] +
                                                              "; left: " + style["left"] +
                                                              "; top: " + style["top"] +
                                                              "; height: " + style["height"] +
                                                              "; width: " + style["width"] +
                                                              "; box-shadow: inset 0px 0px 0px 4px red;",
                                                       "name": "Mark-" + comp["class"][0]}))

    return ret


def check_search_view_docked(comps, comp_stats, soup):
    comp_name = "search view"
    stats = comp_stats["search_view_docked"]
    ret = ""

    for comp in comps:
        id = comp["id"]
        comp_str = "the " + comp_name + " with id " + id
        style = parseStyle(comp["style"])
        header = comp.find_all("div", attrs={"class": "header"})[0]
        header_style = parseStyle(header["style"])

        min_height = stats["min_height"]
        max_height = int(float(DEVICE_HEIGHT) * 2.0 / 3.0)
        height = int(style["height"].replace("px", ""))
        if height < min_height or height > max_height:
            ret += comp_str.capitalize().capitalize() + " needs to have its height set to a value between " + str(min_height) + " and " + str(
                max_height) + ".\n"

        min_width = stats["min_width"]
        max_width = stats["max_width"]
        width = int(style["width"].replace("px", ""))
        if width < min_width or width > max_width:
            ret += comp_str.capitalize().capitalize() + " needs to have its width set to a value between " + str(min_width) + " and " + str(
                max_width) + ".\n"

        header_height = stats["header_height"]
        if not check_height(header_style, header_height):
            ret += comp_str.capitalize().capitalize() + "'s header needs to have its height set to " + str(header_height) + ".\n"

        left_padding = stats["left_padding"]
        if not check_left_padding(header, left_padding):
            ret += "Ensure that every direct child of " + comp_str + "'s header has a left value of at least " + str(
                left_padding) + ".\n "

        right_padding = stats["right_padding"]
        if not check_right_padding(header, right_padding):
            ret += "Ensure that every direct child of " + comp_str + "'s header has a distance to the right of at least " + str(
                right_padding) + ".\n"

        padding_between = stats["padding_between"]
        if not check_padding_between(header, padding_between):
            ret += "Ensure that the distance between every direct child of " + comp_str + "'s header is equal to " + str(
                padding_between) + ".\n"

        corner_radius = stats["corner_radius"]
        if not check_corner_radius(style, corner_radius):
            ret += comp_str.capitalize().capitalize() + " needs to have its corner radius set to " + str(corner_radius) + ".\n"

        icon_size = stats["icon_size"]
        icons = comp.find_all("div", attrs={"class": "Icon"})
        for icon in icons:
            icon_style = parseStyle(icon["style"])
            icon_str = "the icon with id " + icon["id"] + " in " + comp_str
            if not check_height(icon_style, icon_size) or not check_width(icon_style, icon_size):
                ret += icon_str + " needs to have its height and width set to " + str(icon_size) + ".\n"

        avatar_size = stats["avatar_size"]
        if len(comp.find_all("div", attrs={"class": "Avatar"})) > 0:
            avatar = comp.find_all("div", attrs={"class": "Avatar"})[0]
            avatar_style = parseStyle(avatar["style"])
            if not check_width(avatar_style, avatar_size) or not check_height(avatar_style, avatar_size):
                ret += "The avatar in " + comp_str + " needs to have its height and width set to " + str(
                    avatar_size) + ".\n"

        if len(comp.find_all("div", attrs={"class": "supporting-text"})) > 0:
            text = comp.find_all("div", attrs={"class": "supporting-text"})[0]
            text_size = stats["text_size"]
            if not check_text_size(text, text_size):
                ret += "The text in " + comp_str + " needs to have its size set to " + str(text_size) + ".\n"

            text_weight = stats["text_weight"]
            if not check_text_weight(text, text_weight):
                ret += "The text in " + comp_str + " needs to have its weight set to " + str(text_weight) + ".\n"

        if ret != "":
            comp.parent.append(soup.new_tag(name = "div",
                                              attrs = {"class": "Mark-" + comp["class"][0],
                                                     "style": "position: " + style["position"] +
                                                              "; left: " + style["left"] +
                                                              "; top: " + style["top"] +
                                                              "; height: " + style["height"] +
                                                              "; width: " + style["width"] +
                                                              "; box-shadow: inset 0px 0px 0px 4px red;",
                                                       "name": "Mark-" + comp["class"][0]}))

    return ret


def check_search_view_full_screen(comps, comp_stats, soup):
    comp_name = "search view"
    stats = comp_stats["search_view_full_screen"]
    ret = ""

    for comp in comps:
        id = comp["id"]
        comp_str = "the " + comp_name + " with id " + id
        style = parseStyle(comp["style"])
        header = comp.find_all("div", attrs={"class": "header"})[0]
        header_style = parseStyle(header["style"])

        width = stats["width"]
        if width == "device":
            width = DEVICE_WIDTH
        if not check_width(style, width):
            ret += comp_str.capitalize().capitalize() + " needs to have its width changed to " + str(width) + ".\n"

        height = stats["height"]
        if height == "device":
            height = DEVICE_HEIGHT
        if not check_height(style, height):
            ret += comp_str.capitalize().capitalize() + " needs to have its height changed to " + str(height) + ".\n"

        header_height = stats["header_height"]
        if not check_height(header_style, header_height):
            ret += comp_str.capitalize().capitalize() + "'s header needs to have its height set to " + str(header_height) + ".\n"

        left_padding = stats["left_padding"]
        if not check_left_padding(header, left_padding):
            ret += "Ensure that every direct child of " + comp_str + "'s header has a left value of at least " + str(
                left_padding) + ".\n "

        right_padding = stats["right_padding"]
        if not check_right_padding(header, right_padding):
            ret += "Ensure that every direct child of " + comp_str + "'s header has a distance to the right of at least " + str(
                right_padding) + ".\n"

        padding_between = stats["padding_between"]
        if not check_padding_between(header, padding_between):
            ret += "Ensure that the distance between every direct child of " + comp_str + "'s header is equal to " + str(
                padding_between) + ".\n"

        corner_radius = stats["corner_radius"]
        if not check_corner_radius(style, corner_radius):
            ret += comp_str.capitalize().capitalize() + " needs to have its corner radius set to " + str(corner_radius) + ".\n"

        icon_size = stats["icon_size"]
        icons = comp.find_all("div", attrs={"class": "Icon"})
        for icon in icons:
            icon_style = parseStyle(icon["style"])
            icon_str = "the icon with id " + icon["id"] + " in " + comp_str
            if not check_height(icon_style, icon_size) or not check_width(icon_style, icon_size):
                ret += icon_str + " needs to have its height and width set to " + str(icon_size) + ".\n"

        avatar_size = stats["avatar_size"]
        if len(comp.find_all("div", attrs={"class": "Avatar"})) > 0:
            avatar = comp.find_all("div", attrs={"class": "Avatar"})[0]
            avatar_style = parseStyle(avatar["style"])
            if not check_width(avatar_style, avatar_size) or not check_height(avatar_style, avatar_size):
                ret += "The avatar in " + comp_str + " needs to have its height and width set to " + str(
                    avatar_size) + ".\n"

        text = comp.find_all("div", attrs={"class": "supporting-text"})[0]
        text_size = stats["text_size"]
        if not check_text_size(text, text_size):
            ret += "The text in " + comp_str + " needs to have its size set to " + str(text_size) + ".\n"

        text_weight = stats["text_weight"]
        if not check_text_weight(text, text_weight):
            ret += "The text in " + comp_str + " needs to have its weight set to " + str(text_weight) + ".\n"

        if ret != "":
            comp.parent.append(soup.new_tag(name = "div",
                                              attrs = {"class": "Mark-" + comp["class"][0],
                                                     "style": "position: " + style["position"] +
                                                              "; left: " + style["left"] +
                                                              "; top: " + style["top"] +
                                                              "; height: " + style["height"] +
                                                              "; width: " + style["width"] +
                                                              "; box-shadow: inset 0px 0px 0px 4px red;",
                                                       "name": "Mark-" + comp["class"][0]}))

    return ret


def check_bottom_sheet(comps, comp_stats, soup):
    comp_name = "bottom sheet"
    stats = comp_stats["bottom_sheet"]
    ret = ""

    for comp in comps:
        id = comp["id"]
        comp_str = "the " + comp_name + " with id " + id
        style = parseStyle(comp["style"])
        sheet = comp.find_all("div", attrs={"class": "Bottom-Sheet"})[0]
        sheet_style = parseStyle(sheet["style"])

        width = stats["width"]
        if width == "device":
            width = DEVICE_WIDTH
        if not check_width(style, width):
            ret += comp_str.capitalize().capitalize() + " needs to have its width changed to " + str(width) + ".\n"

        corner_radius = stats["corner_radius"]
        if sheet_style["border-radius"] != corner_radius:
            ret += comp_str.capitalize().capitalize() + " needs to have its border radius set to " + corner_radius + ".\n"

        if len(comp.find_all("div", attrs={"class": "Drag-handle"})) > 0:
            handle = comp.find_all("div", attrs={"class": "Drag-handle"})[0]
            handle_style = parseStyle(handle["style"])
            drag_handle_width = stats["drag_handle_width"]
            if not check_width(handle_style, drag_handle_width):
                ret += comp_str.capitalize().capitalize() + "'s drag handle needs to have its width changed to " + str(drag_handle_width) + ".\n"

            drag_handle_height = stats["drag_handle_height"]
            if not check_height(handle_style, drag_handle_height):
                ret += comp_str.capitalize().capitalize() + "'s drag handle needs to have its height changed to " + str(drag_handle_height) + ".\n"

        if ret != "":
            comp.parent.append(soup.new_tag(name = "div",
                                              attrs = {"class": "Mark-" + comp["class"][0],
                                                     "style": "position: " + style["position"] +
                                                              "; left: " + style["left"] +
                                                              "; top: " + style["top"] +
                                                              "; height: " + style["height"] +
                                                              "; width: " + style["width"] +
                                                              "; box-shadow: inset 0px 0px 0px 4px red;",
                                                       "name": "Mark-" + comp["class"][0]}))

    return ret


def check_snackbar_one_line(comps, comp_stats, soup):
    comp_name = "snackbar"
    stats = comp_stats["snackbar_one_line"]
    ret = ""

    for comp in comps:
        id = comp["id"]
        comp_str = "the " + comp_name + " with id " + id
        style = parseStyle(comp["style"])
        supporting_text = comp.find_all("div", attrs={"class": re.compile("Label|Supporting-text")})[0]

        height = stats["height"]
        if not check_height(style, height):
            ret += comp_str.capitalize().capitalize() + " needs to have its height set to " + str(height) + ".\n"

        left_padding = stats["left_padding"]
        if not check_left_padding(comp, left_padding):
            ret += "Ensure that every child of " + comp_str + " has a left value of at least " + str(
                left_padding) + ".\n"

        supporting_text_size = stats["supporting_text_size"]
        if not check_text_size(supporting_text, supporting_text_size):
            ret += comp_str.capitalize().capitalize() + "'s label text needs to have its size set to " + str(supporting_text_size) + ".\n"

        support_text_weight = stats["support_text_weight"]
        if not check_text_weight(supporting_text, support_text_weight):
            ret += comp_str.capitalize().capitalize() + "'s label text needs to have its weight set to " + str(support_text_weight) + ".\n"

        right_padding = stats["right_padding"]

        if len(comp.find_all("div", attrs={"class": "Inverse-button"})) > 0:
            action = comp.find_all("div", attrs={"class": "Inverse-button"})[0].find_all("div", attrs={"class": "label-text"})[0]

            text_size = stats["text_size"]
            if not check_text_size(action, text_size):
                ret += comp_str.capitalize() + "'s action text needs to have its size changed to " + str(text_size) + ".\n"

            text_weight = stats["text_weight"]
            if not check_text_weight(action, text_weight):
                ret += comp_str.capitalize() + "'s action text needs to have its weight changed to " + str(text_weight) + ".\n"

            right_padding = stats["right_padding_action"]

        if len(comp.find_all("div", attrs={"class": "Close-affordance"})) > 0:
            icon = comp.find_all("div", attrs={"class": "Close-affordance"})[0].div.div.div
            icon_style = parseStyle(icon["style"])

            icon_size = stats["icon_size"]
            if not check_height(icon_style, icon_size) or not check_width(icon_style, icon_size):
                ret += "The icon in " + comp_str + " needs to have its height and width set to " + str(
                    icon_size) + ".\n"

            right_padding = stats["right_padding_icon"]

        if not check_right_padding(comp, right_padding):
            ret += "Ensure that every direct child of " + comp_str + " has a distance to the right of at least " + str(
                right_padding) + ".\n"

        if ret != "":
            comp.parent.append(soup.new_tag(name = "div",
                                              attrs = {"class": "Mark-" + comp["class"][0],
                                                     "style": "position: " + style["position"] +
                                                              "; left: " + style["left"] +
                                                              "; top: " + style["top"] +
                                                              "; height: " + style["height"] +
                                                              "; width: " + style["width"] +
                                                              "; box-shadow: inset 0px 0px 0px 4px red;",
                                                       "name": "Mark-" + comp["class"][0]}))

    return ret


def check_snackbar_two_line(comps, comp_stats, soup):
    comp_name = "snackbar"
    stats = comp_stats["snackbar_two_line"]
    ret = ""

    for comp in comps:
        id = comp["id"]
        comp_str = "the " + comp_name + " with id " + id
        style = parseStyle(comp["style"])
        supporting_text = comp.find_all("div", attrs={"class": "Supporting-text"})[0]

        height = stats["height"]
        if not check_height(style, height):
            ret += comp_str.capitalize() + " needs to have its height set to " + str(height) + ".\n"

        left_padding = stats["left_padding"]
        if not check_left_padding(comp, left_padding):
            ret += "Ensure that every child of " + comp_str + " has a left value of at least " + str(
                left_padding) + ".\n"

        supporting_text_size = stats["supporting_text_size"]
        if not check_text_size(supporting_text, supporting_text_size):
            ret += comp_str.capitalize() + "'s supporting text needs to have its size set to " + str(supporting_text_size) + ".\n"

        support_text_weight = stats["support_text_weight"]
        if not check_text_weight(supporting_text, support_text_weight):
            ret += comp_str.capitalize() + "'s supporting text needs to have its weight set to " + str(support_text_weight) + ".\n"

        right_padding = stats["right_padding"]

        if len(comp.find_all("div", attrs={"class": "Inverse-button"})) > 0:
            action = comp.find_all("div", attrs={"class": "Inverse-button"})[0].find_all("div", attrs={"class": "label-text"})[0]

            text_size = stats["text_size"]
            if not check_text_size(action, text_size):
                ret += comp_str.capitalize() + "'s action text needs to have its size changed to " + str(text_size) + ".\n"

            text_weight = stats["text_weight"]
            if not check_text_weight(action, text_weight):
                ret += comp_str.capitalize() + "'s action text needs to have its weight changed to " + str(text_weight) + ".\n"

            right_padding = stats["right_padding_action"]

        if len(comp.find_all("div", attrs={"class": "Close-affordance"})) > 0:
            icon = comp.find_all("div", attrs={"class": "Close-affordance"})[0].div.div.div
            icon_style = parseStyle(icon["style"])

            icon_size = stats["icon_size"]
            if not check_height(icon_style, icon_size) or not check_width(icon_style, icon_size):
                ret += "The icon in " + comp_str + " needs to have its height and width set to " + str(
                    icon_size) + ".\n"

            right_padding = stats["right_padding_icon"]

        if not check_right_padding(comp, right_padding):
            ret += "Ensure that every direct child of " + comp_str + " has a distance to the right of at least " + str(
                right_padding) + ".\n"

        if ret != "":
            comp.parent.append(soup.new_tag(name = "div",
                                              attrs = {"class": "Mark-" + comp["class"][0],
                                                     "style": "position: " + style["position"] +
                                                              "; left: " + style["left"] +
                                                              "; top: " + style["top"] +
                                                              "; height: " + style["height"] +
                                                              "; width: " + style["width"] +
                                                              "; box-shadow: inset 0px 0px 0px 4px red;",
                                                       "name": "Mark-" + comp["class"][0]}))

    return ret


def check_snackbar_longer_action(comps, comp_stats, soup):
    comp_name = "snackbar"
    stats = comp_stats["snackbar_longer_action"]
    ret = ""

    for comp in comps:
        id = comp["id"]
        comp_str = "the " + comp_name + " with id " + id
        style = parseStyle(comp["style"])
        supporting_text = comp.find_all("div", attrs={"class": "Supporting-text"})[0]
        action_area = comp.find_all("div", attrs={"class": "action-&-close affordance"})[0]

        height = stats["height"]
        if not check_height(style, height):
            ret += comp_str.capitalize() + " needs to have its height set to " + str(height) + ".\n"

        left_padding = stats["left_padding"]
        if not check_left_padding(comp, left_padding):
            ret += "Ensure that every child of " + comp_str + " has a left value of at least " + str(
                left_padding) + ".\n"

        supporting_text_size = stats["supporting_text_size"]
        if not check_text_size(supporting_text, supporting_text_size):
            ret += comp_str.capitalize() + "'s supporting text needs to have its size set to " + str(supporting_text_size) + ".\n"

        support_text_weight = stats["support_text_weight"]
        if not check_text_weight(supporting_text, support_text_weight):
            ret += comp_str.capitalize() + "'s supporting text needs to have its weight set to " + str(support_text_weight) + ".\n"

        right_padding = stats["right_padding"]

        if len(comp.find_all("div", attrs={"class": "Close-affordance"})) > 0:
            icon = comp.find_all("div", attrs={"class": "Close-affordance"})[0].div.div.div
            icon_style = parseStyle(icon["style"])

            icon_size = stats["icon_size"]
            if not check_height(icon_style, icon_size) or not check_width(icon_style, icon_size):
                ret += "The icon in " + comp_str + " needs to have its height and width set to " + str(
                    icon_size) + ".\n"

            right_padding = stats["right_padding_icon"]

        if not check_right_padding(action_area, right_padding):
            ret += "Ensure that every direct child of " + comp_str + "'s action area has a distance to the right of at least " + str(
                right_padding) + ".\n"

        if ret != "":
            comp.parent.append(soup.new_tag(name = "div",
                                              attrs = {"class": "Mark-" + comp["class"][0],
                                                     "style": "position: " + style["position"] +
                                                              "; left: " + style["left"] +
                                                              "; top: " + style["top"] +
                                                              "; height: " + style["height"] +
                                                              "; width: " + style["width"] +
                                                              "; box-shadow: inset 0px 0px 0px 4px red;",
                                                       "name": "Mark-" + comp["class"][0]}))

    return ret


def check_switch_unselected(comps, comp_stats, soup):
    comp_name = "switch"
    stats = comp_stats["switch_unselected"]
    ret = ""

    for comp in comps:
        id = comp["id"]
        comp_str = "the " + comp_name + " with id " + id
        style = parseStyle(comp["style"])
        target = comp.find_all("div", attrs={"class": re.compile("Handle-container|Target")})[0]
        target_style = parseStyle(target["style"])
        handle = comp.find_all("div", attrs={"class": re.compile("Handle-shape|Handle")})[0]
        handle_style = parseStyle(handle["style"])
        track = comp.find_all("div", attrs={"class": "Track"})[0]
        track_style = parseStyle(track["style"])

        height = stats["height"]
        if not check_height(style, height):
            ret += comp_str.capitalize() + " needs to have its height changed to " + str(height) + ".\n"

        width = stats["width"]
        if not check_width(style, width):
            ret += comp_str.capitalize() + " needs to have its width changed to " + str(width) + ".\n"

        corner_radius = stats["corner_radius"]
        if not check_corner_radius(style, corner_radius):
            ret += comp_str.capitalize() + " needs to have its corner radius changed to " + str(corner_radius) + ".\n"

        outline = stats["outline"]
        if not check_outline(track_style, outline):
            ret += comp_str.capitalize() + "'s track needs to have its border width changed to " + str(outline) + ".\n"

        target_size = stats["target_size"]
        if not check_height(target_style, target_size) or not check_width(target_style, target_size):
            ret += comp_str.capitalize() + "'s target needs to have its height and width changed to " + str(target_size) + ".\n"

        if len(comp.find_all("div", attrs={"class": re.compile("State-layer|state-layer")}))> 0:
            state_layer = comp.find_all("div", attrs={"class": re.compile("State-layer|state-layer")})[0]
            state_layer_style = parseStyle(state_layer["style"])
            state_layer_size = stats["state_layer_size"]
            if not check_height(state_layer_style, state_layer_size) or not check_width(state_layer_style,
                                                                                        state_layer_size):
                ret += comp_str.capitalize() + "'s state layer needs to have its height and width changed to " + str(
                    state_layer_size) + ".\n"

        handle_corner_radius = stats["handle_corner_radius"]
        if not check_corner_radius(handle_style, handle_corner_radius):
            ret += comp_str.capitalize() + "'s handle needs to have its corner radius changed to " + str(
                handle_corner_radius) + ".\n"

        handle_size = stats["handle_size"]
        if len(comp.find_all("div", attrs={"class": "Icon"})) > 0:
            icon = comp.find_all("div", attrs={"class": "Icon"})[0]
            icon_style = parseStyle(icon["style"])

            icon_size = stats["icon_size"]
            if not check_height(icon_style, icon_size) or not check_width(icon_style, icon_size):
                ret += comp_str.capitalize() + "'s icon needs to have its height and width changed to " + str(icon_size) + ".\n"

            handle_size = stats["handle_size_icon"]

        if not check_height(handle_style, handle_size) or not check_width(handle_style, handle_size):
            ret += comp_str.capitalize() + "'s handle needs to have its height and width changed to " + str(handle_size) + ".\n"

        if ret != "":
            comp.parent.append(soup.new_tag(name = "div",
                                              attrs = {"class": "Mark-" + comp["class"][0],
                                                     "style": "position: " + style["position"] +
                                                              "; left: " + style["left"] +
                                                              "; top: " + style["top"] +
                                                              "; height: " + style["height"] +
                                                              "; width: " + style["width"] +
                                                              "; box-shadow: inset 0px 0px 0px 4px red;",
                                                       "name": "Mark-" + comp["class"][0]}))

    return ret


def check_switch_selected(comps, comp_stats, soup):
    comp_name = "switch"
    stats = comp_stats["switch_selected"]
    ret = ""

    for comp in comps:
        id = comp["id"]
        comp_str = "the " + comp_name + " with id " + id
        style = parseStyle(comp["style"])
        target = comp.find_all("div", attrs={"class": "Target"})[0]
        target_style = parseStyle(target["style"])
        handle = comp.find_all("div", attrs={"class": "Handle-shape"})[0]
        handle_style = parseStyle(handle["style"])
        state_layer = comp.find_all("div", attrs={"class": "state-layer"})[0]
        state_layer_style = parseStyle(state_layer["style"])

        height = stats["height"]
        if not check_height(style, height):
            ret += comp_str.capitalize() + " needs to have its height changed to " + str(height) + ".\n"

        width = stats["width"]
        if not check_width(style, width):
            ret += comp_str.capitalize() + " needs to have its width changed to " + str(width) + ".\n"

        corner_radius = stats["corner_radius"]
        if not check_corner_radius(style, corner_radius):
            ret += comp_str.capitalize() + " needs to have its corner radius changed to " + str(corner_radius) + ".\n"

        outline = stats["outline"]
        if not check_outline(style, outline):
            ret += comp_str.capitalize() + "'s needs to have its border width changed to " + str(outline) + ".\n"

        target_size = stats["target_size"]
        if not check_height(target_style, target_size) or not check_width(target_style, target_size):
            ret += comp_str.capitalize() + "'s target needs to have its height and width changed to " + str(target_size) + ".\n"

        state_layer_size = stats["state_layer_size"]
        if not check_height(state_layer_style, state_layer_size) or not check_width(state_layer_style,
                                                                                    state_layer_size):
            ret += comp_str.capitalize() + "'s state layer needs to have its height and width changed to " + str(
                state_layer_size) + ".\n"

        handle_corner_radius = stats["handle_corner_radius"]
        if not check_corner_radius(handle_style, handle_corner_radius):
            ret += comp_str.capitalize() + "'s handle needs to have its corner radius changed to " + str(
                handle_corner_radius) + ".\n"

        if len(comp.find_all("div", attrs={"class": "Icon"})) > 0:
            icon = comp.find_all("div", attrs={"class": "Icon"})[0]
            icon_style = parseStyle(icon["style"])

            icon_size = stats["icon_size"]
            if not check_height(icon_style, icon_size) or not check_width(icon_style, icon_size):
                ret += comp_str.capitalize() + "'s icon needs to have its height and width changed to " + str(icon_size) + ".\n"

        handle_size = stats["handle_size"]
        if not check_height(handle_style, handle_size) or not check_width(handle_style, handle_size):
            ret += comp_str.capitalize() + "'s handle needs to have its height and width changed to " + str(handle_size) + ".\n"

        if ret != "":
            comp.parent.append(soup.new_tag(name = "div",
                                              attrs = {"class": "Mark-" + comp["class"][0],
                                                     "style": "position: " + style["position"] +
                                                              "; left: " + style["left"] +
                                                              "; top: " + style["top"] +
                                                              "; height: " + style["height"] +
                                                              "; width: " + style["width"] +
                                                              "; box-shadow: inset 0px 0px 0px 4px red;",
                                                       "name": "Mark-" + comp["class"][0]}))

    return ret


def check_tabs_primary(comps, comp_stats, soup):
    comp_name = "tabs"
    stats = comp_stats["tabs_primary"]
    ret = ""

    for comp in comps:
        id = comp["id"]
        comp_str = "the " + comp_name + " with id " + id
        style = parseStyle(comp["style"])

        height = stats["height"]
        if not check_height(style, height):
            ret += comp_str.capitalize() + " need to have their height changed to " + str(height) + ".\n"

        tabs = comp.find_all("div", attrs={"class": re.compile("^Tab")})
        num_tabs = len(tabs)
        tab_width = float(style["width"].replace("px", "")) / num_tabs
        for tab in tabs:
            tab_style = parseStyle(tab["style"])
            tab_str = "the tab with id " + tab["id"] + " in " + comp_str
            contents = tab.find_all("div", attrs={"class": "Tab-Contents"})[0]
            text = tab.find_all("div", attrs={"class": "Label"})[0]

            if not check_width(tab_style, tab_width):
                ret += tab_str.capitalize() + " needs to have its width changed to " + str(tab_width) + ".\n"

            padding_between_vert = stats["padding_between_vert"]
            if not check_padding_between_vert(contents, padding_between_vert):
                ret += "Ensure that the vertical distance between every direct child of " + tab_str + "'s contents is equal to " + str(
                    padding_between_vert) + ".\n"

            text_size = stats["text_size"]
            if not check_text_size(text, text_size):
                ret += tab_str.capitalize() + "'s label text needs to have its size set to " + str(text_size) + ".\n"

            text_weight = stats["text_weight"]
            if not check_text_weight(text, text_weight):
                ret += tab_str.capitalize() + "'s label text needs to have its weight set to " + str(text_weight) + ".\n"

            if len(tab.find_all("div", attrs={"class": "icon"})) > 0:
                icon = tab.find_all("div", attrs={"class": "icon"})[0]
                icon_style = parseStyle(icon["style"])

                icon_size = stats["icon_size"]
                if not check_height(icon_style, icon_size) or not check_width(icon_style, icon_size):
                    ret += "The icon in " + tab_str + " needs to have its height and width changed to " + str(
                        icon_size) + ".\n"

            if len(tab.find_all("div", attrs={"class": "Shape"})) > 0:
                indicator = tab.find_all("div", attrs={"class": "Shape"})[0]
                indicator_style = parseStyle(indicator["style"])

                active_indicator_height = stats["active_indicator_height"]
                if not check_height(indicator_style, active_indicator_height):
                    ret += tab_str.capitalize() + "'s active indicator needs to have its height changed to " + str(
                        active_indicator_height) + ".\n"

                active_indicator_shape = stats["active_indicator_shape"]
                if indicator_style["border-radius"] != active_indicator_shape:
                    ret += tab_str.capitalize() + "'s active indicator needs to have its corner radius changed to " + active_indicator_shape + ".\n"

        if len(comp.find_all("div", attrs={"class": "Divider"})):
            divider = comp.find_all("div", attrs={"class": "Divider"})[0]
            divider_style = parseStyle(divider["style"])

            divider_height = stats["divider_height"]
            if not check_height(divider_style, divider_height):
                ret += comp_str.capitalize() + "'s divider needs to have its height changed to " + str(divider_height) + ".\n"

        if ret != "":
            comp.parent.append(soup.new_tag(name = "div",
                                              attrs = {"class": "Mark-" + comp["class"][0],
                                                     "style": "position: " + style["position"] +
                                                              "; left: " + style["left"] +
                                                              "; top: " + style["top"] +
                                                              "; height: " + style["height"] +
                                                              "; width: " + style["width"] +
                                                              "; box-shadow: inset 0px 0px 0px 4px red;",
                                                       "name": "Mark-" + comp["class"][0]}))

    return ret


def check_tabs_secondary(comps, comp_stats, soup):
    comp_name = "tabs"
    stats = comp_stats["tabs_secondary"]
    ret = ""

    for comp in comps:
        id = comp["id"]
        comp_str = "the " + comp_name + " with id " + id
        style = parseStyle(comp["style"])

        height = stats["height"]
        if not check_height(style, height):
            ret += comp_str.capitalize() + " need to have their height changed to " + str(height) + ".\n"

        tabs = comp.find_all("div", attrs={"class": re.compile("^Tab-[0-9]+")})
        num_tabs = len(tabs)
        tab_width = float(style["width"].replace("px", "")) / num_tabs
        for tab in tabs:
            tab_style = parseStyle(tab["style"])
            tab_str = "the tab with id " + tab["id"] + " in " + comp_str
            contents = tab.find_all("div", attrs={"class": "Tab-Contents"})[0]

            if not check_width(tab_style, tab_width):
                ret += tab_str.capitalize() + " needs to have its width changed to " + str(tab_width) + ".\n"

            padding_between = stats["padding_between"]
            if "Label & icon" in comp["config"]:
                if not check_padding_between(contents, padding_between):
                    ret += "Ensure that the distance between every direct child of " + tab_str + "'s contents is equal to " + str(
                        padding_between) + ".\n"

            if len(tab.find_all("div", attrs={"class": "Label"})) > 0:
                text = tab.find_all("div", attrs={"class": "Label"})[0]
                text_size = stats["text_size"]
                if not check_text_size(text, text_size):
                    ret += tab_str.capitalize() + "'s label text needs to have its size set to " + str(text_size) + ".\n"

                text_weight = stats["text_weight"]
                if not check_text_weight(text, text_weight):
                    ret += tab_str.capitalize() + "'s label text needs to have its weight set to " + str(text_weight) + ".\n"

            if len(tab.find_all("div", attrs={"class": "icon"})) > 0:
                icon = tab.find_all("div", attrs={"class": "icon"})[0]
                icon_style = parseStyle(icon["style"])

                icon_size = stats["icon_size"]
                if not check_height(icon_style, icon_size) or not check_width(icon_style, icon_size):
                    ret += "The icon in " + tab_str + " needs to have its height and width changed to " + str(
                        icon_size) + ".\n"

            if len(tab.find_all("div", attrs={"class": "Shape"})) > 0:
                indicator = tab.find_all("div", attrs={"class": "Shape"})[0]
                indicator_style = parseStyle(indicator["style"])

                active_indicator_height = stats["active_indicator_height"]
                if not check_height(indicator_style, active_indicator_height):
                    ret += tab_str.capitalize() + "'s active indicator needs to have its height changed to " + str(
                        active_indicator_height)
                    ".\n"

                active_indicator_shape = stats["active_indicator_shape"]
                if indicator_style["border-radius"] != active_indicator_shape:
                    ret += tab_str.capitalize() + "'s active indicator needs to have its corner radius changed to " + str(active_indicator_shape) + ".\n"

        if len(comp.find_all("div", attrs={"class": "Divider"})) > 0:
            divider = comp.find_all("div", attrs={"class": "Divider"})[0]
            divider_style = parseStyle(divider["style"])

            divider_height = stats["divider_height"]
            if not check_height(divider_style, divider_height):
                ret += comp_str.capitalize() + "'s divider needs to have its height changed to " + str(divider_height) + ".\n"

        if ret != "":
            comp.parent.append(soup.new_tag(name = "div",
                                              attrs = {"class": "Mark-" + comp["class"][0],
                                                     "style": "position: " + style["position"] +
                                                              "; left: " + style["left"] +
                                                              "; top: " + style["top"] +
                                                              "; height: " + style["height"] +
                                                              "; width: " + style["width"] +
                                                              "; box-shadow: inset 0px 0px 0px 4px red;",
                                                       "name": "Mark-" + comp["class"][0]}))

    return ret


def check_text_field_filled(comps, comp_stats, soup):
    comp_name = "text field"
    stats = comp_stats["text_field_filled"]
    ret = ""

    for comp in comps:
        id = comp["id"]
        comp_str = "the " + comp_name + " with id " + id
        style = parseStyle(comp["style"])
        state_layer = comp.find_all("div", attrs={"class": "state-layer"})[0]
        state_layer_style = parseStyle(state_layer["style"])
        supporting_text = comp.find_all("div", attrs={"class": "supporting-text"})[0]
        label_text = comp.find_all("div", attrs={"class": "label-text"})[0]

        height = stats["height"]
        if not check_height(style, height):
            ret += comp_str.capitalize() + " needs to have its height changed to " + str(height) + ".\n"

        padding_left = stats["padding_left"]
        padding_right = stats["padding_right"]
        if len(comp.find_all("div", attrs={"class": "Icon"})) > 0:
            for icon in comp.find_all("div", attrs={"class": "Icon"}):
                icon_str = "the icon with id " + icon["id"] + " in " + comp_str
                icon_style = parseStyle(icon["style"])

                icon_size = stats["icon_size"]
                if not check_height(icon_style, icon_size) or not check_width(icon_style, icon_size):
                    ret += icon_str + " needs to have its height and width changed to " + str(icon_size) + ".\n"

        if len(comp.find_all("div", attrs={"class": "leading-icon"})) > 0:
            padding_left = stats["padding_left_icon"]

        if len(comp.find_all("div", attrs={"class": "trailing-icon"})) > 0:
            padding_left = stats["padding_right_icon"]

        if not check_left_padding(state_layer, padding_left):
            ret += "Ensure that every direct child of " + comp_str + "'s state layer has a left value of at least " + str(
                padding_left) + ".\n"

        if not check_right_padding(state_layer, padding_right):
            ret += "Ensure that every direct child of " + comp_str + "'s state layer has a distance to the right of at least " + str(
                padding_right) + ".\n"

        padding_between = stats["padding_between"]
        if not check_padding_between(state_layer, padding_between):
            ret += "Ensure that the distance between every direct child of " + comp_str + "'s state layer is equal to " + str(
                padding_between) + ".\n"

        corner_radius = stats["corner_radius"]
        if style["border-radius"] != corner_radius:
            ret += comp_str.capitalize() + " needs to have its corner radius changed to " + corner_radius + ".\n"

        supporting_text_top_padding = stats["supporting_text_top_padding"]
        if not check_top_padding(supporting_text, supporting_text_top_padding):
            ret += comp_str.capitalize() + "'s supporting text needs to be " + str(
                supporting_text_top_padding) + " away from the text field."

        supporting_text_left_padding = stats["supporting_text_left_padding"]
        if not check_left_padding(supporting_text, supporting_text_left_padding):
            ret += comp_str.capitalize() + "'s supporting text needs to be " + str(
                supporting_text_left_padding) + " away from the left."

        supporting_text_size = stats["supporting_text_size"]
        if not check_text_size(supporting_text, supporting_text_size):
            ret += comp_str.capitalize() + "'s supporting text needs to have its size changed to " + str(
                supporting_text_size) + ".\n"

        supporting_text_weight = stats["supporting_text_weight"]
        if not check_text_weight(supporting_text, supporting_text_weight):
            ret += comp_str.capitalize() + "'s supporting text needs to have its weight changed to " + str(
                supporting_text_weight) + ".\n"

        label_text_size = stats["text_size"]
        label_text_weight = stats["text_weight"]
        if len(comp.find_all("div", attrs={"class": "input-text"})) > 0:
            input_text = comp.find_all("div", attrs={"class": "input-text"})

            input_text_size = stats["text_size"]
            if not check_text_size(input_text, input_text_size):
                ret += comp_str.capitalize() + "'s input text needs to have its size changed to " + str(input_text_size) + ".\n"

            input_text_weight = stats["text_weight"]
            if not check_text_weight(input_text, input_text_weight):
                ret += comp_str.capitalize() + "'s input text needs to have its weight changed to " + str(input_text_weight) + ".\n"

            label_text_size = stats["label_text_populated_size"]

        if len(comp.find_all("div", attrs={"class": "placeholder-text"})) > 0:
            placeholder_text = comp.find_all("div", attrs={"class": "placeholder-text"})

            placeholder_text_size = stats["text_size"]
            if not check_text_size(placeholder_text, placeholder_text_size):
                ret += comp_str.capitalize() + "'s placeholder text needs to have its size changed to " + str(
                    placeholder_text_size) + ".\n"

            placeholder_text_weight = stats["text_weight"]
            if not check_text_weight(placeholder_text, placeholder_text_weight):
                ret += comp_str.capitalize() + "'s placeholder text needs to have its weight changed to " + str(
                    placeholder_text_weight) + ".\n"

            label_text_size = stats["label_text_populated_size"]

        if not check_text_size(label_text, label_text_size):
            ret += comp_str.capitalize() + "'s label text needs to have its size changed to " + str(label_text_size) + ".\n"

        if not check_text_weight(label_text, label_text_weight):
            ret += comp_str.capitalize() + "'s label text needs to have its weight changed to " + str(label_text_weight) + ".\n"

        if ret != "":
            comp.parent.append(soup.new_tag(name = "div",
                                              attrs = {"class": "Mark-" + comp["class"][0],
                                                     "style": "position: " + style["position"] +
                                                              "; left: " + style["left"] +
                                                              "; top: " + style["top"] +
                                                              "; height: " + style["height"] +
                                                              "; width: " + style["width"] +
                                                              "; box-shadow: inset 0px 0px 0px 4px red;",
                                                       "name": "Mark-" + comp["class"][0]}))

    return ret


def check_text_field_outlined(comps, comp_stats, soup):
    comp_name = "text field"
    stats = comp_stats["text_field_outlined"]
    ret = ""

    for comp in comps:
        id = comp["id"]
        comp_str = "the " + comp_name + " with id " + id
        style = parseStyle(comp["style"])
        state_layer = comp.find_all("div", attrs={"class": "state-layer"})[0]
        state_layer_style = parseStyle(state_layer["style"])

        label_text = comp.find_all("div", attrs={"class": "label-text"})[1]
        field = comp.find_all("div", attrs={"class": "text-field"})[0]
        field_style = parseStyle(field["style"])

        outline = stats["outline"]
        if not check_outline(field_style, outline):
            ret += comp_str.capitalize() + " needs to have its outline width changed to " + str(outline) + ".\n"

        height = stats["height"]
        if not check_height(style, height):
            ret += comp_str.capitalize() + " needs to have its height changed to " + str(height) + ".\n"

        padding_left = stats["padding_left"]
        padding_right = stats["padding_right"]
        if len(comp.find_all("div", attrs={"class": "Icon"})) > 0:
            for icon in comp.find_all("div", attrs={"class": "Icon"}):
                icon_str = "the icon with id " + icon["id"] + " in " + comp_str
                icon_style = parseStyle(icon["style"])

                icon_size = stats["icon_size"]
                if not check_height(icon_style, icon_size) or not check_width(icon_style, icon_size):
                    ret += icon_str + " needs to have its height and width changed to " + str(icon_size) + ".\n"

        if len(comp.find_all("div", attrs={"class": "leading-icon"})) > 0:
            padding_left = stats["padding_left_icon"]

        if len(comp.find_all("div", attrs={"class": "trailing-icon"})) > 0:
            padding_left = stats["padding_right_icon"]

        if not check_left_padding(state_layer, padding_left):
            ret += "Ensure that every direct child of " + comp_str + "'s state layer has a left value of at least " + str(
                padding_left) + ".\n"

        if not check_right_padding(state_layer, padding_right):
            ret += "Ensure that every direct child of " + comp_str + "'s state layer has a distance to the right of at least " + str(
                padding_right) + ".\n"

        padding_between = stats["padding_between"]
        if not check_padding_between(state_layer, padding_between):
            ret += "Ensure that the distance between every direct child of " + comp_str + "'s state layer is equal to " + str(
                padding_between) + ".\n"

        corner_radius = stats["corner_radius"]
        if style["border-radius"] != corner_radius:
            ret += comp_str.capitalize() + " needs to have its corner radius changed to " + corner_radius + ".\n"

        if len(comp.find_all("div", attrs={"class": "supporting-text"})) > 0:
            supporting_text = comp.find_all("div", attrs={"class": "supporting-text"})[0]

            supporting_text_top_padding = stats["supporting_text_top_padding"]
            if not check_top_padding(supporting_text, supporting_text_top_padding):
                ret += comp_str.capitalize() + "'s supporting text needs to be " + str(
                    supporting_text_top_padding) + " away from the text field."

            supporting_text_left_padding = stats["supporting_text_left_padding"]
            if not check_left_padding(supporting_text, supporting_text_left_padding):
                ret += comp_str.capitalize() + "'s supporting text needs to be " + str(
                    supporting_text_left_padding) + " away from the left."

            supporting_text_size = stats["supporting_text_size"]
            if not check_text_size(supporting_text, supporting_text_size):
                ret += comp_str.capitalize() + "'s supporting text needs to have its size changed to " + str(
                    supporting_text_size) + ".\n"

            supporting_text_weight = stats["supporting_text_weight"]
            if not check_text_weight(supporting_text, supporting_text_weight):
                ret += comp_str.capitalize() + "'s supporting text needs to have its weight changed to " + str(
                    supporting_text_weight) + ".\n"

        label_text_size = stats["text_size"]
        label_text_weight = stats["text_weight"]
        if len(comp.find_all("div", attrs={"class": "input-text"})) > 0:
            input_text = comp.find_all("div", attrs={"class": "input-text"})[1]

            input_text_size = stats["text_size"]
            if not check_text_size(input_text, input_text_size):
                ret += comp_str.capitalize() + "'s input text needs to have its size changed to " + str(input_text_size) + ".\n"

            input_text_weight = stats["text_weight"]
            if not check_text_weight(input_text, input_text_weight):
                ret += comp_str.capitalize() + "'s input text needs to have its weight changed to " + str(input_text_weight) + ".\n"

            label_text_size = stats["label_text_populated_size"]

        if len(comp.find_all("div", attrs={"class": "placeholder-text"})) > 0:
            placeholder_text = comp.find_all("div", attrs={"class": "placeholder-text"})[1]

            placeholder_text_size = stats["text_size"]
            if not check_text_size(placeholder_text, placeholder_text_size):
                ret += comp_str.capitalize() + "'s placeholder text needs to have its size changed to " + str(
                    placeholder_text_size) + ".\n"

            placeholder_text_weight = stats["text_weight"]
            if not check_text_weight(placeholder_text, placeholder_text_weight):
                ret += comp_str.capitalize() + "'s placeholder text needs to have its weight changed to " + str(
                    placeholder_text_weight) + ".\n"

            label_text_size = stats["label_text_populated_size"]

        if not check_text_size(label_text, label_text_size):
            ret += comp_str.capitalize() + "'s label text needs to have its size changed to " + str(label_text_size) + ".\n"

        if not check_text_weight(label_text, label_text_weight):
            ret += comp_str.capitalize() + "'s label text needs to have its weight changed to " + str(label_text_weight) + ".\n"

        if label_text_size != 16:
            label_text_padding = stats["label_text_padding"]

            if not check_left_padding(label_text, label_text_padding) or not check_right_padding(label_text,
                                                                                                 label_text_padding):
                ret += "Ensure that " + comp_str + "'s label text has a distance to the left and right of " + str(
                    label_text_padding) + ".\n"

        if ret != "":
            comp.append("<div class = 'Mark-" + comp["class"][0] + "' style = 'position: " + style["position"] + "; box-shadow: inset 0px 0px 0px 4px red;'")

    return ret
