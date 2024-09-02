from utils.prompt_gpt import *
from utils.metric_utils import *
from utils.comp_stat_checking import *
import json
import argparse
import os

def full_analysis(location, filename, destination, method, type, use_img, use_ex, use_fs):
    comp_classes = json.load(open("data/comp_classes.json"))
    full_measurement_check(location, filename, destination, comp_classes, screenshot=True)
    calc_metrics_and_show(location, filename, destination)
    for comp_type in comp_classes.keys():
        if type == "all" or type == comp_type:
            fix_loc = ""
            worked = False
            if method == "two-step":
                if not os.path.exists(destination + "/" + filename + "_" + comp_type + "_two_step"):
                    os.mkdir(destination + "/" + filename + "_" + comp_type + "_two_step")
                worked, fix_loc = two_steps(location, filename, comp_type, "auto", use_img, use_ex, use_fs,
                                            destination + "/" + filename + "_" + comp_type + "_two_step", False, 0.75)
            elif method == "one-step":
                if not os.path.exists(destination + "/" + filename + "_" + comp_type + "_one_step"):
                    os.mkdir(destination + "/" + filename + "_" + comp_type + "_one_step")
                worked, fix_loc = one_step(location, filename, comp_type, "auto", use_img, use_ex, use_fs,
                                           destination + "/" + filename + "_" + comp_type + "_one_step", False, 0.75)
            if not worked:
                print(comp_type + " does not exist in " + location + filename + ".")
            else:
                implement_changes(location, filename, fix_loc)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--location')
    parser.add_argument('--filename')
    parser.add_argument('--destination')
    parser.add_argument('--method', default='one-step')
    parser.add_argument('-t', '--type', default='all')

    parser.add_argument('--use-img', action='store_true')
    parser.add_argument('--use-ex', action='store_true')
    parser.add_argument('--use-fs', action='store_true')
    parser.add_argument('--no-img', action='store_false', dest='use_img')
    parser.add_argument('--no-ex', action='store_false', dest='use_ex')
    parser.add_argument('--no-fs', action='store_false', dest='use_fs')
    parser.set_defaults(use_img=True, use_ex=True, use_fs=True)

    args = parser.parse_args()

    full_analysis(args.location, args.filename, args.destination, args.method, args.type, args.use_img, args.use_ex, args.use_fs)