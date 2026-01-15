import random
from datetime import datetime, timedelta
from database.connection import DatabaseConnection

class DatabaseSeeder:
    def __init__(self):
        self.db = DatabaseConnection()
        
    def limpar_banco(self):
        """Apaga as tabelas antigas e recria a estrutura nova vazia."""
        print("Recriando estrutura do banco de dados...")
        
        # Ordem importa por causa das Foreign Keys
        cmds_drop = [
            "DROP TABLE IF EXISTS conciliacao CASCADE;",
            "DROP TABLE IF EXISTS notas_retorno CASCADE;",
            "DROP TABLE IF EXISTS itens_notas CASCADE;",
            "DROP TABLE IF EXISTS notas_fiscais CASCADE;",
            "DROP TABLE IF EXISTS itens CASCADE;",
            "DROP TABLE IF EXISTS clientes CASCADE;",
            "DROP TABLE IF EXISTS avarias CASCADE;",
        ]
        
        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                for cmd in cmds_drop:
                    try:
                        cursor.execute(cmd)
                    except Exception as e:
                        print(f"Aviso ao dropar tabela: {e}")
                conn.commit()

        # Chama o setup do banco real
        sucesso = self.db.setup_database()
        
        if sucesso:
            print("✅ Tabelas recriadas e limpas!")
        else:
            raise Exception("Falha ao recriar schema do banco.")

    def seed_clientes(self):
        print("Inserindo Clientes padrão...")
        clientes = [
            ("12345678000199", "AUTO PEÇAS SILVA", "Varejo", "São Paulo", "SP", "Sudeste"),
            ("98765432000155", "OFICINA DO ZÉ", "Oficina", "Rio de Janeiro", "RJ", "Sudeste"),
            ("11222333000188", "DISTRIBUIDORA NORTE", "Distribuidor", "Manaus", "AM", "Norte"),
            ("44555666000177", "SUL PEÇAS LTDA", "Varejo", "Porto Alegre", "RS", "Sul"),
            ("99888777000122", "CENTRO AUTO MINAS", "Oficina", "Belo Horizonte", "MG", "Sudeste"),
        ]
        sql = """
            INSERT INTO clientes (cnpj, cliente, grupo, cidade, estado, regiao) 
            VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING
        """
        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                for c in clientes:
                    cursor.execute(sql, c)
            conn.commit()
            
    def seed_itens(self):
        print("Inserindo Produtos padrão...")
        produtos = [
            ("P001", "Bomba de Combustível", "Motor"),
            ("P002", "Pastilha de Freio Diant.", "Freios"),
            ("P003", "Alternador 12V", "Elétrica"),
            ("P004", "Amortecedor Traseiro", "Suspensão"),
            ("P005", "Kit Embreagem", "Transmissão"),
            ("P006", "Sensor Lambda", "Injeção"),
            ("P007", "Radiador", "Arrefecimento"),
            ("P008", "Vela de Ignição", "Ignição"),
        ]
        sql = """
            INSERT INTO itens (codigo_item, descricao_item, grupo_item) 
            VALUES (%s, %s, %s) ON CONFLICT DO NOTHING
        """
        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                for p in produtos:
                    cursor.execute(sql, p)
            conn.commit()

    def seed_avarias(self):
        print("Inserindo Avarias padrão...")
        avarias = [
            ("001", "Quebra Física / Mau Uso", "Improcedente"),
            ("002", "Defeito de Fabricação (Vazamento)", "Procedente"),
            ("003", "Ruído Excessivo", "Procedente"),
            ("004", "Instalação Incorreta", "Improcedente"),
            ("005", "Desgaste Natural", "Improcedente"),
            ("006", "Falha Elétrica Interna", "Procedente"),
        ]
        sql = """
            INSERT INTO avarias (codigo_avaria, descricao_avaria, status_avaria) 
            VALUES (%s, %s, %s) ON CONFLICT DO NOTHING
        """
        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                for a in avarias:
                    cursor.execute(sql, a)
            conn.commit()

    def seed_movimentacao(self):
        print("Gerando Movimentação Histórica (Jan/2025 a Nov/2025)...")
        
        # 1. Recuperar dados base
        lista_cnpjs = []
        lista_produtos = [] 
        lista_avarias = []

        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT cnpj FROM clientes")
                lista_cnpjs = [row[0] for row in cursor.fetchall()]
                
                cursor.execute("SELECT codigo_item FROM itens")
                lista_produtos = [row[0] for row in cursor.fetchall()]
                
                cursor.execute("SELECT codigo_avaria, descricao_avaria, status_avaria FROM avarias")
                lista_avarias = cursor.fetchall()

        if not lista_cnpjs or not lista_produtos:
            print("❌ Erro: Faltam clientes ou produtos.")
            return

        contadores_mes = {m: 1 for m in range(1, 13)}

        total_notas = 0
        total_itens = 0

        # LOOP MESES
        for mes in range(1, 12): # Jan a Nov
            letra_mes = chr(ord('A') + mes - 1)
            
            # LOOP NOTAS (20 por mês)
            for _ in range(20): 
                cnpj_escolhido = random.choice(lista_cnpjs)
                num_nota = f"{random.randint(10000, 99999)}"
                
                dia = random.randint(1, 28)
                data_nota = datetime(2025, mes, dia)
                data_recebimento = data_nota + timedelta(days=random.randint(1, 5))
                data_lancamento = data_recebimento 

                with self.db.get_connection() as conn:
                    with conn.cursor() as cursor:
                        # Inserir Nota
                        sql_nota = """
                            INSERT INTO notas_fiscais (numero_nota, cnpj_cliente, data_nota, data_recebimento, data_lancamento)
                            VALUES (%s, %s, %s, %s, %s) RETURNING id
                        """
                        try:
                            cursor.execute(sql_nota, (num_nota, cnpj_escolhido, data_nota, data_recebimento, data_lancamento))
                            id_nota = cursor.fetchone()[0]
                            total_notas += 1
                        except Exception as e:
                            print(f"Erro nota: {e}")
                            continue

                        # LOOP ITENS (5 a 10 por nota)
                        qtd_itens = random.randint(5, 10) 
                        
                        for _ in range(qtd_itens):
                            cod_prod = random.choice(lista_produtos)
                            valor = round(random.uniform(100.00, 1500.00), 2)
                            
                            seq = contadores_mes[mes]
                            cod_analise = f"{letra_mes}{seq:04d}"
                            contadores_mes[mes] += 1
                            
                            is_pendente = random.random() < 0.40
                            
                            status_final = 'Pendente'
                            data_analise_item = None
                            cod_avaria = None
                            desc_avaria = None
                            proc_improc = None
                            ressarcimento = 0.0
                            
                            if not is_pendente:
                                avaria_db = random.choice(lista_avarias)
                                resultado_analise = avaria_db[2] # 'Procedente' ou 'Improcedente'
                                
                                status_final = resultado_analise 
                                proc_improc = resultado_analise
                                
                                cod_avaria = avaria_db[0]
                                desc_avaria = avaria_db[1]
                                data_analise_item = data_recebimento + timedelta(days=random.randint(1, 10))
                                
                                # Lógica de Ressarcimento:
                                # Se procedente, vamos supor um ressarcimento entre 10% a 30% do valor (Mão de Obra)
                                # Se improcedente, ressarcimento é 0.
                                if status_final == 'Procedente':
                                    ressarcimento = round(valor * random.uniform(0.10, 0.30), 2)
                                else:
                                    ressarcimento = 0.0

                            sql_item = """
                                INSERT INTO itens_notas (
                                    id_nota_fiscal, codigo_item, valor_item, ressarcimento, 
                                    status, codigo_analise, data_analise, numero_serie,
                                    codigo_avaria, descricao_avaria, procedente_improcedente,
                                    produzido_revenda, fornecedor
                                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """
                            
                            valores_item = (
                                id_nota, cod_prod, valor, ressarcimento,
                                status_final, cod_analise, data_analise_item,
                                f"NS{random.randint(100000,999999)}",
                                cod_avaria, desc_avaria, proc_improc,
                                random.choice(['Produzido', 'Revenda']),
                                "Fornecedor Padrão LTDA"
                            )
                            cursor.execute(sql_item, valores_item)
                            total_itens += 1
                    
                    conn.commit()
        
        print(f"\n✅ Geração de Entradas Concluída!")
        print(f"   Total Notas Entrada: {total_notas}")
        print(f"   Total Itens: {total_itens}")

    def seed_retornos(self):
        """
        Gera notas de retorno (financeiro/físico) baseadas nos itens já analisados.
        Regra: Agrupa itens analisados por Cliente e gera uma Nota de Retorno para eles.
        """
        print("\nGerando Notas de Retorno e Conciliação...")

        # 1. Buscar todos os itens que já foram analisados (Procedente/Improcedente)
        #    e que ainda não têm vínculo na tabela 'conciliacao' (embora o banco esteja limpo agora)
        sql_candidatos = """
            SELECT 
                i.id, i.valor_item, i.ressarcimento, i.procedente_improcedente, 
                i.data_analise, n.cnpj_cliente
            FROM itens_notas i
            JOIN notas_fiscais n ON i.id_nota_fiscal = n.id
            WHERE i.status IN ('Procedente', 'Improcedente')
            ORDER BY n.cnpj_cliente, i.data_analise
        """

        itens_candidatos = []
        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql_candidatos)
                itens_candidatos = cursor.fetchall() # Retorna lista de dicts ou tuplas dependendo do cursor

        if not itens_candidatos:
            print("Nenhum item analisado encontrado para gerar retorno.")
            return

        # 2. Agrupar por Cliente (CNPJ)
        from collections import defaultdict
        itens_por_cliente = defaultdict(list)
        
        for item in itens_candidatos:
            # item[5] é cnpj_cliente (se for tupla) ou item['cnpj_cliente']
            cnpj = item['cnpj_cliente'] if isinstance(item, dict) else item[5]
            itens_por_cliente[cnpj].append(item)

        total_notas_retorno = 0
        total_conciliados = 0

        # 3. Para cada cliente, criar notas de retorno em lotes
        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                
                for cnpj, lista_itens in itens_por_cliente.items():
                    # Vamos processar em lotes de 3 a 8 itens por Nota de Retorno
                    # Para simular que a empresa junta alguns itens antes de emitir a nota
                    
                    random.shuffle(lista_itens) # Embaralha para não pegar só sequencial
                    
                    # Fatiar a lista em chunks
                    chunk_size = random.randint(3, 8)
                    chunks = [lista_itens[i:i + chunk_size] for i in range(0, len(lista_itens), chunk_size)]
                    
                    for batch in chunks:
                        # Dados para o Cabeçalho da Nota de Retorno
                        # A data da nota de retorno deve ser posterior à última análise do lote
                        datas_analise = [x['data_analise'] if isinstance(x, dict) else x[4] for x in batch]
                        max_data_analise = max(datas_analise)
                        
                        # Data Emissão = Data da última análise + 2 a 15 dias
                        data_emissao = max_data_analise + timedelta(days=random.randint(2, 15))
                        
                        # Se a data calculada for no futuro (além de hoje), ajustamos para hoje ou ignoramos
                        # Como o seed vai até Nov/2025 (no script), e estamos simulando, assumimos ok.
                        
                        numero_nota_ret = f"RET-{random.randint(1000, 99999)}"
                        
                        # Calcula totais
                        valor_total_nota = 0.0
                        
                        # Inserir Cabeçalho (Nota Retorno) inicialmente com valor 0
                        sql_insert_nota = """
                            INSERT INTO notas_retorno (
                                numero_nota, data_emissao, tipo_retorno, cnpj_cliente, 
                                grupo_economico, valor_total_nota
                            ) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
                        """
                        cursor.execute(sql_insert_nota, (
                            numero_nota_ret, 
                            data_emissao, 
                            "Garantia/Devolucao", 
                            cnpj, 
                            "Varejo", # Simplificação
                            0.0 
                        ))
                        id_nota_retorno = cursor.fetchone()[0]
                        total_notas_retorno += 1

                        # Inserir Itens na Conciliação
                        for item in batch:
                            # Extrair dados
                            if isinstance(item, dict):
                                i_id = item['id']
                                i_valor = item['valor_item']
                                i_ressarc = item['ressarcimento']
                                i_status = item['procedente_improcedente']
                            else:
                                i_id, i_valor, i_ressarc, i_status = item[0], item[1], item[2], item[3]

                            # Regra de Negócio para Valor Abatido:
                            # Se PROCEDENTE: Valor Abatido = Valor Item + Ressarcimento (Empresa paga tudo)
                            # Se IMPROCEDENTE: Valor Abatido = 0 (Geralmente devolução física sem crédito financeiro)
                            # Mas vinculamos a nota para provar que foi devolvido.
                            
                            valor_abatido = 0.0
                            if i_status == 'Procedente':
                                valor_abatido = float(i_valor) + float(i_ressarc)
                            
                            sql_concilia = """
                                INSERT INTO conciliacao (
                                    id_nota_retorno, id_item_entrada, valor_abatido, data_conciliacao
                                ) VALUES (%s, %s, %s, %s)
                            """
                            cursor.execute(sql_concilia, (
                                id_nota_retorno, i_id, valor_abatido, data_emissao
                            ))
                            
                            valor_total_nota += valor_abatido
                            total_conciliados += 1

                        # Atualizar o valor total da Nota de Retorno
                        cursor.execute(
                            "UPDATE notas_retorno SET valor_total_nota = %s WHERE id = %s",
                            (valor_total_nota, id_nota_retorno)
                        )

                conn.commit()

        print(f"✅ Geração de Retornos Concluída!")
        print(f"   Total Notas Retorno: {total_notas_retorno}")
        print(f"   Itens Conciliados: {total_conciliados}")

    def run(self):
        try:
            self.limpar_banco()
            
            self.seed_clientes()
            self.seed_itens()
            self.seed_avarias()
            
            self.seed_movimentacao() # Gera Entradas e Análises
            self.seed_retornos()     # Gera Saídas (Retornos) baseadas nas análises
            
            print("\n✅ Banco de dados populado com sucesso!")
        except Exception as e:
            print(f"\n❌ Erro ao popular banco: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    seeder = DatabaseSeeder()
    seeder.run()