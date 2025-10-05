# 🚀 Deploy Monorepo no Render

Este projeto está configurado para deploy completo (frontend + backend + database) no Render usando Blueprint.

## 📋 Arquivos de Configuração

```
sales/
├── render.yaml              # Configuração Blueprint do Render (monorepo)
├── backend/
│   ├── build.sh            # Script de build do Django
│   └── .env.example        # Variáveis de ambiente (backend)
└── frontend/
    ├── build.sh            # Script de build do React
    ├── .env.example        # Variáveis de ambiente (frontend)
    ├── _redirects          # SPA routing (/* /index.html)
    └── public/_headers     # Security headers
```

## 🎯 Deploy em 4 Passos

### 1️⃣ Criar Blueprint no Render

```bash
# No Render Dashboard:
New + → Blueprint → Selecionar repositório "sales"
```

O `render.yaml` criará automaticamente:
- ✅ `sales-backend` - Django API (Python)
- ✅ `sales-frontend` - React App (Node/Static)
- ✅ `sales-postgres` - PostgreSQL Database

### 2️⃣ Configurar Variáveis de Ambiente

#### Backend (`sales-backend`)
```env
SECRET_KEY=[Gerar usando botão "Generate"]
DEBUG=False
RENDER_EXTERNAL_HOSTNAME=[Auto-preenchido]
DATABASE_URL=[Auto-preenchido]
CORS_ALLOWED_ORIGINS=https://sales-frontend.onrender.com
PYTHON_VERSION=3.12.0
```

#### Frontend (`sales-frontend`)
```env
VITE_API_URL=https://sales-backend.onrender.com/api
NODE_VERSION=20.18.0
```

> ⚠️ **Importante:** Atualize as URLs após o primeiro deploy com as URLs reais geradas pelo Render.

### 3️⃣ Criar Superusuário

No Render Dashboard, acesse `sales-backend` → **Shell**:

```bash
python manage.py createsuperuser
```

### 4️⃣ Acessar a Aplicação

- **Frontend:** `https://sales-frontend.onrender.com`
- **API:** `https://sales-backend.onrender.com/api/`
- **Admin:** `https://sales-backend.onrender.com/admin/`

## 🔄 Deploy Automático

✅ **Push para `main`** → Render faz deploy automático de frontend + backend

## 🛠️ Comandos Úteis

### Backend (Shell no Render)
```bash
# Executar migrações
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Coletar arquivos estáticos
python manage.py collectstatic --no-input

# Verificar status
python manage.py check
```

### Local (Desenvolvimento)
```bash
# Backend
cd backend
source venv/bin/activate
python manage.py runserver

# Frontend
cd frontend
npm run dev
```

## 📊 Estrutura dos Serviços

| Serviço | Tipo | Runtime | Build | Start |
|---------|------|---------|-------|-------|
| **sales-backend** | Web Service | Python 3.12 | `./build.sh` | `gunicorn core.wsgi:application` |
| **sales-frontend** | Static Site | Node 20 | `./build.sh` | Serve `dist/` |
| **sales-postgres** | PostgreSQL | - | - | - |

## 🔐 Segurança

O frontend inclui:
- **SPA Routing:** `_redirects` para React Router
- **Security Headers:** `_headers` com X-Frame-Options, CSP, etc.
- **HTTPS:** Automático no Render

## 📚 Documentação Completa

Ver [DEPLOYMENT.md](./DEPLOYMENT.md) para:
- Deploy híbrido (Render + Cloudflare)
- Domínio customizado
- Troubleshooting
- Monitoramento

## 💰 Custos

**Free Tier:**
- Backend: Spin down após 15min inativo
- Frontend: Sempre ativo (static site)
- PostgreSQL: 90 dias retenção, 1GB

**Upgrade Recomendado (Produção):**
- Web Service: $7/mês (sem spin down)
- PostgreSQL: $7/mês (backups diários)

---

**Última atualização:** 2025-10-05
