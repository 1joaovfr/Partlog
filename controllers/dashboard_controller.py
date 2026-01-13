from models import DashboardModel
from dtos.dashboard_dto import (
    DashboardDTO, ComparativoFinDTO, StatusDTO, EntradaMensalDTO
)

class DashboardController:
    """
    Orquestrador de dados para o Dashboard gerencial.
    Agrega múltiplas fontes de dados do Model em um único DTO para a View.
    """
    def __init__(self):
        self.model = DashboardModel()

    def get_kpis(self) -> DashboardDTO:
        # Busca dados brutos
        val_gap = self.model.get_gap_atual_recebimento()
        raw_fin = self.model.get_comparativo_financeiro()
        raw_status = self.model.get_status_geral()
        raw_entrada = self.model.get_entrada_mensal()

        # Serialização para DTOs tipados
        list_fin = [
            ComparativoFinDTO(
                mes=d['mes'],
                valor_recebido=float(d['val_recebido']),
                valor_retornado=float(d['val_retornado'])
            ) for d in raw_fin
        ]

        list_status = [
            StatusDTO(status=d['status_final'], qtd=int(d['qtd']))
            for d in raw_status
        ]

        list_entrada = [
            EntradaMensalDTO(
                mes=d['mes'],
                qtd=int(d['qtd']),
                valor=float(d['valor'])
            ) for d in raw_entrada
        ]

        return DashboardDTO(
            comparativo_financeiro=list_fin,
            status_data=list_status,
            entrada_mensal=list_entrada,
            gap_cronologico=val_gap
        )