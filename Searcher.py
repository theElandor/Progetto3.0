import os, os.path
from functools import partial
from whoosh.index import open_dir
from whoosh import qparser as qp
from whoosh.fields import *
from Misc import *
from whoosh.lang.wordnet import Thesaurus
from whoosh import scoring


class Searcher:
    """
    Classe che predispone tutto il necessario per la ricerca su un indice
    Whoosh. Fornisce metodi per sottoporre query e per la stampa di
    suggerimenti.
    """

    def __init__(self, *fields, idx_dir = "./Index", thes_dir = "./wn_s.pl",
        scoring_fun = "BM25F"):
        """
        Costruttore di classe.
        :param *fields:     str, specificati dall'utente, campi di ricerca.
        :param idx_dir:     str, "./Index" di default, directory dell'indice.
        :param thes_dir:    str, "./wn_s.pl" di default, directory del thesaurus.
        :param scoring_fun: str, "BM25F" di default, nome del sistema di scoring
                            da applicare.
        """
        self.__open_index(idx_dir)      # Apertura dell'indice.
        self.__open_thesaurus(thes_dir) # Apertura del thesaurus.
        self.__make_parser(*fields)     # Creazione del QueryParser.
        self.__make_searcher(scoring_fun)   # Creazione dell'index searcher.


    # I campi di ricerca possono essere letti e cambiati tramite i metodi
    # getter/setter.
    @property
    def src_fields(self):
        return self._src_fields

    @src_fields.setter
    def src_fields(self, *value):
        # In questo caso, deve essere re-istanziato il QueryParser.
        self.__make_parser(*value)

    # La query inserita può essere mostrata con un metodo getter.
    @property
    def raw_query(self):
        return self._raw_query


    def __open_index(self, idx_dir):
        """
        Apre un indice Whoosh, assegnando l'oggetto ad un attributo di istanza.
        :param idx_dir:   str, directory dell'indice.
        """
        # Tenta l'apertura, lanciando OSError in caso di directory non
        # esistente.
        try:
            ix = open_dir(idx_dir)
        except:
            raise OSError(
                "Directory 'Index' non trovata. Specificarne una valida."
                )

        # Imposta l'indice aperto come attributo d'istanza.
        self._ix = ix


    def __open_thesaurus(self, thes_dir):
        """
        Apre un thesaurus WordNet da file. Ne assegna il contenuto ad un ogget-
        to Thesaurus di Whoosh, che è attributo di istanza.
        :param thes_dir:    str, directory e nome del thesaurus file.
        """
        # L'apertura è interamente gestita da open.
        with open(thes_dir) as f:
            self._thesaurus = Thesaurus.from_file(f)


    @staticmethod
    def __check_fields(selected_fields, available_fields):
        """
        Metodo statico. Controlla la validità dei campi selezionati.
        :param selected_fields:     list, lista di campi selezionati.
        :param available_fields:    list, lista di campi disponibili.
        """
        # Se un campo non è disponibile, lancia ValueError.
        for i in selected_fields:
            if i not in available_fields:
                raise ValueError(
                    "Campo selezionato per la ricerca su indice inesistente."
                    )


    def __make_parser(self, *fields, grouping_factor = 0.8):
        """
        Crea un oggetto Whoosh QueryParser e lo assegna come attributo di
        istanza.
        :param *fields:             str, argomenti variabili, campi selezionati.
        :param grouping_factor:     float, default 0.8, coefficiente che premia
                                    i duplicati a discapito delle parole
                                    consecutive.
        """
        # Abilita la ricerca in OR logico.
        orgroup = qp.OrGroup.factory(grouping_factor)

        # Carica i campi disponibili dall'indice.
        available_fields = self._ix.schema.stored_names()
        # Verifica i campi selezionati.
        Searcher.__check_fields(fields, available_fields)

        # Imposta i campi selezionati come attributo di istanza.
        self._src_fields = fields
        # Costruisce il Whoosh QueryParser e lo imposta come attributo di
        # istanza.
        self._parser = qp.MultifieldParser(
            self._src_fields,
            schema = self._ix.schema,
            group = orgroup
            )


    def __make_searcher(self, scoring_fun):
        """
        Crea un oggetto Whoosh searcher dall'indice e lo assegna come
        attributo di istanza.
        :param scoring_fun  str, nome del sistema di scoring da adottare.
        """
        scoring_system = eval("scoring.{}()".format(scoring_fun))
        self._searcher = self._ix.searcher(weighting = scoring_system)


    def submit_query(self, raw_query, results_threshold = 20, expand = True):
        """
        Sottopone una query all'indice Whoosh.
        :param raw_query:   str, una query a discrezione dell'utente.
        """
        # Imposta la query come attributo di istanza.
        self._raw_query = raw_query
        # Se opportuno, espande la query con sinonimi. Dopodiché esegue parsing.
        if expand:
            words = [i for i in raw_query.split()]
            synonyms = [
                j for i in words for j in self._thesaurus.synonyms(i)
                ]
            words.extend(synonyms)
            expanded_query = " ".join(words)
            query = self._parser.parse(expanded_query)
        else:
            query = self._parser.parse(self._raw_query)
        # Decoratore che stampa il tempo di esecuzione.
        clock = time_function(self._searcher.search)
        # Definisce il numero massimo di risultati considerati.
        # Sottopone la query.
        results = clock(query, limit = results_threshold)
        # Se vi sono risultati, li restituisce, altrimenti stampa suggerimenti.
        if results:
            return results
        else:
            print("Nessun risultato per la query.")
            self.__make_suggestions()


    def __make_suggestions(self):
        """
        Chiamata quando una query non restituisce risultati. Stampa suggerimenti
        attingendo al vocabolario dell'indice.
        """
        # Numero max di suggerimenti per ciascun termine non trovato.
        suggestions_limit = 10
        # Correzione max in valore edit distance da applicare ai termini non
        # trovati.
        max_edit_distance = 2

        # Rimuove i doppi apici agli estremi della query, nel caso di ricerche
        # in prossimità.
        if self._raw_query[0] == '"' and self._raw_query[-1] == '"':
            raw_query = self._raw_query[1:-1]
        else:
            raw_query = self._raw_query

        # Cerca i termini che non hanno fatto matching, e propone delle correzioni.
        for word in raw_query.split():
            # Se questi non sono tra gli operatori booleani di Whoosh.
            if word not in ("OR", "AND", "NOT"):
                not_found = True
                # La ricerca avviene per tutti i campi di ricerca selezionati.
                for field in self._src_fields:
                    try:
                        self._searcher.postings(field, word)
                        not_found = False
                    except:
                        not_found = True and not_found

                if not_found:
                    print(
                        "Il termine\"",
                        word,
                        "\"non è presente tra i vocaboli del corpus."
                        )
                    # Crea i suggerimenti.
                    suggestions = self._searcher.suggest(
                        field,
                        word,
                        limit = suggestions_limit,
                        maxdist = max_edit_distance
                    )
                    # Propone i suggerimenti.
                    if suggestions:
                        print("Quello che volevi scrivere è forse nell'elenco?")
                        print(", ".join(suggestions))
                    else:
                        print("Non sono disponibili correzioni per", word)
