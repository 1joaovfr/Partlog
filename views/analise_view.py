import sys
import qtawesome as qta
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                               QComboBox, QPushButton, QFrame, QTableWidget, QTableWidgetItem, 
                               QHeaderView, QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIntValidator

from controllers import AnaliseController
from styles.analise_styles import ANALISE_STYLES

class PageAnalise(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = AnaliseController()
        self.setWindowTitle("Análise Técnica de Itens")
        self.setStyleSheet(ANALISE_STYLES)

        self.codigos_avaria = {
            "001": {"desc": "Dano Físico / Quebra", "status": "Improcedente"},
            "002": {"desc": "Defeito de Fabricação", "status": "Procedente"},
            "003": {"desc": "Instalação Incorreta", "status": "Improcedente"},
            "004": {"desc": "Ruído Excessivo", "status": "Procedente"},
        }
        self.item_atual = None

        layout = QVBoxLayout(self) 
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # --- CARD TABELA ---
        card_tabela = QFrame(objectName="FormCard")
        layout_tabela = QVBoxLayout(card_tabela)
        
        lbl_lista = QLabel("Itens Aguardando Análise")
        lbl_lista.setObjectName("SectionTitle")
        layout_tabela.addWidget(lbl_lista)

        self.table = QTableWidget()
        colunas = ["ENTRADA", "ITEM", "CÓD. ANÁLISE", "NOTA FISCAL", "RESSARCIMENTO"]
        self.table.setColumnCount(len(colunas))
        self.table.setHorizontalHeaderLabels(colunas)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setShowGrid(True) 
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        
        self.table.itemClicked.connect(self.carregar_item_para_analise)

        layout_tabela.addWidget(self.table)
        layout.addWidget(card_tabela, stretch=1)

        # --- CARD FORMULÁRIO ---
        card_form = QFrame(objectName="FormCard")
        layout_form = QVBoxLayout(card_form)
        
        lbl_analise = QLabel("Dados da Análise Técnica")
        lbl_analise.setObjectName("SectionTitle")
        layout_form.addWidget(lbl_analise)

        # =================================================================
        # LINHA 1: TODOS OS INPUTS (TAMANHOS IGUAIS)
        # Removemos setFixedWidth e aplicamos stretch=1 em TODOS
        # =================================================================
        row1 = QHBoxLayout()
        
        # 1. Cód. Análise
        self.txt_id_item = QLineEdit(placeholderText="Cód.", readOnly=True)
        # Sem FixedWidth
        
        # 2. Peça
        self.txt_peca_nome = QLineEdit(placeholderText="Selecione um item...", readOnly=True)
        
        # 3. Série
        self.txt_serie = QLineEdit(placeholderText="Nº Série")
        # Sem FixedWidth
        
        # 4. Origem
        self.combo_origem = QComboBox()
        self.combo_origem.addItem("Produzido")
        self.combo_origem.addItem("Revenda")
        self.combo_origem.currentTextChanged.connect(self.verificar_origem)
        # Sem FixedWidth

        # 5. Fornecedor
        self.txt_fornecedor = QLineEdit(placeholderText="Cód.")
        self.txt_fornecedor.setMaxLength(4)
        self.txt_fornecedor.setValidator(QIntValidator(0, 9999))
        self.txt_fornecedor.setEnabled(False) 
        # Sem FixedWidth

        # Adicionando ao Layout com STRETCH=1 para todos terem o mesmo peso
        row1.addWidget(QLabel("Cód. Análise:"))
        row1.addWidget(self.txt_id_item, stretch=1)
        
        row1.addWidget(QLabel("Item:"))
        row1.addWidget(self.txt_peca_nome, stretch=1)
        
        row1.addWidget(QLabel("Série:"))
        row1.addWidget(self.txt_serie, stretch=1)
        
        row1.addWidget(QLabel("Origem:"))
        row1.addWidget(self.combo_origem, stretch=1)
        
        row1.addWidget(QLabel("Fornecedor:"))
        row1.addWidget(self.txt_fornecedor, stretch=1) 

        layout_form.addLayout(row1)

        # =================================================================
        # LINHA 2: DIAGNÓSTICO E AÇÕES
        # =================================================================
        row_diag = QHBoxLayout()

        self.combo_cod_avaria = QComboBox()
        self.combo_cod_avaria.addItem("Selecione...", None)
        for cod in self.codigos_avaria:
            self.combo_cod_avaria.addItem(f"{cod}", cod)
        self.combo_cod_avaria.setFixedWidth(130) # Avaria mantive fixo pois é um seletor pequeno
        self.combo_cod_avaria.currentTextChanged.connect(self.atualizar_detalhes_avaria)

        self.txt_desc_avaria = QLineEdit(readOnly=True, placeholderText="Descrição da avaria...")

        self.lbl_status_resultado = QLabel("AGUARDANDO")
        self.lbl_status_resultado.setObjectName("StatusNeutro")
        self.lbl_status_resultado.setAlignment(Qt.AlignCenter)
        self.lbl_status_resultado.setFixedSize(130, 32)

        self.btn_cancelar = QPushButton(" Cancelar")
        self.btn_cancelar.setObjectName("btn_secondary")
        self.btn_cancelar.setIcon(qta.icon('fa5s.times', color='#a0aec0'))
        
        self.btn_concluir = QPushButton(" Concluir")
        self.btn_concluir.setObjectName("btn_primary")
        self.btn_concluir.setIcon(qta.icon('fa5s.check-double', color='white'))
        self.btn_concluir.clicked.connect(self.salvar_analise)

        row_diag.addWidget(QLabel("Cód. Avaria:"))
        row_diag.addWidget(self.combo_cod_avaria)
        row_diag.addWidget(self.txt_desc_avaria, stretch=1) # A descrição ocupa o resto
        row_diag.addWidget(self.lbl_status_resultado)
        row_diag.addSpacing(10)
        row_diag.addWidget(self.btn_cancelar)
        row_diag.addWidget(self.btn_concluir)

        layout_form.addLayout(row_diag)
        layout.addWidget(card_form)

        self.carregar_dados_tabela()
        self.bloquear_form(True)

    def verificar_origem(self, texto):
        if texto == "Revenda":
            self.txt_fornecedor.setEnabled(True)
            self.txt_fornecedor.setPlaceholderText("0000")
            self.txt_fornecedor.setFocus()
        else:
            self.txt_fornecedor.clear()
            self.txt_fornecedor.setEnabled(False)
            self.txt_fornecedor.setPlaceholderText("Bloq.")

    def carregar_item_para_analise(self, item):
        row = item.row()
        id_item = str(self.table.item(row, 0).data(Qt.UserRole))
        codigo_analise_visual = self.table.item(row, 2).text()
        desc_item = self.table.item(row, 1).text()

        self.bloquear_form(False)
        self.item_atual = id_item
        self.txt_id_item.setText(codigo_analise_visual)
        self.txt_peca_nome.setText(desc_item)
        
        self.txt_serie.clear()
        
        self.combo_origem.setCurrentIndex(0) 
        self.verificar_origem("Produzido")   
        
        self.combo_cod_avaria.setCurrentIndex(0)
        self.txt_serie.setFocus()

    def atualizar_detalhes_avaria(self, text):
        if not text: return
        codigo_puro = text.split(" ")[0]
        dados = self.codigos_avaria.get(codigo_puro)
        
        if dados:
            self.txt_desc_avaria.setText(dados['desc'])
            status = dados['status']
            self.lbl_status_resultado.setText(status.upper())
            
            if status == "Procedente":
                self.lbl_status_resultado.setObjectName("StatusProcedente")
            else:
                self.lbl_status_resultado.setObjectName("StatusImprocedente")
        else:
            self.txt_desc_avaria.clear()
            self.lbl_status_resultado.setText("AGUARDANDO")
            self.lbl_status_resultado.setObjectName("StatusNeutro")
        
        self.lbl_status_resultado.style().unpolish(self.lbl_status_resultado)
        self.lbl_status_resultado.style().polish(self.lbl_status_resultado)

    def bloquear_form(self, bloquear):
        inputs = [self.txt_serie, self.combo_origem, self.combo_cod_avaria, self.btn_concluir]
        for widget in inputs:
            widget.setEnabled(not bloquear)
        
        if bloquear:
            self.txt_fornecedor.setEnabled(False)
        else:
            self.verificar_origem(self.combo_origem.currentText())

    def salvar_analise(self):
        if not self.item_atual: return
        
        origem = self.combo_origem.currentText()
        fornecedor = self.txt_fornecedor.text()
        
        if origem == "Revenda" and not fornecedor:
             QMessageBox.warning(self, "Aviso", "Para itens de Revenda, o código do fornecedor é obrigatório.")
             self.txt_fornecedor.setFocus()
             return

        if self.combo_cod_avaria.currentIndex() == 0:
            QMessageBox.warning(self, "Aviso", "Selecione um código de avaria.")
            return

        dados = {
            'serie': self.txt_serie.text(),
            'origem': origem,
            'fornecedor': fornecedor if origem == "Revenda" else "",
            'cod_avaria': self.combo_cod_avaria.currentText().split(" ")[0],
            'desc_avaria': self.txt_desc_avaria.text(),
            'status_resultado': self.lbl_status_resultado.text().capitalize()
        }

        try:
            self.controller.salvar_analise(self.item_atual, dados)
            QMessageBox.information(self, "Sucesso", "Análise salva!")
            self.bloquear_form(True)
            self.txt_id_item.clear()
            self.txt_peca_nome.clear()
            self.txt_desc_avaria.clear()
            self.lbl_status_resultado.setText("AGUARDANDO")
            self.lbl_status_resultado.setObjectName("StatusNeutro")
            self.lbl_status_resultado.style().unpolish(self.lbl_status_resultado)
            self.lbl_status_resultado.style().polish(self.lbl_status_resultado)
            self.carregar_dados_tabela()
        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))
    
    def criar_item_tabela(self, texto):
        item = QTableWidgetItem(str(texto) if texto else "")
        item.setTextAlignment(Qt.AlignCenter)
        return item

    def carregar_dados_tabela(self):
        itens_dto = self.controller.listar_pendentes()
        self.table.setRowCount(0)
        for item in itens_dto:
            row = self.table.rowCount()
            self.table.insertRow(row)
            val_entrada = self.criar_item_tabela(item.data_fmt)
            val_entrada.setData(Qt.UserRole, item.id) 
            self.table.setItem(row, 0, val_entrada)
            self.table.setItem(row, 1, self.criar_item_tabela(item.codigo_item))
            self.table.setItem(row, 2, self.criar_item_tabela(item.codigo_analise))
            self.table.setItem(row, 3, self.criar_item_tabela(item.numero_nota))
            if item.ressarcimento is not None:
                valor_fmt = f"{item.ressarcimento:.2f}".replace('.', ',')
            else:
                valor_fmt = "0,00"
            self.table.setItem(row, 4, self.criar_item_tabela(valor_fmt))