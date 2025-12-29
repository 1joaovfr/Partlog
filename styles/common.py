# styles/common.py
from styles.theme import *

# --- FUNÇÃO PARA O DATE EDIT (Para injetar o ícone) ---
def get_date_edit_style(icon_path=""):
    """
    Retorna o estilo do QDateEdit. 
    Se icon_path for passado, usa como seta. Se não, usa estilo padrão.
    """
    arrow_style = ""
    if icon_path:
        arrow_style = f'image: url("{icon_path}"); width: 14px; height: 14px;'

    return f"""
    QDateEdit {{
        background-color: {COLOR_INPUT_BG};
        border: 1px solid {COLOR_INPUT_BORDER};
        border-radius: 4px;
        padding: 6px;
        color: {COLOR_TEXT};
        font-size: 13px;
    }}
    QDateEdit:focus {{ border: 1px solid {COLOR_FOCUS}; background-color: #1a202c; }}
    QDateEdit::drop-down {{
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 25px;
        border-left: 1px solid {COLOR_INPUT_BORDER};
        background-color: {COLOR_INPUT_BG};
        border-top-right-radius: 4px;
        border-bottom-right-radius: 4px;
    }}
    QDateEdit::down-arrow {{
        {arrow_style}
    }}
    /* O Popup do Calendário herda o estilo do QCalendarWidget abaixo */
    """

# --- CSS UNIVERSAL (Aplica em todo o sistema) ---
COMMON_STYLES = f"""
/* --- BASE --- */
QWidget {{
    background-color: {COLOR_BACKGROUND};
    color: {COLOR_TEXT};
    font-family: 'Segoe UI', sans-serif;
    font-size: 13px;
}}

/* Força o fundo dos Cards */
QFrame#FormCard, QFrame#Card {{
    background-color: {COLOR_CARD_BG};
    border-radius: 8px;
    border: 1px solid {COLOR_CARD_BORDER};
}}

/* --- LABELS --- */
/* Define background transparente para herdar a cor do pai (seja Card ou Janela) */
QLabel {{
    background-color: transparent;
    color: {COLOR_TEXT_DIM};
    font-weight: 500;
}}
/* Títulos de Seção */
QLabel#SectionTitle {{
    color: #8ab4f8;
    background-color: transparent; /* Garante que não fique cinza */
    font-size: 15px;
    font-weight: bold;
    padding-bottom: 5px;
    border-bottom: 1px solid {COLOR_CARD_BORDER};
}}

/* --- INPUTS GERAIS --- */
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
    background-color: {COLOR_INPUT_BG};
    border: 1px solid {COLOR_INPUT_BORDER};
    border-radius: 4px;
    padding: 6px;
    color: {COLOR_TEXT};
}}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
    border: 1px solid {COLOR_FOCUS};
    background-color: #1a202c;
}}
QLineEdit:read-only {{
    background-color: #141820;
    color: #718096;
    border: 1px solid #252b38;
}}

/* --- TABELAS PADRONIZADAS --- */
QTableWidget {{
    background-color: {COLOR_TABLE_BG};
    alternate-background-color: {COLOR_TABLE_ALT};
    gridline-color: {COLOR_CARD_BORDER};
    border: 1px solid {COLOR_CARD_BORDER};
    border-radius: 4px;
}}
QHeaderView::section {{
    background-color: {COLOR_HEADER_BG};
    color: {COLOR_TEXT};
    padding: 6px;
    border: 1px solid {COLOR_CARD_BORDER};
    font-weight: bold;
    text-transform: uppercase;
}}
/* Seleção */
QTableWidget::item:selected {{
    background-color: {COLOR_SELECTION};
    color: white;
}}
/* Hover na linha (Remove padrão do SO) */
QTableWidget::item:hover {{
    background-color: {COLOR_HOVER_ROW};
}}

/* --- SCROLLBARS PERSONALIZADAS --- */
QScrollBar:vertical {{
    background: {COLOR_INPUT_BG};
    width: 8px;
    margin: 0px;
}}
QScrollBar::handle:vertical {{
    background-color: {COLOR_FOCUS};
    min-height: 30px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical:hover {{ background-color: {COLOR_INFO}; }}
QScrollBar:horizontal {{
    background: {COLOR_INPUT_BG};
    height: 8px;
    margin: 0px;
}}
QScrollBar::handle:horizontal {{
    background-color: {COLOR_FOCUS};
    min-width: 30px;
    border-radius: 4px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px; height: 0px; background: none;
}}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical,
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
    background: none;
}}

/* --- CALENDÁRIO POP-UP (QDateEdit Popup) --- */
QCalendarWidget QWidget {{
    background-color: {COLOR_CALENDAR_BG};
    alternate-background-color: {COLOR_TABLE_ALT};
    color: {COLOR_TEXT};
}}
/* Navegação do Calendário (Botões de mês/ano) */
QCalendarWidget QToolButton {{
    color: {COLOR_TEXT};
    background-color: {COLOR_CALENDAR_BG};
    icon-size: 20px;
    border: none;
    margin: 2px;
}}
QCalendarWidget QToolButton:hover {{
    background-color: {COLOR_HOVER_ROW};
    border-radius: 3px;
}}
/* Menu de seleção de mês (Drop down) */
QCalendarWidget QMenu {{
    background-color: {COLOR_CALENDAR_BG};
    color: {COLOR_TEXT};
    border: 1px solid {COLOR_CARD_BORDER};
}}
/* Dias selecionados e SpinBox do ano */
QCalendarWidget QAbstractItemView:enabled {{
    color: {COLOR_TEXT};
    background-color: {COLOR_INPUT_BG};
    selection-background-color: {COLOR_SELECTION};
    selection-color: white;
}}
QCalendarWidget QSpinBox {{
    background-color: {COLOR_INPUT_BG};
    color: {COLOR_TEXT};
    border: 1px solid {COLOR_INPUT_BORDER};
    border-radius: 0px;
}}
QCalendarWidget QAbstractItemView:disabled {{ color: #4a5568; }}

/* --- BOTÕES GENÉRICOS --- */
QPushButton {{ padding: 8px 15px; border-radius: 4px; font-weight: bold; }}
QPushButton#btn_primary {{
    background-color: {COLOR_PRIMARY}; color: white; border: 1px solid #1b5e20;
}}
QPushButton#btn_primary:hover {{ background-color: {COLOR_PRIMARY_HOVER}; }}
QPushButton#btn_secondary {{
    background-color: {COLOR_SECONDARY}; color: {COLOR_TEXT_DIM}; border: 1px solid {COLOR_SECONDARY_BORDER};
}}
QPushButton#btn_secondary:hover {{ background-color: {COLOR_CARD_BORDER}; color: white; }}
"""