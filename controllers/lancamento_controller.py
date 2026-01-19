from models import LancamentoModel
from dtos.lancamento_dto import NotaFiscalDTO, ItemNotaDTO

class LancamentoController:
    """
    Controlador responsável pelo fluxo de entrada de Notas Fiscais.
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
        """
        # Sanitização
        cnpj_emitente_limpo = ''.join(filter(str.isdigit, dados_nota['cnpj']))
        cnpj_remetente_limpo = ''.join(filter(str.isdigit, dados_nota['cnpj_remetente']))
        
        # 1. Validação de Regra: O EMITENTE (Quem mandou/Cliente) deve existir
        if not self.model.buscar_cliente_nome(cnpj_emitente_limpo):
            raise Exception(f"Erro de Validação: O CNPJ Emitente {dados_nota['cnpj']} não está cadastrado.")

        # 2. Validação de Regra: O REMETENTE (Sua Empresa/Destino) deve existir
        if not cnpj_remetente_limpo:
             raise Exception("Erro: O campo CNPJ Remetente é obrigatório.")
             
        if not self.model.buscar_cliente_nome(cnpj_remetente_limpo):
            raise Exception(f"Erro de Validação: O CNPJ Remetente (Sua Empresa) {dados_nota['cnpj_remetente']} não está cadastrado no sistema.")

        # Conversão para DTOs
        nota_dto = NotaFiscalDTO(
            numero=dados_nota['numero'],
            emissao=dados_nota['emissao'],
            recebimento=dados_nota['recebimento'],
            cnpj_cliente=cnpj_emitente_limpo,   # Coluna: cnpj_cliente
            cnpj_remetente=cnpj_remetente_limpo # Coluna: cnpj_remetente
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