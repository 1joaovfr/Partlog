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
        # 1. Regra de Negócio: Lançamento é AGORA (Data do Sistema)
        data_lancamento_sistema = datetime.now().date() 
        
        # O campo 'nota.recebimento' vem da View (o usuário escolheu no calendário)
        # O campo 'nota.emissao' vem da View (o usuário escolheu)
        
        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                sql_nf = """
                    INSERT INTO notas_fiscais 
                    (numero_nota, data_nota, cnpj_cliente, data_recebimento, data_lancamento)
                    VALUES (%s, %s, %s, %s, %s) RETURNING id
                """
                cursor.execute(sql_nf, (
                    nota.numero, 
                    nota.emissao, 
                    nota.cnpj_cliente,
                    nota.recebimento,        # <--- Data manual (chegada na fábrica)
                    data_lancamento_sistema  # <--- Data automática (hoje)
                ))
                id_nota = cursor.fetchone()[0]

                # 2. Preparação para o Código de Análise (Lógica do Sequencial)
                data_atual = datetime.now()
                letra_mes = chr(ord('A') + data_atual.month - 1) # A = Jan, B = Fev...

                # Busca o maior sequencial existente para este mês
                sql_seq = "SELECT MAX(codigo_analise) FROM itens_notas WHERE codigo_analise LIKE %s"
                cursor.execute(sql_seq, (f"{letra_mes}%",))
                resultado = cursor.fetchone()
                ultimo_codigo = resultado[0] if resultado else None
                
                if ultimo_codigo:
                    # Ex: A0005 -> pega '0005' -> int 5 -> soma 1 -> 6
                    sequencial_atual = int(ultimo_codigo[1:]) + 1
                else:
                    sequencial_atual = 1

                # 3. Inserir Itens (Com loop de explosão por quantidade)
                sql_item = """
                    INSERT INTO itens_notas 
                    (id_nota_fiscal, codigo_item, valor_item, ressarcimento, codigo_analise, status)
                    VALUES (%s, %s, %s, %s, %s, 'Pendente')
                """
                
                for item in itens:
                    # Loop para criar uma linha por unidade (Explosão)
                    for _ in range(item.quantidade):
                        # Formata: Letra + 4 dígitos (Ex: A0001)
                        cod_analise = f"{letra_mes}{sequencial_atual:04d}"

                        cursor.execute(sql_item, (
                            id_nota,
                            item.codigo,
                            item.valor,
                            item.ressarcimento,
                            cod_analise
                        ))
                        
                        sequencial_atual += 1

            conn.commit()