from styles.common import COMMON_STYLES
from styles.theme import *

RETORNO_STYLES = COMMON_STYLES + f"""

/* --- CORREÇÃO DE FUNDO (#1b212d) --- */
QCheckBox, QRadioButton {{
    background-color: #1b212d;
    spacing: 8px;
    color: {COLOR_TEXT};
    font-weight: 500;
}}

/* --- ESTILO DOS INDICADORES (Bolinhas e Quadrados) --- */
QRadioButton::indicator {{
    width: 16px;
    height: 16px;
    border-radius: 9px;
    border: 1px solid {COLOR_INPUT_BORDER};
    background-color: {COLOR_INPUT_BG};
}}
QRadioButton::indicator:hover {{ border-color: {COLOR_FOCUS}; }}
QRadioButton::indicator:checked {{
    background-color: {COLOR_FOCUS};
    border: 1px solid {COLOR_FOCUS};
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border-radius: 3px;
    border: 1px solid {COLOR_INPUT_BORDER};
    background-color: {COLOR_INPUT_BG};
}}
QCheckBox::indicator:hover {{ border-color: {COLOR_FOCUS}; }}
QCheckBox::indicator:checked {{
    background-color: {COLOR_FOCUS};
    border: 1px solid {COLOR_FOCUS};
}}

/* --- TABELA (QTableView) --- */
QTableView::indicator {{
    width: 18px;
    height: 18px;
    border: 1px solid {COLOR_INPUT_BORDER};
    background-color: {COLOR_INPUT_BG};
}}
QTableView::indicator:hover {{ border: 1px solid {COLOR_FOCUS}; }}
QTableView::indicator:checked {{
    background-color: {COLOR_FOCUS};
    border: 1px solid {COLOR_FOCUS};
}}

/* --- LABELS --- */
QLabel {{
    background-color: transparent; 
    color: {COLOR_TEXT};
}}
QLabel#SectionTitle {{
    color: #8ab4f8;
    border-bottom: 1px solid {COLOR_CARD_BORDER};
    padding-bottom: 5px;
    font-weight: bold;
}}

/* --- TABELA CONFIG --- */
QTableWidget {{
    selection-background-color: {COLOR_SELECTION};
    gridline-color: {COLOR_CARD_BORDER};
    border: none; 
    background-color: {COLOR_TABLE_BG};
}}
/* Ajuste dos cantos superiores da tabela dentro do card */
QHeaderView::section:first {{ border-top-left-radius: 6px; }}
QHeaderView::section:last {{ border-top-right-radius: 6px; }}
QTableWidget::item {{ padding: 5px; }}
"""