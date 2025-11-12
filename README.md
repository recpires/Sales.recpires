# README (Português)

Este repositório contém a documentação principal em português em `README.pt.md`.

Se preferir a versão em inglês, consulte `README.en.md`.

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd sales
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Optional: Configure API URL
# Create .env file with: VITE_API_URL=http://localhost:8000/api
```

### 4. Database Setup with Docker

```bash
# From project root, start PostgreSQL and pgAdmin
docker-compose up -d

# Verify containers are running
docker-compose ps
```

**Database Credentials:**

- **PostgreSQL**: `localhost:5432`

  - Database: `sales_db`
  - Username: `postgres`
  - Password: `postgres123`

- **pgAdmin**: `http://localhost:5050`
  - Email: `admin@admin.com`
  - Password: `admin`

### 5. Run Database Migrations

```bash
# From backend directory
cd backend
source venv/bin/activate

# Create and apply migrations
python3 manage.py makemigrations
python3 manage.py migrate

# Create superuser for admin access
python3 manage.py createsuperuser
```

## 🎯 Running the Application

### Start Backend Server

```bash
cd backend
source venv/bin/activate
python3 manage.py runserver
```

Backend will be available at: `http://localhost:8000`

- API Base URL: `http://localhost:8000/api`
- Admin Panel: `http://localhost:8000/admin`

### Start Frontend Server

```bash
cd frontend
npm run dev
```

Frontend will be available at: `http://localhost:5173`

## 📁 Project Structure

```
sales/
├── backend/
│   ├── core/                 # Django project settings
│   │   ├── settings.py      # Configuration
│   │   └── urls.py          # Main URL routing
│   ├── sales/               # Sales application
│   │   ├── models.py        # Data models (Product, Order, OrderItem)
│   │   ├── serializers.py   # DRF serializers
│   │   ├── views.py         # ViewSets for CRUD operations
│   │   ├── auth_views.py    # Authentication endpoints
│   │   └── urls.py          # API routes
│   ├── manage.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/      # Reusable components
│   │   │   ├── aside/       # Sidebar components
│   │   │   ├── common/      # UI components (Button, Input, Card)
│   │   │   ├── layout/      # Layout components
│   │   │   └── navbar/      # Navigation
│   │   ├── pages/           # Route-level components
│   │   ├── services/        # API client and services
│   │   │   ├── api.ts       # Axios instance with interceptors
│   │   │   ├── authService.ts
│   │   │   └── productService.ts
│   │   └── App.tsx          # Main app with routing
│   ├── package.json
│   └── vite.config.ts
│
├── docker-compose.yml       # Docker services configuration
├── CLAUDE.md               # Development guidelines
└── README.md               # This file
```

## 📚 API Documentation

### Authentication Endpoints

```
POST   /api/auth/register/         - User registration
POST   /api/auth/login/            - Login (get JWT tokens)
POST   /api/auth/logout/           - Logout (blacklist token)
POST   /api/auth/token/refresh/    - Refresh access token
GET    /api/auth/profile/          - Get user profile
PUT    /api/auth/profile/          - Update user profile
POST   /api/auth/change-password/  - Change password
```

### Resource Endpoints

```
GET    /api/products/              - List all products
POST   /api/products/              - Create product
GET    /api/products/{id}/         - Get product details
PUT    /api/products/{id}/         - Update product
DELETE /api/products/{id}/         - Delete product

GET    /api/orders/                - List all orders
POST   /api/orders/                - Create order
GET    /api/orders/{id}/           - Get order details
PUT    /api/orders/{id}/           - Update order
DELETE /api/orders/{id}/           - Delete order

GET    /api/order-items/           - List all order items
POST   /api/order-items/           - Create order item
GET    /api/order-items/{id}/      - Get order item
PUT    /api/order-items/{id}/      - Update order item
DELETE /api/order-items/{id}/      - Delete order item
```

### Authentication Flow

1. **Login**: POST to `/api/auth/login/` with credentials
   - Response: `{ access_token, refresh_token, user }`
2. **API Requests**: Include header `Authorization: Bearer <access_token>`
3. **Token Refresh**: POST to `/api/auth/token/refresh/` with refresh token
4. **Logout**: POST to `/api/auth/logout/` to blacklist tokens

## 🗄️ Database Management

### Connecting with DBeaver

1. Create new connection → PostgreSQL
2. Connection settings:
   - Host: `localhost`
   - Port: `5432`
   - Database: `sales_db`
   - Username: `postgres`
   - Password: `postgres123`
3. Test Connection → Finish

### Docker Database Commands

