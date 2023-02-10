import Database as dd
from transformers import pipeline
from tqdm import tqdm

db = dd.Database("./csv/sanders.csv")
db.fillDb()
fields = ["Sentiment", "TweetText"]
db.filterFields(*fields)

p = pipeline("sentiment-analysis") #scarica in automatico un modello per fare SA
c = 0
for tweet in tqdm(db._tweets):
    score = p(tweet.TweetText)
    sent = tweet.Sentiment
    if sent == "neutral" or sent == "irrelevant":
        continue
    elif sent == "positive" and score[0]['label'] == "POSITIVE":
        c+=1
    elif sent == "negative" and score[0]['label'] == "NEGATIVE":
        c+=1
total_len = len([t for t in db._tweets if t.Sentiment != "neutral" and t.Sentiment != "irrelevant"])
print("Analyzed tweets: "+str(total_len))
print("Precision: " +str(c*100/total_len)+"%")
