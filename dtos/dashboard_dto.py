from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ComparativoFinDTO:
    mes: str
    valor_recebido: float
    valor_retornado: float

@dataclass
class StatusDTO:
    status: str
    qtd: int
    valor: float # <--- Novo Campo

@dataclass
class RetornoMensalDTO:
    mes: str
    valor: float

@dataclass
class DashboardDTO:
    comparativo_financeiro: List[ComparativoFinDTO]
    status_data: List[StatusDTO]
    historico_retornos: List[RetornoMensalDTO]
    gap_cronologico: Optional[float] = 0.0