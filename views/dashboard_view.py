import sys
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                               QLabel, QFrame, QPushButton, QSizePolicy)
from PySide6.QtCore import Qt
from PySide6.QtWebEngineWidgets import QWebEngineView 
import plotly.graph_objects as go
import qtawesome as qta

from controllers import DashboardController
from styles.dashboard_styles import (
    DASHBOARD_STYLES, apply_chart_theme, get_plotly_html_wrapper
)
from styles.theme import (
    COLOR_DANGER, COLOR_SUCCESS, COLOR_WARNING, COLOR_TEXT_DIM,
    CHART_BLUE_PRIMARY, CHART_NEON_BLUE, COLOR_CARD_BORDER, COLOR_TEXT
)

class PlotlyWidget(QWebEngineView):
    def __init__(self, fig):
        super().__init__()
        self.page().setBackgroundColor(Qt.transparent)
        self.settings().setAttribute(self.settings().WebAttribute.ShowScrollBars, False)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        full_html = get_plotly_html_wrapper(fig)
        self.setHtml(full_html)

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
        for i in range(2):
            self.grid.setColumnStretch(i, 1)
            self.grid.setRowStretch(i, 1)

        main_layout.addLayout(self.grid)
        self.carregar_dados()

    def carregar_dados(self):
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        kpis = self.controller.get_kpis()
        
        # 1. Financeiro (Safra)
        fig1 = self.criar_grafico_financeiro(kpis.comparativo_financeiro)
        self.grid.addWidget(self.criar_card("Qualidade da Safra (Recebido x Devolvido)", fig1), 0, 0)

        # 2. Status
        fig2 = self.criar_grafico_status(kpis.status_data)
        self.grid.addWidget(self.criar_card("Distribuição de Status", fig2), 0, 1)

        # 3. Volume Financeiro de Retorno
        fig3 = self.criar_grafico_retorno_mensal(kpis.historico_retornos)
        self.grid.addWidget(self.criar_card("Valor Retornado (Data Emissão NF)", fig3), 1, 0)

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
        if fig: layout.addWidget(PlotlyWidget(fig))
        else: layout.addWidget(QLabel("Sem dados", styleSheet="color: #666; font-style: italic;"))
        return card

    # --- HELPER FORMATACAO ---
    def formatar_data_pt(self, data_iso):
        if not data_iso or '-' not in str(data_iso): return str(data_iso)
        try:
            parts = str(data_iso).split('-')
            if len(parts) < 2: return data_iso
            meses = {'01': 'Jan', '02': 'Fev', '03': 'Mar', '04': 'Abr', '05': 'Mai', '06': 'Jun',
                     '07': 'Jul', '08': 'Ago', '09': 'Set', '10': 'Out', '11': 'Nov', '12': 'Dez'}
            return f"{meses.get(parts[1], parts[1])}/{parts[0][2:] if len(parts[0]) == 4 else parts[0]}"
        except:
            return data_iso

    # --- GRÁFICOS ---

    def criar_grafico_financeiro(self, dados):
        if not dados: return None
        meses = [self.formatar_data_pt(d.mes) for d in dados]
        rec = [d.valor_recebido for d in dados]
        ret = [d.valor_retornado for d in dados]

        fig = go.Figure()
        
        # Barra Azul (Recebido)
        fig.add_trace(go.Bar(
            x=meses, 
            y=rec, 
            name="Recebido (R$)", 
            marker_color=CHART_BLUE_PRIMARY, 
            opacity=0.6, # Leve transparência para destacar a linha
            hovertemplate='Mês: %{x}<br>Recebido: R$ %{y:,.2f}<extra></extra>'
        ))
        
        # Linha Neon/Ciano (Retornado) - Substituindo o Vermelho
        fig.add_trace(go.Scatter(
            x=meses, 
            y=ret, 
            name="Devolvido da Safra (R$)", 
            # COR ALTERADA AQUI:
            line=dict(color=CHART_NEON_BLUE, width=4), 
            mode='lines+markers',
            marker=dict(size=8, symbol='circle', color='white', line=dict(width=2, color=CHART_NEON_BLUE)),
            hovertemplate='Mês: %{x}<br>Devolvido: R$ %{y:,.2f}<extra></extra>'
        ))
        
        fig.update_xaxes(type='category')
        fig.update_layout(
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            separators=",." 
        )
        return apply_chart_theme(fig)

    def criar_grafico_retorno_mensal(self, dados):
        if not dados: return None
        meses = [self.formatar_data_pt(d.mes) for d in dados]
        valores = [d.valor for d in dados]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=meses, 
            y=valores, 
            name="Total Retornado (R$)",
            # COR ALTERADA AQUI (Mesma da linha do outro gráfico):
            marker_color=CHART_NEON_BLUE,
            opacity=0.9,
            hovertemplate='Mês: %{x}<br>Total: R$ %{y:,.2f}<extra></extra>'
        ))
        
        fig.update_xaxes(type='category')
        fig.update_layout(
            showlegend=False,
            separators=",." 
        )
        return apply_chart_theme(fig)

    def criar_grafico_status(self, dados):
        """Gráfico de Pizza com Valor R$ na fatia e Legenda Lateral"""
        if not dados: return None
        
        labels = [d.status for d in dados]
        qtds = [d.qtd for d in dados]      
        valores = [d.valor for d in dados] 
        
        colors_map = {'Procedente': COLOR_DANGER, 'Improcedente': COLOR_SUCCESS, 'Pendente': COLOR_WARNING}
        colors = [colors_map.get(l, COLOR_TEXT_DIM) for l in labels]

        fig = go.Figure(data=[go.Pie(
            labels=labels, 
            values=valores, 
            hole=.6, # Buraco um pouco maior para ficar elegante
            marker=dict(colors=colors), 
            
            textinfo='percent', 
            textfont=dict(color='white'),
            
            customdata=qtds,
            hovertemplate='<b>%{label}</b><br>R$ %{value:,.2f}<br>Qtd: %{customdata}<extra></extra>'
        )])

        # Legenda posicionada à esquerda
        fig.update_layout(
            separators=",.", 
            margin=dict(l=0, r=0, t=20, b=20),
            legend=dict(
                orientation="v",      
                yanchor="middle",     
                y=0.5, 
                xanchor="left",       
                x=-0.2                
            )
        )
        return apply_chart_theme(fig)

    def criar_grafico_defasagem(self, valor_dias):
        if valor_dias is None: return None
        META = 2.0 
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = valor_dias,
            delta = {'reference': META, 'position': "top", 'increasing': {'color': COLOR_DANGER}, 'decreasing': {'color': COLOR_SUCCESS}},
            title = {'text': "Idade da Nota Mais Recente", 'font': {'size': 14, 'color': COLOR_TEXT_DIM}},
            gauge = {
                'axis': {'range': [0, 20], 'tickwidth': 1, 'tickcolor': COLOR_TEXT},
                'bar': {'color': CHART_NEON_BLUE},
                'bgcolor': "rgba(0,0,0,0)",
                'borderwidth': 2,
                'bordercolor': COLOR_CARD_BORDER,
                'steps': [
                    {'range': [0, 3], 'color': "rgba(72, 187, 120, 0.2)"}, # Verde suave
                    {'range': [3, 7], 'color': "rgba(236, 201, 75, 0.2)"},  # Amarelo suave
                    {'range': [7, 20], 'color': "rgba(245, 101, 101, 0.2)"} # Vermelho suave
                ],
                'threshold': {'line': {'color': "white", 'width': 4}, 'thickness': 0.75, 'value': META}
            }
        ))
        return apply_chart_theme(fig)