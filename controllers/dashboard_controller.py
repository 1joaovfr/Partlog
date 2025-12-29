from models import DashboardModel
from dtos.dashboard_dto import (
    DashboardDTO, ComparativoFinDTO, StatusDTO, 
    EntradaMensalDTO
)

class DashboardController:
    def __init__(self):
        self.model = DashboardModel()

    def get_kpis(self) -> DashboardDTO:
        # 1. Busca dados do Model
        # Busca o Gap Cronológico (Hoje - Última Nota Recebida)
        val_gap = self.model.get_gap_atual_recebimento()
        
        raw_fin = self.model.get_comparativo_financeiro()
        raw_status = self.model.get_status_geral()
        raw_entrada = self.model.get_entrada_mensal()

        # 2. Converte para DTOs (Listas)
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

        # 3. Retorna o DTO com o novo campo 'gap_cronologico' preenchido
        return DashboardDTO(
            comparativo_financeiro=list_fin,
            status_data=list_status,
            entrada_mensal=list_entrada,
            gap_cronologico=val_gap 
        )