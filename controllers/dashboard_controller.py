from models import DashboardModel
from dtos.dashboard_dto import (
    DashboardDTO, ComparativoFinDTO, StatusDTO, RetornoMensalDTO
)

class DashboardController:
    """
    Orquestrador de dados para o Dashboard gerencial.
    """
    def __init__(self):
        self.model = DashboardModel()

    def get_kpis(self) -> DashboardDTO:
        # Busca dados brutos para os gráficos principais
        val_gap = self.model.get_gap_atual_recebimento()
        raw_fin = self.model.get_comparativo_financeiro()
        raw_status = self.model.get_status_geral()
        raw_retornos = self.model.get_historico_retornos_mes()

        # Serialização para DTOs
        list_fin = [
            ComparativoFinDTO(
                mes=d['mes'],
                valor_recebido=float(d['val_recebido']),
                valor_retornado=float(d['val_retornado'])
            ) for d in raw_fin
        ]

        # --- CORREÇÃO AQUI ---
        # Adicionamos o campo 'valor' pegando de 'valor_total' da query
        list_status = [
            StatusDTO(
                status=d['status_final'], 
                qtd=int(d['qtd']),
                valor=float(d['valor_total']) 
            )
            for d in raw_status
        ]

        list_retornos = [
            RetornoMensalDTO(
                mes=d['mes'],
                valor=float(d['valor_total'])
            ) for d in raw_retornos
        ]

        return DashboardDTO(
            comparativo_financeiro=list_fin,
            status_data=list_status,
            historico_retornos=list_retornos,
            gap_cronologico=val_gap
        )