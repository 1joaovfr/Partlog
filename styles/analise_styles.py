from styles.common import COMMON_STYLES
from styles.theme import *

# Caminhos dos ícones (gerados no main.py)
ICON_ARROW_DOWN = "views/icons/arrow_down.png"
ICON_ARROW_UP   = "views/icons/arrow_up.png"

# --- CSS PARA COMBOBOX MODERNO E REATIVO ---
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
    border-left: 0px solid {COLOR_INPUT_BORDER}; /* Remove divisória para ficar clean */
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
/* O seletor :on é ativado quando o popup está visível */
QComboBox::down-arrow:on {{
    image: url("{ICON_ARROW_UP}");
    width: 12px;
    height: 12px;
    top: 1px; /* Leve deslocamento para efeito visual */
}}

/* Item selecionado na lista dropdown (Popup) */
QComboBox QAbstractItemView {{
    border: 1px solid {COLOR_CARD_BORDER};
    selection-background-color: {COLOR_FOCUS};
    background-color: {COLOR_INPUT_BG};
    color: {COLOR_TEXT};
    outline: 0px; /* Remove pontilhado de foco */
}}
"""

# --- CSS PARA LABELS DE STATUS ---
LABELS_STATUS = f"""
/* Status: PROCEDENTE (Verde) */
QLabel#StatusProcedente {{ 
    color: {COLOR_SUCCESS}; 
    font-weight: bold; 
    background-color: {COLOR_CARD_BG}; 
    border: 1px solid #2f855a; 
    border-radius: 6px; /* Cantos arredondados */
}}

/* Status: IMPROCEDENTE (Vermelho) */
QLabel#StatusImprocedente {{ 
    color: {COLOR_DANGER}; 
    font-weight: bold; 
    background-color: {COLOR_CARD_BG}; 
    border: 1px solid #c53030; 
    border-radius: 6px; /* Cantos arredondados */
}}

/* Status: NEUTRO/AGUARDANDO (Cinza) */
QLabel#StatusNeutro {{ 
    color: {COLOR_TEXT_DIM}; 
    background-color: {COLOR_CARD_BG}; 
    border: 1px solid {COLOR_CARD_BORDER}; 
    border-radius: 6px; /* Cantos arredondados */
}}
"""

# --- JUNÇÃO FINAL DO ESTILO ---
ANALISE_STYLES = COMMON_STYLES + COMBOBOX_MODERNO + LABELS_STATUS