from models import DashboardModel
from dtos.dashboard_dto import (
    DashboardDTO, ComparativoFinDTO, StatusDTO, RetornoMensalDTO
)

class DashboardController:
    def __init__(self):
        self.model = DashboardModel()

    def get_kpis(self) -> DashboardDTO:
        val_gap = self.model.get_gap_atual_recebimento()
        raw_fin = self.model.get_comparativo_financeiro()
        raw_status = self.model.get_status_geral()
        
        # Busca o novo dado
        raw_retornos = self.model.get_historico_retornos_mes()

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
        
        # Mapeia o novo gráfico
        list_retornos = [
            RetornoMensalDTO(
                mes=d['mes'],
                valor=float(d['valor_total'])
            ) for d in raw_retornos
        ]

        return DashboardDTO(
            comparativo_financeiro=list_fin,
            status_data=list_status,
            historico_retornos=list_retornos, # Novo campo
            gap_cronologico=val_gap
        )