from models.retorno_model import RetornoModel

class RetornoController:
    """
    Gerencia o processo de criação de Notas de Retorno (Espelho/Crédito).
    Contém regras críticas de validação financeira.
    """
    def __init__(self):
        self.model = RetornoModel()

    def buscar_pendencias(self, termo, modo, nf=None):
        return self.model.buscar_itens_pendentes(termo, modo, nf)

    def salvar_processo(self, header, itens):
        """
        Valida os valores selecionados contra o valor total da nota antes de salvar.
        
        Regras de Tolerância:
        - Itens de Giro: Permite diferença de até R$ 10,00 (ajustes de arredondamento/pacote).
        - Outros: Tolerância rígida de R$ 0,10.
        """
        total_sel = sum(i.valor_a_abater for i in itens)
        diff = header.valor_total - total_sel
        
        # Validação de Business Logic para tolerância
        if header.tipo_retorno == "Itens de Giro":
            if abs(diff) > 10.0:
                 return False, f"Diferença de valor muito alta (R$ {diff:.2f}). Ajuste os itens."
        else:
            # Validação Rígida
            if diff > 0.10: 
                return False, f"Valor selecionado menor que a nota. Faltam R$ {diff:.2f}"
            if diff < -0.10: 
                return False, f"Valor selecionado excede a nota em R$ {abs(diff):.2f}"

        return self.model.salvar_retorno(header, itens)