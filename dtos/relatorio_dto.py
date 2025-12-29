from dataclasses import dataclass
from typing import Optional

@dataclass
class RelatorioItemDTO:
    status: str
    codigo_analise: str
    data_lancamento: str
    data_recebimento: str
    data_analise: str
    cnpj: str
    nome_cliente: str
    grupo_cliente: str      # <--- NOVO CAMPO
    cidade: str
    estado: str
    regiao: str
    data_emissao: str       # <--- NOVO CAMPO
    nf_entrada: str
    codigo_item: str
    grupo_item: str         # <--- NOVO CAMPO
    numero_serie: str
    codigo_avaria: str
    descricao_avaria: str
    valor_item: float
    ressarcimento: float
    nf_retorno: Optional[str] = None
    tipo_retorno: Optional[str] = None
    data_retorno: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict):
        """
        Converte um dicionário (vindo do banco) para uma instância da classe.
        Usa .get() para evitar erros caso o campo venha nulo do SQL.
        """
        return cls(
            status=data.get('status') or '',
            codigo_analise=data.get('codigo_analise') or '',
            data_lancamento=data.get('data_lancamento') or '',
            data_recebimento=data.get('data_recebimento') or '',
            data_analise=data.get('data_analise') or '',
            
            cnpj=data.get('cnpj') or '',
            nome_cliente=data.get('nome_cliente') or '',
            grupo_cliente=data.get('grupo_cliente') or '', # <--- Mapeando
            cidade=data.get('cidade') or '',
            estado=data.get('estado') or '',
            regiao=data.get('regiao') or '',
            
            data_emissao=data.get('data_emissao') or '',   # <--- Mapeando
            nf_entrada=data.get('nf_entrada') or '',
            
            codigo_item=data.get('codigo_item') or '',
            grupo_item=data.get('grupo_item') or '',       # <--- Mapeando
            numero_serie=data.get('numero_serie') or '',
            
            codigo_avaria=data.get('codigo_avaria') or '',
            descricao_avaria=data.get('descricao_avaria') or '',
            
            # Tratamento para garantir que venha float, mesmo se for None no banco
            valor_item=float(data.get('valor_item') or 0.0),
            ressarcimento=float(data.get('ressarcimento') or 0.0),
            
            nf_retorno=data.get('nf_retorno'),
            tipo_retorno=data.get('tipo_retorno'),
            data_retorno=data.get('data_retorno')
        )