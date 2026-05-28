## 📧 COMO FUNCIONA A SINCRONIZAÇÃO COM GOOGLE CALENDAR E NOTIFICAÇÕES POR EMAIL

### 🔄 **VISÃO GERAL DO SISTEMA**

O sistema possui **DUPLA INTEGRAÇÃO** para garantir que os artistas recebam notificações:

1. **📅 Google Calendar** - Eventos sincronizados automaticamente
2. **📧 Sistema de Email** - Notificações automáticas por email
3. **🖥️ Alertas Nativos** - Pop-ups no computador

---

### 📅 **INTEGRAÇÃO COM GOOGLE CALENDAR**

#### **Como funciona:**

1. **🔗 Conexão Inicial**
   - Empresário conecta sua conta Google via `/google/authorize`
   - Artista também pode conectar sua conta Google (opcional)
   - Tokens OAuth2 salvos no banco de dados

2. **📝 Criação de Eventos**
   - Quando um evento é cadastrado, o sistema:
     - ✅ Cria evento no Google Calendar do **empresário**
     - ✅ Cria evento no Google Calendar do **artista** (se conectado)
     - ✅ Adiciona o artista como **convidado** no evento

3. **📧 Notificações do Google**
   ```python
   'reminders': {
       'useDefault': False,
       'overrides': [
           {'method': 'email', 'minutes': 2 * 24 * 60},  # 2 dias antes
           {'method': 'email', 'minutes': 1 * 24 * 60},  # 1 dia antes  
           {'method': 'email', 'minutes': 3 * 60},       # 3 horas antes
           {'method': 'popup', 'minutes': 15},           # 15 min antes
       ],
   }
   ```

4. **👥 Lista de Convidados**
   ```python
   'attendees': [
       {'email': event.artist.email, 'displayName': event.artist.stage_name},
       {'email': current_user.email, 'displayName': 'Empresário'},
   ]
   ```

---

### 📧 **SISTEMA DE EMAIL PRÓPRIO**

#### **Paralelo ao Google Calendar:**

1. **⏰ Agendamento Automático**
   - Sistema agenda emails independentes do Google
   - Usa APScheduler para disparar no horário correto
   - Backup caso o Google falhe

2. **📬 Templates de Email**
   ```
   Assunto: Lembrete: {evento} em {tempo}
   
   Olá!
   
   Este é um lembrete de que o evento "{título}" está agendado 
   para acontecer em {tempo}.
   
   Detalhes:
   • Artista: {nome_artista}
   • Data/Hora: {data_hora}
   • Local: {local}
   • Descrição: {descricao}
   ```

3. **⏰ Horários de Envio**
   - 📅 **1 dia antes** - Lembrete de preparação
   - ⏰ **2 horas antes** - Lembrete para se arrumar
   - ⚡ **30 minutos antes** - Hora de sair

---

### 🔧 **CONFIGURAÇÃO NECESSÁRIA**

#### **1. Variáveis de Ambiente (.env)**
```bash
# Google Calendar
GOOGLE_CLIENT_ID=seu_client_id_aqui
GOOGLE_CLIENT_SECRET=seu_client_secret_aqui
GOOGLE_REDIRECT_URI=http://127.0.0.1:5005/google/callback

# Email SMTP
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=seu_email@gmail.com
MAIL_PASSWORD=sua_senha_app
```

#### **2. Credenciais do Google**
- Criar projeto no Google Cloud Console
- Ativar Google Calendar API
- Gerar credenciais OAuth2
- Configurar URLs de redirecionamento

---

### 📱 **FLUXO PARA O ARTISTA (GUINHO)**

#### **Cenário 1: Artista COM Google Calendar conectado**

1. **🎭 Evento criado** pelo empresário
2. **📅 Aparece automaticamente** no Google Calendar do Guinho
3. **📧 Google envia emails** automaticamente:
   - 2 dias antes
   - 1 dia antes  
   - 3 horas antes
4. **📧 Sistema envia emails** adicionais:
   - 1 dia antes
   - 2 horas antes
   - 30 minutos antes
5. **🖥️ Alertas nativos** no computador (se logado no sistema)

#### **Cenário 2: Artista SEM Google Calendar**

1. **🎭 Evento criado** pelo empresário
2. **📧 Sistema envia emails** para `guinho@show.com`:
   - 1 dia antes
   - 2 horas antes
   - 30 minutos antes
3. **🖥️ Alertas nativos** no computador (se logado no sistema)

---

### 🚀 **COMO CONECTAR O GOOGLE CALENDAR**

#### **Para o Empresário:**
1. Fazer login no sistema
2. Ir em qualquer página
3. Acessar `/google/authorize`
4. Autorizar acesso ao Google Calendar
5. ✅ Pronto! Eventos serão sincronizados

#### **Para o Artista (Guinho):**
1. Login: `guinho` / `guinho123`
2. Acessar `/google/authorize`
3. Autorizar com sua conta Google
4. ✅ Eventos aparecerão automaticamente na agenda dele

---

### ✅ **VANTAGENS DA DUPLA INTEGRAÇÃO**

| Recurso | Google Calendar | Sistema Próprio |
|---------|----------------|-----------------|
| 📧 **Emails automáticos** | ✅ Sim | ✅ Sim |
| ⏰ **Horários flexíveis** | Configurável | Configurável |
| 📱 **Sincronização mobile** | ✅ Sim | ❌ Não |
| 🖥️ **Alertas desktop** | ✅ Sim | ✅ Sim |
| 🔄 **Backup/redundância** | - | ✅ Sim |
| 🎨 **Templates customizados** | Limitado | ✅ Sim |

---

### 🔍 **COMO VERIFICAR SE ESTÁ FUNCIONANDO**

#### **1. Verificar Conexão Google:**
```python
# No sistema, verificar se user.google_token existe
user = User.query.filter_by(email='guinho@show.com').first()
print(f"Google conectado: {'Sim' if user.google_token else 'Não'}")
```

#### **2. Testar Email:**
- Criar evento futuro para o Guinho
- Verificar logs do sistema
- Aguardar horários de notificação

#### **3. Status do Sistema:**
- Dashboard mostra se alertas estão ativos
- Logs mostram envio de emails
- Google Calendar mostra eventos sincronizados

---

### 🎯 **RESULTADO FINAL**

**Para o Guinho (e qualquer artista):**

1. **📅 Eventos aparecem automaticamente** no Google Calendar
2. **📧 Recebe emails nos horários programados**
3. **🖥️ Vê alertas no computador** (se logado)
4. **📱 Notificações no celular** (via Google Calendar)
5. **🔄 Tudo sincronizado** entre empresa e artista

**O artista nunca perde um evento! 🎭✨**