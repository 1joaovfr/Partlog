import sys
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                               QComboBox, QPushButton, QFrame, QTableWidget, QTableWidgetItem, 
                               QHeaderView, QDoubleSpinBox, QMessageBox, QRadioButton, 
                               QButtonGroup, QDateEdit, QSizePolicy)
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
        
        self.setStyleSheet(RETORNO_STYLES + get_date_edit_style("views/icons/temp_calendar_icon.png"))
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        self.setup_header_area(layout)
        self.setup_content_area(layout)
        self.atualizar_interface_dinamica()

    def setup_header_area(self, parent_layout):
        frame = QFrame(objectName="FormCard")
        vbox = QVBoxLayout(frame)
        
        vbox.addWidget(QLabel("Retorno de Notas de Garantia", objectName="SectionTitle"))
        
        # --- LINHA 1 ---
        hbox_row1 = QHBoxLayout()
        hbox_row1.setContentsMargins(0, 0, 0, 0)

        # 1. Tipo
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(["Garantia Simples", "Tratativa de Crédito", "Itens de Giro"])
        self.combo_tipo.setFixedWidth(170)
        self.combo_tipo.currentIndexChanged.connect(self.atualizar_interface_dinamica)
        self.add_field(hbox_row1, "Tipo de Retorno", self.combo_tipo)

        # 2. CNPJ Emitente
        self.txt_cnpj_emitente = QLineEdit()
        self.txt_cnpj_emitente.setPlaceholderText("Sua Empresa")
        self.txt_cnpj_emitente.setInputMask("99.999.999/9999-99;_")
        self.txt_cnpj_emitente.setFixedWidth(150)
        self.add_field(hbox_row1, "CNPJ Emitente", self.txt_cnpj_emitente)

        # 3. Número Nota
        self.txt_num_nota = QLineEdit()
        self.txt_num_nota.setPlaceholderText("Nº Nota")
        self.txt_num_nota.setFixedWidth(150)
        self.add_field(hbox_row1, "Número Nota", self.txt_num_nota)

        # 4. Emissão
        self.date_emissao = QDateEdit(calendarPopup=True, date=QDate.currentDate())
        self.date_emissao.setFixedWidth(130)
        self.add_field(hbox_row1, "Emissão", self.date_emissao)

        # 5. Valor Total
        self.spin_valor_retorno = QDoubleSpinBox()
        self.spin_valor_retorno.setPrefix("R$ ")
        self.spin_valor_retorno.setRange(0.00, 9999999.99)
        self.spin_valor_retorno.setFixedWidth(100)
        self.spin_valor_retorno.setButtonSymbols(QDoubleSpinBox.NoButtons)
        self.spin_valor_retorno.valueChanged.connect(self.recalcular_totais)
        self.add_field(hbox_row1, "Valor Total", self.spin_valor_retorno)

        self.container_remetente = QWidget()
        self.container_remetente.setObjectName("ContainerRemetente")
        self.container_remetente.setStyleSheet("""
            #ContainerRemetente { 
                background-color: transparent; 
                border: none; 
            }
        """)
        
        self.container_remetente.setFixedWidth(150) 
        v_remetente = QVBoxLayout(self.container_remetente)
        v_remetente.setContentsMargins(0,0,0,0)
        v_remetente.setSpacing(2)
        
        self.lbl_remetente_dinamico = QLabel("CNPJ Remetente")
        self.lbl_remetente_dinamico.setStyleSheet("background-color: transparent; border: none;")
        
        self.txt_remetente_dinamico = QLineEdit()
        self.txt_remetente_dinamico.setInputMask("99.999.999/9999-99;_")
        self.txt_remetente_dinamico.setFixedWidth(150)
        
        v_remetente.addWidget(self.lbl_remetente_dinamico)
        v_remetente.addWidget(self.txt_remetente_dinamico)
        hbox_row1.addWidget(self.container_remetente)
        hbox_row1.addStretch()

        vbox.addLayout(hbox_row1)

        # --- LINHA 2 ---
        hbox_row2 = QHBoxLayout()
        hbox_row2.setContentsMargins(0, 5, 0, 0)
        
        # A) Checkboxes
        self.container_checks = QWidget()
        self.container_checks.setStyleSheet("background-color: transparent; border: none;")
        hbox_checks = QHBoxLayout(self.container_checks)
        hbox_checks.setContentsMargins(0, 0, 15, 0)
        hbox_checks.setSpacing(10)
        
        self.group_modo = QButtonGroup(self)
        self.rb_grupo = QRadioButton("Por Grupo")
        self.rb_cnpj = QRadioButton("Por CNPJ")
        self.rb_cnpj.setChecked(True)
        
        style_rb = f"background-color: transparent; color: {COLOR_TEXT};"
        self.rb_grupo.setStyleSheet(style_rb)
        self.rb_cnpj.setStyleSheet(style_rb)
        
        self.group_modo.addButton(self.rb_grupo)
        self.group_modo.addButton(self.rb_cnpj)
        
        self.rb_grupo.toggled.connect(self.atualizar_interface_dinamica)
        self.rb_cnpj.toggled.connect(self.atualizar_interface_dinamica)

        hbox_checks.addWidget(self.rb_grupo)
        hbox_checks.addWidget(self.rb_cnpj)
        hbox_row2.addWidget(self.container_checks) 

        # B) Campo de Notas
        self.txt_busca_notas = QLineEdit()
        self.txt_busca_notas.setPlaceholderText("Digite notas fiscais (separadas por espaço)...")
        self.txt_busca_notas.setFixedHeight(34)
        hbox_row2.addWidget(self.txt_busca_notas, stretch=1) 

        # C) Botão Buscar
        btn_buscar = QPushButton("Buscar Pendências")
        btn_buscar.setObjectName("btn_primary")
        btn_buscar.setCursor(Qt.PointingHandCursor)
        btn_buscar.setFixedWidth(180)
        btn_buscar.setFixedHeight(34)
        btn_buscar.clicked.connect(self.buscar)
        hbox_row2.addWidget(btn_buscar)

        vbox.addLayout(hbox_row2)
        parent_layout.addWidget(frame)

    def atualizar_interface_dinamica(self):
        tipo = self.combo_tipo.currentText()
        is_giro = (tipo == "Itens de Giro")

        self.container_checks.setVisible(is_giro)
        modo_grupo = is_giro and self.rb_grupo.isChecked()

        if modo_grupo:
            self.lbl_remetente_dinamico.setText("Grupo de Cliente:")
            self.txt_remetente_dinamico.setInputMask("") 
            self.txt_remetente_dinamico.setPlaceholderText("Nome do Grupo")
            
            self.txt_busca_notas.setEnabled(False)
            self.txt_busca_notas.setPlaceholderText("Indisponível: busca por grupo")
            self.txt_busca_notas.clear()
        else:
            self.lbl_remetente_dinamico.setText("CNPJ Remetente:")
            self.txt_remetente_dinamico.setInputMask("99.999.999/9999-99;_")
            self.txt_remetente_dinamico.setPlaceholderText("CNPJ do Cliente")
            
            self.txt_busca_notas.setEnabled(True)
            self.txt_busca_notas.setPlaceholderText("Digite notas fiscais (separadas por espaço)...")

    def buscar(self):
        # 1. Captura e Limpeza
        termo = self.txt_remetente_dinamico.text()
        
        if "CNPJ" in self.lbl_remetente_dinamico.text():
            termo_clean = termo.replace(".", "").replace("/", "").replace("-", "").strip()
        else:
            termo_clean = termo.strip()

        if not termo_clean:
            QMessageBox.warning(self, "Aviso", "Preencha o campo de CNPJ ou Grupo na primeira linha.")
            return

        modo = "GRUPO" if (self.combo_tipo.currentText() == "Itens de Giro" and self.rb_grupo.isChecked()) else "CNPJ"

        lista_notas = []
        if self.txt_busca_notas.isEnabled():
            raw_notas = self.txt_busca_notas.text()
            lista_notas = [n.strip() for n in raw_notas.replace(",", " ").split() if n.strip()]

        # 2. Busca
        self.itens_carregados = self.controller.buscar_pendencias(termo_clean, modo, lista_notas)

        # 3. Validação de Retorno Vazio
        if not self.itens_carregados:
            QMessageBox.information(self, "Busca", "Nenhuma pendência encontrada para os dados informados.\nVerifique se o CNPJ está correto e se a nota possui itens com saldo.")
            self.table.setRowCount(0)
            self.recalcular_totais()
            return

        self.popular_tabela()

    def setup_content_area(self, parent_layout):
        hbox_main = QHBoxLayout()
        hbox_main.setSpacing(15)

        # Tabela
        card_tabela = QFrame(objectName="FormCard")
        layout_tabela = QVBoxLayout(card_tabela)
        layout_tabela.addWidget(QLabel("Itens Pendentes", objectName="SectionTitle"))
        
        self.table = QTableWidget()
        # Colunas atualizadas
        colunas = ["", "NF Origem", "Data", "Item", "Cliente", "Saldo Disp.", "Cód. Análise"]
        self.table.setColumnCount(len(colunas))
        self.table.setHorizontalHeaderLabels(colunas)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.table.setColumnWidth(0, 50)
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.DoubleClicked | QTableWidget.SelectedClicked)
        self.table.itemChanged.connect(self.on_table_change)
        
        layout_tabela.addWidget(self.table)
        hbox_main.addWidget(card_tabela, stretch=1)

        # Resumo
        self.panel_resumo = QFrame(objectName="FormCard")
        self.panel_resumo.setFixedWidth(260)
        vbox_res = QVBoxLayout(self.panel_resumo)
        vbox_res.setSpacing(15)
        
        vbox_res.addWidget(QLabel("Resumo Financeiro", objectName="SectionTitle"))
        
        self.lbl_total_nota = self.add_resumo_row(vbox_res, "Total Nota:", COLOR_TEXT)
        self.lbl_total_sel = self.add_resumo_row(vbox_res, "Selecionado:", COLOR_INFO)
        
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet(f"background-color: {COLOR_CARD_BORDER};")
        line.setFixedHeight(1)
        vbox_res.addWidget(line)
        
        self.lbl_diff = self.add_resumo_row(vbox_res, "Diferença:", COLOR_TEXT_DIM)
        
        vbox_res.addStretch()
        self.btn_confirmar = QPushButton("CONFIRMAR", objectName="btn_success")
        self.btn_confirmar.setFixedHeight(45)
        self.btn_confirmar.setEnabled(False)
        self.btn_confirmar.clicked.connect(self.salvar_final)
        vbox_res.addWidget(self.btn_confirmar)
        
        hbox_main.addWidget(self.panel_resumo)
        parent_layout.addLayout(hbox_main)

    def add_field(self, layout, text, widget):
        v = QVBoxLayout()
        v.setSpacing(2)
        lbl = QLabel(text)
        lbl.setStyleSheet("background-color: transparent; border: none;") 
        v.addWidget(lbl)
        v.addWidget(widget)
        layout.addLayout(v, stretch=0)

    def add_resumo_row(self, layout, titulo, cor):
        wid = QWidget()
        wid.setStyleSheet("background-color: transparent; border: none;")
        
        h = QHBoxLayout(wid)
        h.setContentsMargins(0,5,0,5)
        
        lbl_tit = QLabel(titulo)
        lbl_tit.setStyleSheet("background-color: transparent; border: none; color: " + COLOR_TEXT)
        h.addWidget(lbl_tit)
        
        val = QLabel("R$ 0,00")
        val.setStyleSheet(f"color: {cor}; font-weight: bold; background-color: transparent; border: none;")
        h.addWidget(val, alignment=Qt.AlignRight)
        
        layout.addWidget(wid)
        return val

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
            
            # Bloqueio de edição para campos informativos
            item_nf = QTableWidgetItem(str(dto.numero_nota_origem))
            item_nf.setFlags(item_nf.flags() ^ Qt.ItemIsEditable)
            self.table.setItem(i, 1, item_nf)

            data_s = dto.data_nota_origem.strftime("%d/%m/%Y") if hasattr(dto.data_nota_origem, 'strftime') else str(dto.data_nota_origem)
            item_data = QTableWidgetItem(data_s)
            item_data.setFlags(item_data.flags() ^ Qt.ItemIsEditable)
            self.table.setItem(i, 2, item_data)

            item_cod = QTableWidgetItem(str(dto.codigo_item))
            item_cod.setFlags(item_cod.flags() ^ Qt.ItemIsEditable)
            self.table.setItem(i, 3, item_cod)

            item_cli = QTableWidgetItem(dto.nome_cliente)
            item_cli.setFlags(item_cli.flags() ^ Qt.ItemIsEditable)
            self.table.setItem(i, 4, item_cli)
            
            val = QTableWidgetItem(f"{dto.saldo_financeiro:.2f}")
            val.setForeground(QColor(COLOR_INFO))
            val.setFlags(val.flags() ^ Qt.ItemIsEditable)
            self.table.setItem(i, 5, val)
            
            # Coluna editável: Código de Análise
            cod_analise = QTableWidgetItem(str(dto.codigo_analise)) 
            self.table.setItem(i, 6, cod_analise)
            
        self.table.blockSignals(False)
        self.recalcular_totais()

    def on_table_change(self, item):
        # Monitora Checkbox (0) e Código de Análise (6)
        if item.column() in [0, 6]: self.recalcular_totais()

    def recalcular_totais(self):
        val_nota = self.spin_valor_retorno.value()
        total_sel = 0.0
        linhas_marcadas = 0
        
        for r in range(self.table.rowCount()):
            chk = self.table.item(r, 0)
            if chk.checkState() == Qt.Checked:
                linhas_marcadas += 1
                dto = chk.data(Qt.UserRole)
                
                # Assume saldo total como valor a abater
                dto.valor_a_abater = dto.saldo_financeiro 
                
                # Lê o código digitado
                texto_cod = self.table.item(r, 6).text() 
                dto.codigo_analise = texto_cod 
                
                total_sel += dto.valor_a_abater

        diff = val_nota - total_sel
        self.lbl_total_nota.setText(f"R$ {val_nota:,.2f}")
        self.lbl_total_sel.setText(f"R$ {total_sel:,.2f}")
        self.lbl_diff.setText(f"R$ {diff:,.2f}")
        
        # --- LÓGICA DE VALIDAÇÃO VISUAL ---
        margem = 10.0 if self.combo_tipo.currentText() == "Itens de Giro" else 0.10
        esta_no_prazo = abs(diff) <= margem

        # ALTERAÇÃO AQUI:
        # Habilita o botão se tiver linhas marcadas, MESMO se o valor estiver errado.
        # Assim o usuário consegue clicar e receber a mensagem de erro.
        self.btn_confirmar.setEnabled(linhas_marcadas > 0)
        
        # Mantém o feedback visual (Verde se OK, Vermelho se Errado)
        cor = COLOR_SUCCESS if esta_no_prazo else COLOR_DANGER
        self.lbl_diff.setStyleSheet(f"color: {cor}; font-weight: bold; background-color: transparent; border: none;")

    def salvar_final(self):
        itens = []
        for r in range(self.table.rowCount()):
            chk = self.table.item(r, 0)
            if chk.checkState() == Qt.Checked:
                itens.append(chk.data(Qt.UserRole))

        cnpj_remetente = None
        grupo = None
        valor_campo_dinamico = self.txt_remetente_dinamico.text()
        
        if self.combo_tipo.currentText() == "Itens de Giro" and self.rb_grupo.isChecked():
            grupo = valor_campo_dinamico
        else:
            cnpj_remetente = valor_campo_dinamico.replace(".", "").replace("/", "").replace("-", "")

        cnpj_emitente_limpo = self.txt_cnpj_emitente.text().replace(".", "").replace("/", "").replace("-", "")

        header = RetornoHeaderDTO(
            numero_nota=self.txt_num_nota.text(),
            data_emissao=self.date_emissao.date().toString("yyyy-MM-dd"),
            tipo_retorno=self.combo_tipo.currentText(),
            valor_total=self.spin_valor_retorno.value(),
            cnpj_emitente=cnpj_emitente_limpo,
            cnpj_remetente=cnpj_remetente,
            grupo=grupo
        )
        
        ok, msg = self.controller.salvar_processo(header, itens)
        
        if ok:
            QMessageBox.information(self, "Sucesso", msg)
            self.resetar_tela()
        else:
            QMessageBox.warning(self, "Erro de Validação", msg)

    def resetar_tela(self):
        self.txt_remetente_dinamico.clear()
        self.txt_busca_notas.clear()
        self.txt_num_nota.clear()
        self.spin_valor_retorno.setValue(0)
        self.table.setRowCount(0)
        self.itens_carregados = []
        self.recalcular_totais()