from datetime import datetime
from models import AnaliseModel
from dtos.analise_dto import ItemPendenteDTO, ResultadoAnaliseDTO

class AnaliseController:
    def __init__(self):
        self.model = AnaliseModel()

    def listar_pendentes(self) -> list[ItemPendenteDTO]:
        # 1. Busca dados crus (dicts) do Model
        dados_brutos = self.model.get_itens_pendentes()
        
        # 2. Converte para lista de DTOs
        lista_dto = []
        for row in dados_brutos:
            dto = ItemPendenteDTO(
                id=row['id'],
                numero_nota=row['numero_nota'],
                codigo_item=row['codigo_item'],
                descricao=row['descricao'],
                data_fmt=row['data_fmt'],
                codigo_analise=row['codigo_analise'],
                ressarcimento=row['ressarcimento']
            )
            lista_dto.append(dto)
            
        return lista_dto

    def salvar_analise(self, id_item, dados_dict):
        # 1. Cria o DTO de salvamento
        dto = ResultadoAnaliseDTO(
            id_item=id_item,
            serie=dados_dict['serie'],
            origem=dados_dict['origem'],
            fornecedor=dados_dict['fornecedor'],
            cod_avaria=dados_dict['cod_avaria'],
            desc_avaria=dados_dict['desc_avaria'],
            status_resultado=dados_dict['status_resultado'],
            data_analise=datetime.now().date() # Data gerada aqui ou no Model
        )
        
        # 2. Manda o Model persistir
        self.model.atualizar_analise(dto)