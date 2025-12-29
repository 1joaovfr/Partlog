from dataclasses import dataclass
from typing import List, Optional

# --- DTOs AUXILIARES ---

@dataclass
class ComparativoFinDTO:
    mes: str
    valor_recebido: float  # Total entrada (R$)
    valor_retornado: float # Total pago em garantia (R$)

@dataclass
class EvolucaoLeadTimeDTO:
    mes: str
    media_dias: float

@dataclass
class StatusDTO:
    status: str
    qtd: int

@dataclass
class EntradaMensalDTO:
    mes: str
    qtd: int
    valor: float

# --- DTO PRINCIPAL ---
@dataclass
class DashboardDTO:
    comparativo_financeiro: List
    status_data: List
    entrada_mensal: List
    
    # Campo que guarda o Gap (Hoje - Data Recebimento da última nota)
    gap_cronologico: Optional[float] = 0.0