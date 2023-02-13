from Tools.SaTool import SaTool
from transformers import pipeline
# per ritornare entrambe le label positive e negative


pipe = pipeline(
    "sentiment-analysis",
    #model = "j-hartmann/emotion-english-distilroberta-base",
    top_k = None
    )

score = pipe("Hello, i fell great today")
print(score)