# Installation

Use `pip install -r requirements.txt` to install all required python packages.

[pyterrier](https://pyterrier.readthedocs.io/en/latest/), which we use for our retrieval indexes, requires a working JDK installation and the path variable JAVA_HOME to be set to that JDK's bin folder.

To use the OpenAI API, insert your API key into Code/utils/openai_api_key.json.

If you want to verify or change our complexity metric statistics, you will also need the [enrico](https://github.com/luileito/enrico) dataset, but it is not necessary for the system to work.

# Overview

<img src = "https://github.com/user-attachments/assets/edfc282b-662a-4ed4-a329-77e809bc2351">

This repository provides a UI design assistance system for Figma and Material Design 3 consisting of three modules: 

- Layout complexity analysis
- Component specification adherence checking
- LLM-based identification of guideline violations, change suggestion, and implementation



# File Structure

```
.
├───Code                                                        # all the code needed to use our system
├───Component Examples                                          # example HTML code for all component types we examine
├───Few Shot Examples                                           # Few-Shot examples for both of our methods for every component type
├───Latex                                                       # Latex files for the full thesis
├───Notebooks                                                   # Jupyter Notebooks used for result analysis and to calculate complexity metrics for enrico sample
├───Screens                                                     # Our dataset of Figma designs
├───User Study                                                  # The results of our first user study, organized by participant and component type
├───User Study Sample                                           # A sample of our first user studies results which we used for our second user study
├───Guidelines.xlsx                                             # Complete list of guidelines we used
├───Mobile UI Fix Application Evaluation.csv                    # Google Forms responses from our second user study
├───User Study Overview.xlsx                                    # list of User Study results with short descriptions of changes
├───User Study Sample annotated.csv                             # annotated results of our second user study
├───User Study Sample uploaded.csv                              # un-annotated list of examples we used for our second user study
├───component_numbers_and_few_shot_and_user_study_mappings.xlsx # lists number of component type instances per screen and
|                                                               # maps screens onto few-shot examples and user study screens
├───metric_statistics_enrico.csv                                # Complexity metrics for enrico sample
├───metric_statistics_figma.csv                                 # Complexity metrics for our dataset
├───metrics_enrico_and_figma.csv                                # Full complexity metric dataset
├───user_study_annotation_one_step_0.xlsx                       # annotations for the performance of the one-step method 
|                                                               # on participant 0's changed designs
├───user_study_annotation_one_step_1.xlsx                       # annotations for the performance of the one-step method 
|                                                               # on participant 1's changed designs
├───user_study_annotation_two_step_0.xlsx                       # annotations for the performance of the two-step method 
|                                                               # on participant 0's changed designs
├───user_study_annotation_two_step_1.xlsx                       # annotations for the performance of the two-step method 
|                                                               # on participant 1's changed designs
```

# Usage

To perform a full analysis on a Figma design, export it as a JSON file using this plug-in: https://www.figma.com/community/plugin/1135653849910773588/json-exporter and as a JPG image. Make sure both files have the same name and are located in the same folder.

Then, navigate to `Code` and run `python full_analysis.py`, which takes the following parameters:

- `--location` (required): The location of the design you want to analyze
- `--filename` (required): The filename of the design you want to analyze (without filetype endings)
- `--destination` (required): Where you want the results of the analysis to be saved
- `--method`: The method you want to use (`one-step or ``two-step`, default `one-step`)
- `-t/--type`: The component type you want to analyze (default `all`, which runs a full analysis)
- `--use-img/--no-img`: Flag to indicate whether or not you want to add the image of your design to the prompt (default `True`)
- `--use-ex/--no-ex`: Flag to indicate whether or not you want to add component examples to the prompt (default `True`)
- `--use-fs/--no-fs`: Flag to indicate whether or not you want to use few-shot prompting (default `True`)

Note: The LLM-based module will create a subfolder for each analyzed component type, so we recommend creating a new destination folder for your outputs. 
Also, make sure the paths in your arguments are relative to `Code`.
