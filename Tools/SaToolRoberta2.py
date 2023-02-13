from Tools.SaTool import SaTool
from transformers import pipeline


class SaToolRoberta(SaTool):
    """
    Classe che implementa le funzionalità di sentiment analysis del tool
    Roberta. Eredita dalla classe astratta SaTool.
    """

    def __init__(self):
        """
        Costruttore per l'analizzatore di Roberta.
        """
        self.classifier = pipeline("text-classification", return_all_scores = True)



    def compute_sentiment(self, text, sentiment):
        """
        Implementazione di metodo astratto per il calcolo del sentiment
        relativo ad un campo testuale.
        :param text:        str, campo testuale da analizzare.
        :param sentiment:   str, tipo di sentiment da valutare.
        """
        score = self.classifier(text)
        # "Spacchetta" la struttura dati restituita da pipeline.
        if sentiment == "positive":
            return self._analyzer.polarity_scores(text)["pos"]
        elif sentiment == "negative":
            return self._analyzer.polarity_scores(text)["neg"]
        elif sentiment == "neutral":
            return self._analyzer.polarity_scores(text)["neu"]       

