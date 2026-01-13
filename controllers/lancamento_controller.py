from models import LancamentoModel
from dtos.lancamento_dto import NotaFiscalDTO, ItemNotaDTO

class LancamentoController:
    """
    Controlador responsável pelo fluxo de entrada de Notas Fiscais.
    Coordena validações de cadastro e conversão de dados da View para o Model.
    """
    def __init__(self):
        self.model = LancamentoModel()

    def buscar_cliente_por_cnpj(self, cnpj_sujo: str):
        """Remove formatação do CNPJ e busca no banco."""
        cnpj = ''.join(filter(str.isdigit, cnpj_sujo))
        return self.model.buscar_cliente_nome(cnpj)
   
    def buscar_produto_por_codigo(self, codigo: str):
        return self.model.existe_produto(codigo)

    def salvar_nota_entrada(self, dados_nota: dict, lista_itens: list):
        """
        Processa a gravação da nota fiscal de entrada.
        
        Raises:
            Exception: Se o CNPJ não estiver cadastrado no sistema.
        """
        # Sanitização
        cnpj_limpo = ''.join(filter(str.isdigit, dados_nota['cnpj']))
        
        # Validação de Regra de Negócio
        if not self.model.buscar_cliente_nome(cnpj_limpo):
            raise Exception(f"Erro de Validação: O CNPJ {dados_nota['cnpj']} não está cadastrado.")

        # Conversão para DTOs
        nota_dto = NotaFiscalDTO(
            numero=dados_nota['numero'],
            emissao=dados_nota['emissao'],
            recebimento=dados_nota['recebimento'],
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

        self.model.salvar_entrada_completa(nota_dto, itens_dtos)
        return True