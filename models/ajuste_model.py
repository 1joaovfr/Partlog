from database.connection import DatabaseConnection
from dtos.ajuste_dto import AjusteItemDTO

class AjusteModel:
    def __init__(self):
        self.db = DatabaseConnection()

    def get_dados_ajuste(self):
        # Query similar ao relatório, mas pegando os IDs (l.id e n.id)
        sql = """
            SELECT 
                l.id as id_item, n.id as id_nota, -- CAMPOS CRITICOS PARA UPDATE
                l.status, l.codigo_analise, 
                to_char(n.data_lancamento, 'DD/MM/YYYY') as data_lancamento,
                to_char(n.data_recebimento, 'DD/MM/YYYY') as data_recebimento,
                to_char(l.data_analise, 'DD/MM/YYYY') as data_analise,
                c.cnpj, c.cliente as nome_cliente, c.grupo as grupo_cliente,
                c.cidade, c.estado, c.regiao,
                n.cnpj_remetente, cr.cliente as nome_remetente,
                to_char(n.data_nota, 'DD/MM/YYYY') as data_emissao,
                n.numero_nota as nf_entrada,
                l.codigo_item, i.grupo_item, l.numero_serie,
                l.codigo_avaria, a.descricao_avaria,
                l.valor_item, l.ressarcimento,
                nr.numero_nota as nf_retorno, nr.tipo_retorno,
                to_char(nr.data_emissao, 'DD/MM/YYYY') as data_retorno
            FROM itens_notas l
            JOIN notas_fiscais n ON l.id_nota_fiscal = n.id
            LEFT JOIN clientes c ON n.cnpj_cliente = c.cnpj
            LEFT JOIN clientes cr ON n.cnpj_remetente = cr.cnpj
            LEFT JOIN itens i ON l.codigo_item = i.codigo_item
            LEFT JOIN avarias a ON l.codigo_avaria = a.codigo_avaria
            LEFT JOIN conciliacao conc ON l.id = conc.id_item_entrada
            LEFT JOIN notas_retorno nr ON conc.id_nota_retorno = nr.id
            ORDER BY n.data_lancamento DESC
        """
        dados = self.db.execute_query(sql, fetch=True)
        return [AjusteItemDTO.from_dict(d) for d in dados]

    def verificar_vinculo_retorno(self, id_item):
        """Retorna True se o item já possui nota de retorno vinculada (não pode editar)"""
        sql = "SELECT id FROM conciliacao WHERE id_item_entrada = %s"
        res = self.db.execute_query(sql, (id_item,), fetch=True)
        return len(res) > 0

    def atualizar_item(self, dto: AjusteItemDTO, novos_dados: dict):
        """
        Realiza a atualização segura.
        novos_dados: dict com chaves 'nf_entrada', 'data_emissao', 'cnpj_remetente',
                     'codigo_item', 'codigo_analise', 'valor_item', 'numero_serie'
        """
        if self.verificar_vinculo_retorno(dto.id_item):
            raise Exception("Não é possível alterar item vinculado a uma Nota de Retorno.")

        try:
            # 1. Atualizar Tabela Pai (Notas Fiscais) - Cuidado: Afeta todos os itens da nota
            # Se quiser restringir, não atualize a nota, mas geralmente correção é na nota.
            sql_nota = """
                UPDATE notas_fiscais 
                SET numero_nota = %s, data_nota = %s, cnpj_remetente = %s
                WHERE id = %s
            """
            self.db.execute_query(sql_nota, (
                novos_dados['nf_entrada'],
                novos_dados['data_emissao'],
                novos_dados['cnpj_remetente'],
                dto.id_nota
            ))

            # 2. Atualizar Tabela Filho (Itens Notas)
            # Ao mudar codigo_analise, o Status muda logicamente pois é derivado? 
            # Se o status for um campo texto fixo na tabela, precisamos atualizar ele também.
            # Vou assumir que você passa o novo status baseado no código na View ou aqui.
            
            # Exemplo simples: Atualiza os dados diretos
            sql_item = """
                UPDATE itens_notas
                SET codigo_item = %s, codigo_analise = %s, 
                    valor_item = %s, numero_serie = %s,
                    codigo_avaria = %s
                WHERE id = %s
            """
            self.db.execute_query(sql_item, (
                novos_dados['codigo_item'],
                novos_dados['codigo_analise'],
                novos_dados['valor_item'],
                novos_dados['numero_serie'],
                novos_dados['codigo_avaria'],
                dto.id_item
            ))
            return True
        except Exception as e:
            print(f"Erro no Update: {e}")
            raise e

    def excluir_item(self, id_item):
        if self.verificar_vinculo_retorno(id_item):
            raise Exception("Não é possível excluir item vinculado a uma Nota de Retorno.")
        
        sql = "DELETE FROM itens_notas WHERE id = %s"
        self.db.execute_query(sql, (id_item,))
        return True