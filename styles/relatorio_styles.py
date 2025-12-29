from styles.common import COMMON_STYLES
from styles.theme import *

RELATORIO_STYLES = COMMON_STYLES + f"""
/* --- ESPECÍFICO DE RELATÓRIOS --- */

/* Popup Pequeno (Dialog de Filtro/Exportação) */
QDialog {{ 
    background-color: {COLOR_CARD_BG}; 
    border: 1px solid {COLOR_FOCUS}; 
    border-radius: 4px; 
}}

/* Botão Confirmar Compacto (usado dentro de calendários ou popups) */
QPushButton#btn_confirmar {{ 
    background-color: {COLOR_PRIMARY}; 
    color: white; 
    border: none; 
    padding: 6px; 
    border-radius: 3px; 
    font-weight: bold; 
    font-size: 12px;
}}
QPushButton#btn_confirmar:hover {{ background-color: {COLOR_PRIMARY_HOVER}; }}

/* Botão Excel (Cabeçalho) */
QPushButton#btn_excel {{ 
    background-color: transparent; 
    border: none; 
    padding: 5px; 
}}
QPushButton#btn_excel:hover {{ 
    background-color: {COLOR_CARD_BORDER}; 
    border-radius: 4px; 
}}

/* --- PAGINAÇÃO --- */
QPushButton#btn_pag {{ 
    background-color: {COLOR_FOCUS}; 
    color: white; 
    border: 1px solid {COLOR_SECONDARY_BORDER}; 
}}
QPushButton#btn_pag:hover {{ background-color: {COLOR_INFO}; }}

QPushButton#btn_pag:disabled {{ 
    background-color: {COLOR_INPUT_BG}; 
    color: #4a5568; 
    border: 1px solid {COLOR_INPUT_BORDER}; 
}}

QLabel#lbl_pag {{ 
    color: {COLOR_TEXT_DIM}; 
    background-color: transparent; 
    font-weight: bold; 
    font-size: 13px; 
}}
"""