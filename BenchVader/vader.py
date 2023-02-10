import Database as dd
from tqdm import tqdm
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

db = dd.Database("./csv/airline.csv")
db.fillDb()
fields = ["airline_sentiment", "text"]
db.filterFields(*fields)

c = 0 
analyzer = SentimentIntensityAnalyzer()
for tweet in tqdm(db._tweets):
    vs = analyzer.polarity_scores(tweet.text)["compound"]
    if tweet.airline_sentiment == "irrelevant":
        continue
    if vs > 0.05 and tweet.airline_sentiment == "positive":
        c+=1
    elif vs < -0.05 and tweet.airline_sentiment == "negative":
        c+=1
    elif vs < 0.05 and vs > -0.05 and tweet.airline_sentiment == "neutral":
        c+=1
total = len([t for t in db._tweets if t.airline_sentiment != "irrelevant"])
print("Analyzed tweets: "+str(total))
print("Precision: " +str(c*100/total)+"%")
        
