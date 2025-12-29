from styles.common import COMMON_STYLES, get_date_edit_style
from styles.theme import *

# 1. Caminho do ícone atualizado (note que usei barras normais '/' que funcionam melhor no Python)
DATE_EDIT_CSS = get_date_edit_style("views/icons/temp_calendar_icon.png")

LANCAMENTO_STYLES = COMMON_STYLES + DATE_EDIT_CSS + f"""
/* ESPECÍFICO DE LANÇAMENTO */

/* 4. Ajuste do Checkbox: background transparent para pegar a cor do container pai */
QCheckBox {{ 
    color: {COLOR_TEXT}; 
    spacing: 8px; 
    background-color: transparent; 
}}
QCheckBox::indicator {{ 
    width: 18px; 
    height: 18px; 
    border-radius: 3px; 
    border: 1px solid {COLOR_INPUT_BORDER}; 
    background: {COLOR_INPUT_BG}; 
}}
QCheckBox::indicator:checked {{ 
    background-color: {COLOR_FOCUS}; 
    border: 1px solid {COLOR_FOCUS}; 
}}

/* 3. Remover botões +/- dos SpinBoxes e DoubleSpinBoxes */
QSpinBox::up-button, QSpinBox::down-button,
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
    width: 0px;
    border-width: 0px;
}}

/* Ajuste visual para quando o botão some, o texto não ficar colado na borda */
QSpinBox, QDoubleSpinBox {{
    padding-right: 0px; 
}}

QPushButton#btn_add {{
    background-color: {COLOR_FOCUS}; color: white; border: none; padding: 8px 15px; border-radius: 4px; font-weight: bold;
}}
QPushButton#btn_add:hover {{ background-color: {COLOR_INFO}; }}
"""