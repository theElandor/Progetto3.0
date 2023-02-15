# TwOR
## (Twitter Opinion Retrieval)

TwOR is a framework written in python3 based on **whoosh**, specially made for **opinion retrieval**. It has been tested and used mainly for corpora made of tweets.
# Dependencies 
Theese dependencies are **mandatory**:
- whoosh
- tqdm
- pyexcel_ods3
- expertai-nlapi
- vaderSentiment
- transformers
# Optional dependencies
- tensorflow
- textblob
- matplotlib
- 
# Quick start
+ Clone the repo;
+ Install the dependencies;
+ Run `indexing_script.py` to create the Index;
+ Run `query_script.py` to launch queries;
    + Insert any query;
    + The default sentiment analysis tool is [**Vader**](https://github.com/cjhutto/vaderSentiment), which supports one of **positive**, **neutral** or **negative** as sentiment parameters.
+ Check `output.txt` or `output.ods` to see results;

# Indexing


```python
import Main.Database as dd
import Main.IndexGenerator as ig
from whoosh.fields import *
from whoosh.analysis import StemmingAnalyzer


db = dd.Database('./csv/airline.csv')
db.fillDb()
db.filterFields('handle','text')
schema = Schema(
    handle = TEXT(stored = True, analyzer = StemmingAnalyzer()),
    text = TEXT(stored = True, analyzer = StemmingAnalyzer())
    )
i = ig.IndexGenerator(schema, db)
i.fillIndex()
```
+ The `Database` objects is used to process raw data extracted from the csv file. The /csv contains 2 files downloaded from [Kaggle](https://www.kaggle.com/) used as an example.
+ The `filterFields` method is used to keep only the specified fields from the dataset. In      this case, we keep only the author and the text of the tweet.
+ The `IndexGenerator` object is used to create the Index. The `fillIndex` method fills the Index with documents. It might take some time according to the size of the documents.

# Queries
```python
from Main.Results import Results
from Main.Searcher import Searcher

query = input("Insert query > ")
sentiment = input("Insert sentiment >" )
s = Searcher("handle", "text")
res = s.submit_query(query)
r = Results("Vader", sentiment, res)
r.printResults(s, "output.txt")
r.printResults(s, "output.ods")
```
+ The `Searcher` object retrieves documents based on pertinence. Takes the fields that need to be scanned as arguments.
+ The `Results` object gives a global ranking to the retrieved documents based on **pertinence** and **sentiment** scores. Takes the sentiment analysis tool as an argument, in this case Vader is left by default. For now theese 4 tools are supported:
    + **Vader**: lexicon and rule-based tool that gives a score in a [-1,1] range, so that a "binary" classification can be applied (positve/negative or neutral).
    + [ExpertAI](https://pypi.org/project/expertai-nlapi/): API based on AI, supports different sentiment types.
    + [Roberta](https://huggingface.co/docs/transformers/model_doc/roberta); AI based, supports different sentiment types, check documentation for more information.
    + **Roberta2 (recommended)**: same as Roberta but uses a different pre-trained model that only gives a positive and negative score to the input text. Really usefull during benchmarking if you want to compare an AI-based approach (Roberta2) to a symbolic approach (Vader).
# Other
+ `benchmark.py` contains a script used for performance evaluation;
+ `./BenchGraphs` is the output folder for the graphs plotted during the benchmark;
+ `./frame` contains some nice frames for a cleaner output on .txt files;
+ `piechart.py` contains a simple script that generates a sentiment-based piechart based on the input query. The output is saved in the `./piechart` folder.
+ `./Main` contains the core of the software;
+ `./Printers` contains modules used to format output;
+ `./Tools` contains the modules corresponding to each sentiment analysis tool;
+ `./sample_results` contains one output file for each query that has been tested during the benchmark.
+ `./samples` contains a random sample of 100 tweet that has been manually annotated to calculate the **DCG** score during the benchmark.
+ `wn_s.pl` is the **Wordnet Thesaurus** that has been used for query expansion;
+ You can use the `wcl.py` script to visualize the most used words in certain types of tweets by creating a wordcloud. The default sentiment analysis tool used is Vader. The output will be stored in the `./Wordcloud` folder.



## License

MIT

**Free Software**
