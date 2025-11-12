# Sistema de Gestão de Vendas

Aplicação full-stack de gestão de vendas construída com Django REST Framework e React + TypeScript, com autenticação JWT, gerenciamento de produtos e pedidos, e uma interface moderna baseada em componentes.

## 📋 Sumário

- [Recursos](#recursos)
- [Stack Tecnológica](#stack-tecnológica)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Executando a Aplicação](#executando-a-aplicação)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Documentação da API](#documentação-da-api)
- [Gerenciamento do Banco de Dados](#gerenciamento-do-banco-de-dados)
- [Desenvolvimento](#desenvolvimento)
- [Licença](#licença)

## ✨ Recursos
- **Autenticação de Usuário**
  - Autenticação baseada em JWT com renovação de token
  - Registro e login de usuários
  - Alteração de senha
  - Rotação automática de tokens com blacklist

- **Gerenciamento de Produtos**
  - Criar, listar, atualizar e remover produtos
  - Controle de SKU e gerenciamento de estoque
  - Controle de status de produto (ativo/inativo)

- **Gerenciamento de Pedidos**
  - Controle completo do ciclo de vida do pedido
  - Rastreamento de status do pedido (pendente, processando, enviado, entregue, cancelado)
  - Gerenciamento das informações do cliente
  - Itens do pedido com quantidade e preço

- **Interface Moderna**
  - Layout responsivo com Tailwind CSS
  - Arquitetura baseada em componentes
  - Rotas protegidas com redirecionamento automático
  - Gerenciamento do estado de autenticação em tempo real

## 🛠️ Stack Tecnológica

### Backend
- **Django 5.2.6** - Framework web
- **Django REST Framework 3.16.1** - API REST
- **PostgreSQL** - Banco de dados
- **djangorestframework-simplejwt** - Autenticação JWT
- **python-decouple** - Gerenciamento de variáveis de ambiente
- **Docker & Docker Compose** - Contêineres

### Frontend
- **React 19.1.1** - Biblioteca de UI
- **TypeScript** - Tipagem estática
- **Vite 7.1.7** - Ferramenta de build
- **React Router DOM** - Navegação
- **Axios** - Cliente HTTP com interceptors
- **Tailwind CSS** - Estilização

## 📦 Pré-requisitos

- Python 3.8+
- Node.js 16+
- Docker & Docker Compose
- Git

## 🚀 Instalação

### 1. Clonar o repositório

```powershell
git clone <repository-url>
cd sales
```

### 2. Configurar o Backend

```powershell
# Ir para o diretório backend
cd backend

# Criar virtualenv
python -m venv .venv

# Ativar virtualenv (PowerShell)
.venv\Scripts\Activate.ps1

# Instalar dependências
pip install -r requirements.txt

# Copiar arquivo de exemplo de variáveis de ambiente
copy .env.example .env
```

### 3. Configurar o Frontend

```powershell
# Ir para o diretório frontend
cd frontend

# Instalar dependências
npm install

# (Opcional) Configurar URL da API
# Crie um arquivo .env com: VITE_API_URL=http://localhost:8000/api
```

### 4. Iniciar banco via Docker

```powershell
# A partir da raiz do projeto, subir containers (Postgres, pgAdmin)
docker-compose up -d

# Verificar containers em execução
docker-compose ps
```

Credenciais padrão de desenvolvimento:
- PostgreSQL: `localhost:5432` (Database: `sales_db`, Usuário: `postgres`, Senha: `postgres123`)
- pgAdmin: `http://localhost:5050` (Email: `admin@admin.com`, Senha: `admin`)

### 5. Aplicar migrações

```powershell
# Do diretório backend
cd backend
.venv\Scripts\Activate.ps1

# Criar e aplicar migrações
python manage.py makemigrations
python manage.py migrate

# Criar superuser para acesso ao admin
python manage.py createsuperuser
```

## 🎯 Executando a Aplicação

### Iniciar Backend

```powershell
cd backend
.venv\Scripts\Activate.ps1
python manage.py runserver
```

O backend ficará disponível em: `http://localhost:8000`
- Base da API: `http://localhost:8000/api`
- Painel Admin: `http://localhost:8000/admin`

### Iniciar Frontend

```powershell
cd frontend
npm run dev
```

O frontend ficará disponível em: `http://localhost:5173`

## 📁 Estrutura do Projeto

```
sales/
├── backend/
│   ├── core/                 # Configurações do projeto Django
│   │   ├── settings.py      # Configuração
│   │   └── urls.py          # Roteamento principal
│   ├── sales/               # Aplicação de vendas
│   │   ├── models.py        # Modelos de dados (Product, Order, OrderItem)
│   │   ├── serializers.py   # Serializadores do DRF
│   │   ├── views.py         # ViewSets para operações CRUD
│   │   ├── auth_views.py    # Endpoints de autenticação
│   │   └── urls.py          # Rotas da API
│   ├── manage.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/      # Componentes reutilizáveis
│   │   │   ├── aside/       # Componentes da barra lateral
│   │   │   ├── common/      # Componentes UI (Button, Input, Card)
│   │   │   ├── layout/      # Componentes de layout
│   │   │   └── navbar/      # Navegação
│   │   ├── pages/           # Componentes por rota
│   │   ├── services/        # Cliente API e serviços
│   │   │   ├── api.ts       # Instância Axios com interceptors
│   │   │   ├── authService.ts
│   │   │   └── productService.ts
│   │   └── App.tsx          # App principal com rotas
│   ├── package.json
│   └── vite.config.ts
│
├── docker-compose.yml       # Configuração dos serviços Docker
├── CLAUDE.md               # Diretrizes de desenvolvimento
└── README.md               # Este arquivo
```

## 📚 Documentação da API

### Endpoints de Autenticação

```
POST   /api/auth/register/         - Registro de usuário
POST   /api/auth/login/            - Login (obtém tokens JWT)
POST   /api/auth/logout/           - Logout (blacklist do token)
POST   /api/auth/token/refresh/    - Renovar token de acesso
GET    /api/auth/profile/          - Obter perfil do usuário
PUT    /api/auth/profile/          - Atualizar perfil do usuário
POST   /api/auth/change-password/  - Alterar senha
```

### Endpoints de Recursos

```
GET    /api/products/              - Listar produtos
POST   /api/products/              - Criar produto
GET    /api/products/{id}/         - Detalhes do produto
PUT    /api/products/{id}/         - Atualizar produto
DELETE /api/products/{id}/         - Remover produto

GET    /api/orders/                - Listar pedidos
POST   /api/orders/                - Criar pedido
GET    /api/orders/{id}/           - Detalhes do pedido
PUT    /api/orders/{id}/           - Atualizar pedido
DELETE /api/orders/{id}/           - Remover pedido

GET    /api/order-items/           - Listar itens de pedido
POST   /api/order-items/           - Criar item de pedido
GET    /api/order-items/{id}/      - Detalhes do item
PUT    /api/order-items/{id}/      - Atualizar item de pedido
DELETE /api/order-items/{id}/      - Remover item de pedido
```

### Fluxo de Autenticação

1. **Login**: POST para `/api/auth/login/` com credenciais
   - Resposta: `{ access_token, refresh_token, user }`
2. **Requisições à API**: Inclua o header `Authorization: Bearer <access_token>`
3. **Renovação**: POST para `/api/auth/token/refresh/` com o refresh token
4. **Logout**: POST para `/api/auth/logout/` para invalidar tokens

## 🗄️ Gerenciamento do Banco de Dados

### Conectando com DBeaver

1. Criar nova conexão → PostgreSQL
2. Configurações de conexão:
   - Host: `localhost`
   - Port: `5432`
   - Database: `sales_db`
   - Username: `postgres`
   - Password: `postgres123`
3. Testar conexão → Finalizar

### Comandos Docker para o banco

```powershell
# Ver logs
docker-compose logs -f postgres

# Acessar shell do PostgreSQL
docker exec -it sales_postgres psql -U postgres -d sales_db

# Fazer backup
docker exec -t sales_postgres pg_dump -U postgres sales_db > backup.sql

# Restaurar backup
docker exec -i sales_postgres psql -U postgres sales_db < backup.sql

# Parar containers
docker-compose down

# Parar e remover volumes (CUIDADO: apaga os dados)
docker-compose down -v
```

## 👨‍💻 Desenvolvimento

### Backend

The file was created successfully.
