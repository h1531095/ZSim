from .QTEData import QTEData


class QTEManager:
    def __init__(self, enemy_instance):
        self.qte_data = QTEData(enemy_instance)

    def receive_hit(self, hit):
        self.qte_data.try_qte(hit)
