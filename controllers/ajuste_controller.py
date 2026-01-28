from models.ajuste_model import AjusteModel

class AjusteController:
    def __init__(self):
        self.model = AjusteModel()

    def buscar_dados(self):
        return self.model.get_dados_ajuste()

    def salvar_edicao(self, dto_original, form_data):
        """
        Recebe o DTO original e um dicionário com os dados editados do formulário.
        """
        # Validações básicas de negócio antes de ir pro banco
        if not form_data['nf_entrada']:
            raise Exception("Número da Nota é obrigatório.")
        
        if not form_data['codigo_analise']:
            raise Exception("Código de Análise é obrigatório.")

        # Chama o model
        return self.model.atualizar_item(dto_original, form_data)

    def excluir_registro(self, id_item):
        return self.model.excluir_item(id_item)