import sys
import math
import os 
from datetime import date, datetime, timedelta
import qtawesome as qta
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                               QFrame, QTableWidget, QTableWidgetItem, QHeaderView, 
                               QFileDialog, QMessageBox, QAbstractItemView,
                               QDialog, QDateEdit, QFormLayout)
from PySide6.QtCore import Qt, QDate, QPoint

from controllers import RelatorioController

from styles.relatorio_styles import RELATORIO_STYLES
from styles.common import get_date_edit_style

class ExportarPopup(QDialog):
    def __init__(self, target_widget, parent=None):
        super().__init__(parent)
        self.target_widget = target_widget 
        
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setFixedWidth(200) 
        
        self.icon_path = self.gerar_icone_calendario()
        
        style_date_edit = get_date_edit_style(self.icon_path)
        self.setStyleSheet(RELATORIO_STYLES + style_date_edit)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        lbl_style = "color: #a0aec0; font-size: 11px; font-weight: bold;"
        
        lbl_ini = QLabel("De:")
        lbl_ini.setStyleSheet(lbl_style)
        self.dt_inicio = QDateEdit()
        self.dt_inicio.setCalendarPopup(True) 
        self.dt_inicio.setDisplayFormat("dd/MM/yyyy")
        hoje = date.today()
        self.dt_inicio.setDate(date(hoje.year, hoje.month, 1))
        
        lbl_fim = QLabel("Até:")
        lbl_fim.setStyleSheet(lbl_style)
        self.dt_fim = QDateEdit()
        self.dt_fim.setCalendarPopup(True)
        self.dt_fim.setDisplayFormat("dd/MM/yyyy")
        self.dt_fim.setDate(hoje)

        layout.addWidget(lbl_ini)
        layout.addWidget(self.dt_inicio)
        layout.addWidget(lbl_fim)
        layout.addWidget(self.dt_fim)
        
        self.btn_confirmar = QPushButton("Exportar")
        self.btn_confirmar.setObjectName("btn_confirmar")
        self.btn_confirmar.setCursor(Qt.PointingHandCursor)
        self.btn_confirmar.clicked.connect(self.accept) 
        
        layout.addSpacing(5)
        layout.addWidget(self.btn_confirmar)
        
        self.posicionar_janela()

    def posicionar_janela(self):
        # 1. Pega a posição absoluta do botão na tela
        pos_global = self.target_widget.mapToGlobal(QPoint(0, 0))
        
        # 2. Calcula o X: Alinha à direita do botão
        x = pos_global.x() + self.target_widget.width() - self.width()
        
        # 3. Calcula o Y: Logo abaixo do botão
        y = pos_global.y() + self.target_widget.height()
        
        self.move(x, y)

    def gerar_icone_calendario(self):
        """Gera um ícone temporário para ser usado no CSS do QDateEdit"""
        icon = qta.icon('fa5s.calendar-alt', color='#8ab4f8') 
        caminho_arquivo = "temp_calendar_icon.png"
        # Salva o ícone em disco para que o CSS possa ler (image: url(...))
        icon.pixmap(16, 16).save(caminho_arquivo)
        # Retorna o caminho absoluto com barras normais (evita erro no Windows)
        return os.path.abspath(caminho_arquivo).replace("\\", "/")


