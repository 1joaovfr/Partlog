import pandas as pd
from database.connection import DatabaseConnection
from dtos.relatorio_dto import RelatorioItemDTO

class RelatorioModel:
    def __init__(self):
        self.db = DatabaseConnection()

    def get_dados_relatorio(self):
        # JOIN duplo na tabela clientes: um para Emitente (c), outro para Remetente (cr)
        sql = """
            SELECT 
                l.status, 
                l.codigo_analise, 
                to_char(n.data_lancamento, 'DD/MM/YYYY') as data_lancamento,
                to_char(n.data_recebimento, 'DD/MM/YYYY') as data_recebimento,
                to_char(l.data_analise, 'DD/MM/YYYY') as data_analise,
                
                -- EMITENTE
                c.cnpj,
                c.cliente as nome_cliente,
                c.grupo as grupo_cliente,
                c.cidade, c.estado, c.regiao,

                -- REMETENTE (NOVO)
                n.cnpj_remetente,
                cr.cliente as nome_remetente,

                to_char(n.data_nota, 'DD/MM/YYYY') as data_emissao,
                n.numero_nota as nf_entrada,
                l.codigo_item, i.grupo_item, l.numero_serie,
                l.codigo_avaria, a.descricao_avaria,
                l.valor_item, l.ressarcimento,
                
                -- DADOS DE RETORNO
                nr.numero_nota as nf_retorno,
                nr.tipo_retorno,
                to_char(nr.data_emissao, 'DD/MM/YYYY') as data_retorno

            FROM itens_notas l
            JOIN notas_fiscais n ON l.id_nota_fiscal = n.id
            
            -- Join do Emitente (Cliente da Garantia)
            LEFT JOIN clientes c ON n.cnpj_cliente = c.cnpj
            
            -- Join do Remetente (Sua Empresa/Filial) <--- NOVO
            LEFT JOIN clientes cr ON n.cnpj_remetente = cr.cnpj
            
            LEFT JOIN itens i ON l.codigo_item = i.codigo_item
            LEFT JOIN avarias a ON l.codigo_avaria = a.codigo_avaria
            
            LEFT JOIN conciliacao conc ON l.id = conc.id_item_entrada
            LEFT JOIN notas_retorno nr ON conc.id_nota_retorno = nr.id
            
            ORDER BY n.data_lancamento DESC
        """
        dados_brutos = self.db.execute_query(sql, fetch=True)
        return [RelatorioItemDTO.from_dict(d) for d in dados_brutos]

    def gerar_excel(self, caminho, data_inicio, data_fim):
        """Exporta para Excel recuperando os dados de notas de retorno."""
        sql = """
            SELECT 
                to_char(n.data_lancamento, 'DD/MM/YYYY') as "Lançamento",
                to_char(n.data_recebimento, 'DD/MM/YYYY') as "Recebimento",
                to_char(l.data_analise, 'DD/MM/YYYY') as "Análise",
                l.status as "Status", 
                l.codigo_analise as "Cód. Análise", 
                
                -- REMETENTE (Primeiro)
                n.cnpj_remetente as "CNPJ Remetente",
                cr.cliente as "Remetente",

                -- EMITENTE
                c.cnpj as "CNPJ Emitente",
                c.cliente as "Emitente", 
                c.grupo as "Grp. Cliente",
                c.cidade as "Cidade",
                c.estado as "UF",
                c.regiao as "Região",
                
                to_char(n.data_nota, 'DD/MM/YYYY') as "Emissão",
                n.numero_nota as "Nota Fiscal", 
                l.codigo_item as "Item", 
                i.grupo_item as "Grp. Item",
                l.numero_serie as "Num. Série", 
                l.codigo_avaria as "Cód. Avaria",
                a.descricao_avaria as "Desc. Avaria", 
                l.valor_item as "Valor", 
                l.ressarcimento as "Ressarcimento",
                
                to_char(nr.data_emissao, 'DD/MM/YYYY') as "Retorno",
                nr.numero_nota as "Nota Fiscal (Retorno)",
                nr.tipo_retorno as "Desc. Retorno"

            FROM itens_notas l
            JOIN notas_fiscais n ON l.id_nota_fiscal = n.id
            LEFT JOIN clientes c ON n.cnpj_cliente = c.cnpj
            LEFT JOIN clientes cr ON n.cnpj_remetente = cr.cnpj -- <--- NOVO JOIN
            LEFT JOIN itens i ON l.codigo_item = i.codigo_item
            LEFT JOIN avarias a ON l.codigo_avaria = a.codigo_avaria
            
            LEFT JOIN conciliacao conc ON l.id = conc.id_item_entrada
            LEFT JOIN notas_retorno nr ON conc.id_nota_retorno = nr.id

            WHERE n.data_lancamento BETWEEN %s AND %s
            ORDER BY n.data_lancamento ASC
        """
        try:
            dados = self.db.execute_query(sql, (data_inicio, data_fim), fetch=True)
            if not dados: 
                return False
            
            df = pd.DataFrame(dados)
            
            # Garantir a ordem exata das colunas no Excel
            ordem_colunas = [
                "Lançamento", "Recebimento", "Análise", "Status", "Cód. Análise",
                "CNPJ Remetente", "Remetente", # <--- NOVAS COLUNAS NO EXCEL
                "CNPJ Emitente", "Emitente", "Grp. Cliente", "Cidade", "UF", "Região", 
                "Emissão", "Nota Fiscal",
                "Item", "Grp. Item", "Num. Série", "Cód. Avaria", "Desc. Avaria", 
                "Valor", "Ressarcimento",
                "Retorno", "Nota Fiscal (Retorno)", "Desc. Retorno"
            ]
            
            colunas_finais = [c for c in ordem_colunas if c in df.columns]
            df = df[colunas_finais]
            
            df.to_excel(caminho, index=False)
            return True
        except Exception as e:
            print(f"Erro no Model ao exportar Excel: {e}")
            return False