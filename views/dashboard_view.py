import sys
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                               QLabel, QFrame, QPushButton, QSizePolicy)
from PySide6.QtCore import Qt
from PySide6.QtWebEngineWidgets import QWebEngineView 
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import qtawesome as qta

from controllers import DashboardController

# --- Estilos ---
from styles.dashboard_styles import DASHBOARD_STYLES
from styles.theme import (
    COLOR_CARD_BG, COLOR_CARD_BORDER, COLOR_TEXT, COLOR_TEXT_DIM,
    COLOR_SUCCESS, COLOR_DANGER, COLOR_WARNING,
    CHART_BLUE_PRIMARY, CHART_CYAN_TEAL, CHART_INDIGO, 
    CHART_NEON_BLUE, CHART_LINE_HIGHLIGHT, COLOR_INFO
)

class PlotlyWidget(QWebEngineView):
    def __init__(self, fig):
        super().__init__()
        self.page().setBackgroundColor(Qt.transparent)
        self.settings().setAttribute(self.settings().WebAttribute.ShowScrollBars, False)
        config = {'scrollZoom': False, 'displayModeBar': False, 'responsive': True}
        html = fig.to_html(include_plotlyjs='cdn', full_html=False, config=config)
        
        full_html = f"""<html><head><style>
        body {{ background-color: {COLOR_CARD_BG}; margin: 0; padding: 0; overflow: hidden; }}
        </style></head><body>{html}</body></html>"""
        self.setHtml(full_html)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

class PageDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = DashboardController()
        self.setWindowTitle("Dashboard Garantia")
        self.setStyleSheet(DASHBOARD_STYLES)

        main_layout = QVBoxLayout(self) 
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # --- TOPO ---
        top_bar = QHBoxLayout()
        lbl_titulo = QLabel("Visão Geral - Indicadores")
        lbl_titulo.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {CHART_NEON_BLUE}; background: transparent;")
        
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
        self.grid.setColumnStretch(0, 1)
        self.grid.setColumnStretch(1, 1)
        self.grid.setRowStretch(0, 1)
        self.grid.setRowStretch(1, 1)

        main_layout.addLayout(self.grid)
        
        self.carregar_dados()

    def carregar_dados(self):
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        kpis = self.controller.get_kpis()
        
        # 1. Financeiro
        fig1 = self.criar_grafico_financeiro(kpis.comparativo_financeiro)
        self.grid.addWidget(self.criar_card("Valor Recebido x Valor Retornado (R$)", fig1), 0, 0)

        # 2. Status
        fig2 = self.criar_grafico_status(kpis.status_data)
        self.grid.addWidget(self.criar_card("Distribuição de Status", fig2), 0, 1)

        # 3. Entrada
        fig3 = self.criar_grafico_entrada(kpis.entrada_mensal)
        self.grid.addWidget(self.criar_card("Itens Recebidos por Mês (Qtd x R$)", fig3), 1, 0)

        # 4. Velocímetro (GAP Cronológico)
        # Passamos o novo campo do DTO
        fig4 = self.criar_grafico_defasagem(kpis.gap_cronologico)
        self.grid.addWidget(self.criar_card("Dias de Atraso (Recebimento vs Hoje)", fig4), 1, 1)

    def criar_card(self, titulo, fig):
        card = QFrame(objectName="Card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 10, 10, 10)
        lbl = QLabel(titulo)
        lbl.setObjectName("CardTitle")
        layout.addWidget(lbl)
        if fig: layout.addWidget(PlotlyWidget(fig))
        else: layout.addWidget(QLabel("Sem dados", styleSheet="color: #666; font-style: italic;"))
        return card

    # --- LÓGICA DE DATA ---
    def formatar_data_pt(self, data_iso):
        """Converte '2025-12' para 'Dez/25'."""
        if not data_iso or '-' not in str(data_iso): return str(data_iso)
        try:
            parts = str(data_iso).split('-')
            if len(parts) < 2: return data_iso
            ano, mes = parts[0], parts[1]
            meses = {'01': 'Jan', '02': 'Fev', '03': 'Mar', '04': 'Abr', '05': 'Mai', '06': 'Jun',
                     '07': 'Jul', '08': 'Ago', '09': 'Set', '10': 'Out', '11': 'Nov', '12': 'Dez'}
            nome_mes = meses.get(mes, mes)
            ano_curto = ano[2:] if len(ano) == 4 else ano
            return f"{nome_mes}/{ano_curto}"
        except:
            return data_iso

    # --- GRÁFICOS ---

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
        self._apply_theme(fig)
        fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        return fig

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
        self._apply_theme(fig)
        fig.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.1))
        return fig

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
        self._apply_theme(fig)
        fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        fig.update_yaxes(showgrid=False, secondary_y=False)
        fig.update_yaxes(showgrid=False, secondary_y=True)
        return fig

    def criar_grafico_defasagem(self, valor_dias):
        """
        Calcula a 'Recência' da informação.
        Valor mostrado = Hoje - DataRecebimento da Última Nota Lançada.
        """
        if valor_dias is None: return None
        
        # Meta: O ideal é que a equipe esteja processando itens que chegaram a no máximo 2 dias.
        META = 2.0 

        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = valor_dias,
            
            # ACELERADOR:
            # increasing color = Vermelho (Pois se o gap sobe, estamos atrasando mais)
            # decreasing color = Verde (Pois se o gap desce, estamos alcançando o dia atual)
            delta = {
                'reference': META, 
                'position': "top",
                'increasing': {'color': COLOR_DANGER}, 
                'decreasing': {'color': COLOR_SUCCESS} 
            },
            
            title = {
                'text': "Idade da Nota Mais Recente", 
                'font': {'size': 14, 'color': COLOR_TEXT_DIM}
            },
            
            gauge = {
                # Faixa até 20 dias para cobrir o cenário de atraso
                'axis': {'range': [0, 20], 'tickwidth': 1, 'tickcolor': COLOR_TEXT},
                'bar': {'color': CHART_NEON_BLUE}, # Cor do ponteiro
                'bgcolor': "rgba(0,0,0,0)",
                'borderwidth': 2,
                'bordercolor': COLOR_CARD_BORDER,
                
                # Faixas de Cores
                'steps': [
                    {'range': [0, 3], 'color': "rgba(72, 187, 120, 0.2)"},   # 0-3 dias: Ótimo (Tempo Real)
                    {'range': [3, 7], 'color': "rgba(236, 201, 75, 0.2)"},   # 3-7 dias: Atenção (Semanal)
                    {'range': [7, 20], 'color': "rgba(245, 101, 101, 0.2)"}  # >7 dias: Crítico
                ],
                
                # Linha da Meta
                'threshold': {
                    'line': {'color': "white", 'width': 4},
                    'thickness': 0.75,
                    'value': META
                }
            }
        ))
        
        self._apply_theme(fig)
        return fig

    def _apply_theme(self, fig):
        fig.update_layout(
            paper_bgcolor=COLOR_CARD_BG, plot_bgcolor=COLOR_CARD_BG,
            font_color=COLOR_TEXT, font_family="Segoe UI",
            margin=dict(l=10, r=10, t=30, b=10),
            xaxis=dict(showgrid=False, linecolor=COLOR_CARD_BORDER),
            yaxis=dict(showgrid=False, zeroline=False),
            hovermode="x unified"
        )