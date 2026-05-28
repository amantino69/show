# INSTRUÇÕES PARA CONFIGURAR GOOGLE CLOUD CONSOLE

## 1. ADICIONAR USUÁRIOS DE TESTE

1. Acesse: https://console.cloud.google.com/
2. Selecione seu projeto
3. Vá em "APIs & Services" → "OAuth consent screen"
4. Na seção "Test users", clique em "ADD USERS"
5. Adicione os emails:
   - claudio.vieiraamantino@gmail.com (empresário)
   - emails dos artistas que vão usar o sistema

## 2. CONFIGURAR REDIRECT URIs

1. Vá em "APIs & Services" → "Credentials"
2. Clique na sua credencial OAuth 2.0
3. Em "Authorized redirect URIs", adicione:
   - http://localhost:5000/auth/google/callback
   - https://SUA_URL_NGROK.ngrok.io/auth/google/callback (se usar ngrok)

## 3. SCOPES NECESSÁRIOS

Certifique-se que estes scopes estão habilitados:
- https://www.googleapis.com/auth/calendar
- https://www.googleapis.com/auth/calendar.events

## 4. PUBLICAR APP (OPCIONAL - PARA PRODUÇÃO)

Para uso público sem limitações:
1. Complete todas as informações do "OAuth consent screen"
2. Adicione política de privacidade
3. Submeta para verificação do Google
4. Aguarde aprovação (pode demorar alguns dias)
