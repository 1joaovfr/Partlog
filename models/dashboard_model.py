from database.connection import DatabaseConnection

class DashboardModel:
    """
    Camada de acesso a dados para os indicadores gerenciais (KPIs).
    Responsável por queries analíticas e agregações financeiras.
    """
    
    def __init__(self):
        self.db = DatabaseConnection()

    def get_kpi_financeiro(self):
        """Calcula o impacto financeiro total das garantias procedentes."""
        sql = """
            SELECT
                SUM(valor_item + ressarcimento) as total_custo,
                COUNT(*) as qtd
            FROM itens_notas
            WHERE procedente_improcedente = 'Procedente'
        """
        res = self.db.execute_query(sql, fetch=True)
        
        if res and res[0]['total_custo']:
            total = float(res[0]['total_custo'])
            qtd = int(res[0]['qtd'])
            medio = total / qtd if qtd > 0 else 0.0
            return {'total': total, 'qtd': qtd, 'medio': medio}
            
        return {'total': 0.0, 'qtd': 0, 'medio': 0.0}

    def get_gap_atual_recebimento(self):
        """Calcula a diferença em dias entre HOJE e a data da nota mais recente lançada."""
        sql = """
            SELECT CURRENT_DATE - MAX(data_recebimento) as dias_defasagem
            FROM notas_fiscais
            WHERE data_recebimento IS NOT NULL
        """
        res = self.db.execute_query(sql, fetch=True)
        
        if res and res[0]['dias_defasagem'] is not None:
            return float(res[0]['dias_defasagem'])
        return 0.0

    def get_comparativo_financeiro(self):
        """
        Gera dados para o gráfico comparativo: Entrada (Recebido) vs Saída (Garantia Paga).
        
        LÓGICA AJUSTADA:
        - Recebido: Baseado na data de LANÇAMENTO da nota de entrada.
        - Retornado: Baseado na tabela CONCILIAÇÃO (itens efetivamente abatidos/pagos via Nota de Retorno).
          Usa a data de EMISSÃO da Nota de Retorno.
        """
        sql = """
            WITH meses_entrada AS (
                SELECT DISTINCT TO_CHAR(data_lancamento, 'YYYY-MM') as mes
                FROM notas_fiscais
            ),
            meses_saida AS (
                SELECT DISTINCT TO_CHAR(data_emissao, 'YYYY-MM') as mes
                FROM notas_retorno
            ),
            todos_meses AS (
                SELECT mes FROM meses_entrada
                UNION 
                SELECT mes FROM meses_saida
                ORDER BY mes DESC 
                LIMIT 6
            ),
            meses_final AS (
                SELECT mes FROM todos_meses ORDER BY mes ASC
            ),
            recebido AS (
                -- Totaliza o valor das peças que entraram (Data Lançamento)
                SELECT TO_CHAR(n.data_lancamento, 'YYYY-MM') as mes, SUM(i.valor_item) as total
                FROM itens_notas i JOIN notas_fiscais n ON i.id_nota_fiscal = n.id
                GROUP BY mes
            ),
            retornado AS (
                -- Totaliza apenas o que tem vínculo na tabela CONCILIACAO (efetivamente pago)
                SELECT 
                    TO_CHAR(nr.data_emissao, 'YYYY-MM') as mes, 
                    SUM(c.valor_abatido) as total
                FROM conciliacao c
                JOIN notas_retorno nr ON c.id_nota_retorno = nr.id
                GROUP BY mes
            )
            SELECT
                m.mes,
                COALESCE(r.total, 0) as val_recebido,
                COALESCE(p.total, 0) as val_retornado
            FROM meses_final m
            LEFT JOIN recebido r ON m.mes = r.mes
            LEFT JOIN retornado p ON m.mes = p.mes
            ORDER BY m.mes ASC
        """
        return self.db.execute_query(sql, fetch=True)

    def get_status_geral(self):
        """Retorna distribuição de status para gráfico de rosca."""
        sql = """
            SELECT
                CASE
                    WHEN status = 'Pendente' THEN 'Pendente'
                    WHEN procedente_improcedente = 'Procedente' THEN 'Procedente'
                    WHEN procedente_improcedente = 'Improcedente' THEN 'Improcedente'
                    ELSE status
                END as status_final,
                COUNT(*) as qtd
            FROM itens_notas
            GROUP BY status_final
        """
        return self.db.execute_query(sql, fetch=True)

    # --- NOVOS MÉTODOS PARA O FILTRO INDEPENDENTE (BACKLOG) ---

    def get_meses_com_pendencia_analise(self):
        """
        Busca os meses de entrada (Lançamento) que possuem itens 
        ainda sem análise técnica realizada (data_analise IS NULL).
        """
        sql = """
            SELECT DISTINCT 
                TO_CHAR(n.data_lancamento, 'MM/YYYY') as mes_formatado,
                TO_CHAR(n.data_lancamento, 'YYYY-MM') as mes_sort
            FROM itens_notas i
            JOIN notas_fiscais n ON i.id_nota_fiscal = n.id
            WHERE i.data_analise IS NULL 
            ORDER BY mes_sort DESC
        """
        return self.db.execute_query(sql, fetch=True)

    def get_kpi_backlog_analise(self, mes_ano_filtro=None):
        """
        Calcula Qtd e Valor SOMENTE DO RESSARCIMENTO dos itens 
        que estão aguardando análise.
        """
        # AJUSTE: Soma APENAS a coluna 'ressarcimento'.
        # Ignora o 'valor_item' (preço da peça).
        sql = """
            SELECT 
                COUNT(*) as qtd,
                COALESCE(SUM(i.ressarcimento), 0) as total
            FROM itens_notas i
            JOIN notas_fiscais n ON i.id_nota_fiscal = n.id
            WHERE i.data_analise IS NULL
        """
        
        params = []
        if mes_ano_filtro and mes_ano_filtro != "Todos":
            # Filtra pela data de chegada (Lançamento da Nota)
            sql += " AND TO_CHAR(n.data_lancamento, 'MM/YYYY') = %s"
            params.append(mes_ano_filtro)
            
        res = self.db.execute_query(sql, params=tuple(params), fetch=True)
        
        if res:
            return {'qtd': int(res[0]['qtd']), 'total': float(res[0]['total'])}
        return {'qtd': 0, 'total': 0.0}