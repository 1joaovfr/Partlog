from database.connection import DatabaseConnection
from dtos.analise_dto import ResultadoAnaliseDTO
from typing import List

class AnaliseModel:
    def __init__(self):
        self.db = DatabaseConnection()

    def get_itens_pendentes(self) -> List[dict]:
        """
        Retorna dicionários puros do banco. 
        """
        sql = """
            SELECT i.id, 
                   nf.numero_nota, 
                   i.codigo_item, 
                   p.descricao_item as descricao, 
                   to_char(nf.data_lancamento, 'DD/MM/YYYY') as data_fmt, 
                   i.codigo_analise,
                   i.ressarcimento
            FROM itens_notas i
            JOIN notas_fiscais nf ON i.id_nota_fiscal = nf.id
            LEFT JOIN itens p ON i.codigo_item = p.codigo_item
            WHERE i.status = 'Pendente'
            ORDER BY nf.data_lancamento ASC
        """
        return self.db.execute_query(sql, fetch=True)

    def atualizar_analise(self, dados: ResultadoAnaliseDTO):
        """
        Atualiza o item com o resultado da análise técnica.
        """
        # AQUI ESTAVA O PROBLEMA: Este método precisa existir para o Controller chamar.
        sql = """
            UPDATE itens_notas
            SET numero_serie = %s, 
                produzido_revenda = %s, 
                fornecedor = %s,
                codigo_avaria = %s, 
                descricao_avaria = %s, 
                status = %s,               -- Define se é Procedente ou Improcedente
                procedente_improcedente = %s, 
                data_analise = %s 
            WHERE id = %s
        """
        
        params = (
            dados.serie,
            dados.origem,
            dados.fornecedor,
            dados.cod_avaria,
            dados.desc_avaria,
            dados.status_resultado,  # Atualiza o status geral
            dados.status_resultado,  # Atualiza o campo específico
            dados.data_analise,
            dados.id_item
        )
        self.db.execute_query(sql, params)