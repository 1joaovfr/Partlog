import sys
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                               QComboBox, QPushButton, QFrame, QTableWidget, QTableWidgetItem, 
                               QHeaderView, QDoubleSpinBox, QMessageBox, QRadioButton, 
                               QButtonGroup, QDateEdit)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor

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
        
        self.setStyleSheet(RETORNO_STYLES + get_date_edit_style())
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # 1. Topo
        self.setup_header(layout)

        # 2. Filtros
        self.setup_filters(layout)

        # 3. Área Conteúdo (Tabela Separada + Resumo Separado)
        self.setup_content_area(layout)

    def setup_header(self, parent_layout):
        frame = QFrame(objectName="FormCard") # Padronizado como FormCard
        vbox = QVBoxLayout(frame)
        
        vbox.addWidget(QLabel("DADOS DA NOTA DE RETORNO", objectName="SectionTitle"))
        
        hbox = QHBoxLayout()
        
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(["Garantia Comum", "Tratativa de Crédito", "Itens de Giro"])
        self.combo_tipo.currentIndexChanged.connect(self.ao_mudar_tipo_retorno)
        
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

    def add_field(self, layout, label_text, widget, stretch=0):
        v = QVBoxLayout()
        v.setSpacing(2)
        v.addWidget(QLabel(label_text))
        v.addWidget(widget)
        layout.addLayout(v, stretch)

    def setup_filters(self, parent_layout):
        frame = QFrame(objectName="FormCard")
        hbox = QHBoxLayout(frame)
        hbox.setContentsMargins(15, 15, 15, 15)
        
        self.group_modo = QButtonGroup(self)
        self.rb_grupo = QRadioButton("Por Grupo Econômico")
        self.rb_nota = QRadioButton("Por Nota Fiscal (CNPJ + NF)")
        self.rb_grupo.setCursor(Qt.PointingHandCursor)
        self.rb_nota.setCursor(Qt.PointingHandCursor)
        self.group_modo.addButton(self.rb_grupo)
        self.group_modo.addButton(self.rb_nota)
        
        self.rb_grupo.toggled.connect(self.toggle_input_filters)
        
        self.txt_termo = QLineEdit()
        self.txt_nf_filtro = QLineEdit(placeholderText="Nº NF Original")
        
        self.txt_termo.returnPressed.connect(self.buscar)
        self.txt_nf_filtro.returnPressed.connect(self.buscar)

        btn_buscar = QPushButton(" BUSCAR PENDÊNCIAS", objectName="btn_primary")
        btn_buscar.setCursor(Qt.PointingHandCursor)
        btn_buscar.clicked.connect(self.buscar)

        hbox.addWidget(self.rb_grupo)
        hbox.addWidget(self.rb_nota)
        hbox.addSpacing(20)
        hbox.addWidget(self.txt_termo, 2)
        hbox.addWidget(self.txt_nf_filtro, 1)
        hbox.addWidget(btn_buscar)
        
        parent_layout.addWidget(frame)
        self.ao_mudar_tipo_retorno() 

    def setup_content_area(self, parent_layout):
        # Layout Horizontal para separar os dois Cards
        hbox_main = QHBoxLayout()
        hbox_main.setSpacing(15) # Espaço entre Tabela e Resumo
        hbox_main.setContentsMargins(0, 0, 0, 0)

        # --- CARD 1: TABELA (Estilo solicitado) ---
        card_tabela = QFrame(objectName="FormCard")
        layout_tabela = QVBoxLayout(card_tabela)
        
        lbl_lista = QLabel("Itens Pendentes")
        lbl_lista.setObjectName("SectionTitle")
        layout_tabela.addWidget(lbl_lista)
        
        self.table = QTableWidget()
        colunas = ["", "NF Origem", "Data", "Item", "Cliente", "Saldo Disp.", "Abater (R$)"]
        self.table.setColumnCount(len(colunas))
        self.table.setHorizontalHeaderLabels(colunas)
        
        # Configurações do seu snippet
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers) # Edição via clique ou código apenas
        self.table.setShowGrid(True) # Grid visível como pedido
        self.table.setFrameShape(QFrame.NoFrame)
        
        # Cabeçalhos
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.table.setColumnWidth(0, 50) 
        header.setSectionResizeMode(0, QHeaderView.Fixed) # Checkbox fixo
        
        self.table.itemChanged.connect(self.on_table_change)
        
        layout_tabela.addWidget(self.table)
        hbox_main.addWidget(card_tabela, stretch=1)

        # --- CARD 2: RESUMO (Menor e separado) ---
        self.panel_resumo = QFrame(objectName="FormCard")
        self.panel_resumo.setFixedWidth(260) # Largura reduzida
        
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

    # --- LÓGICA (Mantida) ---
    def ao_mudar_tipo_retorno(self):
        tipo = self.combo_tipo.currentText()
        if tipo == "Itens de Giro":
            self.rb_grupo.setEnabled(True); self.rb_grupo.setChecked(True)
        else:
            self.rb_grupo.setEnabled(False); self.rb_nota.setChecked(True)
        self.toggle_input_filters()

    def toggle_input_filters(self):
        if self.rb_grupo.isChecked():
            self.txt_termo.setPlaceholderText("Nome do Grupo Econômico")
            self.txt_nf_filtro.setVisible(False)
        else:
            self.txt_termo.setPlaceholderText("CNPJ do Cliente")
            self.txt_nf_filtro.setVisible(True)

    def buscar(self):
        termo = self.txt_termo.text()
        nf = self.txt_nf_filtro.text() if self.rb_nota.isChecked() else None
        modo = "GRUPO" if self.rb_grupo.isChecked() else "CNPJ"
        self.itens_carregados = self.controller.buscar_pendencias(termo, modo, nf)
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
                it = QTableWidgetItem(t); it.setTextAlignment(Qt.AlignCenter); return it
            
            self.table.setItem(i, 1, c(dto.numero_nota_origem))
            self.table.setItem(i, 2, c(dto.data_nota_origem.strftime("%d/%m/%Y")))
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
                    dto = chk.data(Qt.UserRole); dto.valor_a_abater = val; dto.selecionado = True
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
        
        header = RetornoHeaderDTO(
            numero_nota=self.txt_num_nota.text(),
            data_emissao=self.date_emissao.date().toString("yyyy-MM-dd"),
            tipo_retorno=self.combo_tipo.currentText(),
            valor_total=self.spin_valor_retorno.value(),
            cnpj=self.txt_termo.text() if not self.rb_grupo.isChecked() else None,
            grupo=self.txt_termo.text() if self.rb_grupo.isChecked() else None
        )
        
        ok, msg = self.controller.salvar_processo(header, itens)
        if ok:
            QMessageBox.information(self, "Sucesso", msg)
            self.resetar_tela()
        else:
            QMessageBox.warning(self, "Erro", msg)

    def resetar_tela(self):
        self.txt_termo.clear()
        self.txt_nf_filtro.clear()
        self.txt_num_nota.clear()
        self.spin_valor_retorno.setValue(0)
        self.table.setRowCount(0)
        self.itens_carregados = []
        self.recalcular_totais()