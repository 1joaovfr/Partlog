from dataclasses import dataclass
from typing import List, Optional

# --- DTOs AUXILIARES ---

@dataclass
class ComparativoFinDTO:
    mes: str
    valor_recebido: float
    valor_retornado: float

@dataclass
class StatusDTO:
    status: str
    qtd: int

@dataclass
class RetornoMensalDTO:
    mes: str
    valor: float

# --- DTO PRINCIPAL ---
@dataclass
class DashboardDTO:
    comparativo_financeiro: List[ComparativoFinDTO]
    status_data: List[StatusDTO]
    # Substituímos a lista antiga por esta nova
    historico_retornos: List[RetornoMensalDTO]
    
    gap_cronologico: Optional[float] = 0.0