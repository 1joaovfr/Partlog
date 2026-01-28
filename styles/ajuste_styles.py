from styles.common import COMMON_STYLES, get_date_edit_style
from styles.theme import *

# Reutiliza o ícone de calendário se quiser
DATE_EDIT_CSS = get_date_edit_style("views/icons/temp_calendar_icon.png")

AJUSTE_STYLES = COMMON_STYLES + DATE_EDIT_CSS + f"""
/* --- ESTILOS DO POPUP DE EDIÇÃO --- */
QDialog {{
    background-color: {COLOR_CARD_BG};
}}

QLabel#lbl_aviso {{
    color: #e53e3e; /* Vermelho erro */
    font-weight: bold;
    font-size: 12px;
}}

QLabel#lbl_info {{
    color: {COLOR_TEXT_DIM};
    font-size: 11px;
}}

/* Campos ReadOnly (Bloqueados) */
QLineEdit[readOnly="true"], QDateEdit[readOnly="true"] {{
    background-color: {COLOR_BACKGROUND};
    color: {COLOR_TEXT_DIM};
    border: 1px solid {COLOR_INPUT_BORDER};
}}

/* Botão Excluir */
QPushButton#btn_excluir {{
    background-color: transparent;
    border: 1px solid #e53e3e;
    color: #e53e3e;
    font-weight: bold;
}}
QPushButton#btn_excluir:hover {{
    background-color: #e53e3e;
    color: white;
}}
"""