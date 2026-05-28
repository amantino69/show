# 🚀 **USO DIÁRIO - Sistema de Alertas Remoto com Ngrok**

## 📋 **CENÁRIO DE USO:**
- **Servidor:** Computador remoto executando o Show Manager
- **Acesso:** Via ngrok (https://abc123.ngrok.io)
- **Usuários:** Empresário e artistas acessando por PC/celular
- **Objetivo:** Alertas automáticos funcionando 24/7

---

## 🖥️ **CONFIGURAÇÃO NO SERVIDOR (UMA VEZ APENAS)**

### 1. **Preparar o Servidor:**
```bash
# No computador servidor (onde ficará rodando)
cd c:\workspace\show

# Instalar dependências se ainda não foi feito
pip install plyer schedule reportlab openpyxl twilio requests

# Testar se funciona localmente
python test_alerts.py
```

### 2. **Configurar Ngrok:**
```bash
# Instalar ngrok se não tiver
# Baixar de: https://ngrok.com/download

# Configurar token (só uma vez)
ngrok config add-authtoken SEU_TOKEN_AQUI

# Testar ngrok
ngrok http 5001
```

---

## ⚙️ **ROTINA DIÁRIA NO SERVIDOR**

### **Opção A: Automática (RECOMENDADA)**

Criar um script que inicia tudo automaticamente:

**`start_daily_server.bat`:**
```batch
@echo off
echo ==========================================
echo Show Manager - Servidor Diario com Alertas
echo ==========================================
echo.

echo Iniciando servidor Flask...
start "Flask Server" cmd /k "cd /d c:\workspace\show && python app.py"

echo.
echo Aguardando 10 segundos para servidor iniciar...
timeout /t 10 /nobreak > nul

echo.
echo Iniciando Ngrok (acesso remoto)...
start "Ngrok" cmd /k "ngrok http 5001"

echo.
echo Iniciando aplicativo de alertas desktop...
start "Desktop Alerts" cmd /k "cd /d c:\workspace\show && python desktop_alerts.py"

echo.
echo ==========================================
echo TUDO INICIADO!
echo.
echo 1. Aguarde 30 segundos
echo 2. Abra o Ngrok e copie a URL (https://xyz.ngrok.io)
echo 3. Compartilhe a URL com artistas
echo 4. Minimize esta janela (mas nao feche!)
echo ==========================================
pause
```

### **Opção B: Manual (3 comandos diários)**

**Terminal 1 - Servidor Web:**
```bash
cd c:\workspace\show
python app.py
```

**Terminal 2 - Ngrok (acesso remoto):**
```bash
ngrok http 5001
```

**Terminal 3 - Alertas Desktop (opcional, mas recomendado):**
```bash
cd c:\workspace\show
python desktop_alerts.py
```

---

## 👥 **USO PELOS USUÁRIOS (EMPRESÁRIO E ARTISTAS)**

### **1. Acesso Inicial (uma vez por pessoa):**

#### **Via PC:**
1. Receber link do ngrok: `https://abc123.ngrok.io`
2. Abrir no navegador
3. Fazer login (empresario/123456 ou conta própria)
4. **IMPORTANTE:** Autorizar notificações quando o navegador perguntar

#### **Via Celular:**
1. Abrir link no navegador do celular
2. **iPhone:** Safari → Compartilhar → "Adicionar à Tela Inicial"
3. **Android:** Chrome → Menu → "Adicionar à tela inicial"
4. **IMPORTANTE:** Autorizar notificações quando solicitado

### **2. Uso Diário (automático após configuração):**

#### **Para criar alertas automáticos:**
1. Acessar "Eventos" no menu
2. Ao criar/editar evento, clicar no ícone 🪄 (varinha mágica)
3. Confirmar "Criar alertas automáticos"
4. Pronto! Alertas criados: 1 dia, 2h e 30min antes

#### **Para alertas personalizados:**
1. Ir em "Alertas Nativos" no menu
2. Clicar "Criar Alerta"
3. Escolher evento e horário
4. Salvar

---

## 🔔 **COMO OS ALERTAS FUNCIONAM:**

### **Automático (SEM ação necessária):**
- ✅ Alertas são criados automaticamente ao cadastrar eventos
- ✅ Sistema verifica a cada 30 segundos se há alertas para enviar
- ✅ Notificações aparecem automaticamente nos dispositivos

### **Tipos de alertas que cada usuário recebe:**

#### **No PC (Windows):**
- Notificações nativas do Windows (pop-up no canto da tela)
- Som de notificação (se habilitado)
- Funciona mesmo com navegador minimizado

#### **No Celular:**
- **iPhone:** Notificações push nativas (como WhatsApp)
- **Android:** Notificações push + som
- Funciona mesmo com app em segundo plano

---

## 📅 **FLUXO TÍPICO DE UM DIA**

### **Manhã (Empresário no servidor):**
```bash
# Executar uma vez
./start_daily_server.bat
```
- Tudo inicia automaticamente
- Ngrok gera nova URL (anotar e compartilhar)
- Sistema fica rodando 24h

### **Durante o dia (Artistas/Empresário):**
- **09:00** - João cria um show para amanhã → Alertas automáticos criados
- **14:30** - Maria recebe alerta: "🎵 Lembrete: Show no Clube Tomorrow às 20:00"
- **18:00** - Pedro recebe alerta: "🚨 URGENTE: Show em 2 horas!"
- **19:30** - Todos recebem: "🚨 URGENTE: Show em 30 minutos!"

### **Notificações aparecem:**
- ✅ PC: Pop-up do Windows
- ✅ iPhone: Notificação nativa 
- ✅ Android: Notificação nativa
- ✅ **SEM necessidade de ter o navegador aberto!**

---

## 🛡️ **REDUNDÂNCIA E BACKUP**

### **Múltiplas camadas de segurança:**
1. **Cache local:** `alerts_cache.json` (funciona offline)
2. **Banco de dados:** Registros no SQLite
3. **App desktop:** Funciona independente do navegador
4. **Sincronização:** App desktop sincroniza com servidor

### **Se algo der errado:**
- App desktop continua funcionando offline
- Alertas ficam salvos no cache local
- Quando servidor voltar, sincroniza automaticamente

---

## ⚡ **AÇÕES NECESSÁRIAS - RESUMO**

### **Uma vez (configuração):**
1. ✅ Instalar dependências no servidor
2. ✅ Configurar ngrok
3. ✅ Criar script de inicialização
4. ✅ Cada usuário autorizar notificações no primeiro acesso

### **Diariamente:**
1. ✅ **Servidor:** Executar `start_daily_server.bat` (1 clique)
2. ✅ **Usuários:** NENHUMA ação necessária! 
   - Alertas funcionam automaticamente
   - Notificações chegam sozinhas

### **Por evento:**
1. ✅ Ao criar evento: Clicar no 🪄 para alertas automáticos
2. ✅ **OU:** Sistema pode criar alertas automaticamente (se configurado)

---

## 🎯 **VANTAGENS DESTA CONFIGURAÇÃO**

✅ **Servidor sempre online** (computador remoto)  
✅ **Acesso de qualquer lugar** (ngrok)  
✅ **Notificações nativas** (PC e celular)  
✅ **Funciona offline** (app desktop)  
✅ **Zero manutenção diária** para usuários  
✅ **Alertas automáticos** inteligentes  
✅ **Múltiplas redundâncias** de segurança  

---

## 🚀 **PRÓXIMOS PASSOS**

1. **Hoje:** Configurar servidor com script automático
2. **Compartilhar:** URL do ngrok com todos os usuários
3. **Testar:** Criar um evento de teste e verificar se alertas funcionam
4. **Usar:** Sistema funcionará automaticamente a partir de então!

**Resultado:** Sistema de alertas profissional funcionando 24/7 com ZERO ação diária dos usuários! 🎵✨
