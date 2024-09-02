import sys
sys.path.append("./utils")

import pickle
from json_to_html_utils import extract_comp, extract_comp_containers, json_to_html, create_html_file, get_soup
from ast import literal_eval
from comp_stat_checking import check_comp_issues
import os

def create_prompts(comp_type, soup, guidelines, method, comp_classes, few_shot_examples=False, example_comps=None,
                   image=None, include_system_prompt=True, change_code=True, descriptions=None):
    prompts = []
    # few shot examples
    if few_shot_examples:
        if method == "descriptions":
            few_shot_path = sys.path[0] + "/../Few Shot Examples/" + comp_type + "/two_step/"
            for root, dir, files in os.walk(few_shot_path):
                for file in files:
                    if ".json" in file:
                        filename = file.replace(".json", "")
                        change_prompts = pickle.load(open(few_shot_path + filename + "_changes_prompt.pkl", "rb"))
                        prompts.extend(change_prompts)
                        answer = open(few_shot_path + filename + "_changes.txt", "r").read()
                        prompts.append(("assistant", answer, None))
        elif not change_code:
            few_shot_path = sys.path[0] + "/../Few Shot Examples/" + comp_type + "/two_step/"
            for root, dir, files in os.walk(few_shot_path):
                for file in files:
                    if ".json" in file:
                        filename = file.replace(".json", "")
                        change_prompts = pickle.load(open(few_shot_path + filename + "_changes_from_code_prompt.pkl", "rb"))
                        prompts.extend(change_prompts)
                        answer = open(few_shot_path + filename + "_changes.txt", "r").read()
                        prompts.append(("assistant", answer, None))
        else:
            few_shot_path = sys.path[0] + "/../Few Shot Examples/" + comp_type + "/one_step/"
            for root, dir, files in os.walk(few_shot_path):
                for file in files:
                    if ".json" in file:
                        filename = file.replace(".json", "")
                        #print(filename)
                        change_prompts = pickle.load(open(few_shot_path + filename + "_prompts.pkl", "rb"))
                        prompts.extend(change_prompts)
                        answer = open(few_shot_path + filename + "_fixed.txt", "r").read()
                        prompts.append(("assistant", answer, None))
                        #print(len(prompts))

    # system prompt
    comp_guidelines = guidelines[comp_type]
    system_prompt = "You are an assistant for mobile UI design, with your knowledge being focused on the Material Design 3 Guidelines. " \
                    "You give very specific and detailed guidance. Do not use guidelines other than those provided to you. Only give guidance " \
                    "if you are very sure a guideline is violated. Never suggest any changes that are conflicting with one another. " \
                    "Your guidance is very precise: There is absolutely no pressure to always identify errors. You would rather maybe miss a small error than give useless guidance." \
                    "Do not give any guidance related to 'verifying' anything, only actual implementable changes. It is okay if you do not find any issues. " \
                    "You can assume that aspects of the mockup like border radiuses, stroke design, and the alignment of content " \
                    "inside Material Design components are ok as presented, since another system takes care of these issues. " \
                    "Note that since your guidance will be concerning mockups, not working implementations, you should not be concerned " \
                    "with functionality, just design. If the data you are provided does not contain enough information to check if " \
                    "certain guidelines are violated, you point this out and indicate which extra information you would need. " \
                    "You always give reasoning for your decisions: Explain which parts of the data provided to you you based your " \
                    "decisions upon and what extra information would be useful to you. Only use the guidelines given to you in this prompt " \
                    "as a basis for your guidance. Here are some general Material Design 3 Guidelines:"

    for guideline in guidelines["general"]:
        system_prompt += "\n" + guideline

    system_prompt += "Here is a description of the various types of components in Material Design 3:"
    for guideline in guidelines["component_types"]:
        system_prompt += "\n" + guideline

    system_prompt += "\nAdditionally, the Material Design 3 Guidelines include these guidelines for " + comp_type.replace(
        "_", " ") + "s:"
    for guideline in comp_guidelines:
        system_prompt += "\n" + guideline

    # component examples
    if example_comps is not None:
        examples = example_comps[comp_type]

        system_prompt += "\nHere are some examples of what the code for a " + comp_type.replace("_",
                                                                                                " ") + " looks like:"
        for example in examples:
            system_prompt += "\n\n" + example

    # user prompts
    user_prompt = ""
    final_prompt = ""
    if method == "comps":
        user_prompt = "I will send you html code snippets representing parts of a mockup of a mobile user interface, " \
                      "in this case specifically the " + \
                      comp_type.replace("_", " ") + \
                      "s contained in the mockup. Can you identify any potential Material Design 3 Guideline violations, point them out to me"
        if change_code:
            user_prompt += ", and alter the code to fix them? If you are replacing one type of component with another, the new component's styling takes priority. " +\
                         "Also indicate any elements you delete from the code (for these, their id suffices), and new components " +\
                         "you add to the code (for these, also provide the id of their parent elements). If the new components are " +\
                         "already included in the changes for another component, you don't need to include them again. Please answer in json format " +\
                         "like so: {'violations': 'Ordered natural language description of violations', " \
                         "'changes': 'Natural language list of your changes'," +\
                         "'changed_components': [list of changed components], " +\
                         "'deleted_components': [list of deleted components ids], " +\
                         "'new_components': [list of tuples that look like this: (new component code, parent id)]} " +\
                         "Make sure to keep your answer as brief as possible by including only the html tags that actually changed " +\
                         "(although they should still be identifiable using their ids and contain their respective full code). " +\
                         "Please be faithful to the json format I described, this includes not adding any further dictionary nesting. " +\
                         "The list of changed components should just be a list of html code snippets that are complete enough to " +\
                         "be parsed as tags and inserted into other code without any complications. This includes making sure your changes do not lead to duplicate ids in the code."
        else:
            user_prompt += ", and describe the necessary changes to fix them? Do not make changes to the code and do not give code examples, just give me a natural-language description. " \
                      "You can assume that aspects of the mockup like border radiuses, stroke design, click area sizes, typography, and the alignment of content " \
                      "inside Material Design components are ok as presented, since another system takes care of these issues. " \
                      "Do not give any guidance related to 'verifying' anything, only actual implementable changes. It is okay if you do not find any issues. " \
                      "Also, indicate how severe you think the violations are, order your suggestions based on how necessary you think " \
                      "they are, and explain your ordering. I have two resources with extra information available: " \
                      "A collection of the Material Design 3 Guidelines (although the ones you have access to right now should be sufficient), " \
                      "and a collection of example html implementations of Material Design 3 components. " \
                      "Let me know if you think any information from these collections (and only these collections) would be useful for someone trying to apply your suggested fixes. " \
                      "If so, please very specifically indicate what information exactly you would look for (name the types of guidelines and which example components would be helpful). "
            user_prompt += "Please reply in json format, like so: {'violations': 'Ordered natural language description of violations', 'changes': 'Natural language list of suggested changes', " \
                       "'guideline_request': 'A search query you would use to retrieve any guidelines you think might be useful to implement your suggested changes from a collection of Material Design 3 guidelines', " \
                       "'example_request': 'A search query you would use to retrieve example html implementations of components you think might be useful to implement your suggested changes from a collection of Material Design 3 component implementations'} " \
                       "Make sure your answer is interpretable as json data without any issues. "

        comps = extract_comp(soup, comp_type, comp_classes)
        final_prompt = "Here are the code snippets:\n"
        for comp in comps:
            final_prompt += "\n" + str(comp.prettify())

    elif method == "comp_containers":
        user_prompt = "I will send you html code snippets representing parts of a mockup of a mobile user interface, " \
                      "in this case specifically the elements containing " + \
                      comp_type.replace("_", " ") + \
                      "s contained in the mockup. Can you identify any potential Material Design 3 Guideline violations, point them out to me"
        if change_code:
            user_prompt += ", and alter the code to fix them? If you are replacing one type of component with another, the new component's styling takes priority. " +\
                         "Also indicate any elements you delete from the code (for these, their id suffices), and new components " +\
                         "you add to the code (for these, also provide the id of their parent elements). If the new components are " +\
                         "already included in the changes for another component, you don't need to include them again. Please answer in json format " +\
                         "like so: {'violations': 'Ordered natural language description of violations', " \
                         "'changes': 'Natural language list of your changes'," +\
                         "'changed_components': [list of changed components], " +\
                         "'deleted_components': [list of deleted components ids], " +\
                         "'new_components': [list of tuples that look like this: (new component code, parent id)]} " +\
                         "Make sure to keep your answer as brief as possible by including only the html tags that actually changed " +\
                         "(although they should still be identifiable using their ids and contain their respective full code). " +\
                         "Please be faithful to the json format I described, this includes not adding any further dictionary nesting. " +\
                         "The list of changed components should just be a list of html code snippets that are complete enough to " +\
                         "be parsed as tags and inserted into other code without any complications. This includes making sure your changes do not lead to duplicate ids in the code."
        else:
            user_prompt += ", and describe the necessary changes to fix them? Do not make changes to the code and do not give code examples, just give me a natural-language description. " \
                      "You can assume that aspects of the mockup like border radiuses, stroke design, click area sizes, typography, and the alignment of content " \
                      "inside Material Design components are ok as presented, since another system takes care of these issues. " \
                      "Do not give any guidance related to 'verifying' anything, only actual implementable changes. It is okay if you do not find any issues. " \
                      "Also, indicate how severe you think the violations are, order your suggestions based on how necessary you think " \
                      "they are, and explain your ordering. I have two resources with extra information available: " \
                      "A collection of the Material Design 3 Guidelines (although the ones you have access to right now should be sufficient), " \
                      "and a collection of example html implementations of Material Design 3 components. " \
                      "Let me know if you think any information from these collections (and only these collections) would be useful for someone trying to apply your suggested fixes. " \
                      "If so, please very specifically indicate what information exactly you would look for (name the types of guidelines and which example components would be helpful). "
            user_prompt += "Please reply in json format, like so: {'violations': 'Ordered natural language description of violations', 'changes': 'Natural language list of suggested changes', " \
                       "'guideline_request': 'A search query you would use to retrieve any guidelines you think might be useful to implement your suggested changes from a collection of Material Design 3 guidelines', " \
                       "'example_request': 'A search query you would use to retrieve example html implementations of components you think might be useful to implement your suggested changes from a collection of Material Design 3 component implementations'} " \
                       "Make sure your answer is interpretable as json data without any issues. "

        containers = []
        extract_comp_containers(soup, comp_type, containers, comp_classes)
        containers = list(set(containers))
        final_prompt = "Here are the code snippets:\n"
        for container in containers:
            final_prompt += "\n" + str(container.prettify())

    elif method == "full_code":
        user_prompt = "I will send you html code representing a mockup of a mobile user interface. " \
                      "Can you identify any potential Material Design 3 Guideline violations," \
                      " regarding the " + \
                      comp_type.replace("_", " ") + \
                      "s contained in the mockup. Can you identify any potential Material Design 3 Guideline violations, point them out to me"
        if change_code:
            user_prompt += ", and alter the code to fix them? If you are replacing one type of component with another, the new component's styling takes priority. " +\
                         "Also indicate any elements you delete from the code (for these, their id suffices), and new components " +\
                         "you add to the code (for these, also provide the id of their parent elements). If the new components are " +\
                         "already included in the changes for another component, you don't need to include them again. Please answer in json format " +\
                         "like so: {'violations': 'Ordered natural language description of violations', " \
                         "'changes': 'Natural language list of your changes'," +\
                         "'changed_components': [list of changed components], " +\
                         "'deleted_components': [list of deleted components ids], " +\
                         "'new_components': [list of tuples that look like this: (new component code, parent id)]} " +\
                         "Make sure to keep your answer as brief as possible by including only the html tags that actually changed " +\
                         "(although they should still be identifiable using their ids and contain their respective full code). " +\
                         "Please be faithful to the json format I described, this includes not adding any further dictionary nesting. " +\
                         "The list of changed components should just be a list of html code snippets that are complete enough to " +\
                         "be parsed as tags and inserted into other code without any complications. This includes making sure your changes do not lead to duplicate ids in the code."
        else:
            user_prompt += ", and describe the necessary changes to fix them? Do not make changes to the code and do not give code examples, just give me a natural-language description. " \
                      "You can assume that aspects of the mockup like border radiuses, stroke design, click area sizes, typography, and the alignment of content " \
                      "inside Material Design components are ok as presented, since another system takes care of these issues. " \
                      "Do not give any guidance related to 'verifying' anything, only actual implementable changes. It is okay if you do not find any issues. " \
                      "Also, indicate how severe you think the violations are, order your suggestions based on how necessary you think " \
                      "they are, and explain your ordering. I have two resources with extra information available: " \
                      "A collection of the Material Design 3 Guidelines (although the ones you have access to right now should be sufficient), " \
                      "and a collection of example html implementations of Material Design 3 components. " \
                      "Let me know if you think any information from these collections (and only these collections) would be useful for someone trying to apply your suggested fixes. " \
                      "If so, please very specifically indicate what information exactly you would look for (name the types of guidelines and which example components would be helpful). "
            user_prompt += "Please reply in json format, like so: {'violations': 'Ordered natural language description of violations', 'changes': 'Natural language list of suggested changes', " \
                       "'guideline_request': 'A search query you would use to retrieve any guidelines you think might be useful to implement your suggested changes from a collection of Material Design 3 guidelines', " \
                       "'example_request': 'A search query you would use to retrieve example html implementations of components you think might be useful to implement your suggested changes from a collection of Material Design 3 component implementations'} " \
                       "Make sure your answer is interpretable as json data without any issues. "

        final_prompt = "Here is the code:\n"
        final_prompt += "\n" + str(soup.prettify())

    elif method == "descriptions":
        user_prompt = "I will send you descriptions representing some components of a mockup of a mobile user interface, namely the " + \
                      comp_type.replace("_", " ") + "s contained in the mockup. " + \
                      "Can you identify any potential Material Design 3 Guideline violations," \
                      " based on the descriptions, point them out to me, and describe the necessary changes to fix them? " \
                      "Do not make changes to the code and do not give code examples, just give me a natural-language description. " \
                      "You can assume that aspects of the mockup like border radiuses, stroke design, click area sizes, typography, and the alignment of content " \
                      "inside Material Design components are ok as presented, since another system takes care of these issues. " \
                      "Do not give any guidance related to 'verifying' anything, only actual implementable changes. It is okay if you do not find any issues. " \
                      "Also, indicate how severe you think the violations are, order your suggestions based on how necessary you think " \
                      "they are, and explain your ordering. I have two resources with extra information available: " \
                      "A collection of the Material Design 3 Guidelines (although the ones you have access to right now should be sufficient), " \
                      "and a collection of example html implementations of Material Design 3 components. " \
                      "Let me know if you think any information from these collections (and only these collections) would be useful for someone trying to apply your suggested fixes. " \
                      "If so, please very specifically indicate what information exactly you would look for (name the types of guidelines and which example components would be helpful). "
        user_prompt += "Please reply in json format, like so: {'violations': 'Ordered natural language description of violations', 'changes': 'Natural language list of suggested changes', " \
                       "'guideline_request': 'A search query you would use to retrieve any guidelines you think might be useful to implement your suggested changes from a collection of Material Design 3 guidelines', " \
                       "'example_request': 'A search query you would use to retrieve example html implementations of components you think might be useful to implement your suggested changes from a collection of Material Design 3 component implementations'} " \
                       "Make sure your answer is interpretable as json data without any issues. "

        final_prompt = "Here are the descriptions:\n"
        final_prompt += "\n" + descriptions

    if image is not None:
        if method != "no_code":
            user_prompt += "I will also send you an image of the mockup."
        if include_system_prompt:
            prompts.insert(0, ("system", system_prompt, None))
        prompts.append(("user", user_prompt, None))
        prompts.append(("user", "Here is the image:\n", image))
        prompts.append(("user", final_prompt, None))
    else:
        if include_system_prompt:
            prompts.insert(0, ("system", system_prompt, None))
        prompts.append(("user", user_prompt))
        prompts.append(("user", final_prompt))

    # print(user_prompt)

    return prompts


