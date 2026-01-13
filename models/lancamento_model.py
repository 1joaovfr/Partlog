from datetime import datetime
from database.connection import DatabaseConnection
from dtos.lancamento_dto import NotaFiscalDTO, ItemNotaDTO
from typing import List, Optional

class LancamentoModel:
    def __init__(self):
        self.db = DatabaseConnection()

    def buscar_cliente_nome(self, cnpj: str) -> Optional[str]:
        query = "SELECT cliente FROM clientes WHERE cnpj = %s"
        result = self.db.execute_query(query, (cnpj,), fetch=True)
        return result[0]['cliente'] if result else None

    def existe_produto(self, codigo: str) -> bool:
        query = "SELECT codigo_item FROM itens WHERE codigo_item = %s"
        result = self.db.execute_query(query, (codigo,), fetch=True)
        return True if result else False

    def salvar_entrada_completa(self, nota: NotaFiscalDTO, itens: List[ItemNotaDTO]):
        """
        Persiste a Nota Fiscal e seus itens.
        Realiza a 'explosão' dos itens (uma linha no banco para cada unidade física)
        e gera o Código de Análise sequencial (Ex: A0001, A0002).
        """
        data_lancamento_sistema = datetime.now().date()
        
        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                # 1. Inserir Cabeçalho
                sql_nf = """
                    INSERT INTO notas_fiscais
                    (numero_nota, data_nota, cnpj_cliente, data_recebimento, data_lancamento)
                    VALUES (%s, %s, %s, %s, %s) RETURNING id
                """
                cursor.execute(sql_nf, (
                    nota.numero,
                    nota.emissao,
                    nota.cnpj_cliente,
                    nota.recebimento,        
                    data_lancamento_sistema 
                ))
                id_nota = cursor.fetchone()[0]

                # 2. Gerar Sequencial de Análise (A = Jan, B = Fev...)
                data_atual = datetime.now()
                letra_mes = chr(ord('A') + data_atual.month - 1) 

                sql_seq = "SELECT MAX(codigo_analise) FROM itens_notas WHERE codigo_analise LIKE %s"
                cursor.execute(sql_seq, (f"{letra_mes}%",))
                resultado = cursor.fetchone()
                ultimo_codigo = resultado[0] if resultado else None
                
                sequencial_atual = int(ultimo_codigo[1:]) + 1 if ultimo_codigo else 1

                # 3. Inserir Itens (Explosão por quantidade)
                sql_item = """
                    INSERT INTO itens_notas
                    (id_nota_fiscal, codigo_item, valor_item, ressarcimento, codigo_analise, status)
                    VALUES (%s, %s, %s, %s, %s, 'Pendente')
                """
                
                for item in itens:
                    for _ in range(item.quantidade):
                        cod_analise = f"{letra_mes}{sequencial_atual:04d}"
                        cursor.execute(sql_item, (
                            id_nota, item.codigo, item.valor, item.ressarcimento, cod_analise
                        ))
                        sequencial_atual += 1
            
            conn.commit()