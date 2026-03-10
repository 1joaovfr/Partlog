import os
import oracledb
from dotenv import load_dotenv

load_dotenv()

oracledb.init_oracle_client(lib_dir=r"C:/oracle/instantclient_23_0")

def get_oracle_connection():

    try:
        conexao = oracledb.connect(
            user=os.getenv("ORA_USER"),
            password=os.getenv("ORA_PASSWORD"),
            dsn=os.getenv("ORA_DSN")
        )
        return conexao
    
    except oracledb.DatabaseError as erro:
        erro_obj, = erro.args
        print(f"Erro ao conectar na base Oracle: {erro_obj.message}")
        return None
    
if __name__ == "__main__":
    
    conn = get_oracle_connection()
    
    if conn:
        print("✅ Conexão estabelecida com sucesso!")
        
        try:
            with conn.cursor() as cursor:
                cursor.execute("select count (*) from mega.glo_agentes@bozza")
                resultado = cursor.fetchone()
                
                print(f"Retorno do banco: {resultado[0]}")
                
        except Exception as e:
            print(f"❌ Erro ao executar a consulta de teste: {e}")
            
        finally:
            conn.close()
            print("🔒 Conexão encerrada.")
    else:
        print("❌ Falha no teste: A conexão não pôde ser estabelecida.")