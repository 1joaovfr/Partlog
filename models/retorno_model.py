from database import DatabaseConnection
# Ajuste o import conforme o nome exato da sua pasta de DTOs
from dtos.retorno_dto import ItemPendenteDTO, RetornoHeaderDTO

class RetornoModel:
    def __init__(self):
        self.db = DatabaseConnection()

    def buscar_itens_pendentes(self, filtro_valor, tipo_filtro, nf_filtro=None) -> list[ItemPendenteDTO]:
        # Usamos COALESCE para garantir que nulos sejam tratados como 0
        query = """
            SELECT 
                i.id, nf.numero_nota, nf.data_nota, 
                i.codigo_item, i.valor_item, i.saldo_financeiro,
                c.cliente as nome_cliente, c.grupo
            FROM itens_notas i
            JOIN notas_fiscais nf ON i.id_nota_fiscal = nf.id
            JOIN clientes c ON nf.cnpj_cliente = c.cnpj
            WHERE COALESCE(i.saldo_financeiro, 0) > 0 
              AND i.status IN ('Procedente', 'Improcedente')
        """
        params = []

        if tipo_filtro == 'CNPJ':
            # Remove caracteres especiais do CNPJ para garantir busca limpa, se necessário
            # Aqui mantive o like para flexibilidade ou = se for estrito
            query += " AND nf.cnpj_cliente = %s"
            params.append(filtro_valor)
            
            if nf_filtro:
                query += " AND nf.numero_nota = %s"
                params.append(nf_filtro)
        
        elif tipo_filtro == 'GRUPO':
            # ILIKE faz a busca ignorando Maiúsculas/Minúsculas (Case Insensitive)
            # O % ao redor permite buscar parte do nome
            query += " AND c.grupo ILIKE %s"
            params.append(f"%{filtro_valor}%")

        query += " ORDER BY nf.data_nota ASC"

        print(f"SQL: {query}") # DEBUG
        print(f"PARAMS: {params}") # DEBUG

        resultados = self.db.execute_query(query, params, fetch=True)
        
        lista_dto = []
        for r in resultados:
            lista_dto.append(ItemPendenteDTO(
                id=r['id'],
                numero_nota_origem=r['numero_nota'],
                data_nota_origem=r['data_nota'],
                codigo_item=r['codigo_item'],
                descricao_item="", 
                valor_original=float(r['valor_item']),
                saldo_financeiro=float(r['saldo_financeiro']),
                nome_cliente=r['nome_cliente'],
                grupo_economico=r['grupo']
            ))
        return lista_dto

    def salvar_retorno(self, header: RetornoHeaderDTO, itens: list[ItemPendenteDTO]):
        conn_manager = self.db.get_connection()
        with conn_manager as conn:
            try:
                cursor = conn.cursor()
                
                # 1. Inserir Cabeçalho da Nota de Retorno
                sql_head = """
                    INSERT INTO notas_retorno 
                    (numero_nota, data_emissao, tipo_retorno, cnpj_cliente, grupo_economico, valor_total_nota)
                    VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
                """
                cursor.execute(sql_head, (
                    header.numero_nota, header.data_emissao, header.tipo_retorno,
                    header.cnpj, header.grupo, header.valor_total
                ))
                id_retorno = cursor.fetchone()[0]

                # 2. Processar Itens (Baixa de Saldo + Vinculo Conciliação)
                for item in itens:
                    # Abate do saldo na tabela de entrada
                    sql_upd = "UPDATE itens_notas SET saldo_financeiro = saldo_financeiro - %s WHERE id = %s"
                    cursor.execute(sql_upd, (item.valor_a_abater, item.id))

                    # Cria registro na tabela de conciliação
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