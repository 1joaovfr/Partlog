from models.retorno_model import RetornoModel

class RetornoController:
    def __init__(self):
        self.model = RetornoModel()

    def buscar_pendencias(self, termo, modo, nf=None):
        return self.model.buscar_itens_pendentes(termo, modo, nf)

    def salvar_processo(self, header, itens):
        total_sel = sum(i.valor_a_abater for i in itens)
        diff = header.valor_total - total_sel
        
        # Validação Flexível para Giro
        if header.tipo_retorno == "Itens de Giro":
            # Aceita diferença de até R$ 10,00 (pode ajustar)
            if abs(diff) > 10.0:
                 return False, f"Diferença de valor muito alta (R$ {diff:.2f}). Ajuste os itens."
        else:
            # Rígido para outros
            if diff > 0.10: # Falta selecionar
                return False, f"Valor selecionado menor que a nota. Faltam R$ {diff:.2f}"
            if diff < -0.10: # Excedeu
                return False, f"Valor selecionado excede a nota em R$ {abs(diff):.2f}"

        return self.model.salvar_retorno(header, itens)