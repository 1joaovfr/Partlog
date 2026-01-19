import sys
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                               QComboBox, QPushButton, QFrame, QTableWidget, QTableWidgetItem, 
                               QHeaderView, QDoubleSpinBox, QMessageBox, QRadioButton, 
                               QButtonGroup, QDateEdit)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor

# Mantendo seus imports originais
from controllers.retorno_controller import RetornoController
from dtos.retorno_dto import RetornoHeaderDTO, ItemPendenteDTO
from styles.common import get_date_edit_style
from styles.retorno_styles import RETORNO_STYLES
from styles.theme import *

class PageRetorno(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = RetornoController()
        self.itens_carregados: list[ItemPendenteDTO] = []
        
        self.setStyleSheet(RETORNO_STYLES + get_date_edit_style("views/icons/temp_calendar_icon.png"))
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        self.setup_header(layout)
        self.setup_filters(layout) # Alterado
        self.setup_content_area(layout)

        # Garante o estado inicial correto
        self.atualizar_visibilidade_filtros()

    def setup_header(self, parent_layout):
        frame = QFrame(objectName="FormCard")
        vbox = QVBoxLayout(frame)
        vbox.addWidget(QLabel("DADOS DA NOTA DE RETORNO", objectName="SectionTitle"))
        
        hbox = QHBoxLayout()
        
        # --- 1. COMBOBOX (Tamanho Fixo) ---
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(["Garantia Simples", "Tratativa de Crédito", "Itens de Giro"])
        self.combo_tipo.setFixedWidth(200) # Tamanho fixo definido
        self.combo_tipo.currentIndexChanged.connect(self.atualizar_visibilidade_filtros)
        
        # --- 2. NOTA FISCAL (Tamanho Fixo igual Lançamento) ---
        self.txt_num_nota = QLineEdit(placeholderText="Nº Nota Retorno")
        self.txt_num_nota.setFixedWidth(150) # Tamanho fixo definido
        
        # --- 3. EMISSÃO (Já estava fixo) ---
        self.date_emissao = QDateEdit(calendarPopup=True, date=QDate.currentDate())
        self.date_emissao.setFixedWidth(130) 
        
        # --- 4. VALOR (Já estava fixo) ---
        self.spin_valor_retorno = QDoubleSpinBox()
        self.spin_valor_retorno.setPrefix("R$ ")
        self.spin_valor_retorno.setRange(0.00, 999999.99)
        self.spin_valor_retorno.setFixedWidth(100)
        self.spin_valor_retorno.setSpecialValueText(" ")
        self.spin_valor_retorno.setValue(0.00)
        self.spin_valor_retorno.valueChanged.connect(self.recalcular_totais)

        # Adicionando ao layout com stretch=0 (para respeitar o tamanho fixo)
        self.add_field(hbox, "Tipo de Retorno:", self.combo_tipo, 0)
        self.add_field(hbox, "Número Nota:", self.txt_num_nota, 0)
        self.add_field(hbox, "Emissão:", self.date_emissao, 0)
        self.add_field(hbox, "Valor Total:", self.spin_valor_retorno, 0)
        
        # Empurra tudo para a esquerda para não ficar buracos entre os campos
        hbox.addStretch()
        
        vbox.addLayout(hbox)
        parent_layout.addWidget(frame)

    def setup_filters(self, parent_layout):
        """
        REFORMULADO: Separa os Radio Buttons dos Inputs para permitir
        reutilizar o container padrão (CNPJ+NF) no modo Giro.
        """
        frame = QFrame(objectName="FormCard")
        # Layout principal horizontal
        self.layout_filtros_wrapper = QHBoxLayout(frame)
        self.layout_filtros_wrapper.setContentsMargins(15, 15, 15, 15)
        
        # --- 1. CONTAINER DOS RADIO BUTTONS (Aparece só em Giro) ---
        self.container_radios = QWidget()
        layout_radios_wrapper = QVBoxLayout(self.container_radios)
        layout_radios_wrapper.setContentsMargins(0, 0, 15, 0) # Margem direita para separar
        
        self.group_modo = QButtonGroup(self)
        self.rb_grupo = QRadioButton("Por Grupo Econômico")
        self.rb_nota = QRadioButton("Por CNPJ (Nota Fiscal)")
        
        self.rb_grupo.setCursor(Qt.PointingHandCursor)
        self.rb_nota.setCursor(Qt.PointingHandCursor)
        self.rb_grupo.setChecked(True) # Padrão
        
        self.group_modo.addButton(self.rb_grupo)
        self.group_modo.addButton(self.rb_nota)
        
        # Conecta a mudança dos radios à visibilidade dos inputs
        self.rb_grupo.toggled.connect(self.atualizar_visibilidade_filtros)
        self.rb_nota.toggled.connect(self.atualizar_visibilidade_filtros)

        layout_radios_wrapper.addWidget(QLabel("Modo de Busca:"))
        layout_radios_wrapper.addWidget(self.rb_grupo)
        layout_radios_wrapper.addWidget(self.rb_nota)
        
        # --- 2. CONTAINER DE INPUTS (Stack lógico) ---
        
        # A) Container PADRÃO (CNPJ + NF) - Usado em Garantia, Crédito e Giro(Por CNPJ)
        self.container_padrao = QWidget()
        layout_padrao = QHBoxLayout(self.container_padrao)
        layout_padrao.setContentsMargins(0, 0, 0, 0)
        
        # --- ALTERAÇÃO AQUI: Padronização com o Módulo de Lançamento ---
        self.txt_cnpj_padrao = QLineEdit(placeholderText="CNPJ Emitente") 
        self.txt_cnpj_padrao.setInputMask("99.999.999/9999-99;_")
        self.txt_cnpj_padrao.setFixedWidth(150)
        
        self.txt_nf_garantia = QLineEdit(placeholderText="Nº Nota(s) de Garantia")
        
        # O stretch do CNPJ foi alterado para 0 (fixo) e o da Nota para 1 (expansível)
        self.add_field(layout_padrao, "CNPJ do Cliente:", self.txt_cnpj_padrao, 0)
        self.add_field(layout_padrao, "Nota Fiscal (Opcional):", self.txt_nf_garantia, 1)
        
        # B) Container GRUPO (Apenas input de texto simples) - Usado em Giro(Por Grupo)
        self.container_input_grupo = QWidget()
        layout_grupo = QHBoxLayout(self.container_input_grupo)
        layout_grupo.setContentsMargins(0, 0, 0, 0)
        
        self.txt_termo_grupo = QLineEdit(placeholderText="Digite o nome do Grupo Econômico")
        self.add_field(layout_grupo, "Nome do Grupo:", self.txt_termo_grupo, 1)

        # --- 3. BOTÃO BUSCAR ---
        vbox_btn = QVBoxLayout()
        vbox_btn.addStretch()
        btn_buscar = QPushButton(" BUSCAR PENDÊNCIAS", objectName="btn_primary")
        btn_buscar.setCursor(Qt.PointingHandCursor)
        btn_buscar.setFixedHeight(34)
        btn_buscar.clicked.connect(self.buscar)
        vbox_btn.addWidget(btn_buscar)

        # ADICIONANDO TUDO AO LAYOUT
        # Ordem: Radios (se visivel) -> Inputs (Padrao ou Grupo) -> Botão
        self.layout_filtros_wrapper.addWidget(self.container_radios, stretch=0)
        self.layout_filtros_wrapper.addWidget(self.container_padrao, stretch=4)
        self.layout_filtros_wrapper.addWidget(self.container_input_grupo, stretch=4)
        self.layout_filtros_wrapper.addSpacing(15)
        self.layout_filtros_wrapper.addLayout(vbox_btn, stretch=1)
        
        parent_layout.addWidget(frame)

    def setup_content_area(self, parent_layout):
        # ... (O código da tabela e resumo permanece idêntico ao seu original) ...
        hbox_main = QHBoxLayout()
        hbox_main.setSpacing(15)
        hbox_main.setContentsMargins(0, 0, 0, 0)

        # --- CARD ESQUERDA: TABELA ---
        card_tabela = QFrame(objectName="FormCard")
        layout_tabela = QVBoxLayout(card_tabela)
        
        lbl_lista = QLabel("Itens Pendentes")
        lbl_lista.setObjectName("SectionTitle")
        layout_tabela.addWidget(lbl_lista)
        
        self.table = QTableWidget()
        colunas = ["", "NF Origem", "Data", "Item", "Cliente", "Saldo Disp.", "Abater (R$)"]
        self.table.setColumnCount(len(colunas))
        self.table.setHorizontalHeaderLabels(colunas)
        
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setShowGrid(True)
        self.table.setFrameShape(QFrame.NoFrame)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.table.setColumnWidth(0, 50) 
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        
        self.table.itemChanged.connect(self.on_table_change)
        
        layout_tabela.addWidget(self.table)
        hbox_main.addWidget(card_tabela, stretch=1)

        # --- CARD DIREITA: RESUMO ---
        self.panel_resumo = QFrame(objectName="FormCard")
        self.panel_resumo.setFixedWidth(260)
        
        vbox_res = QVBoxLayout(self.panel_resumo)
        vbox_res.setContentsMargins(15, 20, 15, 20)
        
        vbox_res.addWidget(QLabel("Resumo Financeiro", objectName="SectionTitle"))
        vbox_res.addSpacing(15)
        
        self.lbl_total_nota = self.add_resumo_row(vbox_res, "Total Nota:", COLOR_TEXT)
        self.lbl_total_sel = self.add_resumo_row(vbox_res, "Selecionado:", COLOR_INFO)
        
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet(f"color: {COLOR_CARD_BORDER}; background-color: {COLOR_CARD_BORDER};")
        line.setFixedHeight(1)
        vbox_res.addWidget(line)
        
        self.lbl_diff = self.add_resumo_row(vbox_res, "Diferença:", COLOR_TEXT_DIM)
        
        vbox_res.addStretch()
        
        self.btn_confirmar = QPushButton("CONFIRMAR", objectName="btn_success")
        self.btn_confirmar.setFixedHeight(45)
        self.btn_confirmar.setCursor(Qt.PointingHandCursor)
        self.btn_confirmar.setEnabled(False)
        self.btn_confirmar.clicked.connect(self.salvar_final)
        vbox_res.addWidget(self.btn_confirmar)
        
        hbox_main.addWidget(self.panel_resumo)
        parent_layout.addLayout(hbox_main, stretch=1)

    def add_field(self, layout, label_text, widget, stretch=0):
        v = QVBoxLayout()
        v.setSpacing(2)
        lbl = QLabel(label_text)
        v.addWidget(lbl)
        v.addWidget(widget)
        layout.addLayout(v, stretch)

    def add_resumo_row(self, layout, titulo, cor):
        wid = QWidget()
        h = QHBoxLayout(wid)
        h.setContentsMargins(0,6,0,6)
        lbl = QLabel(titulo)
        lbl.setStyleSheet("background-color: transparent;") 
        h.addWidget(lbl)
        
        val = QLabel("R$ 0,00")
        val.setStyleSheet(f"color: {cor}; font-size: 15px; font-weight: bold; background-color: transparent;")
        val.setAlignment(Qt.AlignRight)
        h.addWidget(val)
        layout.addWidget(wid)
        return val

    # --- LÓGICA DE INTERFACE REFORMULADA ---
    def atualizar_visibilidade_filtros(self):
        tipo_selecionado = self.combo_tipo.currentText()
        is_giro = (tipo_selecionado == "Itens de Giro")
        
        # 1. Visibilidade dos Radio Buttons
        self.container_radios.setVisible(is_giro)
        
        # 2. Lógica para mostrar qual container de Input usar
        if is_giro:
            # Dentro de Giro, olhamos os Radios
            if self.rb_grupo.isChecked():
                # Giro -> Por Grupo
                self.container_padrao.setVisible(False)
                self.container_input_grupo.setVisible(True)
            else:
                # Giro -> Por CNPJ (Aqui reutilizamos o container padrão!)
                self.container_padrao.setVisible(True)
                self.container_input_grupo.setVisible(False)
        else:
            # Garantia ou Crédito -> Sempre usa CNPJ+NF
            self.container_padrao.setVisible(True)
            self.container_input_grupo.setVisible(False)

    # --- LÓGICA DE NEGÓCIO REFORMULADA ---
    def buscar(self):
        tipo = self.combo_tipo.currentText()
        
        termo = ""
        modo = "CNPJ"
        nf_filtro = None

        # Lógica para decidir de onde tirar os dados
        usar_busca_grupo = False
        
        if tipo == "Itens de Giro":
            if self.rb_grupo.isChecked():
                usar_busca_grupo = True
            else:
                usar_busca_grupo = False # É Giro, mas por CNPJ
        else:
            usar_busca_grupo = False # Garantia/Crédito

        if usar_busca_grupo:
            # Busca por Grupo
            termo = self.txt_termo_grupo.text()
            modo = "GRUPO"
        else:
            # Busca por CNPJ (seja Giro ou Normal)
            termo = self.txt_cnpj_padrao.text()
            modo = "CNPJ"
            nf_input = self.txt_nf_garantia.text()
            if nf_input:
                nf_filtro = nf_input

        # Validação
        if not termo:
            msg_campo = "Nome do Grupo" if modo == "GRUPO" else "CNPJ do Cliente"
            QMessageBox.warning(self, "Atenção", f"Preencha o campo {msg_campo}.")
            return

        self.itens_carregados = self.controller.buscar_pendencias(termo, modo, nf_filtro)
        self.popular_tabela()

    def popular_tabela(self):
        # ... (O código permanece idêntico) ...
        self.table.blockSignals(True)
        self.table.setRowCount(0)
        for i, dto in enumerate(self.itens_carregados):
            self.table.insertRow(i)
            
            chk = QTableWidgetItem()
            chk.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            chk.setCheckState(Qt.Unchecked)
            chk.setData(Qt.UserRole, dto)
            self.table.setItem(i, 0, chk)
            
            def c(t): 
                it = QTableWidgetItem(str(t)) 
                it.setTextAlignment(Qt.AlignCenter)
                return it
            
            self.table.setItem(i, 1, c(dto.numero_nota_origem))
            data_str = dto.data_nota_origem.strftime("%d/%m/%Y") if hasattr(dto.data_nota_origem, 'strftime') else str(dto.data_nota_origem)
            self.table.setItem(i, 2, c(data_str))
            
            self.table.setItem(i, 3, c(dto.codigo_item))
            self.table.setItem(i, 4, c(dto.nome_cliente))
            
            val = c(f"{dto.saldo_financeiro:.2f}")
            val.setForeground(QColor(COLOR_INFO))
            self.table.setItem(i, 5, val)
            
            abat = c(f"{dto.saldo_financeiro:.2f}")
            abat.setBackground(QColor(COLOR_INPUT_BG))
            self.table.setItem(i, 6, abat)
        self.table.blockSignals(False)
        self.recalcular_totais()

    def on_table_change(self, item):
        if item.column() in [0, 6]: self.recalcular_totais()

    def recalcular_totais(self):
        # ... (O código permanece idêntico) ...
        val_nota = self.spin_valor_retorno.value()
        total_sel = 0.0
        linhas_marcadas = 0
        
        for r in range(self.table.rowCount()):
            chk = self.table.item(r, 0)
            if chk.checkState() == Qt.Checked:
                linhas_marcadas += 1
                try:
                    val = float(self.table.item(r, 6).text().replace(",", "."))
                    total_sel += val
                    dto = chk.data(Qt.UserRole)
                    dto.valor_a_abater = val
                    dto.selecionado = True
                except: pass
            else:
                chk.data(Qt.UserRole).selecionado = False

        diff = val_nota - total_sel
        self.lbl_total_nota.setText(f"R$ {val_nota:,.2f}")
        self.lbl_total_sel.setText(f"R$ {total_sel:,.2f}")
        self.lbl_diff.setText(f"R$ {diff:,.2f}")

        liberado = False
        msg = "CONFIRMAR"
        cor = COLOR_TEXT_DIM

        if linhas_marcadas > 0:
            if self.combo_tipo.currentText() == "Itens de Giro":
                liberado = abs(diff) < 10.0
            else:
                liberado = abs(diff) < 0.10
            
            if liberado: cor = COLOR_SUCCESS
            elif total_sel > val_nota: msg = "VALOR EXCEDIDO"; cor = COLOR_DANGER
            else: msg = "AJUSTE VALOR"; cor = COLOR_WARNING

        if linhas_marcadas == 0: msg = "SELECIONE ITENS"

        self.lbl_diff.setStyleSheet(f"color: {cor}; font-size: 15px; font-weight: bold; background-color: transparent;")
        self.btn_confirmar.setText(msg)
        self.btn_confirmar.setEnabled(liberado)
        self.btn_confirmar.setObjectName("btn_success" if liberado else "btn_disabled")
        self.btn_confirmar.setStyle(self.btn_confirmar.style())

    def salvar_final(self):
        # ... (O código permanece idêntico até a parte de pegar os CNPJs) ...
        itens = []
        for r in range(self.table.rowCount()):
            chk = self.table.item(r, 0)
            if chk.checkState() == Qt.Checked:
                itens.append(chk.data(Qt.UserRole))
        
        cnpj_final = None
        grupo_final = None
        
        # Ajuste na lógica de captura dos dados finais
        if self.combo_tipo.currentText() == "Itens de Giro":
            if self.rb_grupo.isChecked():
                grupo_final = self.txt_termo_grupo.text()
            else:
                # Giro por CNPJ usa o campo padrão
                cnpj_final = self.txt_cnpj_padrao.text()
        else:
            cnpj_final = self.txt_cnpj_padrao.text()

        header = RetornoHeaderDTO(
            numero_nota=self.txt_num_nota.text(),
            data_emissao=self.date_emissao.date().toString("yyyy-MM-dd"),
            tipo_retorno=self.combo_tipo.currentText(),
            valor_total=self.spin_valor_retorno.value(),
            cnpj=cnpj_final,
            grupo=grupo_final
        )
        
        ok, msg = self.controller.salvar_processo(header, itens)
        if ok:
            QMessageBox.information(self, "Sucesso", msg)
            self.resetar_tela()
        else:
            QMessageBox.warning(self, "Erro", msg)

    def resetar_tela(self):
        self.txt_cnpj_padrao.clear()
        self.txt_nf_garantia.clear()
        self.txt_termo_grupo.clear()
        self.txt_num_nota.clear()
        self.spin_valor_retorno.setValue(0)
        self.table.setRowCount(0)
        self.itens_carregados = []
        self.recalcular_totais()