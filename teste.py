import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QTableWidget, 
                               QTableWidgetItem, QVBoxLayout, QWidget, 
                               QLineEdit, QHeaderView, QProgressBar, 
                               QCheckBox, QHBoxLayout, QFrame)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

class WarrantyTable(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema CARDEX - Gestão de Garantias")
        self.resize(1200, 600)

        # Layout Principal
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Configuração da Tabela
        self.table = QTableWidget()
        layout.addWidget(self.table)

        # Colunas baseadas na sua imagem
        columns = [
            "", "Claim ID", "Category", "Part no.", "Brand", 
            "Sender", "Receiver", "Progress", "Status", 
            "Decision", "Item Status", "Modified date"
        ]
        
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)

        # Estilo para parecer com a imagem (cabeçalho cinza, grid suave)
        self.table.setStyleSheet("""
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 4px;
                border: 1px solid #d0d0d0;
                font-weight: bold;
            }
            QTableWidget {
                alternate-background-color: #fafafa;
            }
        """)
        self.table.setAlternatingRowColors(True)
        
        # Ajuste de cabeçalho
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setStretchLastSection(True)
        
        # 1. CRIAR A LINHA DE FILTROS (Linha 0)
        self.create_filter_row()

        # 2. POPULAR COM DADOS DE EXEMPLO
        self.load_dummy_data()

    def create_filter_row(self):
        """Insere uma linha no topo reservada apenas para os widgets de busca."""
        self.table.insertRow(0)
        self.table.setRowHeight(0, 40) # Altura da linha de filtros
        
        # Dicionário para guardar os filtros {coluna_index: widget}
        self.filters = {}

        # Loop pelas colunas (pulando a 0 que é checkbox)
        for col in range(1, self.table.columnCount()):
            # Cria o campo de busca
            search_input = QLineEdit()
            search_input.setPlaceholderText(f"Filtrar...")
            search_input.setStyleSheet("QLineEdit { border: 1px solid #ccc; border-radius: 4px; padding: 2px; }")
            
            # Conecta o sinal de mudança de texto à função de filtro
            search_input.textChanged.connect(self.apply_filters)
            
            # Adiciona na célula da linha 0
            self.table.setCellWidget(0, col, search_input)
            self.filters[col] = search_input

        # Bloqueia a edição da linha 0 para o usuário não digitar nela como se fosse dado
        item = QTableWidgetItem()
        item.setFlags(Qt.NoItemFlags)
        self.table.setItem(0, 0, item)

    def load_dummy_data(self):
        """Gera dados falsos similares à imagem para teste."""
        data = [
            ("177200", "Warranty", "DH206107", "SAMARC", "Indisa", 20, True, "23/01/2026"),
            ("177197", "Warranty", "45167", "SAMARC", "Indisa", 45, True, "23/01/2026"),
            ("177196", "Warranty", "EC254916", "Motor 100", "Indisa", 100, False, "23/01/2026"),
            ("177195", "Warranty", "DH454131", "SAMARC", "Indisa", 10, True, "23/01/2026"),
            ("177194", "Warranty", "9030102", "Tractortem", "Indisa", 0, True, "23/01/2026"),
        ]

        for row_idx, row_data in enumerate(data):
            # Inserir linha (começando da linha 1, pois a 0 é filtro)
            current_row = row_idx + 1
            self.table.insertRow(current_row)

            # Coluna 0: Checkbox
            chk_widget = QWidget()
            chk_layout = QHBoxLayout(chk_widget)
            chk_layout.addWidget(QCheckBox())
            chk_layout.setAlignment(Qt.AlignCenter)
            chk_layout.setContentsMargins(0,0,0,0)
            self.table.setCellWidget(current_row, 0, chk_widget)

            # Colunas de Texto Simples
            self.table.setItem(current_row, 1, QTableWidgetItem(row_data[0])) # ID
            
            # Coluna Colorida (Warranty)
            cat_item = QTableWidgetItem(row_data[1])
            cat_item.setBackground(QColor("#aaccff")) # Azulzinho igual da foto
            self.table.setItem(current_row, 2, cat_item)
            
            self.table.setItem(current_row, 3, QTableWidgetItem(row_data[2])) # Part no
            self.table.setItem(current_row, 5, QTableWidgetItem(row_data[3])) # Sender
            self.table.setItem(current_row, 6, QTableWidgetItem(row_data[4])) # Receiver

            # Coluna de Progresso (Visual)
            prog_widget = QProgressBar()
            prog_widget.setValue(row_data[5])
            prog_widget.setStyleSheet("QProgressBar { border: 0px; text-align: center; } QProgressBar::chunk { background-color: #5c9cd6; }")
            self.table.setCellWidget(current_row, 7, prog_widget)

            # Coluna de Toggle (Simulada)
            toggle = QCheckBox()
            toggle.setChecked(row_data[6])
            # Estilo simples de toggle (switch)
            toggle.setStyleSheet("QCheckBox::indicator { width: 30px; height: 15px; background-color: #ddd; border-radius: 7px; } QCheckBox::indicator:checked { background-color: #5c9cd6; }")
            container = QWidget()
            layout_t = QHBoxLayout(container)
            layout_t.addWidget(toggle)
            layout_t.setAlignment(Qt.AlignCenter)
            layout_t.setContentsMargins(0,0,0,0)
            self.table.setCellWidget(current_row, 8, container)

            self.table.setItem(current_row, 11, QTableWidgetItem(row_data[7])) # Date

    def apply_filters(self):
        """Lógica de filtragem: Esconde linhas que não batem com os textos."""
        # Começamos da linha 1 (a linha 0 são os widgets)
        for row in range(1, self.table.rowCount()):
            show_row = True
            
            # Verifica cada coluna que tem filtro
            for col, widget in self.filters.items():
                filter_text = widget.text().lower()
                
                # Pega o texto da célula (ou widget se for complexo, aqui simplificado para texto)
                item = self.table.item(row, col)
                cell_text = item.text().lower() if item else ""
                
                # Se tiver widget na célula (ex: sender/receiver complexo), teríamos que tratar diferente
                # Mas para ID, Part No, etc, isso funciona:
                if filter_text and filter_text not in cell_text:
                    show_row = False
                    break
            
            self.table.setRowHidden(row, not show_row)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WarrantyTable()
    window.show()
    sys.exit(app.exec())