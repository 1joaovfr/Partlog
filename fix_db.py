from database import DatabaseConnection

def criar_coluna_faltante():
    db = DatabaseConnection()
    conn_manager = db.get_connection()
    
    with conn_manager as conn:
        try:
            cursor = conn.cursor()
            print("Tentando criar a coluna 'codigo_analise'...")
            
            # O comando 'IF NOT EXISTS' evita erro se você rodar 2 vezes sem querer
            sql = """
            ALTER TABLE conciliacao 
            ADD COLUMN IF NOT EXISTS codigo_analise VARCHAR(50);
            """
            
            cursor.execute(sql)
            conn.commit()
            print("✅ Sucesso! Coluna criada. Pode rodar o sistema.")
            
        except Exception as e:
            conn.rollback()
            print(f"❌ Erro ao alterar banco: {e}")

if __name__ == "__main__":
    criar_coluna_faltante()