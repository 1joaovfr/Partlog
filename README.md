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
    <a href="#-pré-requisitos">Pré-requisitos</a> •
    <a href="#-instalação">Instalação</a> •
    <a href="#-estrutura-do-projeto">Estrutura</a> •
    <a href="#-segurança">Segurança</a>
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

## 🚀 Instalação e Primeira Execução

```bash
# 1. Clone o repositório
git clone https://github.com/SEU_USUARIO/partlog.git
cd partlog

# 2. Inicie o banco de dados PostgreSQL (em container)
docker-compose up -d

# 3. (Recomendado) Crie e ative ambiente virtual
python -m venv .venv
source .venv/bin/activate    # Linux / macOS
# ou
.venv\Scripts\activate       # Windows

# 4. Instale as dependências
pip install -r requirements.txt

# 5. Execute o sistema
python main.py
