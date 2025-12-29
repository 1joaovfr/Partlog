from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class ItemPendenteDTO:
    """Dados para preencher a Tabela de Pendências"""
    id: int
    numero_nota: str
    codigo_item: str
    descricao: str
    data_fmt: str  # Já vem formatada do banco (DD/MM/YYYY)
    codigo_analise: str
    ressarcimento: Optional[float] = 0.0

@dataclass
class ResultadoAnaliseDTO:
    """Dados para Salvar a Análise"""
    id_item: int
    serie: str
    origem: str
    fornecedor: str
    cod_avaria: str
    desc_avaria: str
    status_resultado: str # Procedente/Improcedente
    data_analise: date