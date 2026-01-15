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
        Gera dados para o gráfico comparativo: Entrada vs Devolução.
        Lógica de Safra (Últimos 6 meses de RECEBIMENTO).
        """
        sql = """
            WITH meses AS (
                -- Busca os últimos 6 meses de ENTRADA
                SELECT DISTINCT TO_CHAR(data_recebimento, 'YYYY-MM') as mes
                FROM notas_fiscais
                WHERE data_recebimento IS NOT NULL
                ORDER BY mes DESC 
                LIMIT 6
            ),
            meses_final AS (
                SELECT mes FROM meses ORDER BY mes ASC
            ),
            recebido AS (
                SELECT 
                    TO_CHAR(n.data_recebimento, 'YYYY-MM') as mes, 
                    SUM(i.valor_item) as total
                FROM itens_notas i 
                JOIN notas_fiscais n ON i.id_nota_fiscal = n.id
                WHERE n.data_recebimento IS NOT NULL
                GROUP BY mes
            ),
            retornado_por_safra AS (
                SELECT 
                    TO_CHAR(n.data_recebimento, 'YYYY-MM') as mes, 
                    SUM(i.valor_item) as total
                FROM itens_notas i
                JOIN notas_fiscais n ON i.id_nota_fiscal = n.id
                JOIN conciliacao c ON i.id = c.id_item_entrada
                WHERE n.data_recebimento IS NOT NULL
                GROUP BY mes
            )
            SELECT
                m.mes,
                COALESCE(r.total, 0) as val_recebido,
                COALESCE(p.total, 0) as val_retornado
            FROM meses_final m
            LEFT JOIN recebido r ON m.mes = r.mes
            LEFT JOIN retornado_por_safra p ON m.mes = p.mes
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

    def get_historico_retornos_mes(self):
        """
        Retorna o valor total dos itens retornados agrupados pelo Mês de Emissão da Nota de Retorno.
        Filtra pelos últimos 6 meses disponíveis (Lógica corrigida: DESC -> ASC).
        """
        sql = """
            WITH meses AS (
                -- 1. Busca apenas os meses que existem na tabela de notas de retorno
                SELECT DISTINCT TO_CHAR(data_emissao, 'YYYY-MM') as mes
                FROM notas_retorno
                ORDER BY mes DESC -- Garante que pegamos os ÚLTIMOS (mais recentes)
                LIMIT 6
            ),
            meses_final AS (
                -- 2. Reordena para exibir cronologicamente (crescente)
                SELECT mes FROM meses ORDER BY mes ASC
            ),
            dados AS (
                -- 3. Agrega os valores por mês
                SELECT 
                    TO_CHAR(nr.data_emissao, 'YYYY-MM') as mes,
                    SUM(i.valor_item) as valor_total
                FROM itens_notas i
                JOIN conciliacao c ON i.id = c.id_item_entrada
                JOIN notas_retorno nr ON c.id_nota_retorno = nr.id
                GROUP BY mes
            )
            SELECT 
                m.mes,
                COALESCE(d.valor_total, 0) as valor_total
            FROM meses_final m
            LEFT JOIN dados d ON m.mes = d.mes
            ORDER BY m.mes ASC
        """
        return self.db.execute_query(sql, fetch=True)