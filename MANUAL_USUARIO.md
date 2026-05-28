# 📱 MANUAL DO USUÁRIO - Sistema de Gerenciamento de Artistas

## 🎯 ACESSO AO SISTEMA

### Para o Empresário:
- **URL:** http://localhost:5000 (ou URL do ngrok)
- **Usuário:** empresario
- **Senha:** 123456
- **Tipo:** Empresário (acesso completo)

### Para Artistas:
1. Clique em "Cadastre-se" na tela de login
2. Preencha seus dados
3. Selecione "Artista" como tipo de usuário
4. Aguarde o empresário vincular sua conta

## 🏢 FUNÇÕES DO EMPRESÁRIO

### 1. CADASTRAR ARTISTAS
- Acesse "Artistas" → "Novo Artista"
- Preencha: Nome, Nome Artístico, Email, Telefone, Gênero
- O sistema atribui uma cor automaticamente
- Use o mesmo email se o artista quiser fazer login

### 2. CRIAR EVENTOS
- Acesse "Eventos" → "Novo Evento"
- Selecione o artista
- Escolha o tipo: Show, Entrevista, Sessão de Fotos, etc.
- Defina data, hora e local
- **ALERTAS AUTOMÁTICOS:** 2 dias, 1 dia e 3 horas antes

### 3. VISUALIZAR AGENDA
- Acesse "Agenda" para ver calendário completo
- Cada artista tem sua cor
- Clique nos eventos para ver detalhes
- Visão mensal, semanal ou diária

### 4. RELATÓRIOS
- Acesse "Relatórios" para estatísticas
- Gráficos de performance por artista
- Eventos por mês e por tipo
- Exportar dados em CSV

## 🎤 FUNÇÕES DOS ARTISTAS

### 1. VER AGENDA PESSOAL
- Acesse "Agenda" para ver APENAS seus eventos
- Mesmas funcionalidades do empresário
- Cores e alertas automáticos

### 2. CRIAR EVENTOS PRÓPRIOS
- Pode criar eventos para si mesmo
- Mesmo sistema de alertas
- Notificações por email

### 3. DASHBOARD PESSOAL
- Vê apenas suas estatísticas
- Próximos eventos
- Eventos do dia

## 📧 SISTEMA DE NOTIFICAÇÕES

### EMAILS AUTOMÁTICOS:
- ✅ **2 dias antes** do evento
- ✅ **1 dia antes** do evento
- ✅ **3 horas antes** do evento

### QUEM RECEBE:
- **Artista responsável** pelo evento
- **Todos os empresários** (managers)

### CONTEÚDO DO EMAIL:
- Nome do evento
- Data e horário
- Local
- Descrição
- Nome do artista

## 🔧 CONFIGURAÇÕES

## 📅 INTEGRAÇÃO GOOGLE CALENDAR

### CONFIGURAÇÃO INICIAL (ADMINISTRADOR):

#### 1. GOOGLE CLOUD CONSOLE:
1. **Acesse:** https://console.cloud.google.com/
2. **Crie ou selecione** um projeto
3. **Habilite a API:** APIs & Services → Library → "Google Calendar API"
4. **Crie credenciais:** APIs & Services → Credentials → Create Credentials → OAuth 2.0
5. **Configure URLs:** Adicione `http://localhost:5000/auth/google/callback`
6. **Baixe credenciais:** Salve como `credentials.json` na pasta do projeto

#### 2. USUÁRIOS DE TESTE:
1. **OAuth consent screen** → Test users
2. **Adicione emails** dos empresários e artistas
3. **Status:** Manter em "Testing" para uso privado

#### 3. PRIMEIRO USO:
1. **No Dashboard:** Clique em "Conectar Google Calendar"
2. **Autorize:** Permita acesso ao Google Calendar
3. **Status:** Verá "Conectado" em verde
4. **Teste:** Crie um evento e verifique no calendar.google.com

### COMO FUNCIONA:

#### SINCRONIZAÇÃO AUTOMÁTICA:
- ✅ **Novos eventos** → Criados automaticamente no Google Calendar
- ✅ **Edições** → Atualizadas no Google Calendar
- ✅ **Exclusões** → Removidas do Google Calendar
- ✅ **Cores por artista** → Mantidas no Google Calendar

#### MÚLTIPLAS AGENDAS:
- 📋 **Empresário:** Evento criado na agenda do empresário
- 🎤 **Artista:** Evento criado na agenda do artista específico
- 📧 **Convites:** Ambos recebem convite automático

