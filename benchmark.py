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
    l = [li[idx] / math.log(idx + 1) if idx != 0 else li[idx] for idx in range(num_results)]
    return reduce(lambda x, y : x + y, l)


# Struttura dati per la stampa finale.
final_data = []

counter = 1
for k, v in queries.items():
    res = s.submit_query(v)
    try:
        r = Results("Vader", "compound", res)
        print("Query:", queries[k], "; valore DCG:", count_dcg(r.ordered, k))
        final_data.append((queries[k], count_dcg(r.ordered, k)))
    except:
        final_data.append((queries[k], 0))
        print("Query:", queries[k], "; valore DCG: 0")
    finally:
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

# Asse x: query.
qrs = ["q{}".format(i) for i in range(1, len(queries) + 1)]
# Asse y: valore DCG (all'indice 1 nella tupla).
vls = [element[1] for element in final_data]
# Creazione del plot.
fig = plt.figure(figsize = (10, 5))
plt.bar(qrs, vls, color ='blue', width = 0.4)

# Creazione delle etichette di plot ed assi.
plt.xlabel("Queries")
plt.ylabel("DCG score")
plt.title("Distance Cumulative Gain")
# Salvataggio del plot su file.
plt.savefig("bench.png")
