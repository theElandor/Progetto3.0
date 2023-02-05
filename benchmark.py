SEPARATOR = "\n-----------------\n"


# Parte 1: costruzione dell'indice da un campione casuale preso dal corpora.
# Import necessari.
import Database as dd
import IndexGenerator as ig
from whoosh.fields import *
from whoosh.analysis import StemmingAnalyzer


# Dizionario di query per il benchmarking.
queries = {
    "r1"    : "reviews on customer service",
    "r2"    : "sauvignon wine",                     # !
    "r3"    : "technical problems with flight",
    "r4"    : "quality of personal",
    "r5"    : "rerouting or rescheduling",          # !
    "r6"    : "late arrival",                       # !
    "r7"    : "tickets and bookings",
    "r8"    : "luggage and bags",
    "r9"    : "departures and arrivals",
    "r10"   : "internet connection",
    }

# Costruzione della struttura dati Database.
db = dd.Database("sample.csv")
db.fillDb()
fields = ["handle", "text"]
fields.extend(list(queries.keys()))
db.filterFields(*fields)

# Costruzione dello schema dell'indice.
schema_fields = {
    "handle"  : TEXT(stored = True, analyzer = StemmingAnalyzer()),
    "text"    : TEXT(stored = True, analyzer = StemmingAnalyzer())
        }

# Per abilitare stopwords, inserire:
# stoplist = None, minsize = 0
# come parametri nel costruttore di StemmingAnalyzer.

for i in queries.keys():
    schema_fields[i] = eval("NUMERIC(stored = True, numtype = int)")

schema = Schema(**schema_fields)

# Costruzione dell'indice.
ix = ig.IndexGenerator(schema, db)
ix.fillIndex()


# Parte 2: sottomissione delle query all'indice precedentemente costruito,
# estrazione dei risultati e valutazione del sistema di IR tramite DCG.
# Import necessari.
from Results import Results
from Searcher import Searcher
import math
from functools import reduce


# Creazione del Searcher.
# Per variare funzione di scoring aggiungere scoring = "template" come
# parametro, al costruttore di Searcher.
s = Searcher("handle", "text", scoring_fun = "PL2")


def count_dcg(ordered, field):
    """Calcola la DCG del nostro sistema di IR."""
    li = [int(i[field]) for i in ordered]
    num_results = len(li)
    l = [li[idx] / math.log(idx + 2, 2) if idx != 0 else li[idx] for idx in range(num_results)]
    return reduce(lambda x, y : x + y, l)


# Struttura dati per la stampa finale.
dcg_data = []
ndcg_data = []
tweets_returned = []
counter = 1

# Sottomissione, una ad una, delle query pre-impostate.
for k, v in queries.items():
    res = s.submit_query(v)
    try:
        print(k)
        # Per variare funzione di ranking aggiungere ranking_fun = "template"
        # come parametro, al costruttore di Results.
        r = Results("Vader", "compound", res)
        # Calcolo del ranking ottimale per la NDCG.
        optimal_ranking = sorted(r.ordered, key = lambda d: d[k], reverse = True)
        dcg = count_dcg(r.ordered, k)
        optimal_dcg = count_dcg(optimal_ranking, k)
        ndcg = dcg / optimal_dcg
        dcg_data.append((queries[k], dcg))
        ndcg_data.append((queries[k], ndcg))
        print(
            "Query:", queries[k], "\n",
            "; valore DCG misurato:", dcg, "\n",
            "; valore DCG ottimale:", optimal_dcg, "\n",
            "; valore NDCG:", ndcg
            )
        tweets_returned.append(len(r.ordered))
    except:
        ndcg_data.append((queries[k], 0))
        print("Query:", queries[k],
              "; valore DCG misurato: 0",
              "; valore DCG ottimale: 0",
              "; valore NDCG: 0 \t NESSUN RISULTATO"
              )
    finally:
        print("----------DEBUG--------------")
        for element in optimal_ranking:
            print(element)
        print("----------DEBUG--------------")
        with open("./sample_results/query" + str(counter) + ".txt", "w") as f:
            for element in r.ordered:
                f.write(str(element) + "\n" + SEPARATOR)
        counter += 1
        print("\n")


# Parte 3: plotting dei risultati.
# Import necessari.
import matplotlib.pyplot as plt
import numpy as np


def custom_plot(data, parameter, file_name):
    """Stampa i grafici per DCG/NDCG."""
    # Asse x: query.
    qrs = ["q{}".format(i) for i in range(1, len(queries) + 1)]
    # Asse y: valore DCG/NDCG (all'indice 1 nella tupla).
    vls = [round(element[1],1) for element in data]
    # Creazione del plot.
    x = np.arange(len(qrs))
    width = 0.35
    fig, ax = plt.subplots()
    rec1 = ax.bar(x - width / 2, vls, width, label = parameter)
    rec2 = ax.bar(
        x + width / 2, tweets_returned, width, label = 'num. of retrieved tweets'
        )
    ax.set_ylabel('Val')
    ax.set_title(parameter + ' and number of retrieved tweets')
    ax.set_xticks(x,qrs)
    ax.legend()
    ax.bar_label(rec1, padding = 5)
    ax.bar_label(rec2, padding = 5)
    fig.tight_layout()
    plt.savefig(file_name)
    # plt.show()    # Abilita stampa grafico a run-time, su apposita finestra.


# Stampa dei grafici.
custom_plot(dcg_data, "DCG", "dcg.png")
custom_plot(ndcg_data, "NDCG", "ndcg.png")
