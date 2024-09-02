import sys
sys.path.append("./utils")

from openai_utils import *
from prompting_utils import *
from json_to_html_utils import extract_comp
from retrieval_utils import *
import json
import pyterrier as pt
import os
import argparse
import datetime
import pickle
import copy
from bs4 import BeautifulSoup

pt.init()

comp_classes = json.load(open(sys.path[0] + "/data/comp_classes.json"))
example_comps = json.load(open(sys.path[0] + "/data/example_comps.json"))
guidelines = json.load(open(sys.path[0] + "/data/guidelines_for_indexing.json"))
extraction_methods = json.load(open(sys.path[0] + "/data/comp_extraction_methods.json"))
api_key = json.load(open(sys.path[0] + "/data/openai_api_key.json"))["api_key"]
client = login_openai()


def implement_changes(data_path, filename, changes_loc):
    changes_file = changes_loc + "/fixed.txt"
    soup = get_soup(data_path, filename)
    errors = {"file": 0, "delete": 0, "change": 0, "new": 0}
    try:
        changes_txt = open(changes_file, "r").read()
        changes_txt = changes_txt.replace("\n", "")
        changes_txt = changes_txt.replace("(\"", "[\"")
        changes_txt = changes_txt.replace("\")", "\"]")
        changes = extract_answers(changes_txt)

        for deleted_comp_id in changes["deleted_components"]:
            try:
                soup.find(id=deleted_comp_id).decompose()
            except Exception as e:
                print("    deleting error")
                print(deleted_comp_id)
                print("   ", type(e), e)
                errors["delete"] += 1

        for changed_comp in changes["changed_components"]:
            comp_soup = BeautifulSoup(changed_comp, "lxml")
            comp_id = comp_soup.body.contents[0]["id"]
            try:
                # print(comp_soup.prettify())
                soup.find(id=comp_id).replaceWith(comp_soup.body.contents[0])
            except Exception as e:
                print("    change implementation error")
                print(comp_id)
                print("   ", type(e), e)
                errors["change"] += 1

        for new_comp in changes["new_components"]:
            comp_soup = BeautifulSoup(new_comp[0], "lxml")
            parent_id = new_comp[1]
            try:
                parent = soup.find(id=parent_id)
                parent.append(comp_soup.body.contents[0])
            except Exception as e:
                print("    new comps error")
                print(parent_id)
                print("   ", type(e), e)
                errors["add"] += 1

        for x in soup.find_all(string=True):
            if x.text.strip() != "":
                # print(x.text)
                fixed_x = x.replace(x.text, x.text.strip())
                # print(fixed_x)
                x.replaceWith(fixed_x)

        with open(changes_loc + "/" + filename + "_fixed.html", "w", encoding="utf-8") as f:
            f.write(str(soup))
            f.close()

    except Exception as e:
        print("    json extraction error")
        print("   ", type(e), e)
        errors["file"] += 1
        with open(changes_loc + "/" + filename + "_fixed.html", "w", encoding="utf-8") as f:
            f.write(str(soup))
    return errors


