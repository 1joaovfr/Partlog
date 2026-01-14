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
        
        # Aplica o estilo recebido do arquivo styles
        self.setStyleSheet(RETORNO_STYLES + get_date_edit_style())
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # 1. Topo (Dados da Nota)
        self.setup_header(layout)

        # 2. Filtros Dinâmicos (Aqui está a mudança de layout solicitada)
        self.setup_filters(layout)

        # 3. Área Conteúdo (Tabela e Resumo)
        self.setup_content_area(layout)

        # Garante que a tela inicie com a visibilidade correta dos filtros
        self.atualizar_visibilidade_filtros()

    def setup_header(self, parent_layout):
        frame = QFrame(objectName="FormCard")
        vbox = QVBoxLayout(frame)
        
        vbox.addWidget(QLabel("DADOS DA NOTA DE RETORNO", objectName="SectionTitle"))
        
        hbox = QHBoxLayout()
        
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(["Garantia Simples", "Tratativa de Crédito", "Itens de Giro"])
        # Conecta a mudança do combo à função que esconde/mostra campos
        self.combo_tipo.currentIndexChanged.connect(self.atualizar_visibilidade_filtros)
        
        self.txt_num_nota = QLineEdit(placeholderText="Nº Nota Retorno")
        self.date_emissao = QDateEdit(calendarPopup=True, date=QDate.currentDate())
        
        self.spin_valor_retorno = QDoubleSpinBox()
        self.spin_valor_retorno.setPrefix("R$ ")
        self.spin_valor_retorno.setRange(0, 10000000)
        self.spin_valor_retorno.setAlignment(Qt.AlignRight)
        self.spin_valor_retorno.valueChanged.connect(self.recalcular_totais)

        self.add_field(hbox, "Tipo de Retorno:", self.combo_tipo, 1)
        self.add_field(hbox, "Número Nota:", self.txt_num_nota, 1)
        self.add_field(hbox, "Emissão:", self.date_emissao, 1)
        self.add_field(hbox, "Valor Total:", self.spin_valor_retorno, 1)
        
        vbox.addLayout(hbox)
        parent_layout.addWidget(frame)

    def setup_filters(self, parent_layout):
        frame = QFrame(objectName="FormCard")
        self.layout_filtros_wrapper = QHBoxLayout(frame)
        self.layout_filtros_wrapper.setContentsMargins(15, 15, 15, 15)
        
        # --- CONTAINER 1: Filtros Padrão (Garantia/Crédito) ---
        self.container_padrao = QWidget()
        layout_padrao = QHBoxLayout(self.container_padrao)
        layout_padrao.setContentsMargins(0, 0, 0, 0)
        
        self.txt_cnpj_padrao = QLineEdit(placeholderText="CNPJ do Cliente")
        self.txt_nf_garantia = QLineEdit(placeholderText="Nº Nota(s) de Garantia")
        
        self.add_field(layout_padrao, "CNPJ do Cliente:", self.txt_cnpj_padrao, 1)
        self.add_field(layout_padrao, "Notas de Garantia (Origem):", self.txt_nf_garantia, 1)
        
        # --- CONTAINER 2: Filtros de Giro (Radio Buttons) ---
        self.container_giro = QWidget()
        layout_giro = QHBoxLayout(self.container_giro)
        layout_giro.setContentsMargins(0, 0, 0, 0)
        
        self.group_modo = QButtonGroup(self)
        self.rb_grupo = QRadioButton("Por Grupo Econômico")
        self.rb_nota = QRadioButton("Por CNPJ (Nota Fiscal)")
        self.rb_grupo.setCursor(Qt.PointingHandCursor)
        self.rb_nota.setCursor(Qt.PointingHandCursor)
        self.group_modo.addButton(self.rb_grupo)
        self.group_modo.addButton(self.rb_nota)
        self.rb_grupo.setChecked(True)
        
        # Input único para Giro (muda placeholder conforme radio)
        self.txt_termo_giro = QLineEdit()
        self.rb_grupo.toggled.connect(lambda: self.txt_termo_giro.setPlaceholderText("Nome do Grupo") if self.rb_grupo.isChecked() else self.txt_termo_giro.setPlaceholderText("CNPJ do Cliente"))
        self.txt_termo_giro.setPlaceholderText("Nome do Grupo") # Inicial

        layout_radios = QVBoxLayout()
        layout_radios.addWidget(self.rb_grupo)
        layout_radios.addWidget(self.rb_nota)
        
        layout_giro.addLayout(layout_radios)
        self.add_field(layout_giro, "Termo de Busca:", self.txt_termo_giro, 2)

        # --- BOTÃO BUSCAR (Comum) ---
        # Usamos um container vertical para alinhar o botão com a base dos inputs
        vbox_btn = QVBoxLayout()
        vbox_btn.addStretch()
        btn_buscar = QPushButton(" BUSCAR PENDÊNCIAS", objectName="btn_primary")
        btn_buscar.setCursor(Qt.PointingHandCursor)
        btn_buscar.setFixedHeight(34) # Altura para alinhar com inputs
        btn_buscar.clicked.connect(self.buscar)
        vbox_btn.addWidget(btn_buscar)

        # Adiciona containers ao layout principal do frame
        self.layout_filtros_wrapper.addWidget(self.container_padrao, stretch=4)
        self.layout_filtros_wrapper.addWidget(self.container_giro, stretch=4)
        self.layout_filtros_wrapper.addSpacing(15)
        self.layout_filtros_wrapper.addLayout(vbox_btn, stretch=1)
        
        parent_layout.addWidget(frame)

    def setup_content_area(self, parent_layout):
        # Layout Horizontal para separar Tabela e Resumo
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

    # --- MÉTODOS AUXILIARES UI ---
    def add_field(self, layout, label_text, widget, stretch=0):
        v = QVBoxLayout()
        v.setSpacing(2)
        lbl = QLabel(label_text)
        # Pequeno ajuste CSS inline se necessário, ou use styles
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

    # --- LÓGICA DE INTERFACE (VISIBILIDADE) ---
    def atualizar_visibilidade_filtros(self):
        tipo = self.combo_tipo.currentText()
        
        if tipo == "Itens de Giro":
            # Esconde inputs padrão, Mostra inputs de Giro
            self.container_padrao.setVisible(False)
            self.container_giro.setVisible(True)
        else:
            # Mostra inputs padrão, Esconde inputs de Giro
            self.container_padrao.setVisible(True)
            self.container_giro.setVisible(False)

    # --- LÓGICA DE NEGÓCIO DA VIEW ---
    def buscar(self):
        # Define quais variáveis pegar baseado no que está visível
        tipo = self.combo_tipo.currentText()
        
        termo = ""
        modo = "CNPJ"
        nf_filtro = None

        if tipo == "Itens de Giro":
            termo = self.txt_termo_giro.text()
            if self.rb_grupo.isChecked():
                modo = "GRUPO"
            else:
                modo = "CNPJ"
        else:
            # Garantia ou Crédito
            termo = self.txt_cnpj_padrao.text()
            nf_input = self.txt_nf_garantia.text()
            if nf_input:
                nf_filtro = nf_input
            modo = "CNPJ"

        # Validação simples antes de chamar controller
        if not termo:
            QMessageBox.warning(self, "Atenção", "Preencha o campo de busca (CNPJ ou Grupo).")
            return

        # Chama o controller original sem modificação
        self.itens_carregados = self.controller.buscar_pendencias(termo, modo, nf_filtro)
        self.popular_tabela()

    def popular_tabela(self):
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
                it = QTableWidgetItem(str(t)) # str() para segurança
                it.setTextAlignment(Qt.AlignCenter)
                return it
            
            self.table.setItem(i, 1, c(dto.numero_nota_origem))
            # Tratamento caso data seja None ou string
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
        itens = []
        for r in range(self.table.rowCount()):
            chk = self.table.item(r, 0)
            if chk.checkState() == Qt.Checked:
                itens.append(chk.data(Qt.UserRole))
        
        # Determina o CNPJ e o Grupo com base na seleção
        cnpj_final = None
        grupo_final = None
        
        if self.combo_tipo.currentText() == "Itens de Giro":
            if self.rb_grupo.isChecked():
                grupo_final = self.txt_termo_giro.text()
            else:
                cnpj_final = self.txt_termo_giro.text()
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
        self.txt_termo_giro.clear()
        self.txt_num_nota.clear()
        self.spin_valor_retorno.setValue(0)
        self.table.setRowCount(0)
        self.itens_carregados = []
        self.recalcular_totais()