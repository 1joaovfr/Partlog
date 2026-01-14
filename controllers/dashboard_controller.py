from models import DashboardModel
from dtos.dashboard_dto import (
    DashboardDTO, ComparativoFinDTO, StatusDTO, EntradaMensalDTO
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
        
        # O método get_entrada_mensal foi removido pois substituímos pelo Card de Backlog

        # Serialização para DTOs
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

        # Retornamos DTO com lista vazia para entrada_mensal (não será usada na View)
        return DashboardDTO(
            comparativo_financeiro=list_fin,
            status_data=list_status,
            entrada_mensal=[], 
            gap_cronologico=val_gap
        )

    # --- MÉTODOS PARA O FILTRO DE BACKLOG ---
    
    def get_lista_meses_backlog(self):
        """Retorna lista de meses (ex: '01/2026') que têm pendências."""
        raw = self.model.get_meses_com_pendencia_analise()
        return [r['mes_formatado'] for r in raw]

    def get_dados_backlog(self, mes_ano):
        """Retorna dados filtrados para o card de backlog."""
        return self.model.get_kpi_backlog_analise(mes_ano)