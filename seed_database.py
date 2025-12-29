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
        print("Aplicando regras: Código de Análise Único e Status (Pendente/Procedente/Improcedente)...")
        
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

        # Controle de sequencial por mês (A=Jan, B=Fev...)
        # Garante que A0001, A0002... sejam gerados na ordem de entrada
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

                        # LOOP ITENS (10 a 15 por nota)
                        qtd_itens = random.randint(10, 15) 
                        
                        for _ in range(qtd_itens):
                            cod_prod = random.choice(lista_produtos)
                            valor = round(random.uniform(1000.00, 5000.00), 2)
                            
                            # --- REGRA 2: GERA O CÓDIGO DE ANÁLISE SEMPRE ---
                            # O código nasce junto com o cadastro do item, independente do status
                            seq = contadores_mes[mes]
                            cod_analise = f"{letra_mes}{seq:04d}"
                            contadores_mes[mes] += 1
                            
                            # --- REGRA 1: DEFINIÇÃO DE STATUS ---
                            # 40% chance de ser Pendente
                            is_pendente = random.random() < 0.40
                            
                            # Variáveis padrão (caso Pendente)
                            status_final = 'Pendente'
                            data_analise_item = None
                            cod_avaria = None
                            desc_avaria = None
                            proc_improc = None # Coluna redundante ou de apoio
                            ressarcimento = 0.0
                            
                            if not is_pendente:
                                # Se NÃO é pendente, foi analisado -> Procedente ou Improcedente
                                avaria_db = random.choice(lista_avarias) # (cod, desc, status_tabela)
                                
                                # O status da avaria define o status do item
                                resultado_analise = avaria_db[2] # 'Procedente' ou 'Improcedente'
                                
                                status_final = resultado_analise 
                                proc_improc = resultado_analise
                                
                                cod_avaria = avaria_db[0]
                                desc_avaria = avaria_db[1]
                                data_analise_item = data_recebimento + timedelta(days=random.randint(0, 5))
                                
                                if status_final == 'Procedente':
                                    ressarcimento = valor
                                else:
                                    ressarcimento = 0.0

                            # SQL Insert
                            sql_item = """
                                INSERT INTO itens_notas (
                                    id_nota_fiscal, codigo_item, valor_item, ressarcimento, 
                                    status, codigo_analise, data_analise, numero_serie,
                                    codigo_avaria, descricao_avaria, procedente_improcedente,
                                    produzido_revenda, fornecedor
                                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """
                            
                            valores_item = (
                                id_nota,
                                cod_prod,
                                valor,
                                ressarcimento,
                                status_final,      # Agora só entra Pendente, Procedente ou Improcedente
                                cod_analise,       # Sempre preenchido (Ex: A0005)
                                data_analise_item, # Null se pendente
                                f"NS{random.randint(100000,999999)}",
                                cod_avaria,        # Null se pendente
                                desc_avaria,       # Null se pendente
                                proc_improc,       # Null se pendente
                                random.choice(['Produzido', 'Revenda']),
                                "Fornecedor Padrão LTDA"
                            )
                            cursor.execute(sql_item, valores_item)
                            total_itens += 1
                    
                    conn.commit()
        
        print(f"\n✅ Geração Concluída!")
        print(f"   Total Notas: {total_notas}")
        print(f"   Total Itens: {total_itens} (Todos com Código de Análise gerado)")

    def run(self):

        try:
            self.limpar_banco()
            
            self.seed_clientes()
            self.seed_itens()
            self.seed_avarias()
            
            # Nova chamada
            self.seed_movimentacao()
            
            print("\n✅ Banco de dados populado com sucesso!")
        except Exception as e:
            print(f"\n❌ Erro ao popular banco: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    seeder = DatabaseSeeder()
    seeder.run()