#### NOTIFICAÇÕES GOOGLE:
- ⏰ **2 dias antes** → Email do Google
- ⏰ **1 dia antes** → Email do Google  
- ⏰ **3 horas antes** → Email do Google
- ⏰ **30 minutos** → Popup no celular/computador

### RESOLUÇÃO DE PROBLEMAS:

#### "ACESSO BLOQUEADO" OU "APP NÃO VERIFICADO":
- ✅ **Normal em desenvolvimento**
- ✅ **Clique em "Avançado"** → "Ir para [nome do app] (não seguro)"
- ✅ **Autorize mesmo assim** - é seu próprio app

#### EVENTOS NÃO APARECEM NO CELULAR:
1. **Força sincronização:** Puxe para baixo no app Google Calendar
2. **Verifique configurações:** Calendar → Sincronização automática
3. **Teste no browser:** Acesse calendar.google.com
4. **Aguarde:** Pode demorar até 15 minutos

#### ERRO "CREDENTIALS NOT FOUND":
1. **Verifique arquivo:** `credentials.json` na pasta do projeto
2. **Re-baixe credenciais** do Google Cloud Console
3. **Reinicie servidor:** `python app.py`

#### DESCONECTAR/RECONECTAR:
1. **No Dashboard:** Clique em "Desconectar"
2. **Google Account:** Remova permissão em myaccount.google.com/permissions
3. **Reconecte:** Clique novamente em "Conectar Google Calendar"

### BENEFÍCIOS DA INTEGRAÇÃO:

#### PARA EMPRESÁRIOS:
- 🗓️ **Agenda unificada** - Todos os artistas em uma agenda
- 📱 **Acesso mobile** - Google Calendar app
- 🔔 **Alertas automáticos** - Nunca esquecer eventos
- 👥 **Compartilhamento** - Fácil de mostrar para terceiros

#### PARA ARTISTAS:
- 📅 **Agenda pessoal** - Apenas seus eventos
- 🎨 **Cor personalizada** - Identificação visual
- 📧 **Convites automáticos** - Confirmação de presença
- 📲 **Sincronização** - Todos os dispositivos

### DICAS IMPORTANTES:

#### SEGURANÇA:
- 🔒 **Dados privados** - Apenas você acessa sua agenda
- 🛡️ **OAuth 2.0** - Padrão de segurança do Google
- ❌ **Sem senhas** - Sistema não armazena senha do Google

#### LIMITAÇÕES:
- 👥 **Usuários de teste** - Máximo 100 usuários em desenvolvimento
- 🔄 **Sincronização** - Apenas do sistema → Google (unidirecional)
- 📝 **Edições** - Alterar no sistema, não direto no Google

### ALTERAR SENHA:
1. Faça logout
2. Entre novamente
3. Acesse configurações (em desenvolvimento)

## 🎨 CORES DOS ARTISTAS

O sistema atribui cores automaticamente:
- 🔴 Vermelho
- 🟢 Verde  
- 🔵 Azul
- 🟡 Amarelo
- 🟣 Roxo
- 🟠 Laranja

## 📊 TIPOS DE EVENTOS

### PRÉ-CONFIGURADOS:
- **Show** - Apresentações musicais
- **Entrevista** - Mídia e imprensa
- **Sessão de Fotos** - Fotografia
- **Gravação** - Estúdio
- **Reunião** - Planejamento
- **Live/Stream** - Online
- **Radio/TV** - Mídia tradicional
- **Evento Promocional** - Marketing

## 🚨 DICAS IMPORTANTES

### PARA O EMPRESÁRIO:
1. **Sempre altere a senha padrão**
2. **Cadastre artistas com email correto** (para notificações)
3. **Use tipos de eventos** para melhor organização
4. **Verifique relatórios** regularmente

### PARA ARTISTAS:
1. **Use o mesmo email** cadastrado pelo empresário
2. **Confirme recebimento** das notificações
3. **Comunique mudanças** ao empresário
4. **Acesse regularmente** para ver novos eventos

## 📞 SUPORTE

Em caso de problemas:
1. Verifique se está logado corretamente
2. Confirme o tipo de usuário (Empresário/Artista)
3. Teste em navegador atualizado
4. Entre em contato com o desenvolvedor

## 🎉 BENEFÍCIOS

### PARA EMPRESÁRIOS:
- ✅ Organização completa da agenda
- ✅ Notificações automáticas
- ✅ Relatórios profissionais
- ✅ Cores para fácil identificação
- ✅ Backup dos eventos

### PARA ARTISTAS:
- ✅ Nunca esquecer compromissos
- ✅ Agenda sempre atualizada
- ✅ Alertas por email
- ✅ Visão profissional
- ✅ Integração com Google
