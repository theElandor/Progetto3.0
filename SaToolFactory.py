from SaToolExpertAI import SaToolExpertAI
from SaToolVader import SaToolVader
from SaToolRoberta import SaToolRoberta


class SaToolFactory:
    """
    Classe factory per la creazione di oggetti tool per sentiment analysis.
    """

    # Dizionario dei sentiment disponibili per ciascun tool di sentiment analysis.
    _tool_sentiments = {
        "ExpertAI"  : ("positive", "negative", "overall"),
        "Vader"     : ("positive", "negative", "neutral", "compound"),
        "Roberta"   : ("surprise", "neutral", "sadness", "joy", "anger", "fear", "disgust")
        }


    @staticmethod
    def check_sentiment(tool_name, sentiment):
        """
        Controlla la regolarità del sentiment inserito, in relazione al tool di
        sentiment analysis che si sta usando.
        """
        if sentiment not in SaToolFactory._tool_sentiments[tool_name]:
            raise ValueError(
                "Questo sentiment non può essere valutato dal tool impostato."
                )
        else:
            return sentiment


    # Metodi di classe per la produzione di oggetti derivati dalla classe
    # astratta SaTool Utilizzano tutti parametri di default.
    @staticmethod
    def make_ExpertAI():
        return SaToolExpertAI()

    @staticmethod
    def make_Vader():
        return SaToolVader()

    @staticmethod
    def make_Roberta():
        return SaToolRoberta()