def one_step(location, filename, comp_type, main_method, use_image, use_examples, few_shot, dest, verbose, temp, estimate_costs=False):
    if not estimate_costs:
        if dest == "auto":
            timestamp = datetime.datetime.now().strftime("%H_%M_%S_%d_%m_%Y")
            dest_folder = location + filename + "_" + comp_type + "_" + main_method + "_one_step_" + timestamp
        else:
            dest_folder = dest

        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)

    if use_image:
        image = encode_image(location + filename + ".jpg")
    else:
        image = None

    if use_examples:
        examples = example_comps
    else:
        examples = None

    try:
        parsed = create_html_file(location, filename)
    except Exception as e:
        print(e)

    soup = get_soup(location, filename)
    if len(extract_comp(soup, comp_type, comp_classes)) <= 0:
        return False, ""

    if main_method == "auto":
        method = extraction_methods[comp_type]
    else:
        method = main_method
    prompts = create_prompts(comp_type, soup, guidelines, method, comp_classes=comp_classes, image=image,
                             few_shot_examples=few_shot, example_comps=examples)
    if not estimate_costs:
        pickle.dump(prompts, open(dest_folder + "/prompts.pkl", "wb"))

        if verbose:
            print("PROMPTS")
            for i in [4, 3, 2, 1]:
                print(prompts[-i][1])
            print("################################")

        try:
            response = respond_to_image_multiple(prompts, api_key, temp=temp)
            fixed = response["choices"][0]["message"]["content"]
        except Exception as e:
            with open(dest_folder + "/response_error.txt", "w") as f:
                f.write(str(response))
                f.close()
            return False, dest_folder

        with open(dest_folder + "/fixed.txt", "w") as f:
            f.write(fixed)
            f.close()

        if verbose:
            print("RESPONSE")
            print(fixed)
            print("################################")

        return True, dest_folder

    else:
        return estimate_cost(prompts)



