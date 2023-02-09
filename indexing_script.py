"""
Script dimostrativo che coinvolge le classi e le operazioni back-end, cioè
tutto quanto è inerente alla creazione, usando il pacchetto Whoosh, dell'indice,
a partire da un archivio di dati in formato .csv.
"""

import Database as dd
import IndexGenerator as ig
from whoosh.fields import *
from whoosh.analysis import StemmingAnalyzer


# Creazione di un oggetto Database.
db = dd.Database('./csv/airline.csv')
# Popolazione del Database.
db.fillDb()
# Selezione dei campi da indicizzare.
db.filterFields('handle','text')


# Creazione dello schema per l'indice Whoosh.
schema = Schema(
    handle = TEXT(stored = True, analyzer = StemmingAnalyzer()),
    text = TEXT(stored = True, analyzer = StemmingAnalyzer())
    )

# Creazione dell'indice.
i = ig.IndexGenerator(schema, db)
# Popolazione dell'indice.
i.fillIndex()