def prompt_description(comp_type, soup, method, comp_classes, example_comps=None, image=None):
    prompts = []

    # user prompts
    user_prompt = ""
    final_prompt = ""
    if method == "comps":
        user_prompt = "I will send you html code snippets representing parts of a mockup of a mobile user interface, " \
                      "in this case specifically the " + \
                      comp_type.replace("_", " ") + \
                      "s contained in the mockup. Can you give me a detailed, short but succinct, natural-language description of each " + \
                      comp_type.replace("_",
                                        " ") + ", including its specific type, color, size, shape, position (both in terms of numbers and a general description), id, likely function, and any other attributes that might be important?" \
                      " Please also mention if the design is in dark or light (standard) mode. "

        comps = extract_comp(soup, comp_type, comp_classes)
        final_prompt = "Here are the code snippets:\n"
        for comp in comps:
            final_prompt += "\n" + str(comp.prettify())

    elif method == "comp_containers":
        user_prompt = "I will send you html code snippets representing parts of a mockup of a mobile user interface, " \
                      "in this case specifically the elements containing " + \
                      comp_type.replace("_", " ") + \
                      "s contained in the mockup. Can you give me a detailed, short but succinct, natural-language description of each " + \
                      comp_type.replace("_",
                                        " ") + ", including its specific type, color, size, shape, position (both in terms of numbers and a general description), id, likely function, and any other attributes that might be important?"

        containers = []
        extract_comp_containers(soup, comp_type, containers, comp_classes)
        containers = list(set(containers))
        final_prompt = "Here are the code snippets:\n"
        for container in containers:
            final_prompt += "\n" + str(container.prettify())

    elif method == "full_code":
        user_prompt = "I will send you html code representing a mockup of a mobile user interface. " \
                      "Can you give me a detailed, short but succinct, natural-language description of each " + \
                      comp_type.replace("_",
                                        " ") + ", including its specific type, color, size, shape, position (both in terms of numbers and a general description), id, likely function, and any other attributes that might be important?"

        final_prompt = "Here is the code:\n"
        final_prompt += "\n" + str(soup.prettify())

    # component examples
    if example_comps is not None:
        examples = example_comps[comp_type]

        user_prompt += "\nHere are some examples of what the code for a " + comp_type.replace("_",
                                                                                                " ") + " looks like:"
        for example in examples:
            user_prompt += "\n\n" + example

    if image is not None:
        if method != "no_code":
            user_prompt += "I will also send you an image of the mockup."
        prompts.append(("user", user_prompt, None))
        prompts.append(("user", "Here is the image:\n", image))
        prompts.append(("user", final_prompt, None))
    else:
        prompts.append(("user", user_prompt))
        prompts.append(("user", final_prompt))

    # print(user_prompt)
    return prompts


