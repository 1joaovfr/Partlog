import sys
import math
from datetime import datetime, date
import qtawesome as qta
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                               QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
                               QMessageBox, QAbstractItemView, QDialog, QDateEdit, 
                               QLineEdit, QFormLayout, QDoubleSpinBox)
from PySide6.QtCore import Qt

from controllers.ajuste_controller import AjusteController
from styles.ajuste_styles import AJUSTE_STYLES

# --- POPUP DE EDIÇÃO ---
class EdicaoPopup(QDialog):
    def __init__(self, item_dto, parent=None):
        super().__init__(parent)
        self.dto = item_dto
        self.setWindowTitle(f"Ajuste - Item {self.dto.id_item}")
        self.setFixedWidth(400)
        
        # Se tiver retorno, bloqueia visualmente e põe aviso
        self.bloqueado = False
        if self.dto.nf_retorno:
            self.bloqueado = True

        self.setup_ui()
        self.carregar_valores()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        if self.bloqueado:
            lbl_aviso = QLabel("⚠️ Este item possui Nota de Retorno vinculada. Edição não permitida.")
            lbl_aviso.setObjectName("lbl_aviso")
            layout.addWidget(lbl_aviso)

        form = QFormLayout()
        form.setSpacing(10)

        # --- CAMPOS EDITÁVEIS (Se não bloqueado) ---
        
        # 1. Nota Fiscal (Header)
        self.txt_nf = QLineEdit()
        form.addRow("Nota Fiscal:", self.txt_nf)

        # 2. Emissão (Header)
        self.dt_emissao = QDateEdit()
        self.dt_emissao.setCalendarPopup(True)
        form.addRow("Data Emissão:", self.dt_emissao)

        # 3. CNPJ Remetente (Header - Muda o dono)
        self.txt_cnpj_rem = QLineEdit()
        self.txt_cnpj_rem.setPlaceholderText("Apenas números")
        form.addRow("CNPJ Remetente:", self.txt_cnpj_rem)
        
        # Label informativa do nome (não editável diretamente aqui, muda via CNPJ)
        self.lbl_nome_rem = QLabel(self.dto.nome_remetente)
        self.lbl_nome_rem.setObjectName("lbl_info")
        form.addRow("Nome Remetente:", self.lbl_nome_rem)

        # Separador visual
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        form.addRow(line)

        # 4. Código Item
        self.txt_cod_item = QLineEdit()
        form.addRow("Cód. Item:", self.txt_cod_item)

        # 5. Código Avaria
        self.txt_cod_avaria = QLineEdit()
        form.addRow("Cód. Avaria:", self.txt_cod_avaria)

        # 6. Código Análise (Define o status)
        self.txt_cod_analise = QLineEdit()
        self.txt_cod_analise.setPlaceholderText("Ex: 100, 200")
        form.addRow("Cód. Análise:", self.txt_cod_analise)
        
        # Label status (Informativo)
        self.lbl_status = QLabel(self.dto.status)
        self.lbl_status.setObjectName("lbl_info")
        form.addRow("Status Atual:", self.lbl_status)

        # 7. Valor
        self.spin_valor = QDoubleSpinBox()
        self.spin_valor.setRange(0, 999999.99)
        self.spin_valor.setPrefix("R$ ")
        form.addRow("Valor:", self.spin_valor)

        # 8. Num Serie
        self.txt_serie = QLineEdit()
        form.addRow("Nº Série:", self.txt_serie)

        layout.addLayout(form)

        # --- BOTÕES ---
        btn_layout = QHBoxLayout()
        
        self.btn_excluir = QPushButton("Excluir Item")
        self.btn_excluir.setObjectName("btn_excluir")
        self.btn_excluir.setCursor(Qt.PointingHandCursor)
        self.btn_excluir.clicked.connect(self.accept_excluir)
        
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.clicked.connect(self.reject)
        
        self.btn_salvar = QPushButton("Salvar Alterações")
        self.btn_salvar.setObjectName("btn_primary") # Usando estilo do tema principal
        self.btn_salvar.clicked.connect(self.accept_salvar)

        btn_layout.addWidget(self.btn_excluir)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_cancelar)
        btn_layout.addWidget(self.btn_salvar)

        layout.addLayout(btn_layout)

        if self.bloqueado:
            self.txt_nf.setReadOnly(True)
            self.dt_emissao.setReadOnly(True)
            self.txt_cnpj_rem.setReadOnly(True)
            self.txt_cod_item.setReadOnly(True)
            self.txt_cod_avaria.setReadOnly(True)
            self.txt_cod_analise.setReadOnly(True)
            self.spin_valor.setReadOnly(True)
            self.txt_serie.setReadOnly(True)
            self.btn_salvar.setDisabled(True)
            self.btn_excluir.setDisabled(True)

    def carregar_valores(self):
        self.txt_nf.setText(self.dto.nf_entrada)
        
        if self.dto.data_emissao:
            try:
                dt = datetime.strptime(self.dto.data_emissao, "%d/%m/%Y").date()
                self.dt_emissao.setDate(dt)
            except: pass
            
        self.txt_cnpj_rem.setText(self.dto.cnpj_remetente)
        self.txt_cod_item.setText(self.dto.codigo_item)
        self.txt_cod_avaria.setText(self.dto.codigo_avaria)
        self.txt_cod_analise.setText(self.dto.codigo_analise)
        self.spin_valor.setValue(self.dto.valor_item)
        self.txt_serie.setText(self.dto.numero_serie)

    def get_dados(self):
        """Retorna dicionário com os dados editados"""
        data_emissao_str = self.dt_emissao.date().toString("dd/MM/yyyy")
        # Para salvar no banco geralmente precisa converter para object date python ou string ISO
        # O model lá está esperando o formato para update. Vamos passar objeto date
        data_emissao_obj = self.dt_emissao.date().toPython()

        return {
            'nf_entrada': self.txt_nf.text(),
            'data_emissao': data_emissao_obj,
            'cnpj_remetente': self.txt_cnpj_rem.text(),
            'codigo_item': self.txt_cod_item.text(),
            'codigo_avaria': self.txt_cod_avaria.text(),
            'codigo_analise': self.txt_cod_analise.text(),
            'valor_item': self.spin_valor.value(),
            'numero_serie': self.txt_serie.text()
        }
    
    # Sinais customizados para saber qual botão foi clicado
    def accept_salvar(self):
        self.done(1) # Código 1 = Salvar
        
    def accept_excluir(self):
        self.done(2) # Código 2 = Excluir

