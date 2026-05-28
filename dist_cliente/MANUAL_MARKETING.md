# MÓDULO DE MARKETING & DIVULGAÇÃO

Este documento contém instruções detalhadas sobre como usar o módulo de Marketing & Divulgação do Sistema de Gerenciamento, além de soluções para problemas comuns.

## ÍNDICE

1. [Visão Geral do Módulo](#visão-geral-do-módulo)
2. [Como Usar](#como-usar)
   - [Banco de Mídia](#banco-de-mídia)
   - [Posts para Redes Sociais](#posts-para-redes-sociais)
   - [Press Kit](#press-kit)
   - [Métricas de Redes Sociais](#métricas-de-redes-sociais)
3. [Solução de Problemas](#solução-de-problemas)
   - [Erro ao Criar Posts](#erro-ao-criar-posts)
   - [Erro ao Fazer Upload de Arquivos](#erro-ao-fazer-upload-de-arquivos)
   - [Outros Problemas Comuns](#outros-problemas-comuns)
4. [Dicas e Melhores Práticas](#dicas-e-melhores-práticas)

## VISÃO GERAL DO MÓDULO

O módulo de Marketing & Divulgação é projetado para ajudar a gerenciar todos os aspectos relacionados à divulgação dos artistas, incluindo:

- **Banco de Mídia**: Armazenamento e organização de fotos, vídeos e arquivos
- **Posts para Redes Sociais**: Agendamento e controle de posts para diversas plataformas
- **Press Kit Digital**: Criação e gestão de press kits profissionais para cada artista
- **Métricas e Relatórios**: Acompanhamento do desempenho nas redes sociais

## COMO USAR

### Banco de Mídia

1. Acesse o menu "Marketing" no painel lateral e clique em "Banco de Mídia"
2. Use o botão "Upload Mídia" para adicionar novos arquivos
3. Filtre os arquivos por tipo (imagem, vídeo, documento) ou por artista
4. Cada arquivo pode ser associado a um artista e/ou evento específico
5. Adicione título, descrição e tags para facilitar a busca

### Posts para Redes Sociais

1. Acesse o menu "Marketing" e clique em "Posts"
2. Use o botão "Novo Post" para criar um novo post
3. Preencha todos os campos obrigatórios (marcados com *)
4. Selecione uma data e hora futura para agendar o post
5. Escolha uma imagem do banco de mídia para acompanhar o post
6. Salve como "Rascunho" ou "Agendado"
7. Visualize os posts na visualização de lista ou calendário

> **IMPORTANTE:** Por enquanto, o sistema apenas registra os posts agendados. A publicação efetiva nas redes sociais precisa ser feita manualmente. Em uma futura versão, será implementada a publicação automática.

### Press Kit

1. Acesse o menu "Marketing" e clique em "Press Kit"
2. Selecione o artista para editar seu press kit
3. Preencha os dados de biografia, links, informações técnicas, etc.
4. Selecione fotos do banco de mídia para perfil e banner
5. Marque como "Público" para disponibilizar online
6. Use o botão "Visualizar" para ver como ficará para o público

### Métricas de Redes Sociais

1. Acesse o menu "Marketing" e clique em "Métricas"
2. Adicione dados de cada plataforma usando o botão "Adicionar Métricas"
3. Atualize regularmente para acompanhar o crescimento
4. Veja os posts mais engajados na parte inferior da página

## SOLUÇÃO DE PROBLEMAS

### Erro ao Criar Posts

Se você encontrar erros ao tentar criar ou agendar posts para redes sociais, tente as seguintes soluções:

1. **Verificar campos obrigatórios**: Certifique-se de preencher todos os campos marcados com asterisco (*).

2. **Formato de data e hora**: Certifique-se de que o formato da data/hora está correto. O sistema espera o formato YYYY-MM-DDThh:mm (ex: 2025-07-05T14:30).

3. **Executar script de correção**:
   ```
   cd c:\caminho\para\sistema
   python fix_marketing_module.py
   ```
   
   Este script verificará e corrigirá problemas comuns com as tabelas do banco de dados.

4. **Verificar se há artistas cadastrados**: O sistema precisa de pelo menos um artista ativo para criar posts.

5. **Verificar logs do sistema**: Se o erro persistir, verifique os logs do sistema para mais detalhes.

### Erro ao Fazer Upload de Arquivos

Se você tiver problemas ao fazer upload de arquivos para o banco de mídia:

1. **Tamanho do arquivo**: Verifique se o arquivo não excede 50MB.

2. **Formato permitido**: O sistema aceita apenas imagens (PNG, JPG, GIF, WEBP), vídeos (MP4, MOV, AVI) e documentos (PDF, DOC, DOCX).

3. **Permissões de pasta**: Certifique-se de que a pasta `static/uploads/media` tem permissões de escrita.

4. **Espaço em disco**: Verifique se há espaço suficiente em disco para o upload.

### Outros Problemas Comuns

1. **Press Kit não aparece publicamente**: Verifique se a opção "Press Kit Público" está marcada nas configurações do press kit.

2. **Métricas não são salvas**: Certifique-se de preencher todos os campos obrigatórios, incluindo datas de início e fim do período.

3. **Imagens não aparecem**: Verifique se o caminho da pasta `static/uploads/media` está correto e se os arquivos existem.

4. **Erros após atualização do sistema**: Execute o script `fix_marketing_module.py` para corrigir problemas de incompatibilidade.

## DICAS E MELHORES PRÁTICAS

1. **Organização de mídia**: Use tags e descrições consistentes para facilitar a busca no banco de mídia.

2. **Agendamento estratégico**: Use a visualização de calendário para distribuir os posts de forma equilibrada.

3. **Backup regular**: Faça backup regular da pasta `static/uploads/media` e do banco de dados.

4. **Métricas**: Atualize as métricas de redes sociais pelo menos uma vez por semana para acompanhar o crescimento.

5. **Imagens otimizadas**: Redimensione imagens grandes antes do upload para economizar espaço e melhorar o desempenho.

---

Para mais informações ou suporte, entre em contato com o desenvolvedor do sistema.
