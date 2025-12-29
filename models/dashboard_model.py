from database.connection import DatabaseConnection

class DashboardModel:
    def __init__(self):
        self.db = DatabaseConnection()

    def get_kpi_financeiro(self):
        """Calcula totais financeiros apenas dos itens PROCEDENTES (Peça + Ressarcimento)."""
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
        Calcula o 'Gap Cronológico' do sistema.
        Lógica: Data de Hoje - A data de recebimento MAIS RECENTE registrada no banco.
        
        Isso responde: "A nota mais nova que temos no sistema chegou há quanto tempo?"
        """
        sql = """
            SELECT CURRENT_DATE - MAX(data_recebimento) as dias_defasagem
            FROM notas_fiscais
            WHERE data_recebimento IS NOT NULL
        """
        res = self.db.execute_query(sql, fetch=True)
        
        # Se o banco estiver vazio, retorna 0. Se tiver dados, retorna o valor.
        if res and res[0]['dias_defasagem'] is not None:
            return float(res[0]['dias_defasagem'])
        return 0.0

    def get_comparativo_financeiro(self):
        """
        Gráfico 1: Valor Recebido (Entrada) vs Valor Retornado (Procedente + Ressarcimento).
        """
        sql = """
            WITH meses AS (
                SELECT DISTINCT TO_CHAR(data_lancamento, 'YYYY-MM') as mes
                FROM notas_fiscais
                ORDER BY mes ASC LIMIT 6
            ),
            recebido AS (
                -- Soma do valor das peças que entraram (baseado no lançamento)
                SELECT TO_CHAR(n.data_lancamento, 'YYYY-MM') as mes, SUM(i.valor_item) as total
                FROM itens_notas i JOIN notas_fiscais n ON i.id_nota_fiscal = n.id
                GROUP BY mes
            ),
            retornado AS (
                -- Soma do custo total pago (Procedente) baseado na data da ANÁLISE
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
        """Gráfico 2: Rosca de Status (Pendente, Procedente, Improcedente)."""
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
        """Gráfico 3: Qtd e Valor de itens recebidos por mês (Baseado em Lançamento)."""
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
        """Gráfico 4: Evolução do Lead Time (Gap Médio mensal)."""
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