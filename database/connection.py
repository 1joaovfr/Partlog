import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

# Configuração de Banco de Dados
DB_CONFIG = {
    'dbname': 'cardex_db',
    'user': 'dev',
    'password': 'indisa',  
    'host': 'localhost',
    'port': '5432'
}

class DatabaseConnection:
    """
    Gerencia a conexão com o banco de dados PostgreSQL.
    Utiliza o padrão Context Manager para garantir o fechamento seguro das conexões.
    """

    @contextmanager
    def get_connection(self):
        """
        Generator que fornece uma conexão segura com o banco.
        """
        conn = psycopg2.connect(**DB_CONFIG)
        try:
            yield conn
        finally:
            conn.close()

    def execute_query(self, query: str, params=None, fetch=False):
        """
        Executa uma query SQL de forma segura.
        """
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                if fetch:
                    return cursor.fetchall()
                conn.commit()

    def setup_database(self):
        """
        Executa a Auto-Migração do banco de dados.
        """
        # Estrutura inicial das tabelas (JÁ COM OS CAMPOS NOVOS)
        queries_creation = [
            '''CREATE TABLE IF NOT EXISTS clientes (
                cnpj TEXT PRIMARY KEY,
                cliente TEXT,
                grupo TEXT,
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
            # A tabela notas_fiscais já nasce completa aqui
            '''CREATE TABLE IF NOT EXISTS notas_fiscais (
                id SERIAL PRIMARY KEY,
                numero_nota TEXT,
                data_nota DATE,
                cnpj_cliente TEXT,
                cnpj_remetente TEXT, 
                data_recebimento DATE,
                data_lancamento DATE,
                FOREIGN KEY (cnpj_cliente) REFERENCES clientes(cnpj),
                FOREIGN KEY (cnpj_remetente) REFERENCES clientes(cnpj)
            )''',
            '''CREATE TABLE IF NOT EXISTS itens_notas (
                id SERIAL PRIMARY KEY,
                id_nota_fiscal INTEGER,
                codigo_item TEXT,
                valor_item REAL,
                ressarcimento REAL,
                saldo_financeiro REAL DEFAULT 0,
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

        # Migrações: Mantive apenas as genéricas de correção de dados antigos (saldo e grupo)
        # Removi a criação de coluna e FK na notas_fiscais, pois o CREATE acima já resolve.
        queries_migration = [
            "ALTER TABLE clientes ADD COLUMN IF NOT EXISTS grupo TEXT;",
            "ALTER TABLE itens_notas ADD COLUMN IF NOT EXISTS saldo_financeiro REAL DEFAULT 0;",
            "UPDATE itens_notas SET saldo_financeiro = valor_item WHERE saldo_financeiro = 0 AND valor_item > 0;"
        ]

        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    for q in queries_creation:
                        cursor.execute(q)
                    for q in queries_migration:
                        cursor.execute(q)
                conn.commit()
            print("Database setup completed successfully.")
            return True  
        except Exception as e:
            print(f"Database setup failed: {e}")
            return False