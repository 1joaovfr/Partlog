from styles.common import COMMON_STYLES
from styles.theme import *

# 1. Definição dos Ícones (Copiado da tela de Análise)
ICON_ARROW_DOWN = "views/icons/arrow_down.png"
ICON_ARROW_UP   = "views/icons/arrow_up.png"

# 2. CSS do ComboBox Moderno (Copiado da tela de Análise)
COMBOBOX_MODERNO = f"""
QComboBox {{
    background-color: {COLOR_INPUT_BG};
    border: 1px solid {COLOR_INPUT_BORDER};
    border-radius: 4px;
    padding: 5px;
    padding-left: 10px;
    padding-right: 20px; /* Espaço para a seta não ficar em cima do texto */
    color: {COLOR_TEXT};
    font-size: 13px;
}}

QComboBox:focus {{
    border: 1px solid {COLOR_FOCUS};
    background-color: #1a202c;
}}

/* Área do botão da seta (lado direito) */
QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 25px;
    border-left: 0px solid {COLOR_INPUT_BORDER};
    border-top-right-radius: 4px;
    border-bottom-right-radius: 4px;
}}

/* --- ESTADO PADRÃO (FECHADO) --- */
QComboBox::down-arrow {{
    image: url("{ICON_ARROW_DOWN}");
    width: 12px;
    height: 12px;
}}

/* --- ESTADO ATIVO (ABERTO) --- */
QComboBox::down-arrow:on {{
    image: url("{ICON_ARROW_UP}");
    width: 12px;
    height: 12px;
    top: 1px;
}}

/* Item selecionado na lista dropdown (Popup) */
QComboBox QAbstractItemView {{
    border: 1px solid {COLOR_CARD_BORDER};
    selection-background-color: {COLOR_FOCUS};
    background-color: {COLOR_INPUT_BG};
    color: {COLOR_TEXT};
    outline: 0px;
}}
"""

# 3. Integração com os estilos existentes
RETORNO_STYLES = COMMON_STYLES + COMBOBOX_MODERNO + f"""

/* --- FORÇAR TRANSPARÊNCIA NOS CONTAINERS ESPECÍFICOS --- */
QWidget#ContainerTransparente {{
    background-color: transparent;
    border: none;
}}

/* --- CHECKBOX E RADIO BUTTON --- */
/* Força fundo transparente para pegar a cor da tela */
QCheckBox, QRadioButton {{
    background-color: transparent; 
    spacing: 8px;
    color: {COLOR_TEXT};
    font-weight: 500;
    border: none;
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

/* --- LABELS GERAIS --- */
/* Garante que todas as labels soltas sejam transparentes */
QLabel {{
    background-color: transparent; 
    color: {COLOR_TEXT};
    border: none;
}}

/* --- TÍTULOS DE SEÇÃO --- */
QLabel#SectionTitle {{
    color: #8ab4f8;
    background-color: transparent;
    border-bottom: 1px solid {COLOR_CARD_BORDER};
    padding-bottom: 5px;
    font-weight: bold;
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

/* --- CONFIGURAÇÕES GERAIS DA TABELA --- */
QTableWidget {{
    selection-background-color: {COLOR_SELECTION};
    gridline-color: {COLOR_CARD_BORDER};
    border: none; 
    background-color: {COLOR_TABLE_BG};
}}
QHeaderView::section:first {{ border-top-left-radius: 6px; }}
QHeaderView::section:last {{ border-top-right-radius: 6px; }}
QTableWidget::item {{ padding: 5px; }}

/* --- SPINBOXES --- */
QSpinBox::up-button, QSpinBox::down-button,
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
    width: 0px;
    border-width: 0px;
}}
QSpinBox, QDoubleSpinBox {{
    padding-right: 0px; 
}}
"""