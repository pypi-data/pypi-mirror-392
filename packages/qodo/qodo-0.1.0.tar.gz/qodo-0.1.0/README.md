# 🚀 Qodo PDV - Sistema Completo de Ponto de Venda

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)
![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Version](https://img.shields.io/badge/Version-1.0.0-brightgreen.svg)

**A biblioteca Python que acelera o desenvolvimento de sistemas PDV**

[Documentação da API](#-acesse-a-documentação-interativa) • [Quick Start](#-começando-em-2-minutos) • [Reportar Bug](https://github.com/Gilderlan0101/qodo-pdv/issues)

</div>

---

## 📋 Índice

- [🎯 O Porquê Desta Biblioteca](#-o-porquê-desta-biblioteca)
- [✨ Funcionalidades Principais](#-funcionalidades-principais)
- [🛠️ Tecnologias](#️-tecnologias)
- [⚡ Instalação Rápida](#-instalação-rápida)
- [🚀 Começando em 2 Minutos](#-começando-em-2-minutos)
- [📖 Documentação da API](#-documentação-da-api)
- [⚙️ Configuração](#️-configuração)
- [🎯 Exemplos Práticos](#-exemplos-práticos)
- [🏗️ Estrutura do Projeto](#️-estrutura-do-projeto)
- [🤝 Contribuindo](#-contribuindo)
- [📄 Licença](#-licença)
- [📞 Contato](#-contato)

---

## 🎯 O Porquê Desta Biblioteca

Desenvolver um sistema de PDV do zero costuma ser trabalhoso: copiar e replicar código, corrigir bugs e lidar com tarefas repetitivas consomem tempo e diminuem a produtividade. Pensando nisso, a **Qodo** criou uma biblioteca para **acelerar o desenvolvimento** e **reduzir a complexidade** dessas etapas.

**Assim nasceu o Qodo PDV**, uma biblioteca Python com endpoints prontos, construída em **FastAPI** e **MySQL**, projetada para tornar o desenvolvimento de sistemas de PDV mais simples, rápido e eficiente.

### 💡 Problemas que Resolvemos

- ✅ **Evita retrabalho** - Endpoints prontos para funcionalidades comuns
- ✅ **Padronização** - Estrutura consistente para todos os projetos
- ✅ **Manutenção simplificada** - Atualizações centralizadas
- ✅ **Documentação completa** - APIs bem documentadas e exemplos práticos
- ✅ **Comunidade** - Soluções testadas e validadas pela comunidade

---

## ✨ Funcionalidades Principais

### 🛒 **Vendas & Carrinho**
- Gestão completa de vendas
- Carrinho dinâmico em tempo real
- Cancelamento de vendas
- Múltiplos métodos de pagamento
- Vendas parceladas
- Controle de troco

### 📦 **Produtos & Estoque**
- Cadastro e gestão de produtos
- Controle de inventário inteligente
- Upload de imagens
- Categorização e tickets
- Alertas de estoque baixo
- Validação de data de validade

### 👥 **Clientes & Funcionários**
- CRM integrado
- Gestão de equipe
- Controle de acesso multi-nível
- Sistema de crédito para clientes
- Histórico de compras

### 💳 **Pagamentos**
- Múltiplos métodos de pagamento
- PIX integrado com QR Code
- Pagamentos parcelados
- Controle de contas bancárias
- Reconciliação financeira

### 🚚 **Delivery**
- Gestão completa de entregas
- Rastreamento em tempo real
- Atribuição automática de entregadores
- Controle de status
- Relatórios de performance

### 📊 **Dashboard & Analytics**
- Relatórios em tempo real
- Métricas de performance
- Analytics de vendas
- Indicadores financeiros
- Gráficos e visualizações

---

## 🛠️ Tecnologias

**Backend:**
- ![FastAPI](https://img.shields.io/badge/FastAPI-0.100.0+-green) - Framework web moderno e rápido
- ![Python](https://img.shields.io/badge/Python-3.8+-blue) - Linguagem principal
- ![SQLModel](https://img.shields.io/badge/SQLModel-0.0.27+-orange) - ORM moderno
- ![TortoiseORM](https://img.shields.io/badge/Tortoise_ORM-0.25.1+-yellow) - ORM assíncrono
- ![Pydantic](https://img.shields.io/badge/Pydantic-2.0+-blue) - Validação de dados

**Banco de Dados:**
- ![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange) - Banco relacional principal
- ![SQLite](https://img.shields.io/badge/SQLite-3.0+-lightgrey) - Alternativa para desenvolvimento

**Autenticação & Segurança:**
- ![JWT](https://img.shields.io/badge/JWT-Bearer_Tokens-red) - Autenticação stateless
- ![bcrypt](https://img.shields.io/badge/bcrypt-4.3.0+-green) - Hash de senhas
- ![CORS](https://img.shields.io/badge/CORS-Enabled-blue) - Cross-Origin Resource Sharing

---

## ⚡ Instalação Rápida

### Método 1: Instalação via Pip
```bash
pip install qodo-pdv

Método 2: Instalação em Desenvolvimento

Bash

git clone [https://github.com/Gilderlan0101/qodo-pdv.git](https://github.com/Gilderlan0101/qodo-pdv.git)
cd qodo-pdv
pip install -e .

🚀 Começando em 2 Minutos

Exemplo 1: Uso como Biblioteca

Python

from qodo.controllers.user.create_account import CreateCompany
from qodo.conf.database import init_database, close_database
import asyncio

async def criar_minha_empresa():
    await init_database()
    
    empresa = CreateCompany(
        full_name="Seu Nome",
        email="seu@email.com",
        password="senha123",
        company_name="Sua Empresa LTDA"
    )
    
    resultado = await empresa.new_company()
    print(f"✅ Empresa criada: {resultado['empresa']}")
    
    await close_database()

# Execute
asyncio.run(criar_minha_empresa())

Exemplo 2: Servidor Completo

Python

# server.py
from qodo import main

if __name__ == "__main__":
    main()

Execute:
Bash

python server.py
# Ou use o comando instalado
qodo-pdv

📖 Documentação da API

🔑 Autenticação

A API usa JWT (JSON Web Tokens) para autenticação. Inclua no header:
HTTP

Authorization: Bearer seu_token_jwt

📋 Endpoints Principais

Categoria	Endpoint	Método	Descrição
Auth	/api/v1/auth/login	POST	Login de usuário
Auth	/api/v1/auth/register	POST	Cadastro de empresa
Produtos	/api/v1/produtos/list	GET	Listar produtos
Vendas	/api/v1/carrinho/adicionar	POST	Adicionar ao carrinho
Vendas	/api/v1/carrinho/finalizar	POST	Finalizar venda
Clientes	/api/v1/clientes/create	POST	Cadastrar cliente

🌐 Acesse a Documentação Interativa

Quando o servidor estiver rodando:

    Swagger UI: http://localhost:8000/docs

    ReDoc: http://localhost:8000/redoc

    Health Check: http://localhost:8000/health

⚙️ Configuração

Variáveis de Ambiente (.env)

Snippet de código

DB_HOST=localhost
DB_PORT=3306
DB_NAME=qodo_pdv
DB_USER=seu_usuario
DB_PASS=sua_senha

JWT_SECRET_KEY=sua_chave_secreta_super_segura
ALGORITHM=HS256
DEBUG=True

Configuração do Banco

Python

from qodo.conf.database import init_database

# SQLite (Padrão - Desenvolvimento)
await init_database()

# MySQL (Produção)
from qodo.conf.database import DatabaseConfig
config = DatabaseConfig.get_mysql_config()
if config:
    await init_database(config)

🎯 Exemplos Práticos

Sistema de Vendas Completo

Python

from qodo.controllers.user.create_account import CreateCompany
from qodo.controllers.products.products_infors import ProductController
import asyncio

async def configurar_sistema():
    # 1. Criar empresa
    empresa = CreateCompany(
        full_name="Maria Santos",
        email="maria@loja.com", 
        password="123456",
        company_name="Super Mercado Maria"
    )
    await empresa.new_company()
    
    # 2. Adicionar produtos
    controller = ProductController()
    await controller.create_product({
        "name": "Arroz 5kg",
        "product_code": "ARROZ001", 
        "stock": 100,
        "sale_price": 25.90
    })
    
    # Adicione mais lógica aqui, como finalizar uma venda.

Integração com Frontend

JavaScript

// Exemplo React/Vue usando Fetch
const API_BASE = 'http://localhost:8000/api/v1';

// Login
async function login(email, password) {
    const response = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: `username=${email}&password=${password}`
    });
    return await response.json();
}

🏗️ Estrutura do Projeto

qodo-pdv/
├── 📁 src/qodo/
│   ├── 📁 auth/                 # 🔐 Autenticação e Autorização
│   ├── 📁 controllers/          # 🎮 Lógica de Negócio (Services/Controllers)
│   ├── 📁 model/               # 🗃️ Modelos de Dados (Tortoise ORM)
│   ├── 📁 routes/              # 🛣️ Rotas API (Endpoints FastAPI)
│   ├── 📁 schemas/             # 📋 Schemas Pydantic (Validação de Entrada/Saída)
│   └── 📁 conf/                # ⚙️ Configurações (DB, Settings)
├── 📄 Main.py                  # 🚀 Ponto de Entrada Principal
└── 📄 setup.py                 # 📦 Configuração do Pacote (PyPI)

🤝 Contribuindo

Adoramos contribuições! Veja como ajudar:

    Reportar Bugs: Abra uma issue detalhando o problema

    Sugerir Funcionalidades: Compartilhe suas ideias

    Enviar Pull Requests (PRs):

        Fork o projeto

        Crie uma branch: git checkout -b feature/nova-feature

        Commit: git commit -m 'feat: Adiciona nova funcionalidade'

        Push: git push origin feature/nova-feature

        Abra um Pull Request

📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para detalhes.

📞 Contato

Desenvolvedor: Gilderlan Silva Email: dacruzgg01@gmail.com GitHub: @Gilderlan0101 Projeto: Qodo PDV

<div align="center">

🚀 Poupe semanas de desenvolvimento - Use Qodo PDV hoje!

Feito com ❤️ para a comunidade Python

⭐ Não esqueça de dar uma estrela no repositório!

</div>
