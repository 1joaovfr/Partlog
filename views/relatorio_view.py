import sys
import math
from datetime import date, datetime # Importado datetime para conversão
import qtawesome as qta
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                               QFrame, QTableWidget, QTableWidgetItem, 
                               QFileDialog, QMessageBox, QAbstractItemView,
                               QDialog, QDateEdit, QLineEdit)
from PySide6.QtCore import Qt, QPoint

from controllers.relatorio_controller import RelatorioController
from styles.relatorio_styles import RELATORIO_STYLES

class PageRelatorio(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("PageRelatorio")
        
        self.controller = RelatorioController()
        
        self.setWindowTitle("Relatório Geral de Garantias")
        self.setStyleSheet(RELATORIO_STYLES)
        
        self.todos_dados = []
        self.dados_filtrados = []
        
        self.pagina_atual = 1
        self.itens_por_pagina = 50 
        self.total_paginas = 1

        self.filtros_widgets = {}

        # Mapeamento dos índices das colunas que são DATAS
        # 0=Lançamento, 1=Recebimento, 2=Análise, 13=Emissão, 22=Retorno
        self.colunas_data = [0, 1, 2, 13, 22]

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
        header_layout.addWidget(lbl_titulo)
        
        card_layout.addLayout(header_layout)

        # --- DEFINIÇÃO DAS COLUNAS ---
        self.colunas = [
            "Lançamento", "Recebimento", "Análise", "Status", "Cód. Análise",
            "CNPJ Remetente", "Remetente", 
            "CNPJ Emitente", "Emitente", "Grp. Cliente", "Cidade", "UF", "Região", 
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
        self.table.setShowGrid(False)
        self.table.setFocusPolicy(Qt.StrongFocus)
        
        header = self.table.horizontalHeader()
        header.setDefaultSectionSize(120)
        header.setStretchLastSection(True)
        header.resizeSection(6, 200)
        header.resizeSection(8, 200)

        card_layout.addWidget(self.table)

        # --- PAGINAÇÃO E EXPORTAÇÃO ---
        pag_layout = QHBoxLayout()
        
        self.btn_prev = QPushButton(" Anterior")
        self.btn_prev.setObjectName("btn_pag")
        self.btn_prev.setIcon(qta.icon('fa5s.chevron-left', color='white')) 
        self.btn_prev.clicked.connect(self.voltar_pagina)

        self.btn_next = QPushButton("Próximo ")
        self.btn_next.setObjectName("btn_pag")
        self.btn_next.setLayoutDirection(Qt.RightToLeft)
        self.btn_next.setIcon(qta.icon('fa5s.chevron-right', color='white'))
        self.btn_next.clicked.connect(self.avancar_pagina)

        pag_layout.addWidget(self.btn_prev)
        pag_layout.addWidget(self.btn_next)
        pag_layout.addStretch()

        self.lbl_paginacao = QLabel(f"Página 0 de 0")
        self.lbl_paginacao.setObjectName("lbl_pag")
        self.lbl_paginacao.setAlignment(Qt.AlignCenter)
        pag_layout.addWidget(self.lbl_paginacao)

        pag_layout.addStretch()

        self.btn_excel = QPushButton(" Exportar Excel") 
        self.btn_excel.setCursor(Qt.PointingHandCursor)
        self.btn_excel.setIcon(qta.icon('fa5s.file-excel', color='#8ab4f8', scale_factor=1.0)) 
        self.btn_excel.setIconSize(qta.QtCore.QSize(24, 24)) 
        self.btn_excel.setObjectName("btn_excel") 
        self.btn_excel.setToolTip("Exportar dados visualizados para Excel")
        self.btn_excel.clicked.connect(self.abrir_formulario_exportacao) 
        
        pag_layout.addWidget(self.btn_excel)

        card_layout.addLayout(pag_layout)
        main_layout.addWidget(self.card)

        self.criar_linha_filtros()

    def criar_linha_filtros(self):
        self.table.insertRow(0)
        self.table.setRowHeight(0, 35) 

        for col_idx in range(len(self.colunas)):
            inp = QLineEdit()
            
            # Placeholder diferenciado para colunas de data
            if col_idx in self.colunas_data:
                inp.setPlaceholderText("dd/mm/aa - dd/mm/aa")
                inp.setToolTip("Ex: 01/01/2024 - 31/01/2024")
            else:
                inp.setPlaceholderText("Filtrar...")
                
            inp.setStyleSheet("""
                QLineEdit { 
                    background-color: #12161f; 
                    border: 1px solid #2c3545; 
                    border-radius: 0px;
                    color: #dce1e8;
                    font-size: 11px;
                }
                QLineEdit:focus { border: 1px solid #3a5f8a; }
            """)
            inp.textChanged.connect(self.processar_filtragem)
            self.filtros_widgets[col_idx] = inp
            self.table.setCellWidget(0, col_idx, inp)

    def carregar_dados(self):
        try:
            lista_dtos = self.controller.buscar_dados()
            self.todos_dados = []
            
            for item in lista_dtos:
                def fmt_moeda(val): 
                    if val is None: return "R$ 0,00"
                    return f"R$ {val:.2f}"

                linha = [
                    item.data_lancamento,     # 0
                    item.data_recebimento,    # 1
                    item.data_analise,        # 2
                    item.status,              # 3
                    item.codigo_analise,      # 4
                    item.cnpj_remetente,      # 5
                    item.nome_remetente,      # 6
                    item.cnpj,                # 7
                    item.nome_cliente,        # 8
                    item.grupo_cliente,       # 9
                    item.cidade,              # 10
                    item.estado,              # 11
                    item.regiao,              # 12
                    item.data_emissao,        # 13
                    item.nf_entrada,          # 14
                    item.codigo_item,         # 15
                    item.grupo_item,          # 16
                    item.numero_serie,        # 17
                    item.codigo_avaria,       # 18
                    item.descricao_avaria,    # 19
                    fmt_moeda(item.valor_item),    # 20
                    fmt_moeda(item.ressarcimento), # 21
                    item.data_retorno,        # 22
                    item.nf_retorno,          # 23
                    item.tipo_retorno         # 24
                ]
                self.todos_dados.append(linha)

            self.dados_filtrados = list(self.todos_dados)
            self.calcular_paginacao()
            self.atualizar_tabela()
            
        except Exception as e:
            print(f"Erro ao carregar dados na View: {e}")
            import traceback
            traceback.print_exc()

    # --- LÓGICA DE FILTRO ATUALIZADA ---
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

    def verificar_range_data(self, data_celula_str, filtro_str):
        """
        Tenta comparar data_celula (dd/mm/yyyy) com um range no filtro (ex: '01/01/2023 - 31/01/2023')
        Retorna True se estiver dentro, False se fora.
        Se o filtro estiver mal formatado, retorna False (ou True se quiser fallback).
        """
        try:
            # 1. Converte a data da célula
            # data_celula_str vem do banco, ex: "28/01/2026"
            dt_celula = datetime.strptime(data_celula_str.strip(), "%d/%m/%Y").date()
            
            # 2. Separa o filtro (aceita "-" ou " a ")
            if " a " in filtro_str:
                partes = filtro_str.split(" a ")
            else:
                partes = filtro_str.split("-")
            
            if len(partes) != 2:
                return False # Formato inválido, não bate

            ini_str = partes[0].strip()
            fim_str = partes[1].strip()
            
            # 3. Converte as datas do filtro
            # Tenta formatos com 4 digitos no ano ou 2 digitos
            fmt = "%d/%m/%Y" if len(ini_str.split("/")[-1]) == 4 else "%d/%m/%y"
            dt_ini = datetime.strptime(ini_str, fmt).date()
            
            fmt = "%d/%m/%Y" if len(fim_str.split("/")[-1]) == 4 else "%d/%m/%y"
            dt_fim = datetime.strptime(fim_str, fmt).date()
            
            # 4. Compara
            return dt_ini <= dt_celula <= dt_fim

        except ValueError:
            # Se deu erro de conversão (data inválida ou incompleta), 
            # assumimos que não é um range válido ainda (enquanto o user digita)
            # Retornamos False para esconder, ou poderiamos tentar fallback textual.
            return False
        except Exception:
            return False

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

    def abrir_formulario_exportacao(self):
        # 1. Verifica se tem algum dado para exportar
        if not self.dados_filtrados:
            QMessageBox.warning(self, "Aviso", "Não há dados na tela para exportar.")
            return

        # 2. Verifica se existe algum filtro ativo
        tem_filtro_ativo = False
        for widget in self.filtros_widgets.values():
            if widget.text().strip():
                tem_filtro_ativo = True
                break
        
        # 3. Se NÃO tiver filtro, pede confirmação
        if not tem_filtro_ativo:
            resp = QMessageBox.question(
                self, 
                "Exportar Tudo?", 
                f"Nenhum filtro aplicado. Deseja exportar TODOS os registros ({len(self.dados_filtrados)} linhas)?",
                QMessageBox.Yes | QMessageBox.No
            )
            if resp == QMessageBox.No:
                return

        # 4. Seleciona onde salvar
        nome_padrao = f"Relatorio_Garantias_{date.today()}.xlsx"
        path, _ = QFileDialog.getSaveFileName(self, "Salvar Excel", nome_padrao, "Excel Files (*.xlsx)")
        
        if path:
            sucesso = self.controller.exportar_excel(path, self.dados_filtrados, self.colunas)
            if sucesso:
                QMessageBox.information(self, "Sucesso", "Planilha exportada com sucesso!")
            else:
                QMessageBox.critical(self, "Erro", "Falha ao gerar o arquivo Excel.")