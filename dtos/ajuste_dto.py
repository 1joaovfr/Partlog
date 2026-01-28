from dataclasses import dataclass
from typing import Optional
from .relatorio_dto import RelatorioItemDTO

@dataclass
class AjusteItemDTO(RelatorioItemDTO):
    # Herdamos tudo do RelatorioItemDTO e adicionamos os IDs internos
    id_item: int = 0
    id_nota: int = 0
    
    @classmethod
    def from_dict(cls, data: dict):
        # Cria a instância usando a lógica do pai
        instance = super().from_dict(data)
        # Adiciona os IDs
        instance.id_item = data.get('id_item') or 0
        instance.id_nota = data.get('id_nota') or 0
        return instance