from .QTEData import QTEData


class QTEManager:
    def __init__(self, enemy_instance):
        self.qte_data: QTEData = QTEData(enemy_instance)

    def receive_hit(self, hit):
        self.qte_data.try_qte(hit)

    def reset_myself(self):
        self.qte_data.reset()
