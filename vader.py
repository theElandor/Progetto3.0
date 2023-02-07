import Database as dd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

db = dd.Database("./csv/sanders.csv")
db.fillDb()
fields = ["Sentiment", "TweetText"]
db.filterFields(*fields)

c = 0 
analyzer = SentimentIntensityAnalyzer()
for tweet in db._tweets:
    vs = analyzer.polarity_scores(tweet.TweetText)["compound"]
    if tweet.Sentiment == "irrelevant":
        continue
    if vs > 0.05 and tweet.Sentiment == "positive":
        c+=1
    elif vs < -0.05 and tweet.Sentiment == "negative":
        c+=1
    elif vs < 0.05 and vs > -0.05 and tweet.Sentiment == "neutral":
        c+=1
total = len([t for t in db._tweets if t.Sentiment != "irrelevant"])
print("Analyzed tweets: "+str(total))
print("Precision: " +str(c*100/total)+"%")
        
