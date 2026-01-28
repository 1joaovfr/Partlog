import pandas as pd
from database.connection import DatabaseConnection
from dtos.relatorio_dto import RelatorioItemDTO

class RelatorioModel:
    def __init__(self):
        self.db = DatabaseConnection()

    def get_dados_relatorio(self):
        # (Mantém a sua query SQL original igualzinha estava antes)
        sql = """
            SELECT 
                l.status, 
                l.codigo_analise, 
                to_char(n.data_lancamento, 'DD/MM/YYYY') as data_lancamento,
                to_char(n.data_recebimento, 'DD/MM/YYYY') as data_recebimento,
                to_char(l.data_analise, 'DD/MM/YYYY') as data_analise,
                c.cnpj,
                c.cliente as nome_cliente,
                c.grupo as grupo_cliente,
                c.cidade, c.estado, c.regiao,
                n.cnpj_remetente,
                cr.cliente as nome_remetente,
                to_char(n.data_nota, 'DD/MM/YYYY') as data_emissao,
                n.numero_nota as nf_entrada,
                l.codigo_item, i.grupo_item, l.numero_serie,
                l.codigo_avaria, a.descricao_avaria,
                l.valor_item, l.ressarcimento,
                nr.numero_nota as nf_retorno,
                nr.tipo_retorno,
                to_char(nr.data_emissao, 'DD/MM/YYYY') as data_retorno

            FROM itens_notas l
            JOIN notas_fiscais n ON l.id_nota_fiscal = n.id
            LEFT JOIN clientes c ON n.cnpj_cliente = c.cnpj
            LEFT JOIN clientes cr ON n.cnpj_remetente = cr.cnpj
            LEFT JOIN itens i ON l.codigo_item = i.codigo_item
            LEFT JOIN avarias a ON l.codigo_avaria = a.codigo_avaria
            LEFT JOIN conciliacao conc ON l.id = conc.id_item_entrada
            LEFT JOIN notas_retorno nr ON conc.id_nota_retorno = nr.id
            
            ORDER BY n.data_lancamento DESC, n.numero_nota DESC, l.codigo_analise ASC
        """
        dados_brutos = self.db.execute_query(sql, fetch=True)
        return [RelatorioItemDTO.from_dict(d) for d in dados_brutos]

    # --- NOVO MÉTODO DE EXPORTAÇÃO ---
    def gerar_excel_da_lista(self, caminho, dados_lista, colunas_lista):
        """
        Gera o Excel baseado exatamente no que está na lista fornecida.
        dados_lista: Lista de listas (linhas da tabela).
        colunas_lista: Lista de strings (cabeçalhos).
        """
        try:
            if not dados_lista:
                return False

            # Cria o DataFrame direto da lista
            df = pd.DataFrame(dados_lista, columns=colunas_lista)
            
            # Exporta
            df.to_excel(caminho, index=False)
            return True
            
        except Exception as e:
            print(f"Erro no Model ao exportar Excel da lista: {e}")
            return False