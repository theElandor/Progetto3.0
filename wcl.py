from textblob import TextBlob
import sys
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import re
import string
from wordcloud import WordCloud, STOPWORDS
import Main.Database as dd
import Main.IndexGenerator as ig
from whoosh.fields import *
from whoosh.analysis import StemmingAnalyzer
from Main.Results import Results
from Main.Searcher import Searcher
import time
from PIL import Image
# -----------------GENERAZIONE INDICE----------------
# # Creazione di un oggetto Database.
# db = dd.Database('./csv/airline.csv')
# # Popolazione del Database.
# db.fillDb()
# # Selezione dei campi da indicizzare.
# db.filterFields('handle','text')


# # Creazione dello schema per l'indice Whoosh.
# schema = Schema(
#     handle = TEXT(stored = True, analyzer = StemmingAnalyzer()),
#     text = TEXT(stored = True, analyzer = StemmingAnalyzer())
#     )

# # Creazione dell'indice.
# i = ig.IndexGenerator(schema, db)
# # Popolazione dell'indice.
# i.fillIndex()
#----------------QUERY-------------------
def create_wordcloud(text, file_name):
    stopwords = set(STOPWORDS)
    wordcloud = WordCloud(width = 800, height = 800,
                background_color ='white',
                stopwords = stopwords).generate(text)

    plt.figure(figsize = (8, 8), facecolor = None)
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.tight_layout(pad = 0)
    # plt.show()
    plt.savefig(file_name)

q = "customer service"
s = Searcher("handle", "text")
res = s.submit_query(q, results_threshold = 500)
r = Results("Vader", "positive", res, ranking_fun = "balanced_weighted_avg")
r.printResults(s, "Wordclouds/output_positive.ods")
text = ""
threshold = 0.2 # noise is reduced by a lot, considering only the tweets where sentiment is relevant
for tweet in r._ordered:
    if tweet["sent_score"] > threshold:
        text = text + tweet["text"]
text = text.replace("customer", "")
text = text.replace("service", "")
text = text.replace("USAirways", "")
text = text.replace("united", "")
text = text.replace("SouthwestAir", "")
text = text.replace("JetBlue", "")
text = text.replace("AmericanAir", "")
create_wordcloud(text, "Wordclouds/wcl_positive.png")
