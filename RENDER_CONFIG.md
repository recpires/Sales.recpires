# 🔧 Configuração Rápida - Render

## ⚠️ CONFIGURAÇÃO OBRIGATÓRIA PARA O FRONTEND FUNCIONAR

### 1️⃣ Configurar Variável de Ambiente do Frontend

**No Render Dashboard:**

1. Acesse: https://dashboard.render.com
2. Clique em **`sales-frontend`**
3. Vá em **Environment** (menu lateral)
4. Clique em **Add Environment Variable**
5. Adicione:

```
Key: VITE_API_URL
Value: https://sales-backend-fxp4.onrender.com/api
```

6. Clique em **Save Changes**
7. O Render vai fazer **redeploy automático** do frontend

---

### 2️⃣ Configurar CORS no Backend

**No Render Dashboard:**

1. Acesse: https://dashboard.render.com
2. Clique em **`sales-backend`**
3. Vá em **Environment** (menu lateral)
4. Procure a variável **`CORS_ALLOWED_ORIGINS`**
5. Se não existir, clique em **Add Environment Variable** e adicione:

```
Key: CORS_ALLOWED_ORIGINS
Value: https://[SUA-URL-DO-FRONTEND].onrender.com
```

**Exemplo:**
```
Value: https://sales-frontend-abc123.onrender.com
```

6. Clique em **Save Changes**

---

### 3️⃣ Verificar URLs dos Serviços

**Backend:**
- URL: `https://sales-backend-fxp4.onrender.com`
- API: `https://sales-backend-fxp4.onrender.com/api/`
- Admin: `https://sales-backend-fxp4.onrender.com/admin/`

**Frontend:**
- Copie a URL que aparece no Dashboard do `sales-frontend`
- Exemplo: `https://sales-frontend-xyz789.onrender.com`

---

### 4️⃣ Criar Superusuário (Admin)

**No Render Dashboard:**

1. Clique em **`sales-backend`**
2. Vá em **Shell** (menu lateral)
3. Execute:

```bash
python create_admin.py
```

**Credenciais:**
- Username: `admin`
- Password: `superadmin@1234`
- Email: `admin@example.com`

---

### 5️⃣ Testar a Aplicação

1. **Teste o Backend:**
   ```bash
   curl https://sales-backend-fxp4.onrender.com/
   curl https://sales-backend-fxp4.onrender.com/health/
   ```

2. **Acesse o Frontend:**
   - Abra a URL do frontend no navegador
   - Tente fazer login com as credenciais do admin

3. **Verifique o Console do Navegador:**
   - Pressione `F12` → Aba **Console**
   - Veja se há erros de CORS ou conexão

---

## 🐛 Troubleshooting

### Erro: "Network Error" ou "Failed to fetch"

**Causa:** Frontend não encontra o backend

**Solução:**
1. Verifique se `VITE_API_URL` está configurado no `sales-frontend`
2. Verifique se o valor é: `https://sales-backend-fxp4.onrender.com/api`
3. Aguarde o redeploy completar (2-3 min)

---

### Erro: "CORS policy: No 'Access-Control-Allow-Origin'"

**Causa:** Backend bloqueando requisições do frontend

**Solução:**
1. Vá em `sales-backend` → Environment
2. Configure `CORS_ALLOWED_ORIGINS` com a URL do frontend
3. Exemplo: `https://sales-frontend-abc123.onrender.com`
4. Aguarde o redeploy

---

### Frontend não atualiza após mudanças

**Solução:**
1. Vá em `sales-frontend` → Settings
2. Clique em **Clear build cache & deploy**
3. Aguarde o novo deploy

---

## ✅ Checklist de Configuração

- [ ] `VITE_API_URL` configurado no `sales-frontend`
- [ ] `CORS_ALLOWED_ORIGINS` configurado no `sales-backend`
- [ ] Redeploy do frontend concluído
- [ ] Superusuário criado via Shell
- [ ] Backend responde em `/health/`
- [ ] Frontend carrega sem erros no Console
- [ ] Login funciona corretamente

---

**Última atualização:** 2025-10-05