```bash
# View logs
docker-compose logs -f postgres

# Access PostgreSQL shell
docker exec -it sales_postgres psql -U postgres -d sales_db

# Backup database
docker exec -t sales_postgres pg_dump -U postgres sales_db > backup.sql

# Restore database
docker exec -i sales_postgres psql -U postgres sales_db < backup.sql

# Stop containers
docker-compose down

# Stop and remove volumes (WARNING: deletes all data)
docker-compose down -v
```

## 👨‍💻 Development

### Backend Development

```bash
# Generate model diagram
python3 manage.py graph_models sales -o models.png

# Create new migrations
python3 manage.py makemigrations

# Apply migrations
python3 manage.py migrate

# Create superuser
python3 manage.py createsuperuser
```

### Frontend Development

```bash
# Run dev server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

### Development Guidelines

- Use Ant Design for UI components
- Use React Query for async data management
- Use React Hook Form with Zod for form validation
- Functional components with TypeScript
- Tailwind CSS utility-first styling
- Components should be max 200 lines
- Extract complex logic into custom hooks

## 🔒 Environment Variables

### Backend (.env)

```env
SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=sales_db
DB_USER=postgres
DB_PASSWORD=postgres123
DB_HOST=localhost
DB_PORT=5432
```

### Frontend (.env)

```env
VITE_API_URL=http://localhost:8000/api
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Built with ❤️ using Django and React**

---

## Quick start (short)

1. Backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

2. Frontend

```powershell
cd frontend
npm install
npm run dev
```

Read the full architecture and developer guide in `ARCHITECTURE.md`.

## 🖼️ Gerar diagramas automaticamente (GitHub Actions)

Se você não tem Docker localmente ou prefere que o GitHub gere as imagens, há uma Action configurada para renderizar os arquivos PlantUML (`.puml`) e publicar os PNGs como artefato.

Fluxo resumido:

1. Crie uma branch para o PR (ex.: `add/diagrams-pngs`).
2. Abra um PR; a workflow `Render PlantUML diagrams` rodará automaticamente e fará o upload de um artefato chamado `diagrams` contendo os PNGs gerados.
3. Baixe o artefato pela interface do GitHub (Actions → execução da workflow → Artifacts) ou usando a CLI `gh` (ex.: `gh run download --name diagrams -D docs/diagrams/generated`).
4. Extraia/copiar os arquivos PNG para `docs/diagrams/generated/` no repositório local, adicione-os ao Git e faça um commit/push.

Detalhes e comandos passo-a-passo estão em `docs/DIAGRAMS_ACTION_INSTRUCTIONS.md`.

## 🆕 Novas modificações (12/11/2025)

Abaixo um resumo das alterações recentes encontradas no repositório. O resumo foi gerado a partir do estado atual dos arquivos (migrations, testes e código) — se quiser que eu inclua referências a commits/PRs específicas, diga quais ou forneça um intervalo de commits.

- Backend

  - Suporte a variantes de produto (SKU, cor, tamanho) e imagens: alterações de modelos e migrações presentes em `backend/sales/migrations/0002` até `0006`.
  - Teste automatizado relacionado à migração de produtos para variantes: `backend/sales/tests/test_migrate_products_to_variants.py`.
  - Scripts utilitários: `backend/create_admin.py` (auxilia na criação de usuários/admins em ambientes locais).

- Frontend

  - Internacionalização adicionada (`frontend/src/i18n.ts`, `frontend/src/locales/en.json`, `frontend/src/locales/pt-BR.json`).
  - Novas páginas e testes de frontend (Vitest + `frontend/src/__tests__`).
  - Configurações e ajustes do build: `frontend/vite.config.ts`, `tsconfig.json`, `package.json` (dependências e scripts).

- Documentação & automações
  - Workflow/automação para renderizar diagramas PlantUML e publicar artefatos (ver seção "Gerar diagramas automaticamente").
  - Scripts para geração local/CI de diagramas: `scripts/render-diagrams.sh` e `scripts/render-diagrams.ps1`.

Como validar as alterações rapidamente

1. Backend (migrations + testes):

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py test backend.sales.tests.test_migrate_products_to_variants
```

2. Frontend (dev + testes):

```powershell
cd frontend
npm install
npm run dev            # rodar app localmente
npm run test           # rodar testes (Vitest)
```

3. Gerar diagramas (local/CI):

```powershell
# Usando o script PowerShell
./scripts/render-diagrams.ps1
# Ou no Linux/macOS
./scripts/render-diagrams.sh
```

Notas

- Este resumo é baseado no estado atual do repositório (arquivos e migrações presentes). Se preferir que eu gere uma seção com changelog por commit ou PR, eu posso: me diga o intervalo de commits ou permita que eu acesse o histórico Git.
- Se quiser que eu adicione links diretos para os arquivos mencionados ou exemplos de uso mais detalhados, eu adiciono na próxima atualização.
