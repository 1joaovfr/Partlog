from models import RelatorioModel

class RelatorioController:
    def __init__(self):
        self.model = RelatorioModel()

    def buscar_dados(self):
        return self.model.get_dados_relatorio()

    # AGORA RECEBE A LISTA DIRETO DA VIEW
    def exportar_excel(self, caminho, dados_lista, colunas_lista):
        return self.model.gerar_excel_da_lista(caminho, dados_lista, colunas_lista)