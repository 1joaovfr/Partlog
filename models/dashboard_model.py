from database.connection import DatabaseConnection

class DashboardModel:
    """
    Camada de acesso a dados para os indicadores gerenciais (KPIs).
    Responsável por queries analíticas e agregações financeiras.
    """
    
    def __init__(self):
        self.db = DatabaseConnection()

    def get_kpi_financeiro(self):
        """
        Calcula o impacto financeiro total das garantias procedentes.
        Retorna: Dict com Total (R$), Quantidade e Ticket Médio.
        """
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
        """
        Calcula o 'Lead Time' de entrada (Gap Cronológico).
        Métrica: Diferença em dias entre HOJE e a data da nota mais recente lançada.
        Objetivo: Monitorar atraso no lançamento de notas fiscais.
        """
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
        Utiliza CTEs para segregar as datas de 'Lançamento' das datas de 'Análise'.
        """
        sql = """
            WITH meses AS (
                SELECT DISTINCT TO_CHAR(data_lancamento, 'YYYY-MM') as mes
                FROM notas_fiscais
                ORDER BY mes ASC LIMIT 6
            ),
            recebido AS (
                -- Totaliza o valor das peças que entraram na fábrica (Data Lançamento)
                SELECT TO_CHAR(n.data_lancamento, 'YYYY-MM') as mes, SUM(i.valor_item) as total
                FROM itens_notas i JOIN notas_fiscais n ON i.id_nota_fiscal = n.id
                GROUP BY mes
            ),
            retornado AS (
                -- Totaliza o custo pago (Peça + Ressarcimento) na data efetiva da ANÁLISE
                SELECT TO_CHAR(i.data_analise, 'YYYY-MM') as mes, SUM(i.valor_item + i.ressarcimento) as total
                FROM itens_notas i
                WHERE i.procedente_improcedente = 'Procedente'
                GROUP BY mes
            )
            SELECT
                m.mes,
                COALESCE(r.total, 0) as val_recebido,
                COALESCE(p.total, 0) as val_retornado
            FROM meses m
            LEFT JOIN recebido r ON m.mes = r.mes
            LEFT JOIN retornado p ON m.mes = p.mes
            ORDER BY m.mes ASC
        """
        return self.db.execute_query(sql, fetch=True)

    def get_status_geral(self):
        """Retorna distribuição de status para gráfico de rosca (Pie Chart)."""
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

    def get_entrada_mensal(self):
        """Retorna histórico de volume (Qtd) e financeiro (R$) de entradas por mês."""
        sql = """
            SELECT TO_CHAR(n.data_lancamento, 'YYYY-MM') as mes,
                   COUNT(*) as qtd,
                   SUM(i.valor_item) as valor
            FROM itens_notas i
            JOIN notas_fiscais n ON i.id_nota_fiscal = n.id
            GROUP BY mes
            ORDER BY mes ASC
            LIMIT 6
        """
        return self.db.execute_query(sql, fetch=True)

    def get_evolucao_lead_time(self):
        """Calcula a média mensal de dias entre o Recebimento Físico e a Análise Técnica."""
        sql = """
            SELECT
                TO_CHAR(i.data_analise, 'YYYY-MM') as mes,
                AVG(i.data_analise - n.data_recebimento) as media_dias
            FROM itens_notas i
            JOIN notas_fiscais n ON i.id_nota_fiscal = n.id
            WHERE i.data_analise IS NOT NULL
              AND n.data_recebimento IS NOT NULL
            GROUP BY mes
            ORDER BY mes ASC
            LIMIT 6
        """
        return self.db.execute_query(sql, fetch=True)