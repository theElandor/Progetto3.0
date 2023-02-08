"""
Script dimostrativo per le classi front-end: Searcher e Results.
Crea un oggetto Searcher, gli sottopone una query e stampa i risultati,
ordinati secondo una formula che mischia i punteggi di pertinenza e
sentiment. Viene infine fatta una stampa su file di testo.
La procedura è ripetuta per una seconda query, differente dalla prima.
"""

from Results import Results
from Searcher import Searcher

q=input("inserire query: ")


s = Searcher("handle", "text")

res = s.submit_query(q)
r = Results("Vader", "compound", res)
r.printResults(s, "modTest/output_test.txt") 


s = Searcher("handle", "text", scoring_fun="TF_IDF")

res = s.submit_query(q)
r = Results("Vader", "compound", res)
r.printResults(s, "modTest/output_test1.txt")