def implement_changes_prompt(changes, comp_type, method, soup, comp_classes, example_comps, guidelines, image=None, few_shot_examples=False):
    prompts = []

    if few_shot_examples:
        few_shot_path = sys.path[0] + "/../Few Shot Examples/" + comp_type + "/two_step/"
        for root, dir, files in os.walk(few_shot_path):
            for file in files:
                if ".json" in file:
                    filename = file.replace(".json", "")
                    final_prompts = pickle.load(open(few_shot_path + filename + "_final_prompts.pkl", "rb"))
                    prompts.extend(final_prompts)
                    answer = open(few_shot_path + filename + "_fixed.txt", "r").read()
                    prompts.append(("assistant", answer, None))

    system_prompt = "You are an assistant for mobile UI design, with your knowledge being focused on the Material Design 3 Guidelines. " + \
                    "You are also an HTML expert. You follow instructions very thoroughly, but do not do anything you are not explicitly told to do. " + \
                    "Here are some standard implementations of Material Design 3 components in html that you might need:"
    for example in example_comps:
        system_prompt += "\n" + example
    system_prompt += "Note that background border radius, and stroke styling are important parts of the component's identity and should be the same as in these standard implementations, unless your instructions explicitly state otherwise." \
                     "Also, here are some guidelines that you might need to pay attention to while implementing your changes:"
    for guideline in guidelines:
        system_prompt += "\n" + guideline

    prompt = "I will send you some html code and a description of some changes I want you to make to the code. " +\
             "Please send me back the changed version. If the components you are editing contain text, make sure " +\
             "that you do not add any unnecessary whitespace (like line breaks) to it, as this can cause issues " +\
             "with its presentation. Note that background border radius, color and stroke styling are important parts " + \
             "of a components identity and should be the same as in the standard implementations in most cases. " +\
             "If you are replacing one type of component with another, the new component's styling takes priority. " +\
             "Also indicate any elements you delete from the code (for these, their id suffices), and new components " +\
             "you add to the code (for these, also provide the id of their parent elements). If the new components are " +\
             "already included in the changes for another component, you don't need to include them again. Please answer in json format " +\
             "like so: {'changed_components': [list of changed components], " +\
             "'deleted_components': [list of deleted components ids], " +\
             "'new_components': [list of tuples that look like this: (new component code, parent id)]} " +\
             "Make sure to keep your answer as brief as possible by including only the html tags that actually changed " +\
             "(although they should still be identifiable using their ids and contain their respective full code). " +\
             "Please be faithful to the json format I described, this includes not adding any further dictionary nesting. " +\
             "The list of changed components should just be a list of html code snippets that are complete enough to " +\
             "be parsed as tags and inserted into other code without any complications. This includes making sure your changes do not lead to duplicate ids in the code."

    code_prompt = ""

    if method == "comps":

        comps = extract_comp(soup, comp_type, comp_classes)
        code_prompt = "Here are the code snippets:\n"
        for comp in comps:
            code_prompt += "\n" + str(comp.prettify())

    elif method == "comp_containers":

        containers = []
        extract_comp_containers(soup, comp_type, containers, comp_classes)
        containers = list(set(containers))
        code_prompt = "Here are the code snippets:\n"
        for container in containers:
            code_prompt += "\n" + str(container.prettify())

    elif method == "full_code":

        code_prompt = "Here is the code:\n"
        code_prompt += "\n" + str(soup.prettify())

    change_prompt = "And these are the changes I want you to make:\n" + changes

    if image is not None:
        prompt += "I will also send you an image of the mockup the code represents."
        prompts.append(("system", system_prompt, None))
        prompts.append(("user", prompt, None))
        prompts.append(("user", "Here is the image:\n", image))
        prompts.append(("user", code_prompt, None))
        prompts.append(("user", change_prompt, None))
    else:
        prompts.append(("system", system_prompt, None))
        prompts.append(("user", prompt))
        prompts.append(("user", code_prompt, None))
        prompts.append(("user", change_prompt, None))

    # print(user_prompt)

    return prompts

def extract_answers(response):
    json_start = response.find("{")
    json_end = response.rfind("}")
    json_string = response[json_start:json_end+1]
    dic = literal_eval(json_string)
    return dic