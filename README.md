<div align="center">
  <h1>Partlog</h1>
  <p><strong>Sistema de Gestão de Garantias e Itens</strong></p>

  <p>
    Sistema desktop para controle completo do fluxo de garantias: <br>
    entrada → análise técnica → devolução/reparo/rejeição
  </p>

  <p>
    <img alt="Python" src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
    <img alt="PySide6" src="https://img.shields.io/badge/PySide6-Qt_for_Python-41CD52?style=for-the-badge&logo=qt&logoColor=white"/>
    <img alt="PostgreSQL" src="https://img.shields.io/badge/PostgreSQL-16+-336791?style=for-the-badge&logo=postgresql&logoColor=white"/>
    <img alt="Docker" src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white"/>
  </p>

<p>
    <a href="#-sobre-o-projeto">Sobre</a> •
    <a href="#-tecnologias">Tecnologias</a> •
    <a href="#-instalação-e-execução">Instalação</a> •
    <a href="#-regras-de-negócio-implementadas">Regras de Negócio</a> •
    <a href="#-diagrama-do-banco-de-dados">Diagrama DB</a> •
    <a href="#-acesso-ao-banco-de-dados">Acesso DB</a>
  </p>
</div>

## 📖 Sobre o Projeto

**Partlog** é um sistema desktop desenvolvido para gerenciar todo o ciclo de vida de itens em garantia de forma organizada e eficiente.

Principais funcionalidades:
- Registro de entrada de produtos em garantia
- Análise técnica com registro de diagnóstico e solução
- Controle de status (em análise / aguardando peça / reparado / rejeitado / devolvido)
- Histórico completo por produto/cliente
- Relatórios básicos de desempenho da garantia

## 🛠 Tecnologias

- **Linguagem principal**: Python 3.10+
- **Interface gráfica**: PySide6 (Qt for Python)
- **Banco de dados**: PostgreSQL
- **Containerização do banco**: Docker + docker-compose
- **Padrão de arquitetura**: MVC simplificado + DTO

## ✅ Pré-requisitos

- Python 3.10 ou superior
- Docker Desktop (ou Docker + docker-compose no Linux)
- Git (recomendado)

## 🚀 Instalação e Execução

```bash
# 1. Clone o repositório
git clone https://github.com/1joaovfr/Partlog.git
cd partlog

# 2. Suba o container do Banco de Dados
# Isso criará um banco chamado 'cardex_db' na porta 5432
docker-compose up -d

# 3. Crie e ative o ambiente virtual
python -m venv .venv
source .venv/bin/activate    # Linux / macOS
# ou
.venv\Scripts\activate       # Windows

# 4. Instale as dependências
pip install -r requirements.txt

# 5. Execute a aplicação
python main.py
```

## 📂 Estrutura do Projeto

A arquitetura segue o padrão **MVC (Model-View-Controller)** com a utilização de **DTOs (Data Transfer Objects)** para garantir a integridade dos dados entre as camadas.

```plaintext
partlog/
├── controllers/       # Lógica de controle e orquestração entre UI e Banco
├── database/          # Configurações de conexão e sessão do PostgreSQL
├── dtos/              # Objetos de Transferência de Dados (Pydantic/Dataclasses)
├── models/            # Modelos ORM (Mapeamento das tabelas do banco)
├── styles/            # Arquivos de estilização visual (QSS/Temas)
├── views/             # Componentes da interface gráfica (PySide6)
├── docker-compose.yml # Definição dos containers (Banco de Dados)
├── main.py            # Ponto de entrada da aplicação
├── requirements.txt   # Dependências do projeto
└── seeder.py          # Script para popular o banco com dados iniciais
```

## 🧠 Regras de Negócio Implementadas

O sistema aplica regras estritas para garantir a integridade fiscal e financeira das garantias:

### 1. Rastreabilidade (Traceability)
* **Código de Análise Único:** No momento da entrada (`LancamentoModel`), o sistema gera automaticamente um código sequencial baseado no mês (Ex: `A0052`, onde 'A' representa Janeiro).
* **Conciliação Financeira:** O sistema impede que uma garantia seja paga em duplicidade. A tabela `itens_notas` possui um campo `saldo_financeiro`.
    * Ao lançar uma Nota de Retorno (`RetornoModel`), o valor é abatido desse saldo.
    * O item só é considerado "encerrado" quando o saldo chega a zero.

