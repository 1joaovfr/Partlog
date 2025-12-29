import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

DB_CONFIG = {
    'dbname': 'cardex_db',
    'user': 'dev',
    'password': 'indisa',  
    'host': 'localhost',
    'port': '5432'
}

class DatabaseConnection:
    @contextmanager
    def get_connection(self):
        conn = psycopg2.connect(**DB_CONFIG)
        try:
            yield conn
        finally:
            conn.close()

    def execute_query(self, query, params=None, fetch=False):
        """Executa query de forma segura e retorna dicts se fetch=True"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                if fetch:
                    return cursor.fetchall()
                conn.commit()

    def setup_database(self):
        """
        Cria as tabelas e garante que todas as colunas existam (Auto-Migration).
        """
        # 1. Criação das Tabelas (Estrutura Básica)
        queries_creation = [
            '''CREATE TABLE IF NOT EXISTS clientes (
                cnpj TEXT PRIMARY KEY,
                cliente TEXT,
                grupo TEXT, -- Tenta criar já com grupo
                cidade TEXT, 
                estado TEXT, 
                regiao TEXT
            )''',
            '''CREATE TABLE IF NOT EXISTS itens (
                codigo_item TEXT PRIMARY KEY,
                descricao_item TEXT,
                grupo_item TEXT
            )''',
            '''CREATE TABLE IF NOT EXISTS avarias (
                codigo_avaria TEXT PRIMARY KEY,
                descricao_avaria TEXT,
                status_avaria TEXT
            )''',
            '''CREATE TABLE IF NOT EXISTS notas_fiscais (
                id SERIAL PRIMARY KEY,
                numero_nota TEXT,
                data_nota DATE,
                cnpj_cliente TEXT,
                data_recebimento DATE,
                data_lancamento DATE,
                FOREIGN KEY (cnpj_cliente) REFERENCES clientes(cnpj)
            )''',
            '''CREATE TABLE IF NOT EXISTS itens_notas (
                id SERIAL PRIMARY KEY,
                id_nota_fiscal INTEGER,
                codigo_item TEXT,
                valor_item REAL,
                ressarcimento REAL,
                saldo_financeiro REAL DEFAULT 0, -- Tenta criar já com saldo
                status TEXT DEFAULT 'Pendente',
                codigo_analise TEXT,
                data_analise DATE,
                numero_serie TEXT,
                codigo_avaria TEXT,
                descricao_avaria TEXT,
                procedente_improcedente TEXT,
                produzido_revenda TEXT,
                fornecedor TEXT,
                FOREIGN KEY (id_nota_fiscal) REFERENCES notas_fiscais(id)
            )''',
            '''CREATE TABLE IF NOT EXISTS notas_retorno (
                id SERIAL PRIMARY KEY,
                numero_nota TEXT NOT NULL,
                data_emissao DATE NOT NULL,
                tipo_retorno TEXT NOT NULL,
                cnpj_cliente TEXT,
                grupo_economico TEXT,
                valor_total_nota REAL NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            )''',
            '''CREATE TABLE IF NOT EXISTS conciliacao (
                id SERIAL PRIMARY KEY,
                id_nota_retorno INTEGER REFERENCES notas_retorno(id),
                id_item_entrada INTEGER REFERENCES itens_notas(id),
                valor_abatido REAL NOT NULL,
                data_conciliacao DATE DEFAULT CURRENT_DATE
            )'''
        ]

        # 2. Garantia de Colunas (Para bancos antigos ou volumes persistentes)
        # Se a tabela já existe mas sem a coluna, isso corrige na hora.
        queries_migration = [
            "ALTER TABLE clientes ADD COLUMN IF NOT EXISTS grupo TEXT;",
            "ALTER TABLE itens_notas ADD COLUMN IF NOT EXISTS saldo_financeiro REAL DEFAULT 0;",
            # Garante que os saldos não fiquem zerados em itens antigos
            "UPDATE itens_notas SET saldo_financeiro = valor_item WHERE saldo_financeiro = 0 AND valor_item > 0;"
        ]

        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Executa Criação
                    for q in queries_creation:
                        cursor.execute(q)
                    
                    # Executa Migração/Correção
                    for q in queries_migration:
                        cursor.execute(q)
                        
                conn.commit()
            print("Banco de dados verificado e atualizado com sucesso.")
            return True  
            
        except Exception as e:
            print(f"Erro ao configurar banco: {e}")
            return False