import sys
import qtawesome as qta
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                               QPushButton, QFrame, QTableWidget, QTableWidgetItem, 
                               QHeaderView, QMessageBox, QDateEdit, QCheckBox, 
                               QDoubleSpinBox, QSpinBox)
from PySide6.QtCore import Qt, QDate

from controllers import LancamentoController
from styles.lancamento_styles import LANCAMENTO_STYLES

class PageLancamento(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = LancamentoController()
        
        self.setWindowTitle("Lançamento de NF-e")
        self.setStyleSheet(LANCAMENTO_STYLES)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        card_header = QFrame(objectName="FormCard")
        layout_header = QVBoxLayout(card_header)
        
        lbl_header = QLabel("Entrada de Nota Fiscal")
        lbl_header.setObjectName("SectionTitle")
        layout_header.addWidget(lbl_header)

        # Helper layouts
        def v_box(lbl, widget):
            l = QVBoxLayout()
            l.addWidget(QLabel(lbl))
            l.addWidget(widget)
            return l

        # --- LINHA ÚNICA DE CABEÇALHO ---
        row1 = QHBoxLayout()
        mascara_cnpj = "99.999.999/9999-99"

        # 1. CNPJ REMETENTE (Sua Empresa/Filial) - PRIMEIRO CAMPO
        self.txt_cnpj_remetente = QLineEdit(placeholderText="CNPJ Destino/Grupo")
        self.txt_cnpj_remetente.setInputMask(mascara_cnpj + ";_")
        self.txt_cnpj_remetente.setFixedWidth(150)

        # 2. CNPJ EMITENTE (Cliente)
        self.txt_cnpj = QLineEdit(placeholderText="CNPJ Cliente")
        self.txt_cnpj.setInputMask(mascara_cnpj + ";_")
        self.txt_cnpj.setFixedWidth(150) 
        self.txt_cnpj.textChanged.connect(self.buscar_emitente)        
        
        # 3. NOME EMITENTE (Visualização apenas do cliente)
        self.txt_emitente = QLineEdit(placeholderText="Razão Social Cliente", readOnly=True)
        
        # 4. DADOS DA NOTA
        self.txt_num_nf = QLineEdit(placeholderText="Nº Nota")
        self.txt_num_nf.setFixedWidth(150)

        self.dt_emissao = QDateEdit(calendarPopup=True, date=QDate.currentDate())
        self.dt_emissao.setFixedWidth(130)
        
        self.dt_recebimento = QDateEdit(calendarPopup=True, date=QDate.currentDate())
        self.dt_recebimento.setFixedWidth(130)

        # ADICIONANDO NA ORDEM: Remetente -> Emitente -> Nome -> NF -> Datas
        row1.addLayout(v_box("CNPJ Remetente", self.txt_cnpj_remetente))
        row1.addLayout(v_box("CNPJ Emitente", self.txt_cnpj))
        row1.addLayout(v_box("Razão Social (Emitente)", self.txt_emitente))
        row1.addLayout(v_box("Nº Nota", self.txt_num_nf))
        row1.addLayout(v_box("Emissão", self.dt_emissao))
        row1.addLayout(v_box("Recebimento", self.dt_recebimento))
        
        layout_header.addLayout(row1)
        main_layout.addWidget(card_header)

        # CARD 2: ITENS
        card_itens = QFrame(objectName="FormCard")
        layout_itens = QVBoxLayout(card_itens)
        
        lbl_sec_itens = QLabel("Itens da Nota")
        lbl_sec_itens.setObjectName("SectionTitle")
        layout_itens.addWidget(lbl_sec_itens)

        # Inputs Item
        input_item_layout = QHBoxLayout()
        
        self.txt_cod_item = QLineEdit(placeholderText="Cód.")
        self.txt_cod_item.setFixedWidth(80)

        self.spin_qtd = QSpinBox()
        self.spin_qtd.setFixedWidth(70)
        self.spin_qtd.setRange(0, 9999) 
        self.spin_qtd.setSpecialValueText(" ") 
        self.spin_qtd.setValue(0) 
        
        self.spin_valor = QDoubleSpinBox()
        self.spin_valor.setRange(0.00, 999999.99)
        self.spin_valor.setPrefix("R$ ")
        self.spin_valor.setFixedWidth(100)
        self.spin_valor.setSpecialValueText(" ") 
        self.spin_valor.setValue(0.00)

        self.chk_ressarcimento = QCheckBox("Ressarcimento?")
        self.chk_ressarcimento.setCursor(Qt.PointingHandCursor)
        self.chk_ressarcimento.toggled.connect(self.toggle_ressarcimento)

        self.lbl_vlr_ressarc = QLabel("Vl. Ressarc:")
        self.lbl_vlr_ressarc.setVisible(False)
        
        self.spin_vlr_ressarc = QDoubleSpinBox()
        self.spin_vlr_ressarc.setRange(0.00, 999999.99)
        self.spin_vlr_ressarc.setPrefix("R$ ")
        self.spin_vlr_ressarc.setFixedWidth(100)
        self.spin_vlr_ressarc.setSpecialValueText(" ") 
        self.spin_vlr_ressarc.setValue(0.00)
        self.spin_vlr_ressarc.setVisible(False)

        self.btn_add_item = QPushButton(" Adicionar")
        self.btn_add_item.setObjectName("btn_add")
        self.btn_add_item.setIcon(qta.icon('fa5s.plus', color='white'))
        self.btn_add_item.setCursor(Qt.PointingHandCursor)
        self.btn_add_item.clicked.connect(self.adicionar_item_tabela)

        input_item_layout.addWidget(QLabel("Item:"))
        input_item_layout.addWidget(self.txt_cod_item)
        input_item_layout.addWidget(QLabel("Qtd:"))
        input_item_layout.addWidget(self.spin_qtd)
        input_item_layout.addWidget(QLabel("Valor:"))
        input_item_layout.addWidget(self.spin_valor)
        input_item_layout.addSpacing(15)
        input_item_layout.addWidget(self.chk_ressarcimento)
        input_item_layout.addWidget(self.lbl_vlr_ressarc)
        input_item_layout.addWidget(self.spin_vlr_ressarc)
        input_item_layout.addStretch()
        input_item_layout.addWidget(self.btn_add_item)

        layout_itens.addLayout(input_item_layout)

        # Tabela
        self.table_itens = QTableWidget()
        self.colunas = ["Cód. Item", "Quantidade", "Valor", "Valor Total", "Ressarcimento", "Vlr Ressarc"]
        self.table_itens.setColumnCount(len(self.colunas))
        self.table_itens.setHorizontalHeaderLabels(self.colunas)
        self.table_itens.verticalHeader().setVisible(False)
        self.table_itens.setAlternatingRowColors(True)
        self.table_itens.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_itens.setEditTriggers(QTableWidget.NoEditTriggers)
        
        header = self.table_itens.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        layout_itens.addWidget(self.table_itens)

        # Botões Ação
        action_buttons_layout = QHBoxLayout()
        
        self.btn_cancelar = QPushButton(" Cancelar")
        self.btn_cancelar.setObjectName("btn_secondary")
        self.btn_cancelar.setIcon(qta.icon('fa5s.times', color='#a0aec0'))
        self.btn_cancelar.setCursor(Qt.PointingHandCursor)
        
        self.btn_salvar = QPushButton(" Salvar Nota Fiscal")
        self.btn_salvar.setObjectName("btn_primary")
        self.btn_salvar.setIcon(qta.icon('fa5s.check', color='white'))
        self.btn_salvar.setCursor(Qt.PointingHandCursor)
        self.btn_salvar.clicked.connect(self.salvar_tudo)

        action_buttons_layout.addStretch()
        action_buttons_layout.addWidget(self.btn_cancelar)
        action_buttons_layout.addWidget(self.btn_salvar)

        layout_itens.addLayout(action_buttons_layout)
        main_layout.addWidget(card_itens)

    def toggle_ressarcimento(self, checked):
        self.lbl_vlr_ressarc.setVisible(checked)
        self.spin_vlr_ressarc.setVisible(checked)
        if checked:
            self.spin_vlr_ressarc.setFocus()
        else:
            self.spin_vlr_ressarc.setValue(0.0)

    def adicionar_item_tabela(self):
        codigo = self.txt_cod_item.text().strip()
        
        if not codigo:
            QMessageBox.warning(self, "Aviso", "Preencha o código do item.")
            return

        qtd = self.spin_qtd.value()
        vlr_unit = self.spin_valor.value()
        
        if qtd <= 0:
             QMessageBox.warning(self, "Aviso", "A quantidade deve ser maior que zero.")
             self.spin_qtd.setFocus()
             return

        if vlr_unit <= 0:
             QMessageBox.warning(self, "Aviso", "O valor deve ser maior que zero.")
             self.spin_valor.setFocus()
             return

        existe = self.controller.buscar_produto_por_codigo(codigo)
        
        if not existe:
            QMessageBox.warning(
                self, 
                "Item Não Encontrado", 
                f"O código '{codigo}' não está cadastrado no sistema."
            )
            self.txt_cod_item.selectAll()
            self.txt_cod_item.setFocus()
            return

        total = qtd * vlr_unit
        
        tem_ressarc = self.chk_ressarcimento.isChecked()
        vlr_ressarc = self.spin_vlr_ressarc.value() if tem_ressarc else 0.0

        row = self.table_itens.rowCount()
        self.table_itens.insertRow(row)

        def criar_item_centro(texto):
            item = QTableWidgetItem(str(texto))
            item.setTextAlignment(Qt.AlignCenter)
            return item

        self.table_itens.setItem(row, 0, criar_item_centro(codigo))
        self.table_itens.setItem(row, 1, criar_item_centro(qtd))
        self.table_itens.setItem(row, 2, criar_item_centro(f"R$ {vlr_unit:.2f}"))
        self.table_itens.setItem(row, 3, criar_item_centro(f"R$ {total:.2f}"))
        
        status_ressarc = "SIM" if tem_ressarc else "NÃO"
        item_status = criar_item_centro(status_ressarc)
        item_status.setForeground(Qt.green if tem_ressarc else Qt.gray)
        self.table_itens.setItem(row, 4, item_status)
        
        self.table_itens.setItem(row, 5, criar_item_centro(f"R$ {vlr_ressarc:.2f}"))

        self.txt_cod_item.clear()
        self.spin_qtd.setValue(0)
        self.spin_valor.setValue(0.00)
        self.chk_ressarcimento.setChecked(False)
        self.txt_cod_item.setFocus()

    def buscar_emitente(self):
        cnpj_sujo = self.txt_cnpj.text()
        if len(cnpj_sujo) >= 14:
            nome = self.controller.buscar_cliente_por_cnpj(cnpj_sujo)
            if nome:
                self.txt_emitente.setText(nome)
            else:
                self.txt_emitente.setText("NÃO CADASTRADO")

    def salvar_tudo(self):
        qtd_itens = self.table_itens.rowCount()
        if qtd_itens == 0:
            QMessageBox.warning(self, "Erro", "Adicione pelo menos um item à nota.")
            return
            
        dados_nota = {
            'cnpj': self.txt_cnpj.text(),
            'cnpj_remetente': self.txt_cnpj_remetente.text(), # Capturando o campo novo
            'numero': self.txt_num_nf.text(),
            'emissao': self.dt_emissao.date().toPython(),
            'recebimento': self.dt_recebimento.date().toPython()
        }
        
        lista_itens = []
        for row in range(qtd_itens):
            lista_itens.append({
                'codigo': self.table_itens.item(row, 0).text(),
                'qtd': self.table_itens.item(row, 1).text(),
                'valor': float(self.table_itens.item(row, 2).text().replace("R$ ", "").replace(",", ".")),
                'ressarcimento': float(self.table_itens.item(row, 5).text().replace("R$ ", "").replace(",", "."))
            })
            
        try:
            self.controller.salvar_nota_entrada(dados_nota, lista_itens)
            QMessageBox.information(self, "Sucesso", "Nota lançada com sucesso!")
            self.table_itens.setRowCount(0)
            self.txt_num_nf.clear()
            self.txt_cnpj_remetente.clear()
            self.txt_cod_item.clear()
        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))