import pandas as pd
import pyterrier as pt
import json
import os

pt.init()

examples_json = json.load(open("data/example_comps.json", "r"))

examples_dic = {"type": [], "docno": [], "text": []}

counter = 0
for type in examples_json.keys():
    for example in examples_json[type]:
        examples_dic["type"].append(type)
        examples_dic["docno"].append(str(counter))
        examples_dic["text"].append(type.replace("_", " ") + ": " + example)
        counter += 1

examples_df = pd.DataFrame.from_dict(examples_dic)

print(examples_df.head())
examples_df.to_csv("example_comps.csv")

pd_indexer = pt.DFIndexer("..\\Code\\example_index",
                          meta = {"docno": 26, "type": 2048},
                          meta_tags = {"type": "ELSE"},
                          verbose=True)
indexref = pd_indexer.index(examples_df["type"], examples_df["docno"], examples_df["text"], examples_df["type"])