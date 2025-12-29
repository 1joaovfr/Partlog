from styles.common import COMMON_STYLES
from styles.theme import *

# Herda o comum e adiciona o específico
DASHBOARD_STYLES = COMMON_STYLES + f"""
/* --- ESPECÍFICO DO DASHBOARD --- */

/* O Card do Dashboard é apenas visual, sem borda de formulário se preferir, 
   ou herdando o padrão. Aqui reforçamos o padrão. */
QFrame#Card {{
    background-color: {COLOR_CARD_BG};
    border-radius: 8px;
    border: 1px solid {COLOR_CARD_BORDER};
}}

/* Títulos dos Cards (Pequenos) */
QLabel#CardTitle {{ 
    background-color: transparent; 
    color: {COLOR_TEXT_DIM}; 
    font-size: 14px; 
    font-weight: bold; 
    padding-bottom: 5px; 
    border-bottom: 1px solid {COLOR_CARD_BORDER}; 
}}

/* Botão de Navegação / Atualizar (Topo) */
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