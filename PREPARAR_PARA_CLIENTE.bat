@echo off
chcp 65001 >nul
echo.
echo ============================================================
echo              PREPARAÇÃO PARA CLIENTE
echo ============================================================
echo.

:: Criar pasta de distribuição
echo Criando pasta de distribuição...
if exist "dist_cliente" rmdir /s /q dist_cliente
mkdir dist_cliente
echo ✓ Pasta criada

:: Copiar arquivos essenciais
echo.
echo Copiando arquivos do sistema...

:: Copiar aplicação principal
xcopy "app" "dist_cliente\app" /E /I /Y >nul
xcopy "instance" "dist_cliente\instance" /E /I /Y >nul 2>nul
copy "app.py" "dist_cliente\" >nul
copy "config.py" "dist_cliente\" >nul
copy "dev_config.py" "dist_cliente\" >nul
copy "requirements.txt" "dist_cliente\" >nul
copy "init_db.py" "dist_cliente\" >nul

:: Copiar scripts de instalação
copy "INSTALAR_SISTEMA.bat" "dist_cliente\" >nul
copy "INICIAR_SISTEMA.bat" "dist_cliente\" >nul
copy "VERIFICAR_SISTEMA.bat" "dist_cliente\" >nul

:: Copiar documentação
copy "MANUAL_CLIENTE.md" "dist_cliente\" >nul
copy "MANUAL_MARKETING.md" "dist_cliente\" >nul
copy "GOOGLE_SETUP.md" "dist_cliente\" >nul 2>nul

:: Copiar scripts utilitários
copy "fix_database.py" "dist_cliente\" >nul 2>nul
copy "fix_marketing_module.py" "dist_cliente\" >nul 2>nul

echo ✓ Arquivos copiados

:: Criar arquivo .env padrão
echo.
echo Criando arquivo de configuração padrão...
(
echo # Configurações do Sistema de Gerenciamento de Artistas
echo SECRET_KEY=sua_chave_secreta_super_segura_123456789
echo.
echo # Configurações de Email ^(opcional^)
echo MAIL_SERVER=smtp.gmail.com
echo MAIL_PORT=587
echo MAIL_USE_TLS=True
echo MAIL_USERNAME=seu.email@gmail.com
echo MAIL_PASSWORD=sua_senha_de_app_do_gmail
echo.
echo # Configurações do Banco de Dados
echo DATABASE_URL=sqlite:///instance/artistas_sistema.db
) > "dist_cliente\.env"
echo ✓ Arquivo .env criado

:: Criar README para cliente
echo.
echo Criando instruções rápidas...
(
echo SISTEMA DE GERENCIAMENTO DE ARTISTAS
echo ====================================
echo.
echo INSTRUÇÕES DE INSTALAÇÃO:
echo.
echo 1. Execute: INSTALAR_SISTEMA.bat ^(como administrador^)
echo 2. Aguarde a instalação completa
echo 3. Execute: INICIAR_SISTEMA.bat
echo 4. Acesse no navegador: http://localhost:5001
echo.
echo DADOS DE ACESSO:
echo Usuário: empresario
echo Senha: 123456
echo.
echo Para mais detalhes, consulte: MANUAL_CLIENTE.md
echo.
echo IMPORTANTE: Mantenha a janela do terminal aberta enquanto usar o sistema!
) > "dist_cliente\LEIA-ME.txt"
echo ✓ Instruções criadas

:: Criar script de empacotamento
echo.
echo Criando script de compactação...
(
echo @echo off
echo echo Compactando sistema para distribuição...
echo powershell -Command "Compress-Archive -Path '.\*' -DestinationPath '..\SistemaGerenciamentoArtistas.zip' -Force"
echo echo ✓ Arquivo SistemaGerenciamentoArtistas.zip criado!
echo echo.
echo echo O arquivo está pronto para envio ao cliente.
echo pause
) > "dist_cliente\COMPACTAR.bat"
echo ✓ Script de compactação criado

:: Criar verificador de integridade
echo.
echo Criando verificador de integridade...
(
echo @echo off
echo chcp 65001 ^>nul
echo echo Verificando integridade dos arquivos...
echo echo.
echo if not exist "app.py" echo ❌ app.py faltando
echo if not exist "config.py" echo ❌ config.py faltando
echo if not exist "requirements.txt" echo ❌ requirements.txt faltando
echo if not exist "INSTALAR_SISTEMA.bat" echo ❌ INSTALAR_SISTEMA.bat faltando
echo if not exist "INICIAR_SISTEMA.bat" echo ❌ INICIAR_SISTEMA.bat faltando
echo if not exist ".env" echo ❌ .env faltando
echo if not exist "app\__init__.py" echo ❌ pasta app incompleta
echo echo.
echo echo ✓ Verificação concluída
echo pause
) > "dist_cliente\VERIFICAR_ARQUIVOS.bat"
echo ✓ Verificador criado

echo.
echo ============================================================
echo                PREPARAÇÃO CONCLUÍDA!
echo ============================================================
echo.
echo ✓ Todos os arquivos foram preparados na pasta: dist_cliente
echo.
echo PRÓXIMOS PASSOS:
echo 1. Entre na pasta dist_cliente
echo 2. Execute COMPACTAR.bat para criar o ZIP
echo 3. Envie o arquivo SistemaGerenciamentoArtistas.zip para o cliente
echo.
echo O cliente receberá:
echo - Sistema completo
echo - Scripts de instalação automática
echo - Manual detalhado de uso
echo - Verificadores de sistema
echo.
echo Pressione qualquer tecla para abrir a pasta...
pause >nul
explorer dist_cliente
