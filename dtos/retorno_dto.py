from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class ItemPendenteDTO:
    id: int
    numero_nota_origem: str
    data_nota_origem: date
    codigo_item: str
    descricao_item: str
    valor_original: float
    saldo_financeiro: float
    nome_cliente: str
    grupo_economico: str
    selecionado: bool = False
    valor_a_abater: float = 0.0

@dataclass
class RetornoHeaderDTO:
    numero_nota: str
    data_emissao: str
    tipo_retorno: str
    valor_total: float
    cnpj: Optional[str] = None
    grupo: Optional[str] = None
    observacao: str = ""