### 2. Fluxo de Análise Técnica
O fluxo segue o padrão **DAO (Data Access Object)** com injeção de SQL puro para performance:
1.  **Entrada:** Registro da NF do cliente e criação dos itens como `Pendente`.
2.  **Análise:** O técnico insere dados de engenharia (Nº Série, Código de Avaria) e define se é `Procedente` ou `Improcedente`.
3.  **Fechamento:** O sistema agrupa itens procedentes por cliente ou grupo econômico para gerar a NF de Retorno/Ressarcimento.

### 3. Inteligência de Dados (BI)
O módulo `DashboardModel` calcula KPIs em tempo real:
* **Gap de Recebimento:** Diferença média de dias entre a chegada física e o lançamento no sistema.
* **Análise de Safra:** Comparativo financeiro entre Entrada vs. Saída (Devolução) nos últimos 6 meses.

## 🗺️ Diagrama do Banco de Dados

```mermaid
erDiagram
    %% Tabela Clientes e suas relações
    CLIENTES ||--|{ NOTAS_FISCAIS : "emite (cliente) / envia (remetente)"
    CLIENTES {
        string cnpj PK
        string cliente
        string grupo
        string cidade
        string estado
    }

    %% Tabela Itens e Avarias (Cadastros)
    ITENS ||--|{ ITENS_NOTAS : define
    ITENS {
        string codigo_item PK
        string descricao_item
        string grupo_item
    }

    AVARIAS ||--|{ ITENS_NOTAS : classifica
    AVARIAS {
        string codigo_avaria PK
        string descricao_avaria
        string status_avaria
    }

    %% Tabela Notas Fiscais (Entrada)
    NOTAS_FISCAIS ||--|{ ITENS_NOTAS : contem
    NOTAS_FISCAIS {
        int id PK
        string numero_nota
        date data_nota
        string cnpj_cliente FK
        string cnpj_remetente FK
        date data_recebimento
        date data_lancamento
    }

    %% Tabela Itens das Notas (O coração do sistema)
    ITENS_NOTAS ||--|{ CONCILIACAO : "é abatido em"
    ITENS_NOTAS {
        int id PK
        int id_nota_fiscal FK
        string codigo_item FK
        decimal valor_item
        decimal ressarcimento
        decimal saldo_financeiro
        string status
        string codigo_analise
        string numero_serie
        string codigo_avaria FK
    }

    %% Tabela Notas de Retorno (Saída/Fechamento)
    NOTAS_RETORNO ||--|{ CONCILIACAO : gera
    NOTAS_RETORNO {
        int id PK
        string numero_nota
        date data_emissao
        string tipo_retorno
        string cnpj_emitente "Novo"
        string cnpj_remetente "Novo"
        string grupo_economico "Novo"
        decimal valor_total_nota
    }

    %% Tabela Conciliação (Ligação N:N)
    CONCILIACAO {
        int id PK
        int id_nota_retorno FK
        int id_item_entrada FK
        decimal valor_abatido
        date data_conciliacao
    }
```

## 🗄️ Acesso ao Banco de Dados

O projeto utiliza um container **PostgreSQL 16 Alpine**. Para conectar ferramentas de gerenciamento (DBeaver, pgAdmin, Datagrip), utilize as credenciais definidas no `docker-compose.yml`:

| Parâmetro | Valor Padrão |
| :--- | :--- |
| **Host** | `localhost` |
| **Porta** | `5432` |
| **Database** | `cardex_db` |
| **Usuário** | `dev` |
| **Senha** | `indisa` |

> **Nota:** Os dados persistem no volume `postgres_data`. Para resetar o banco completamente, execute `docker-compose down -v`.

## 🚧 Status do Projeto e Roadmap

O projeto encontra-se em fase de **desenvolvimento/testes**.

- [x] Estrutura MVC e Banco de Dados (Docker)
- [x] CRUD de Garantias e Produtos
- [ ] Implementação de autenticação robusta
- [ ] **Empacotamento (.exe):** Geração de executável para distribuição nas máquinas da empresa.
- [ ] **Ambiente de Produção:** Configuração de variáveis de ambiente (`.env`) para conexão segura com servidor PostgreSQL dedicado.

> **Nota:** Atualmente, as credenciais do banco estão fixadas no `docker-compose.yml` para facilitar o ambiente de desenvolvimento local.
