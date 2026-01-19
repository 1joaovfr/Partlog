import random
from datetime import datetime, timedelta, date # <--- Import 'date' adicionado
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
        # --- LÓGICA DE DATA ATUAL (Corrigido para .date()) ---
        hoje = datetime.now().date()
        print(f"Gerando Movimentação Histórica (Jan/2025 até {hoje.strftime('%d/%m/%Y')})...")
        
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

        # --- LOOP ANUAL (2025 até o ano atual) ---
        ano_inicial = 2025
        ano_final = hoje.year
        
        for ano in range(ano_inicial, ano_final + 1):
            
            # Definir intervalo de meses para este ano
            mes_inicio = 1
            mes_fim = 12
            
            # Se for o ano atual, vai só até o mês atual
            if ano == ano_final:
                mes_fim = hoje.month
            
            # LOOP MESES
            for mes in range(mes_inicio, mes_fim + 1):
                letra_mes = chr(ord('A') + mes - 1)
                
                # Definir dia máximo
                max_dia = 28
                # Se for o mês exato de hoje, limita ao dia de hoje
                if ano == ano_final and mes == hoje.month:
                    max_dia = hoje.day
                
                if max_dia < 1: max_dia = 1

                # LOOP NOTAS (20 por mês)
                for _ in range(20): 
                    cnpj_cliente = random.choice(lista_cnpjs)
                    
                    # 80% Cliente, 20% Outro (Triangulação)
                    if random.random() < 0.8:
                        cnpj_remetente = cnpj_cliente
                    else:
                        cnpj_remetente = random.choice(lista_cnpjs)

                    num_nota = f"{random.randint(10000, 99999)}"
                    
                    dia = random.randint(1, max_dia)
                    # CORREÇÃO: Usar date() em vez de datetime()
                    data_nota = date(ano, mes, dia)
                    
                    # Data recebimento não pode ser futura
                    dias_delay = random.randint(1, 5)
                    data_recebimento = data_nota + timedelta(days=dias_delay)
                    
                    if data_recebimento > hoje:
                        data_recebimento = hoje
                        
                    data_lancamento = data_recebimento 

                    with self.db.get_connection() as conn:
                        with conn.cursor() as cursor:
                            # Inserir Nota (COM O CAMPO REMETENTE)
                            sql_nota = """
                                INSERT INTO notas_fiscais (numero_nota, cnpj_cliente, cnpj_remetente, data_nota, data_recebimento, data_lancamento)
                                VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
                            """
                            try:
                                cursor.execute(sql_nota, (num_nota, cnpj_cliente, cnpj_remetente, data_nota, data_recebimento, data_lancamento))
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
                                    resultado_analise = avaria_db[2] 
                                    
                                    status_final = resultado_analise 
                                    proc_improc = resultado_analise
                                    
                                    cod_avaria = avaria_db[0]
                                    desc_avaria = avaria_db[1]
                                    
                                    # Data análise deve ser > recebimento e <= hoje
                                    dias_analise = random.randint(1, 10)
                                    data_analise_item = data_recebimento + timedelta(days=dias_analise)
                                    if data_analise_item > hoje:
                                        data_analise_item = hoje
                                    
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
        """
        print("\nGerando Notas de Retorno e Conciliação...")
        
        # Data de hoje para comparação (Tipo date)
        hoje = datetime.now().date() 

        # 1. Buscar todos os itens que já foram analisados
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
                itens_candidatos = cursor.fetchall() 

        if not itens_candidatos:
            print("Nenhum item analisado encontrado para gerar retorno.")
            return

        # 2. Agrupar por Cliente (CNPJ)
        from collections import defaultdict
        itens_por_cliente = defaultdict(list)
        
        for item in itens_candidatos:
            if isinstance(item, dict):
                cnpj = item['cnpj_cliente']
            else:
                cnpj = item[5]
            itens_por_cliente[cnpj].append(item)

        total_notas_retorno = 0
        total_conciliados = 0

        # 3. Para cada cliente, criar notas de retorno
        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                
                for cnpj, lista_itens in itens_por_cliente.items():
                    random.shuffle(lista_itens) 
                    
                    chunk_size = random.randint(3, 8)
                    chunks = [lista_itens[i:i + chunk_size] for i in range(0, len(lista_itens), chunk_size)]
                    
                    for batch in chunks:
                        datas_analise = [x['data_analise'] if isinstance(x, dict) else x[4] for x in batch]
                        
                        datas_validas = [d for d in datas_analise if d]
                        if not datas_validas: continue

                        max_data_analise = max(datas_validas)
                        
                        # Data Emissão Retorno > Última Análise e <= Hoje
                        data_emissao = max_data_analise + timedelta(days=random.randint(2, 15))
                        
                        # Ajuste para não gerar datas futuras
                        if data_emissao > hoje:
                            data_emissao = hoje
                        
                        numero_nota_ret = f"RET-{random.randint(1000, 99999)}"
                        valor_total_nota = 0.0
                        
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
                            "Varejo", 
                            0.0 
                        ))
                        id_nota_retorno = cursor.fetchone()[0]
                        total_notas_retorno += 1

                        for item in batch:
                            if isinstance(item, dict):
                                i_id = item['id']
                                i_valor = item['valor_item']
                                i_ressarc = item['ressarcimento']
                                i_status = item['procedente_improcedente']
                            else:
                                i_id, i_valor, i_ressarc, i_status = item[0], item[1], item[2], item[3]

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
            
            self.seed_movimentacao() 
            self.seed_retornos()    
            
            print("\n✅ Banco de dados populado com sucesso!")
        except Exception as e:
            print(f"\n❌ Erro ao popular banco: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    seeder = DatabaseSeeder()
    seeder.run()