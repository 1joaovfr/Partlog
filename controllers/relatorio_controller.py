# controllers/relatorio_controller.py
from models import RelatorioModel

class RelatorioController:
    def __init__(self):
        # O Controller instancia o Model
        self.model = RelatorioModel()

    def buscar_dados(self):
        # Apenas repassa a solicitação para o Model
        return self.model.get_dados_relatorio()

    def exportar_excel(self, caminho, data_inicio, data_fim):
        # Apenas repassa os parametros para o Model fazer o trabalho duro
        return self.model.gerar_excel(caminho, data_inicio, data_fim)