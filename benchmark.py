separator = "\n-----------------\n"

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
db = dd.Database("sample_eros.csv")
db.fillDb()
fields = ["handle", "text"]
fields.extend(list(queries.keys()))
db.filterFields(*fields)

# Costruzione dello schema dell'indice.
schema_fields = {
    "handle"  : TEXT(stored = True, analyzer = StemmingAnalyzer()),
    "text"    : TEXT(stored = True, analyzer = StemmingAnalyzer())
        }

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
s = Searcher("handle", "text")


def count_dcg(ordered, field):
    """Calcola la DCG del nostro sistema di IR."""
    li = [int(i[field]) for i in ordered]
    num_results = len(li)
    l = [li[idx] / math.log(idx + 2,2) if idx != 0 else li[idx] for idx in range(num_results)]
    return reduce(lambda x, y : x + y, l)


# Struttura dati per la stampa finale.
final_data = []

counter = 1
tweets_returned = []
for k, v in queries.items():
    res = s.submit_query(v)
    try:
        print(k)
        r = Results("Vader", "compound", res)
        #r.ordered contiene i risultati ordinati per valore di pertinenza totale
        #si possono ordinare i tweet all'interno di r.ordered secondo il
        #parametro di "soddisfazione" assegnato a mano per quella particolare
        #query. In questo modo calcolando poi la DCG si ottiene il valore
        #ottimale, usato per la normalizzazione.
        print("Query:", queries[k], "; valore DCG:", count_dcg(r.ordered, k))
        
        optimal_ranking = sorted(r.ordered, key=lambda d: d[k], reverse = True)
        final_data.append((queries[k], count_dcg(r.ordered, k)/count_dcg(optimal_ranking, k)))
        print(count_dcg(r.ordered, k))
        print(count_dcg(optimal_ranking, k))
        tweets_returned.append(len(r.ordered))
    except:
        final_data.append((queries[k], 0))
        print("Query:", queries[k], "; valore DCG: 0")
    finally:
        print("----------DEBUG--------------")
        for element in optimal_ranking:
            print(element)
        print("----------DEBUG--------------")
        with open("./sample_results/query"+str(counter)+".txt", "w") as f:
            for element in r.ordered:                
                f.write(str(element)+"\n"+separator)        
        # name = "./sample_results/query"+str(counter)+".txt"
        # r.printResults(s, name)
        counter+=1
        print("\n")
    

# Parte 3: plotting dei risultati.
# Import necessari.
import matplotlib.pyplot as plt
import numpy as np

# Asse x: query.
qrs = ["q{}".format(i) for i in range(1, len(queries) + 1)]
# Asse y: valore DCG (all'indice 1 nella tupla).
vls = [element[1] for element in final_data]
# Creazione del plot.
x = np.arange(len(qrs))
width = 0.35
fig,ax = plt.subplots()
rec1 = ax.bar(x - width/2, vls, width, label='DCG')
rec2 = ax.bar(x + width/2, tweets_returned, width, label='num. of retrieved tweets')
ax.set_ylabel('Val')
ax.set_title('DCG and number of retrieved tweets')
ax.set_xticks(x,qrs)
ax.legend()
#plt.ylim(0, 14) uncomment to remove y limit

ax.bar_label(rec1, padding=5)
ax.bar_label(rec2, padding=5)

fig.tight_layout()
plt.savefig("bench.png")
plt.show()




# fig = plt.figure(figsize = (10, 5))
# plt.bar(qrs, vls, color ='blue', width = 0.4)

# # Creazione delle etichette di plot ed assi.
# plt.xlabel("Queries")
# plt.ylabel("DCG score")
# plt.title("Distance Cumulative Gain")
# plt.ylim(0, 1.50)
# # Salvataggio del plot su file.
# plt.savefig("bench.png")
