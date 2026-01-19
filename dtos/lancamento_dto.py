from dataclasses import dataclass
from datetime import date

@dataclass
class NotaFiscalDTO:
    numero: str
    emissao: date
    recebimento: date
    cnpj_cliente: str
    cnpj_remetente: str # Novo campo obrigatório
    
@dataclass
class ItemNotaDTO:
    codigo: str
    quantidade: int
    valor: float
    ressarcimento: float