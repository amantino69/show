# 🎨 Sistema de Gestão Multi-Artistas

Um sistema completo em Flask para empresários gerenciarem **todos os tipos de artistas** - de cantores a influenciadores digitais, modelos, atores, dançarinos e muito mais! Inclui integração ao Google Agenda, sistema de notificações e analytics avançado.

## 🎯 Funcionalidades Principais

### 🎪 **Gestão Multi-Categoria de Artistas:**
- **9 Tipos de Artistas:** Cantor/Cantora, Influenciador Digital, Modelo, Ator/Atriz, Dançarino, DJ/Produtor, Comediante, Artista Visual, Outros
- **Categorização Visual:** Cada tipo possui ícone e cor específicos  
- **Interface Inclusiva:** Design moderno que representa toda diversidade artística
- **Dashboard Inteligente:** Estatísticas por categoria com gráficos visuais

### 📅 **Agenda Compartilhada Avançada:**
- **Calendário visual** com cores por artista e tipo
- **10 tipos de eventos** (Shows, Entrevistas, Sessões de Fotos, Gravações, etc.)
- **Integração Google Calendar** - Sincronização automática
- **Notificações inteligentes** - Alertas 1 dia, 2 horas e 30 minutos antes

### 📱 **Interface Mobile-First:**
- **Menu Hambúrguer** responsivo para dispositivos móveis
- **Design adaptativo** que funciona perfeitamente em qualquer tela
- **Touch-friendly** com navegação intuitiva
- **Performance otimizada** para conexões lentas

### 📊 **Analytics e Relatórios:**
- **Dashboard com métricas** em tempo real
- **Gráficos por categoria** de artista
- **Relatórios de performance** por tipo de evento
- **Exportação em PDF** e outros formatos

### 🎪 **Marketing Integrado:**
- **Gestão de posts** para redes sociais
- **Press kits digitais** personalizados
- **Calendário de publicações** organizado
- **Métricas de engajamento** por artista

### Para Empresários:
- **Dashboard completo** com estatísticas e visão geral por categoria
- **Gerenciamento multi-categoria** de artistas com tipos específicos
- **Planejamento de eventos** adaptado para cada tipo de artista
- **Agenda compartilhada** com visualização por categoria
- **Relatórios avançados** com analytics por tipo de artista
- **Sistema de marketing** integrado com métricas

### Para Artistas:
- **Acesso personalizado** à própria agenda
- **Perfil específico** do seu tipo artístico
- **Notificações inteligentes** por email e no sistema
- **Interface otimizada** para mobile e desktop

## 🚀 Instalação e Configuração

### 1. Requisitos
- Python 3.8+
- Conta Gmail com senha de app
- Projeto Google Cloud com Calendar API habilitado

### 2. Instalação
```bash
# Clone ou baixe o projeto
cd show

# Ative o ambiente virtual (se tiver)
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Instale as dependências
pip install -r requirements.txt
```

### 3. Configuração

#### 3.1 Arquivo .env
Edite o arquivo `.env` com suas configurações:

```env
# Configurações do Sistema
SECRET_KEY=sua_chave_secreta_muito_segura_aqui
DATABASE_URL=sqlite:///artistas_sistema.db

# Configurações do Email (Gmail)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=seu_email@gmail.com
MAIL_PASSWORD=sua_senha_de_app_do_gmail

# Configurações do Google Calendar API
GOOGLE_CLIENT_ID=seu_client_id_aqui
GOOGLE_CLIENT_SECRET=seu_client_secret_aqui
GOOGLE_REDIRECT_URI=http://localhost:5000/callback
```

#### 3.2 Gmail - Senha de App
1. Acesse https://myaccount.google.com/security
2. Ative a verificação em 2 etapas
3. Gere uma "Senha de app" para o projeto
4. Use essa senha no campo `MAIL_PASSWORD`

#### 3.3 Google Calendar API
1. Acesse https://console.cloud.google.com/
2. Crie um novo projeto ou use um existente
3. Habilite a "Google Calendar API"
4. Crie credenciais OAuth 2.0
5. Adicione `http://localhost:5000/callback` como URI de redirecionamento
6. Copie Client ID e Client Secret para o .env

### 4. Inicialização
```bash
# Inicializar banco de dados
python init_db.py

# Iniciar o sistema
python app.py
```

