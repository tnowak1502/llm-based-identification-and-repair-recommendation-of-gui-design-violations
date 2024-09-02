import pyterrier as pt
import pandas as pd

def retrieve(index_dir, query):
    index = pt.IndexFactory.of(index_dir + "\\data.properties")
    bm25 = pt.BatchRetrieve(index, wmodel="BM25", metadata=["docno", "text", "type"],
                            properties={"termpipelines": "Stopwords,PorterStemmer"})

    pipe = pt.rewrite.tokenise() >> bm25

    res = pipe.search(query)
    return res