class PageRelatorio(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("PageRelatorio")
        self.controller = RelatorioController()
        self.setWindowTitle("Relatório Geral de Garantias")
        
        # --- APLICAÇÃO DE ESTILO ---
        self.setStyleSheet(RELATORIO_STYLES)
        
        self.todos_dados = []    
        self.pagina_atual = 1
        self.itens_por_pagina = 50 
        self.total_paginas = 1

        self.setup_ui()
        self.carregar_dados() 

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        self.card = QFrame()
        self.card.setObjectName("FormCard")
        card_layout = QVBoxLayout(self.card)

        # --- CABEÇALHO ---
        header_layout = QHBoxLayout()
        lbl_titulo = QLabel("Relatório Analítico de Garantias")
        lbl_titulo.setObjectName("SectionTitle")
        header_layout.addWidget(lbl_titulo, 1)
        
        self.btn_excel = QPushButton()
        self.btn_excel.setCursor(Qt.PointingHandCursor)
        self.btn_excel.setIcon(qta.icon('fa5s.file-excel', color='#8ab4f8', scale_factor=1.2)) 
        self.btn_excel.setIconSize(qta.QtCore.QSize(20, 20)) 
        self.btn_excel.setObjectName("btn_excel") 
        self.btn_excel.setToolTip("Exportar para Excel")
        self.btn_excel.clicked.connect(self.abrir_formulario_exportacao) 
        header_layout.addWidget(self.btn_excel)
        
        card_layout.addLayout(header_layout)

        self.colunas = [
            "Lançamento", "Recebimento", "Análise", "Status", "Cód. Análise",
            "CNPJ", "Cliente", "Grp. Cliente", "Cidade", "UF", "Região", 
            "Emissão", "Nota Fiscal",
            "Item", "Grp. Item", "Num. Série", "Cód. Avaria", "Desc. Avaria", 
            "Valor", "Ressarc.",
            "Retorno", "NF Retorno", "Desc. Retorno"
        ]

        
        self.table = QTableWidget()
        self.table.setColumnCount(len(self.colunas))
        self.table.setHorizontalHeaderLabels(self.colunas)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setShowGrid(False)
        self.table.setFocusPolicy(Qt.NoFocus)
        
        header = self.table.horizontalHeader()
        header.setDefaultSectionSize(120)

        header.resizeSection(17, 250)

        card_layout.addWidget(self.table)

        # --- PAGINAÇÃO ---
        pag_layout = QHBoxLayout()
        self.btn_prev = QPushButton(" Anterior")
        self.btn_prev.setObjectName("btn_pag")
        self.btn_prev.setIcon(qta.icon('fa5s.chevron-left', color='white')) 
        self.btn_prev.clicked.connect(self.voltar_pagina)

        self.lbl_paginacao = QLabel(f"Página 0 de 0")
        self.lbl_paginacao.setObjectName("lbl_pag")
        self.lbl_paginacao.setAlignment(Qt.AlignCenter)

        self.btn_next = QPushButton("Próximo ")
        self.btn_next.setObjectName("btn_pag")
        self.btn_next.setLayoutDirection(Qt.RightToLeft)
        self.btn_next.setIcon(qta.icon('fa5s.chevron-right', color='white'))
        self.btn_next.clicked.connect(self.avancar_pagina)

        pag_layout.addWidget(self.btn_prev)
        pag_layout.addStretch()
        pag_layout.addWidget(self.lbl_paginacao)
        pag_layout.addStretch()
        pag_layout.addWidget(self.btn_next)

        card_layout.addLayout(pag_layout)
        main_layout.addWidget(self.card)

    def carregar_dados(self):
        try:
            lista_dtos = self.controller.buscar_dados()
            self.todos_dados = []
            
            for item in lista_dtos:
                def fmt_moeda(val): return f"R$ {val:.2f}"

                # AQUI É O PULO DO GATO: A ordem deve bater com self.colunas
                linha = [
                    item.data_lancamento,     # 1. Lançamento
                    item.data_recebimento,    # 2. Recebimento
                    item.data_analise,        # 3. Análise
                    item.status,              # 4. Status
                    item.codigo_analise,      # 5. Cód Análise
                    
                    item.cnpj,                # 6. CNPJ
                    item.nome_cliente,        # 7. Cliente
                    item.grupo_cliente,       # 8. Grp Cliente
                    item.cidade,              # 9. Cidade
                    item.estado,              # 10. UF
                    item.regiao,              # 11. Região
                    
                    item.data_emissao,        # 12. Emissão
                    item.nf_entrada,          # 13. NF
                    
                    item.codigo_item,         # 14. Item
                    item.grupo_item,          # 15. Grp Item
                    item.numero_serie,        # 16. Série
                    item.codigo_avaria,       # 17. Cód Avaria
                    item.descricao_avaria,    # 18. Desc Avaria
                    
                    fmt_moeda(item.valor_item),    # 19. Valor
                    fmt_moeda(item.ressarcimento), # 20. Ressarc
                    
                    item.data_retorno,        # 21. Retorno (Data) - Ajustei para bater com seu título
                    item.nf_retorno,          # 22. NF Retorno
                    item.tipo_retorno         # 23. Desc Retorno
                ]
                self.todos_dados.append(linha)

            total_itens = len(self.todos_dados)
            self.total_paginas = math.ceil(total_itens / self.itens_por_pagina)
            if self.total_paginas < 1: self.total_paginas = 1
            self.pagina_atual = 1
            self.atualizar_tabela()
            
        except Exception as e:
            print(f"Erro ao carregar dados na View: {e}")
            import traceback
            traceback.print_exc()

    def atualizar_tabela(self):
        inicio = (self.pagina_atual - 1) * self.itens_por_pagina
        fim = inicio + self.itens_por_pagina
        dados_da_pagina = self.todos_dados[inicio:fim]
        self.table.setRowCount(len(dados_da_pagina))
        for row_idx, row_data in enumerate(dados_da_pagina):
            for col_idx, valor in enumerate(row_data):
                item = QTableWidgetItem(str(valor) if valor is not None else "")
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row_idx, col_idx, item)
        self.lbl_paginacao.setText(f"Página {self.pagina_atual} de {self.total_paginas}")
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

    def abrir_formulario_exportacao(self):
        dialog = ExportarPopup(target_widget=self.btn_excel, parent=self)
        if dialog.exec(): 
            data_ini = dialog.dt_inicio.date().toPython()
            data_fim = dialog.dt_fim.date().toPython()
            
            if data_fim < data_ini:
                QMessageBox.warning(self, "Erro", "A data final não pode ser menor que a inicial.")
                return

            nome_arq = f"Relatorio_Geral_{data_ini}_{data_fim}.xlsx"
            path, _ = QFileDialog.getSaveFileName(self, "Salvar Excel", nome_arq, "Excel Files (*.xlsx)")
            
            if path:
                sucesso = self.controller.exportar_excel(path, data_ini, data_fim)
                if sucesso:
                    QMessageBox.information(self, "Sucesso", "Arquivo gerado com sucesso!")
                else:
                    QMessageBox.warning(self, "Aviso", "Não foram encontrados dados neste período.")