import pandas as pd
import pyterrier as pt
import json
import os

pt.init()

guidelines_json = json.load(open("data/guidelines_for_indexing.json", "r"))

guidelines_dic = {"type": [], "docno": [], "text": []}

counter = 0
for type in guidelines_json.keys():
    for guideline in guidelines_json[type]:
        guidelines_dic["type"].append(type)
        guidelines_dic["docno"].append(str(counter))
        guidelines_dic["text"].append(type.replace("_", " ") + ": " + guideline)
        counter += 1

guidelines_df = pd.DataFrame.from_dict(guidelines_dic)

print(guidelines_df.head())
#guidelines_df.to_csv("guidelines.csv")

pd_indexer = pt.DFIndexer("..\\Code\\guideline_index",
                          meta = {"docno": 26, "text": 2048, "type": 2048},
                          meta_tags = {"text": "ELSE"},
                          verbose=True)
indexref = pd_indexer.index(guidelines_df["text"], guidelines_df["docno"], guidelines_df["text"], guidelines_df["type"])