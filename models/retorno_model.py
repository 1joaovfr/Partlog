from database import DatabaseConnection
from dtos.retorno_dto import ItemPendenteDTO, RetornoHeaderDTO

class RetornoModel:
    def __init__(self):
        self.db = DatabaseConnection()

    def buscar_itens_pendentes(self, filtro_valor, tipo_filtro, lista_notas=None) -> list[ItemPendenteDTO]:
            query = """
                SELECT 
                    i.id, nf.numero_nota, nf.data_nota, 
                    i.codigo_item, i.valor_item, i.saldo_financeiro,
                    COALESCE(c.cliente, 'Cliente Sem Cadastro') as nome_cliente, 
                    COALESCE(c.grupo, '-') as grupo,
                    i.codigo_analise  
                FROM itens_notas i
                JOIN notas_fiscais nf ON i.id_nota_fiscal = nf.id
                -- LEFT JOIN: Garante que a nota venha mesmo se o cliente não existir na tabela 'clientes'
                LEFT JOIN clientes c ON c.cnpj IN (nf.cnpj_cliente, nf.cnpj_remetente)
                WHERE COALESCE(i.saldo_financeiro, 0) > 0 
                AND i.status IN ('Pendente', 'Procedente', 'Improcedente')
            """
            params = []

            if tipo_filtro == 'CNPJ':
                # Busca blindada contra colunas nulas (procura no cliente e no remetente)
                query += """ AND (
                    REGEXP_REPLACE(COALESCE(nf.cnpj_remetente, ''), '[^0-9]', '', 'g') = %s 
                    OR REGEXP_REPLACE(COALESCE(nf.cnpj_cliente, ''), '[^0-9]', '', 'g') = %s
                )"""
                params.extend([filtro_valor, filtro_valor])
                
                if lista_notas and len(lista_notas) > 0:
                    # Remove os zeros (ex: '001' e '1' viram a mesma coisa)
                    notas_limpas = [n.lstrip('0') for n in lista_notas]
                    placeholders = ', '.join(['%s'] * len(notas_limpas))
                    
                    query += f" AND LTRIM(COALESCE(nf.numero_nota, ''), '0') IN ({placeholders})"
                    params.extend(notas_limpas)
            
            elif tipo_filtro == 'GRUPO':
                query += " AND c.grupo ILIKE %s"
                params.append(f"%{filtro_valor}%")

            query += " ORDER BY nf.data_nota ASC"

            try:
                resultados = self.db.execute_query(query, params, fetch=True)
                
                lista_dto = []
                for r in resultados:
                    cod_analise_db = r['codigo_analise'] if r['codigo_analise'] else ""
                    
                    lista_dto.append(ItemPendenteDTO(
                        id=r['id'],
                        numero_nota_origem=r['numero_nota'],
                        data_nota_origem=r['data_nota'],
                        codigo_item=r['codigo_item'],
                        descricao_item="", 
                        valor_original=float(r['valor_item']),
                        saldo_financeiro=float(r['saldo_financeiro']),
                        nome_cliente=r['nome_cliente'],
                        grupo_economico=r['grupo'],
                        codigo_analise=cod_analise_db 
                    ))
                return lista_dto
            except Exception as e:
                # Imprime o erro no console para facilitar a investigação
                print(f"Erro ao buscar pendências SQL: {e}")
                return []
        
    def salvar_retorno(self, header: RetornoHeaderDTO, itens: list[ItemPendenteDTO]):
        conn_manager = self.db.get_connection()
        with conn_manager as conn:
            try:
                cursor = conn.cursor()
                
                sql_head = """
                    INSERT INTO notas_retorno 
                    (numero_nota, data_emissao, tipo_retorno, cnpj_emitente, cnpj_remetente, grupo_economico, valor_total_nota)
                    VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id
                """
                
                cursor.execute(sql_head, (
                    header.numero_nota, 
                    header.data_emissao, 
                    header.tipo_retorno,
                    header.cnpj_emitente,
                    header.cnpj_remetente,
                    header.grupo, 
                    header.valor_total
                ))
                id_retorno = cursor.fetchone()[0]

                for item in itens:
                    # Atualiza o saldo
                    sql_upd = "UPDATE itens_notas SET saldo_financeiro = saldo_financeiro - %s WHERE id = %s"
                    cursor.execute(sql_upd, (item.valor_a_abater, item.id))

                    # CORRIGIDO: Removido 'codigo_analise' pois não existe na tabela 'conciliacao'
                    sql_con = """
                        INSERT INTO conciliacao (id_nota_retorno, id_item_entrada, valor_abatido) 
                        VALUES (%s, %s, %s)
                    """
                    cursor.execute(sql_con, (id_retorno, item.id, item.valor_a_abater))
                
                conn.commit()
                return True, "Nota de Retorno gravada com sucesso!"
            except Exception as e:
                conn.rollback()
                return False, f"Erro ao gravar no banco: {str(e)}"