O sistema estará disponível em: http://localhost:5000

### 5. Primeiro Login
- **Usuário:** empresario
- **Senha:** 123456
- **IMPORTANTE:** Altere a senha após o primeiro login!

## 📱 Como Usar

### Para Empresários:

1. **Cadastrar Artistas:**
   - Acesse "Artistas" → "Novo Artista"
   - Preencha os dados (nome, email, gênero, etc.)
   - O sistema atribui automaticamente uma cor

2. **Criar Eventos:**
   - Acesse "Eventos" → "Novo Evento"
   - Selecione o artista e tipo de evento
   - Defina data, hora e local
   - O evento vai automaticamente para o Google Agenda

3. **Acompanhar Agenda:**
   - Use a "Agenda" para visão mensal/semanal
   - Cada artista tem sua cor específica
   - Clique nos eventos para ver detalhes

4. **Relatórios:**
   - Acesse "Relatórios" para ver estatísticas
   - Analise performance por artista
   - Exporte dados para Excel/CSV

### Para Artistas:

1. **Criar Conta:**
   - Use "Cadastre-se" na tela de login
   - Selecione "Artista" como tipo
   - Aguarde o empresário vincular sua conta

2. **Ver Agenda:**
   - Acesse "Agenda" para ver seus eventos
   - Receba notificações por email
   - Veja apenas seus próprios eventos

## 🎨 Tipos de Eventos

O sistema vem com tipos pré-configurados:
- **Show** - Apresentações musicais
- **Entrevista** - Entrevistas para mídia
- **Sessão de Fotos** - Sessões fotográficas
- **Gravação** - Gravação de música/vídeo
- **Reunião** - Reuniões de planejamento
- **Live/Stream** - Transmissões ao vivo
- **Radio/TV** - Participações em rádio/TV
- **Evento Promocional** - Eventos de divulgação

## 🔔 Sistema de Notificações

As notificações são enviadas automaticamente:
- **2 dias antes** do evento
- **1 dia antes** do evento  
- **3 horas antes** do evento

Os emails são enviados para:
- O artista responsável
- Todos os empresários

## 📊 Relatórios e Estatísticas

### Dashboard Principal:
- Total de artistas ativos
- Eventos futuros
- Eventos do dia
- Eventos da semana

### Relatórios Avançados:
- Eventos por mês (gráfico)
- Performance por artista
- Eventos por tipo
- Taxa de sucesso dos eventos
- Exportação para Excel/CSV

## 🛠️ Tecnologias Utilizadas

- **Backend:** Python Flask
- **Banco de Dados:** SQLite (pode ser alterado para PostgreSQL/MySQL)
- **Frontend:** Bootstrap 5, FullCalendar.js, Chart.js
- **Email:** Flask-Mail (SMTP Gmail)
- **Agenda:** Google Calendar API
- **Notificações:** APScheduler para agendamento

## 🔧 Personalização

### Cores dos Artistas:
As cores são definidas automaticamente no arquivo `config.py`. Para personalizar, edite a lista `ARTIST_COLORS`.

### Tipos de Eventos:
Novos tipos podem ser adicionados diretamente no banco de dados ou através do painel administrativo.

### Horários de Notificação:
Edite o arquivo `app/notifications.py` para alterar os horários padrão (2 dias, 1 dia, 3 horas).

## 🆘 Solução de Problemas

### Erro de Email:
- Verifique se a senha de app está correta
- Confirme se a verificação em 2 etapas está ativa
- Teste com um email simples primeiro

### Erro Google Calendar:
- Verifique as credenciais OAuth 2.0
- Confirme se a Calendar API está habilitada
- Teste a autorização manualmente

### Problemas de Login:
- Confirme se o banco de dados foi inicializado
- Verifique se o usuário padrão foi criado
- Tente recriar o banco: `python init_db.py`

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique os logs do sistema
2. Consulte a documentação das APIs utilizadas
3. Teste em modo debug: `python app.py` (debug=True)

## 🔒 Segurança

- Sempre altere a senha padrão
- Use HTTPS em produção
- Mantenha as dependências atualizadas
- Configure firewall adequadamente
- Faça backup regular do banco de dados

## 📈 Próximas Funcionalidades

- Sistema de tarefas/checklist
- Integração com redes sociais
- Relatórios financeiros
- App mobile
- API REST para integrações