def two_steps(location, filename, comp_type, main_method, use_image, use_examples, few_shot, dest, verbose, temp, estimate_costs=False):
    if not estimate_costs:
        if dest == "auto":
            timestamp = datetime.datetime.now().strftime("%H_%M_%S_%d_%m_%Y")
            dest_folder = location + filename + "_" + comp_type + "_" + main_method + "_two_step_" + timestamp
        else:
            dest_folder = dest

        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)
    two_step_costs = {"max_input_tokens": 0, "max_input_cost": 0, "max_output_cost": 0, "max_cost": 0}

    if use_image:
        image = encode_image(location + filename + ".jpg")
    else:
        image = None

    if use_examples:
        examples = example_comps
    else:
        examples = None

    try:
        parsed = create_html_file(location, filename)
    except Exception as e:
        print(e)

    soup = get_soup(location, filename)
    if len(extract_comp(soup, comp_type, comp_classes)) <= 0:
        return False, ""

    if main_method == "auto":
        method = extraction_methods[comp_type]
    else:
        method = main_method

    prompts = create_prompts(comp_type, soup, guidelines, method, comp_classes=comp_classes, image=image,
                                    change_code=False, few_shot_examples=few_shot, example_comps=examples)
    if not estimate_costs:
        pickle.dump(prompts, open(dest_folder + "/first_prompts.pkl", "wb"))

        if verbose:
            print("PROMPTS")
            for i in [4, 3, 2, 1]:
                print(prompts[-i][1])
            print("################################")

        response = respond_to_image_multiple(prompts, api_key, temp=temp)
        try:
            changes = response["choices"][0]["message"]["content"]
        except Exception as e:
            with open(dest_folder + "/error.txt", "w") as f:
                f.write(str(response))
                f.close()
            return False, dest_folder


        with open(dest_folder + "/changes.txt", "w") as f:
            f.write(changes)
            f.close()

        if verbose:
            print("RESPONSE")
            print(changes)
            print("################################")

        extracted = extract_answers(changes)
        retrieved_guidelines = retrieve(sys.path[0] + "/guideline_index", extracted["guideline_request"])
        retrieved_examples = retrieve(sys.path[0] + "/example_index", extracted["example_request"])

        guidelines_to_pass = []
        counter = 0
        for index, row in retrieved_guidelines.iterrows():
            guidelines_to_pass.append(row["text"])
            if counter >= 20:
                break
            counter += 1

        examples_to_pass = []
        counter = 0
        for index, row in retrieved_examples.iterrows():
            examples_to_pass.append(row["text"])
            if counter >= 5:
                break
            counter += 1

        if main_method == "auto":
            method = "full_code"
        else:
            method = main_method
        second_prompts = implement_changes_prompt(changes, comp_type, method, soup, comp_classes, examples_to_pass,
                                                  guidelines_to_pass, image=image, few_shot_examples=True)

        pickle.dump(second_prompts, open(dest_folder + "/second_prompts.pkl", "wb"))

        if verbose:
            print("SECOND PROMPTS")
            for i in [5, 4, 3, 2, 1]:
                print(second_prompts[-i][1])
            print("################################")

        try:
            second_response = respond_to_image_multiple(second_prompts, api_key, temp=temp)
            fixed = second_response["choices"][0]["message"]["content"]
        except Exception as e:
            with open(dest_folder + "/error.txt", "w") as f:
                f.write(str(second_response))
                f.close()
            return False, dest_folder

        with open(dest_folder + "/fixed.txt", "w", encoding="utf-8") as f:
            f.write(fixed)
            f.close()

        if verbose:
            print("SECOND RESPONSE")
            print(fixed)
            print("################################")

        return True, dest_folder

    else:
        costs = estimate_cost(prompts)
        two_step_costs["max_input_tokens"] += costs["input_tokens"]
        two_step_costs["max_input_cost"] += costs["input_cost"]
        two_step_costs["max_output_cost"] += costs["max_output_cost"]
        two_step_costs["max_cost"] += costs["max_cost"]

        max_tokens = 128000
        input_cost_ratio = 5 / 1000000
        max_input_cost = max_tokens * input_cost_ratio
        max_output_cost = 4096 * (15 / 1000000)
        max_cost = max_input_cost + max_output_cost

        two_step_costs["max_input_tokens"] += max_tokens
        two_step_costs["max_input_cost"] += max_input_cost
        two_step_costs["max_output_cost"] += max_output_cost
        two_step_costs["max_cost"] += max_cost

        return two_step_costs


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('location')
    parser.add_argument('filename')
    parser.add_argument('comp_type')

    parser.add_argument('-i', '--image', action='store_true')
    parser.add_argument('-ex', '--examples', action='store_true')
    parser.add_argument('-f', '--few-shot', action='store_true')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-af', '--apply-fixes', action='store_true')
    parser.add_argument('-m', '--mode', default='two-step')
    parser.add_argument('-em', '--extraction-method', default='auto')
    parser.add_argument('-d', '--destination', default='auto')
    parser.add_argument('-t', '--temperature', default=0.75)

    args = parser.parse_args()

    if args.comp_type != "all":
        fix_loc = ""
        if args.mode == "three-step":
            worked, fix_loc = three_steps(args.location, args.filename, args.comp_type, args.extraction_method, args.image,
                                args.examples, args.few_shot, args.destination, args.verbose, args.temperature)
        elif args.mode == "two-step":
            worked, fix_loc = two_steps(args.location, args.filename, args.comp_type, args.extraction_method, args.image,
                                          args.examples, args.few_shot, args.destination, args.verbose, args.temperature)
        elif args.mode == "one-step":
            worked, fix_loc = one_step(args.location, args.filename, args.comp_type, args.extraction_method, args.image,
                                args.examples, args.few_shot, args.destination, args.verbose, args.temperature)

        if not worked:
             print(args.comp_type + " does not exist in " + args.location + args.filename + ".")
        elif args.apply_fixes:
            implement_changes(args.location, args.filename, fix_loc)
    else:
        for comp_type in comp_classes.keys():
            fix_loc = ""
            if args.mode == "three-step":
                worked, fix_loc = three_steps(args.location, args.filename, comp_type, args.extraction_method, args.image,
                                    args.examples, args.few_shot, args.destination, args.verbose, args.temperature)
            elif args.mode == "two-step":
                worked, fix_loc = two_steps(args.location, args.filename, comp_type, args.extraction_method, args.image,
                                            args.examples, args.few_shot, args.destination, args.verbose, args.temperature)
            elif args.mode == "one-step":
                worked, fix_loc = one_step(args.location, args.filename, comp_type, args.extraction_method, args.image,
                                   args.examples, args.few_shot, args.destination, args.verbose, args.temperature)

            if not worked:
                print(comp_type + " does not exist in " + args.location + args.filename + ".")
            elif args.apply_fixes:
                implement_changes(args.location, args.filename, fix_loc)

