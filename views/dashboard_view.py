import sys
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                               QLabel, QFrame, QPushButton, QSizePolicy)
from PySide6.QtCore import Qt
from PySide6.QtWebEngineWidgets import QWebEngineView 
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import qtawesome as qta

from controllers import DashboardController

# Importamos o CSS e as Funções de Estilo
from styles.dashboard_styles import (
    DASHBOARD_STYLES, 
    apply_chart_theme, 
    get_plotly_html_wrapper
)
from styles.theme import (
    COLOR_DANGER, COLOR_SUCCESS, COLOR_WARNING, COLOR_TEXT_DIM,
    CHART_BLUE_PRIMARY, CHART_INDIGO, CHART_NEON_BLUE, CHART_LINE_HIGHLIGHT, 
    COLOR_CARD_BORDER, COLOR_TEXT
)

class PlotlyWidget(QWebEngineView):
    def __init__(self, fig):
        super().__init__()
        # Configuração funcional do Widget
        self.page().setBackgroundColor(Qt.transparent)
        self.settings().setAttribute(self.settings().WebAttribute.ShowScrollBars, False)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # A estilização HTML agora vem do arquivo de estilos
        full_html = get_plotly_html_wrapper(fig)
        self.setHtml(full_html)

class PageDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = DashboardController()
        self.setWindowTitle("Dashboard Garantia")
        
        # Define o CSS global da tela
        self.setStyleSheet(DASHBOARD_STYLES)

        main_layout = QVBoxLayout(self) 
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # --- TOPO ---
        top_bar = QHBoxLayout()
        
        # Agora usamos ObjectName, sem CSS inline
        lbl_titulo = QLabel("Visão Geral - Indicadores")
        lbl_titulo.setObjectName("DashboardTitle")
        
        btn_refresh = QPushButton(" Atualizar")
        btn_refresh.setObjectName("btn_nav")
        btn_refresh.setIcon(qta.icon('fa5s.sync-alt', color='white'))
        btn_refresh.clicked.connect(self.carregar_dados)

        top_bar.addWidget(lbl_titulo)
        top_bar.addStretch()
        top_bar.addWidget(btn_refresh)
        main_layout.addLayout(top_bar)

        # --- GRID 2x2 ---
        self.grid = QGridLayout()
        self.grid.setSpacing(20)
        # Stretches iguais para distribuição 2x2
        for i in range(2):
            self.grid.setColumnStretch(i, 1)
            self.grid.setRowStretch(i, 1)

        main_layout.addLayout(self.grid)
        
        self.carregar_dados()

    def carregar_dados(self):
        # Limpa widgets anteriores
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        kpis = self.controller.get_kpis()
        
        # Criação dos Gráficos
        # Nota: A View monta os dados, mas o estilo final é aplicado pelas helpers
        
        # 1. Financeiro
        fig1 = self.criar_grafico_financeiro(kpis.comparativo_financeiro)
        self.grid.addWidget(self.criar_card("Valor Recebido x Valor Retornado (R$)", fig1), 0, 0)

        # 2. Status
        fig2 = self.criar_grafico_status(kpis.status_data)
        self.grid.addWidget(self.criar_card("Distribuição de Status", fig2), 0, 1)

        # 3. Entrada
        fig3 = self.criar_grafico_entrada(kpis.entrada_mensal)
        self.grid.addWidget(self.criar_card("Itens Recebidos por Mês (Qtd x R$)", fig3), 1, 0)

        # 4. Velocímetro
        fig4 = self.criar_grafico_defasagem(kpis.gap_cronologico)
        self.grid.addWidget(self.criar_card("Dias de Atraso (Recebimento vs Hoje)", fig4), 1, 1)

    def criar_card(self, titulo, fig):
        card = QFrame(objectName="Card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 10, 10, 10)
        
        lbl = QLabel(titulo)
        lbl.setObjectName("CardTitle")
        layout.addWidget(lbl)
        
        if fig: 
            layout.addWidget(PlotlyWidget(fig))
        else: 
            # Inline style simples para label de fallback é aceitável, ou pode criar ID
            layout.addWidget(QLabel("Sem dados", styleSheet="color: #666; font-style: italic;"))
            
        return card

    # --- LÓGICA DE DATA (Helper de Visualização) ---
    def formatar_data_pt(self, data_iso):
        """Converte '2025-12' para 'Dez/25'."""
        if not data_iso or '-' not in str(data_iso): return str(data_iso)
        try:
            parts = str(data_iso).split('-')
            if len(parts) < 2: return data_iso
            meses = {'01': 'Jan', '02': 'Fev', '03': 'Mar', '04': 'Abr', '05': 'Mai', '06': 'Jun',
                     '07': 'Jul', '08': 'Ago', '09': 'Set', '10': 'Out', '11': 'Nov', '12': 'Dez'}
            return f"{meses.get(parts[1], parts[1])}/{parts[0][2:] if len(parts[0]) == 4 else parts[0]}"
        except:
            return data_iso

    # --- MONTAGEM DOS GRÁFICOS (Estrutura de Dados) ---
    
    def criar_grafico_financeiro(self, dados):
        if not dados: return None
        meses = [self.formatar_data_pt(d.mes) for d in dados]
        rec = [d.valor_recebido for d in dados]
        ret = [d.valor_retornado for d in dados]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=meses, y=rec, name="Recebido (R$)",
            marker_color=CHART_BLUE_PRIMARY, opacity=0.7,
            hovertemplate='R$ %{y:,.2f}'
        ))
        fig.add_trace(go.Scatter(
            x=meses, y=ret, name="Retornado (R$)",
            line=dict(color=COLOR_DANGER, width=3), mode='lines+markers',
            hovertemplate='R$ %{y:,.2f}'
        ))
        fig.update_xaxes(type='category')
        fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        
        # APLICA O TEMA EXTERNO
        return apply_chart_theme(fig)

    def criar_grafico_status(self, dados):
        if not dados: return None
        labels = [d.status for d in dados]
        values = [d.qtd for d in dados]
        colors_map = {'Procedente': COLOR_DANGER, 'Improcedente': COLOR_SUCCESS, 'Pendente': COLOR_WARNING}
        colors = [colors_map.get(l, COLOR_TEXT_DIM) for l in labels]

        fig = go.Figure(data=[go.Pie(
            labels=labels, values=values, hole=.5, marker=dict(colors=colors),
            textinfo='percent+label', textfont=dict(color='white')
        )])
        fig.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.1))
        
        # APLICA O TEMA EXTERNO
        return apply_chart_theme(fig)

    def criar_grafico_entrada(self, dados):
        if not dados: return None
        meses = [self.formatar_data_pt(d.mes) for d in dados]
        qtds = [d.qtd for d in dados]
        valores = [d.valor for d in dados]

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Bar(
            x=meses, y=qtds, name="Qtd",
            marker_color=CHART_INDIGO, opacity=0.8
        ), secondary_y=False)
        fig.add_trace(go.Scatter(
            x=meses, y=valores, name="Valor (R$)",
            line=dict(color=CHART_LINE_HIGHLIGHT, width=3), mode='lines+markers'
        ), secondary_y=True)

        fig.update_xaxes(type='category')
        fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        fig.update_yaxes(showgrid=False, secondary_y=False)
        fig.update_yaxes(showgrid=False, secondary_y=True)
        
        # APLICA O TEMA EXTERNO
        return apply_chart_theme(fig)

    def criar_grafico_defasagem(self, valor_dias):
        if valor_dias is None: return None
        META = 2.0 
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = valor_dias,
            delta = {
                'reference': META, 'position': "top",
                'increasing': {'color': COLOR_DANGER}, 
                'decreasing': {'color': COLOR_SUCCESS} 
            },
            title = {
                'text': "Idade da Nota Mais Recente", 
                'font': {'size': 14, 'color': COLOR_TEXT_DIM}
            },
            gauge = {
                'axis': {'range': [0, 20], 'tickwidth': 1, 'tickcolor': COLOR_TEXT},
                'bar': {'color': CHART_NEON_BLUE},
                'bgcolor': "rgba(0,0,0,0)",
                'borderwidth': 2,
                'bordercolor': COLOR_CARD_BORDER,
                'steps': [
                    {'range': [0, 3], 'color': "rgba(72, 187, 120, 0.2)"},
                    {'range': [3, 7], 'color': "rgba(236, 201, 75, 0.2)"},
                    {'range': [7, 20], 'color': "rgba(245, 101, 101, 0.2)"}
                ],
                'threshold': {
                    'line': {'color': "white", 'width': 4},
                    'thickness': 0.75, 'value': META
                }
            }
        ))
        
        # APLICA O TEMA EXTERNO
        return apply_chart_theme(fig)