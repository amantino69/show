# 🔔 Sistema de Alertas Nativos - Show Manager

## 📱 Como ter alertas no computador e celular SEM depender do Google Calendar

Este sistema cria alertas nativos que funcionam independente do Google Calendar, garantindo que artistas e empresários sejam notificados em todas as plataformas.

---

## 🖥️ **ALERTAS NO COMPUTADOR**

### Opção 1: Através do Navegador (Mais Simples)

1. **Acesse o sistema web:**
   ```
   http://localhost:5001
   ```

2. **No menu lateral, clique em "Alertas Nativos"**

3. **Clique em "Iniciar Daemon"**
   - O sistema começará a verificar alertas a cada 30 segundos
   - Notificações aparecerão como alertas nativos do Windows

4. **Para criar alertas automáticos:**
   - Vá em "Eventos" no menu
   - Clique no ícone de "varinha mágica" (🪄) ao lado de qualquer evento
   - Isso criará alertas: 1 dia antes, 2h antes e 30min antes

### Opção 2: Aplicativo Desktop (Funciona Offline)

1. **Execute o arquivo:**
   ```
   run_desktop_alerts.bat
   ```

2. **O aplicativo:**
   - Roda em segundo plano
   - Sincroniza com o servidor web quando possível
   - Funciona OFFLINE usando banco local
   - Mostra notificações nativas do Windows

---

## 📱 **ALERTAS NO CELULAR**

### Para Android:

1. **Instale o Termux (terminal Android):**
   - Download: https://termux.com/

2. **Configure Python no Termux:**
   ```bash
   pkg update
   pkg install python
   pip install plyer requests schedule
   ```

3. **Baixe o script móvel:**
   ```bash
   wget http://seu-servidor:5001/static/mobile_alerts.py
   python mobile_alerts.py
   ```

### Para iPhone:

1. **Use a opção de "Web App":**
   - Abra Safari
   - Acesse: `http://seu-ngrok-url.ngrok.io`
   - Clique em "Compartilhar" → "Adicionar à Tela Inicial"
   - Ative notificações quando solicitado

2. **O iPhone tratará como app nativo**

---

## 🌐 **ACESSO REMOTO (Para funcionar fora de casa)**

### 1. Configure o ngrok:
```bash
# No terminal, execute:
ngrok http 5001
```

### 2. Use a URL fornecida:
```
https://abc123.ngrok.io
```

### 3. Compartilhe com artistas:
- Envie o link para os artistas
- Eles podem acessar de qualquer lugar
- Funciona no celular como uma PWA (Progressive Web App)

---

## ⚙️ **TIPOS DE ALERTAS CRIADOS**

### Automáticos (para cada evento):
- **1 dia antes**: Lembrete geral
- **2 horas antes**: Alerta de preparação  
- **30 minutos antes**: Alerta URGENTE

### Personalizados:
- Você pode criar alertas customizados
- Escolher data/hora específica
- Definir nível de prioridade

---

## 🔧 **CONFIGURAÇÃO AVANÇADA**

### WhatsApp (via Twilio):
1. **Crie conta no Twilio:**
   - https://www.twilio.com/

2. **Configure no arquivo `.env`:**
   ```
   TWILIO_ACCOUNT_SID=seu_account_sid
   TWILIO_AUTH_TOKEN=seu_auth_token
   TWILIO_WHATSAPP_FROM=+14155238886
   ```

3. **Os alertas também serão enviados via WhatsApp**

### Email:
1. **Configure SMTP no `.env`:**
   ```
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USERNAME=seu_email@gmail.com
   MAIL_PASSWORD=sua_senha_app
   ```

2. **Alertas também irão por email**

---

## 🚀 **MODO DE USO RECOMENDADO**

### Para Empresários:
1. **Manter o servidor web sempre rodando**
2. **Usar aplicativo desktop para backup offline**
3. **Configurar WhatsApp para artistas**

### Para Artistas:
1. **Acessar via navegador/celular**
2. **Instalar como Web App**
3. **Receber via WhatsApp como backup**

---

## 🆘 **SOLUÇÃO DE PROBLEMAS**

### "Notificações não aparecem no Windows":
```bash
# Execute como administrador:
pip install --upgrade plyer
```

### "Aplicativo desktop não conecta":
- Verifique se o servidor web está rodando na porta 5001
- Confirme se não há firewall bloqueando

### "Alertas não são criados":
- Verifique se o daemon está rodando
- Consulte a página de Alertas Nativos no menu

### "Não funciona no celular":
- Use o ngrok para acesso externo
- Ative notificações no navegador quando solicitado

---

## 🎯 **VANTAGENS DESTE SISTEMA**

✅ **Independente do Google Calendar**  
✅ **Funciona offline**  
✅ **Multiplataforma (Windows, Android, iPhone)**  
✅ **Múltiplos canais (Desktop, WhatsApp, Email)**  
✅ **Alertas automáticos inteligentes**  
✅ **Interface simples para artistas**  

---

## 📞 **COMANDOS RÁPIDOS**

### Iniciar tudo:
```bash
# Terminal 1 (Servidor Web):
python app.py

# Terminal 2 (ngrok - acesso externo):
ngrok http 5001

# Terminal 3 (Aplicativo Desktop):
python desktop_alerts.py
```

### Testar notificações:
1. Acesse: http://localhost:5001/alerts
2. Clique em "Testar Notificação"
3. Deve aparecer alerta nativo do Windows

---

Com este sistema, você terá alertas nativos funcionando em **qualquer dispositivo**, **independente do Google Calendar** e **mesmo offline**! 🎉
