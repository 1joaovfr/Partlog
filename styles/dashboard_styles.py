from styles.common import COMMON_STYLES
from styles.theme import *
import plotly.graph_objects as go

# --- CSS WIDGETS (Qt) ---
DASHBOARD_STYLES = COMMON_STYLES + f"""
/* --- ESPECÍFICO DO DASHBOARD --- */

QFrame#Card {{
    background-color: {COLOR_CARD_BG};
    border-radius: 8px;
    border: 1px solid {COLOR_CARD_BORDER};
}}

QLabel#CardTitle {{ 
    background-color: transparent; 
    color: {COLOR_TEXT_DIM}; 
    font-size: 14px; 
    font-weight: bold; 
    padding-bottom: 5px; 
    border-bottom: 1px solid {COLOR_CARD_BORDER}; 
}}

/* NOVO: Estilo para o Título Principal que estava inline na View */
QLabel#DashboardTitle {{
    font-size: 20px; 
    font-weight: bold; 
    color: {CHART_NEON_BLUE}; 
    background: transparent;
}}

QPushButton#btn_nav {{ 
    background-color: #2c5282; 
    color: white; 
    border: 1px solid #2a4365; 
    padding: 8px 15px; 
    border-radius: 4px; 
    font-weight: bold; 
}}
QPushButton#btn_nav:hover {{ 
    background-color: {CHART_BLUE_PRIMARY}; 
    border: 1px solid {CHART_BLUE_PRIMARY};
}}
"""

# --- HELPERS DE ESTILO PLOTLY (Python Logic) ---
# Movemos a lógica visual que estava "sujando" a View para cá

def get_plotly_html_wrapper(fig):
    """
    Gera o HTML completo para o QWebEngineView, injetando o CSS de fundo
    para evitar o flash branco e manter a coerência do tema.
    """
    config = {'scrollZoom': False, 'displayModeBar': False, 'responsive': True}
    html_content = fig.to_html(include_plotlyjs='cdn', full_html=False, config=config)
    
    return f"""
    <html>
        <head>
            <style>
                body {{ 
                    background-color: {COLOR_CARD_BG}; 
                    margin: 0; 
                    padding: 0; 
                    overflow: hidden; 
                }}
            </style>
        </head>
        <body>{html_content}</body>
    </html>
    """

def apply_chart_theme(fig):
    """
    Aplica as cores, fontes e configurações de layout padrão do sistema
    ao objeto Figure do Plotly.
    """
    fig.update_layout(
        paper_bgcolor=COLOR_CARD_BG, 
        plot_bgcolor=COLOR_CARD_BG,
        font_color=COLOR_TEXT, 
        font_family="Segoe UI",
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis=dict(showgrid=False, linecolor=COLOR_CARD_BORDER),
        yaxis=dict(showgrid=False, zeroline=False),
        hovermode="x unified"
    )
    return fig