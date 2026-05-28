# ⚡ CORREÇÃO URGENTE - Google Cloud Console

## 🎯 PROBLEMA IDENTIFICADO:
A URL de callback estava incorreta, causando o erro "Not Found"

## 🔧 CORREÇÃO NECESSÁRIA:

### 1. GOOGLE CLOUD CONSOLE:
1. Acesse: https://console.cloud.google.com/
2. Vá em "APIs & Services" → "Credentials" 
3. Clique na sua credencial OAuth 2.0
4. Em "Authorized redirect URIs", SUBSTITUA por:
   ```
   http://localhost:5000/callback
   ```
5. SALVE as alterações

### 2. SE USAR NGROK:
Adicione também a URL do ngrok:
```
https://SUA_URL_NGROK.ngrok.io/callback
```

### 3. REINICIAR O SISTEMA:
```bash
# Pare o sistema (Ctrl+C)
# Reinicie:
C:/workspace/show/venv/Scripts/python.exe app.py
```

## ✅ APÓS CORREÇÃO:
1. Sistema reiniciado ✅
2. Google Cloud atualizado ✅  
3. URL de callback corrigida ✅
4. Teste novamente a conexão do Google Calendar

## 🎯 URLS CORRETAS:
- **Sistema:** http://localhost:5000
- **Callback:** http://localhost:5000/callback  
- **Autorização:** http://localhost:5000/auth/google/authorize
