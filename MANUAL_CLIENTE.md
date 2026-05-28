# SISTEMA DE GERENCIAMENTO DE ARTISTAS
## Manual de Instalação e Uso para Clientes

---

## 📋 PASSO A PASSO PARA INSTALAÇÃO

### PASSO 1: Baixar e Extrair o Sistema
1. Baixe o arquivo ZIP do sistema completo
2. Extraia todos os arquivos para uma pasta de sua escolha (ex: `C:\SistemaArtistas`)
3. Certifique-se de que todos os arquivos foram extraídos corretamente

### PASSO 2: Instalação Automática
1. **Localize o arquivo `INSTALAR_SISTEMA.bat`** na pasta extraída
2. **Clique com botão direito** no arquivo e selecione **"Executar como administrador"**
3. **Aguarde a instalação** (pode demorar alguns minutos)
   - O script irá baixar e instalar o Python automaticamente
   - Instalará todas as dependências necessárias
   - Configurará o banco de dados

⚠️ **IMPORTANTE**: Durante a instalação do Python, **NÃO FECHE** a janela. O processo é automático.

### PASSO 3: Iniciar o Sistema
1. **Localize o arquivo `INICIAR_SISTEMA.bat`**
2. **Clique duas vezes** para executar
3. **Uma janela preta (terminal) irá abrir** - **NÃO FECHE esta janela**
4. **O navegador abrirá automaticamente** mostrando o sistema

---

## 🔐 PRIMEIRO ACESSO

Quando o sistema abrir no navegador, use os dados padrão:
- **Usuário**: `empresario`
- **Senha**: `123456`

⚠️ **IMPORTANTE**: Altere esta senha assim que fizer o primeiro login!

---

## 🖥️ COMO USAR O SISTEMA

### Dashboard Principal
- Visão geral de eventos, artistas e alertas
- Acesso rápido a todas as funcionalidades

### Gerenciar Artistas
1. Vá em **"Artistas"** no menu lateral
2. Clique em **"Novo Artista"** para adicionar
3. Preencha os dados: nome artístico, email, telefone, gênero musical
4. Escolha uma cor para identificar o artista na agenda

### Criar Eventos
1. Vá em **"Eventos"** no menu lateral
2. Clique em **"Novo Evento"**
3. Preencha: título, data/hora, local, artista, tipo de evento
4. O sistema criará alertas automáticos

### Módulo de Marketing
1. **Banco de Mídia**: Faça upload de fotos, vídeos e documentos
2. **Posts para Redes Sociais**: Agende posts para Instagram, Facebook, YouTube, etc.
3. **Press Kit**: Crie materiais promocionais profissionais
4. **Métricas**: Acompanhe o desempenho nas redes sociais

### Sistema de Alertas
- **Alertas automáticos** são criados para cada evento
- **Notificações na tela** aparecem nos horários programados
- **Visualize alertas** na seção "Alertas Nativos"

---

## 🔧 SOLUÇÃO DE PROBLEMAS

### O sistema não abre
1. Verifique se executou como **administrador**
2. Tente executar `INSTALAR_SISTEMA.bat` novamente
3. Verifique sua conexão com a internet

### Janela do sistema fecha sozinha
- **NÃO FECHE** a janela preta (terminal) que aparece
- Esta janela deve permanecer aberta enquanto usar o sistema

### Erro "Porta em uso"
1. Feche todos os navegadores
2. Aguarde 30 segundos
3. Execute `INICIAR_SISTEMA.bat` novamente

### Sistema lento ou trava
1. Feche outros programas desnecessários
2. Reinicie o computador
3. Execute o sistema novamente

### Não consigo fazer login
- Certifique-se de usar: usuário `empresario` e senha `123456`
- Verifique se não há espaços extras ao digitar

---

## ⚙️ CONFIGURAÇÕES AVANÇADAS (OPCIONAL)

### Personalizar Email (para alertas por email)
1. Localize o arquivo `.env` na pasta do sistema
2. Abra com Bloco de Notas
3. Configure suas informações de email:
   ```
   MAIL_USERNAME=seu.email@gmail.com
   MAIL_PASSWORD=sua_senha_de_app
   ```

### Integração com Google Calendar
1. Siga as instruções no arquivo `GOOGLE_SETUP.md`
2. Configure as credenciais do Google API
3. Sincronize eventos automaticamente

---

## 📞 SUPORTE

### Durante o Teste
- **Anote todos os problemas** encontrados
- **Faça screenshots** de erros
- **Teste todas as funcionalidades** principais

### Funcionalidades Principais para Testar
- ✅ Criar e editar artistas
- ✅ Agendar eventos
- ✅ Upload de mídia
- ✅ Criar posts para redes sociais
- ✅ Verificar alertas automáticos
- ✅ Criar press kit

### Informações para Suporte
Se encontrar problemas, anote:
- Que ação estava fazendo quando o erro ocorreu
- Mensagem de erro (se houver)
- Versão do Windows que está usando
- Print da tela do erro

---

## 🚨 AVISOS IMPORTANTES

1. **Mantenha a janela preta aberta** enquanto usar o sistema
2. **Não mova ou delete** arquivos da pasta do sistema
3. **Faça backup** dos dados importantes regularmente
4. **Use apenas navegadores atualizados** (Chrome, Firefox, Edge)
5. **Sistema funciona offline** - não precisa de internet após instalação

---

## ✅ CHECKLIST DE TESTE

Para facilitar seu teste, verifique cada item:

### Instalação
- [ ] Sistema instalou sem erros
- [ ] Conseguiu fazer login
- [ ] Interface carregou corretamente

### Funcionalidades Básicas
- [ ] Criar novo artista
- [ ] Editar dados do artista
- [ ] Criar novo evento
- [ ] Ver eventos na agenda
- [ ] Alertas funcionam

### Módulo de Marketing
- [ ] Upload de arquivos funciona
- [ ] Criar post para redes sociais
- [ ] Editar press kit
- [ ] Visualizar métricas

### Geral
- [ ] Sistema é intuitivo
- [ ] Performance é adequada
- [ ] Não encontrou bugs graves

---

## 📝 FEEDBACK

Após o teste, forneça feedback sobre:
- **Facilidade de instalação** (1-10)
- **Facilidade de uso** (1-10)
- **Funcionalidades que mais gostou**
- **Sugestões de melhorias**
- **Problemas encontrados**

**Seu feedback é muito importante para melhorarmos o sistema!**
