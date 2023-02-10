"""
Script dimostrativo per le classi front-end: Searcher e Results.
Crea un oggetto Searcher, gli sottopone una query e stampa i risultati,
ordinati secondo una formula che mischia i punteggi di pertinenza e
sentiment. Viene infine fatta una stampa su file di testo.
La procedura è ripetuta per una seconda query, differente dalla prima.
"""

from Main.Results import Results
from Main.Searcher import Searcher


s = Searcher("handle", "text")
res = s.submit_query("bad weather")
r = Results("Vader", "compound", res)
r.printResults(s, "output.txt")