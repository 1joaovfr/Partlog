from models import LancamentoModel
from dtos.lancamento_dto import NotaFiscalDTO, ItemNotaDTO

class LancamentoController:
    def __init__(self):
        self.model = LancamentoModel()

    def buscar_cliente_por_cnpj(self, cnpj_sujo):
        # Limpeza básica continua aqui ou num helper utilitário
        cnpj = ''.join(filter(str.isdigit, cnpj_sujo))
        return self.model.buscar_cliente_nome(cnpj)
    
    def buscar_produto_por_codigo(self, codigo):
        return self.model.existe_produto(codigo)

    def salvar_nota_entrada(self, dados_nota: dict, lista_itens: list):
        """
        Recebe dicionários da View, converte para DTOs e chama o Model.
        """
        # 1. Preparação e Limpeza
        cnpj_limpo = ''.join(filter(str.isdigit, dados_nota['cnpj']))
        
        # 2. Validação de Regra de Negócio (Antes de tentar salvar)
        if not self.model.buscar_cliente_nome(cnpj_limpo):
            raise Exception(f"Erro de Validação:\n\nO CNPJ {dados_nota['cnpj']} não está cadastrado.")

        # 3. Conversão para DTO (Data Transfer Object)
        nota_dto = NotaFiscalDTO(
            numero=dados_nota['numero'],
            emissao=dados_nota['emissao'],
            recebimento=dados_nota['recebimento'], # Já vem como objeto date da View
            cnpj_cliente=cnpj_limpo
        )

        itens_dtos = []
        for item in lista_itens:
            itens_dtos.append(ItemNotaDTO(
                codigo=item['codigo'],
                quantidade=int(item['qtd']),
                valor=float(item['valor']),
                ressarcimento=float(item['ressarcimento'])
            ))

        # 4. Chama o Model para persistir
        self.model.salvar_entrada_completa(nota_dto, itens_dtos)
        return True