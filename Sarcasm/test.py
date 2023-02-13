from Tools.SaTool import SaTool
from transformers import pipeline
from Tools.SaTool import SaTool
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

#Roberta
text = ""
classifier = pipeline("sentiment-analysis",top_k = None)
score = classifier(text)


#Vader
analyzer = SentimentIntensityAnalyzer()
print(analyzer.polarity_scores(text))