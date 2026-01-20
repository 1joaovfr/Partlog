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
    cnpj_emitente: str            # <--- NOVO: Sua empresa
    cnpj_remetente: Optional[str] = None # <--- O Cliente
    grupo: Optional[str] = None   # <--- Opcional se for busca por grupo
    observacao: str = ""