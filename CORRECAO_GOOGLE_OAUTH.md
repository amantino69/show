# 🔧 CORREÇÃO DA CONFIGURAÇÃO DO GOOGLE OAUTH

## Problema Identificado
A URL de callback do Google OAuth estava configurada para porta 5000, mas a aplicação roda na porta 5001.

## ✅ Correção Aplicada no Sistema
1. **Arquivo .env atualizado** ✅
   - `GOOGLE_REDIRECT_URI` alterado para `http://localhost:5001/callback`

## 🔧 Configuração Necessária no Google Cloud Console

### Passo a Passo:

1. **Acesse o Google Cloud Console**
   - Vá para: https://console.cloud.google.com/
   - Faça login com sua conta Google

2. **Navegue até APIs & Services**
   - Menu lateral > APIs & Services > Credentials
   - Ou acesse diretamente: https://console.cloud.google.com/apis/credentials

3. **Encontre seu OAuth 2.0 Client ID**
   - Procure por: `827660682661-ifovus9g3o922ikgemrqtot4d137p329.apps.googleusercontent.com`
   - Clique no nome do client ID

4. **Atualize as URIs de Redirecionamento Autorizadas**
   - Na seção "Authorized redirect URIs"
   - **Remova**: `http://localhost:5000/callback`
   - **Adicione**: `http://localhost:5001/callback`
   - Clique em **"SAVE"**

### URIs Corretas para Configurar:

```
Authorized JavaScript origins:
http://localhost:5001

Authorized redirect URIs:
http://localhost:5001/callback
```

## 🚀 Teste da Configuração

Após fazer as alterações no Google Cloud Console:

1. **Reinicie a aplicação**:
   ```bash
   taskkill /F /IM python.exe
   python app.py
   ```

2. **Teste a autenticação**:
   - Acesse: http://localhost:5001
   - Faça login no sistema
   - Tente conectar com Google Calendar
   - A URL de callback deve agora usar a porta 5001

## ⚠️ Importante

- As alterações no Google Cloud Console podem levar alguns minutos para entrar em vigor
- Certifique-se de que a aplicação está rodando na porta 5001
- Se ainda houver problemas, limpe o cache do navegador

## 🔍 Para Verificar se Está Funcionando

O callback correto deve ser:
```
http://localhost:5001/callback?state=...&code=...&scope=...
```

Se ainda estiver aparecendo porta 5000, verifique:
1. Se salvou as alterações no Google Cloud Console
2. Se reiniciou a aplicação
3. Se limpou o cache do navegador
