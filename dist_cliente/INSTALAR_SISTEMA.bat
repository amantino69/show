@echo off
chcp 65001 >nul
echo.
echo ============================================================
echo    SISTEMA DE GERENCIAMENTO DE ARTISTAS - INSTALAÇÃO
echo ============================================================
echo.
echo Este script irá instalar automaticamente o sistema no seu computador.
echo Aguarde enquanto verificamos os requisitos...
echo.

:: Verificar se Python está instalado
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Python já está instalado no sistema.
    goto :install_deps
)

echo ⚠️ Python não foi encontrado. Iniciando instalação...
echo.
echo Baixando Python 3.11...

:: Criar diretório temporário
if not exist "temp" mkdir temp

:: Baixar Python (usando PowerShell)
echo Baixando Python 3.11.9 (pode demorar alguns minutos)...
powershell -Command "& {Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' -OutFile 'temp\python-installer.exe'}"

if not exist "temp\python-installer.exe" (
    echo ❌ Erro ao baixar Python. Verifique sua conexão com a internet.
    echo Por favor, baixe manualmente em: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo.
echo Instalando Python...
echo IMPORTANTE: Durante a instalação, marque a opção "Add Python to PATH"
echo.
start /wait temp\python-installer.exe /quiet InstallAllUsers=1 PrependPath=1

:: Atualizar variáveis de ambiente na sessão atual
call refreshenv >nul 2>&1

:: Verificar instalação
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Erro na instalação do Python.
    echo Por favor, reinstale manualmente e marque "Add Python to PATH"
    pause
    exit /b 1
)

echo ✓ Python instalado com sucesso!

:install_deps
echo.
echo Instalando dependências do sistema...
echo.

:: Atualizar pip
python -m pip install --upgrade pip

:: Instalar dependências
python -m pip install flask flask-sqlalchemy flask-login flask-wtf wtforms apscheduler pillow

if %errorlevel% neq 0 (
    echo ❌ Erro ao instalar dependências.
    echo Tente executar manualmente: pip install -r requirements.txt
    pause
    exit /b 1
)

echo ✓ Dependências instaladas com sucesso!
echo.

:: Inicializar banco de dados
echo Inicializando banco de dados...
python init_db.py

if %errorlevel% neq 0 (
    echo ❌ Erro ao inicializar banco de dados.
    pause
    exit /b 1
)

echo ✓ Sistema instalado com sucesso!
echo.
echo ============================================================
echo                    INSTALAÇÃO CONCLUÍDA
echo ============================================================
echo.
echo O sistema foi instalado e está pronto para uso!
echo.
echo Para iniciar o sistema, execute o arquivo: INICIAR_SISTEMA.bat
echo.
echo Dados de acesso padrão:
echo   Usuário: empresario
echo   Senha: 123456
echo.
echo IMPORTANTE: Altere a senha após o primeiro login!
echo.

:: Limpar arquivos temporários
if exist "temp" rmdir /s /q temp

echo Pressione qualquer tecla para continuar...
pause >nul