# --- PÁGINA PRINCIPAL ---
class PageAjustes(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("PageAjustes")
        self.controller = AjusteController()
        
        self.setWindowTitle("Módulo de Ajustes e Correções")
        self.setStyleSheet(AJUSTE_STYLES)
        
        self.todos_dados = []
        self.dados_filtrados = []
        
        self.pagina_atual = 1
        self.itens_por_pagina = 50 
        self.total_paginas = 1
        self.filtros_widgets = {}

        self.setup_ui()
        self.carregar_dados()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        self.card = QFrame()
        self.card.setObjectName("FormCard")
        card_layout = QVBoxLayout(self.card)

        # Cabeçalho
        header_layout = QHBoxLayout()
        lbl_titulo = QLabel("Ajuste de Divergências")
        lbl_titulo.setObjectName("SectionTitle")
        header_layout.addWidget(lbl_titulo)
        
        lbl_instrucao = QLabel("Duplo clique na linha para editar/excluir")
        lbl_instrucao.setStyleSheet("color: #a0aec0; font-style: italic;")
        header_layout.addWidget(lbl_instrucao, 0, Qt.AlignRight)
        
        card_layout.addLayout(header_layout)

        # Tabela (Cópia da estrutura do relatório)
        self.colunas = [
            "Lançamento", "Recebimento", "Análise", "Status", "Cód. Análise",
            "CNPJ Remetente", "Remetente", 
            "CNPJ Emitente", "Emitente", "Grp. Cliente", "Cidade", "UF", "Região", 
            "Emissão", "Nota Fiscal",
            "Item", "Grp. Item", "Num. Série", "Cód. Avaria", "Desc. Avaria", 
            "Valor", "Ressarc.", "Retorno"
        ]
        
        self.table = QTableWidget()
        self.table.setColumnCount(len(self.colunas))
        self.table.setHorizontalHeaderLabels(self.colunas)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setShowGrid(False)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers) # Edição só via popup
        self.table.setFocusPolicy(Qt.StrongFocus)
        
        # --- EVENTO DE DUPLO CLIQUE ---
        self.table.cellDoubleClicked.connect(self.abrir_edicao)

        card_layout.addWidget(self.table)

        # Paginação
        pag_layout = QHBoxLayout()
        self.btn_prev = QPushButton(" Anterior")
        self.btn_prev.setObjectName("btn_pag")
        self.btn_prev.clicked.connect(self.voltar_pagina)

        self.lbl_paginacao = QLabel(f"Página 0 de 0")
        self.lbl_paginacao.setObjectName("lbl_pag")
        self.lbl_paginacao.setAlignment(Qt.AlignCenter)

        self.btn_next = QPushButton("Próximo ")
        self.btn_next.setObjectName("btn_pag")
        self.btn_next.clicked.connect(self.avancar_pagina)

        pag_layout.addWidget(self.btn_prev)
        pag_layout.addStretch()
        pag_layout.addWidget(self.lbl_paginacao)
        pag_layout.addStretch()
        pag_layout.addWidget(self.btn_next)

        card_layout.addLayout(pag_layout)
        main_layout.addWidget(self.card)

        self.criar_linha_filtros()

    def criar_linha_filtros(self):
        self.table.insertRow(0)
        self.table.setRowHeight(0, 35) 
        for col_idx in range(len(self.colunas)):
            inp = QLineEdit()
            inp.setPlaceholderText("Filtrar...")
            inp.setStyleSheet("""
                QLineEdit { background-color: #12161f; border: 1px solid #2c3545; color: #dce1e8; font-size: 11px; }
                QLineEdit:focus { border: 1px solid #3a5f8a; }
            """)
            inp.textChanged.connect(self.processar_filtragem)
            self.filtros_widgets[col_idx] = inp
            self.table.setCellWidget(0, col_idx, inp)

    def carregar_dados(self):
        try:
            self.todos_dados_dtos = self.controller.buscar_dados() # Guarda lista de objetos
            self.todos_dados_lista = [] # Guarda lista de listas para exibição na table
            
            for item in self.todos_dados_dtos:
                linha = [
                    item.data_lancamento, item.data_recebimento, item.data_analise,
                    item.status, item.codigo_analise,
                    item.cnpj_remetente, item.nome_remetente,
                    item.cnpj, item.nome_cliente, item.grupo_cliente, item.cidade, item.estado, item.regiao,
                    item.data_emissao, item.nf_entrada,
                    item.codigo_item, item.grupo_item, item.numero_serie,
                    item.codigo_avaria, item.descricao_avaria,
                    f"R$ {item.valor_item:.2f}", f"R$ {item.ressarcimento:.2f}",
                    item.nf_retorno if item.nf_retorno else ""
                ]
                self.todos_dados_lista.append(linha)

            self.dados_filtrados = list(self.todos_dados_lista)
            self.calcular_paginacao()
            self.atualizar_tabela()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar dados: {e}")

    def abrir_edicao(self, row, col):
        if row == 0: return # Clicou no filtro
        
        # Precisamos achar o DTO correspondente.
        # Como temos paginação e filtro, o índice visual 'row' não bate com o índice da lista 'todos_dados_dtos'.
        # A estratégia segura: Recuperar o CNPJ, NF e Item da linha selecionada e buscar na lista de DTOs.
        # OU: Mapear o DTO direto na linha (UserRole). Vamos pelo mais simples: Recarregar tudo é pesado? Não.
        # Vamos usar o índice da lista filtrada e paginada.
        
        index_real = (self.pagina_atual - 1) * self.itens_por_pagina + (row - 1)
        
        # ATENÇÃO: self.dados_filtrados é uma lista de strings (visual). 
        # Precisamos do OBJETO DTO.
        # Solução Rápida: Recriar a lógica de filtro sobre os DTOs também ou armazenar o DTO na lista visual.
        # Vamos simplificar: Ao carregar, vamos guardar o DTO 'escondido' na tabela se possível? Não, tabela limpa.
        
        # Vamos achar o DTO comparando ID. Precisamos que o ID esteja na lista visual? Não mostramos ID na tela.
        # Vamos pegar os dados chave da linha clicada:
        nf = self.table.item(row, 14).text()
        cod_item = self.table.item(row, 15).text()
        serie = self.table.item(row, 17).text()
        
        # Procura na lista original de DTOs
        dto_selecionado = None
        for dto in self.todos_dados_dtos:
            if str(dto.nf_entrada) == nf and str(dto.codigo_item) == cod_item and str(dto.numero_serie) == serie:
                dto_selecionado = dto
                break
        
        if not dto_selecionado:
            return

        dialog = EdicaoPopup(dto_selecionado, self)
        resultado = dialog.exec()
        
        if resultado == 1: # Salvar
            novos_dados = dialog.get_dados()
            try:
                self.controller.salvar_edicao(dto_selecionado, novos_dados)
                QMessageBox.information(self, "Sucesso", "Registro atualizado!")
                self.carregar_dados() # Recarrega tudo
            except Exception as e:
                QMessageBox.critical(self, "Erro", str(e))
                
        elif resultado == 2: # Excluir
            resp = QMessageBox.question(self, "Confirmar", "Deseja realmente excluir este item?", QMessageBox.Yes | QMessageBox.No)
            if resp == QMessageBox.Yes:
                try:
                    self.controller.excluir_registro(dto_selecionado.id_item)
                    QMessageBox.information(self, "Sucesso", "Item excluído.")
                    self.carregar_dados()
                except Exception as e:
                    QMessageBox.critical(self, "Erro", str(e))

    # Métodos de Paginação e Filtro (Idênticos ao Relatorio, omitidos para brevidade mas devem estar aqui)
    def processar_filtragem(self):
        filtros_ativos = {}
        for col_idx, widget in self.filtros_widgets.items():
            texto = widget.text().lower().strip()
            if texto:
                filtros_ativos[col_idx] = texto
        
        if not filtros_ativos:
            self.dados_filtrados = list(self.todos_dados)
        else:
            self.dados_filtrados = []
            for linha in self.todos_dados:
                match = True
                for col_idx, texto_filtro in filtros_ativos.items():
                    valor_celula = str(linha[col_idx]).lower() if linha[col_idx] else ""
                    
                    # Verifica se é coluna de data e tenta lógica de range
                    if col_idx in self.colunas_data and ("-" in texto_filtro or " a " in texto_filtro):
                        is_match_data = self.verificar_range_data(valor_celula, texto_filtro)
                        if not is_match_data:
                            match = False
                            break
                    else:
                        # Lógica padrão (texto contém texto)
                        if texto_filtro not in valor_celula:
                            match = False
                            break
                if match:
                    self.dados_filtrados.append(linha)

        self.pagina_atual = 1
        self.calcular_paginacao()
        self.atualizar_tabela()
    
    def calcular_paginacao(self):
        total_itens = len(self.dados_filtrados)
        self.total_paginas = math.ceil(total_itens / self.itens_por_pagina)
        if self.total_paginas < 1: self.total_paginas = 1

    def atualizar_tabela(self):
        inicio = (self.pagina_atual - 1) * self.itens_por_pagina
        fim = inicio + self.itens_por_pagina
        dados_da_pagina = self.dados_filtrados[inicio:fim]

        qtd_linhas_necessarias = 1 + len(dados_da_pagina)
        self.table.setRowCount(qtd_linhas_necessarias)

        for i, row_data in enumerate(dados_da_pagina):
            table_row = i + 1 
            for col_idx, valor in enumerate(row_data):
                item = QTableWidgetItem(str(valor) if valor is not None else "")
                item.setTextAlignment(Qt.AlignCenter)
                item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                self.table.setItem(table_row, col_idx, item)

        self.lbl_paginacao.setText(f"Página {self.pagina_atual} de {self.total_paginas} (Total: {len(self.dados_filtrados)})")
        self.btn_prev.setDisabled(self.pagina_atual == 1)
        self.btn_next.setDisabled(self.pagina_atual >= self.total_paginas)
    
    def avancar_pagina(self):
        if self.pagina_atual < self.total_paginas:
            self.pagina_atual += 1
            self.atualizar_tabela()

    def voltar_pagina(self):
        if self.pagina_atual > 1:
            self.pagina_atual -= 1
            self.atualizar_tabela()
