@echo off
title Show Manager - Servidor Universal
color 0B
echo.
echo ==========================================
echo    SHOW MANAGER - SERVIDOR UNIVERSAL
echo    (Multiplas opcoes de acesso remoto)
echo ==========================================
echo.

REM Verificar se estamos no diretório correto
if not exist "app.py" (
    echo ERRO: Execute este script na pasta do Show Manager
    pause
    exit /b 1
)

echo Escolha o metodo de acesso remoto:
echo.
echo 1) Ngrok (padrao)
echo 2) LocalTunnel (alternativa para firewalls)
echo 3) Serveo (sem instalacao)
echo 4) Apenas rede local (sem acesso externo)
echo 5) Cloudflare Tunnel
echo.
set /p choice="Digite sua opcao (1-5): "

echo.
echo [1/2] Iniciando servidor Flask...
start "Show Manager - Servidor" cmd /k "title Servidor Flask && echo Servidor Flask rodando na porta 5001... && python app.py"

echo ✓ Servidor iniciado
echo.
echo [2/2] Iniciando acesso remoto...

if "%choice%"=="1" goto :ngrok
if "%choice%"=="2" goto :localtunnel  
if "%choice%"=="3" goto :serveo
if "%choice%"=="4" goto :local
if "%choice%"=="5" goto :cloudflare

echo Opcao invalida, usando ngrok...
goto :ngrok

:ngrok
echo.
echo Iniciando Ngrok...
start "Show Manager - Ngrok" cmd /k "title Ngrok && echo Iniciando Ngrok... && ngrok http 5001"
echo.
echo ✓ Ngrok iniciado
echo ℹ️  Copie a URL https://xxxxx.ngrok.io da janela do Ngrok
goto :end

:localtunnel
echo.
echo Verificando LocalTunnel...
where lt >nul 2>&1
if errorlevel 1 (
    echo Instalando LocalTunnel...
    npm install -g localtunnel
)
echo.
echo Iniciando LocalTunnel...
start "Show Manager - LocalTunnel" cmd /k "title LocalTunnel && echo Iniciando LocalTunnel... && lt --port 5001"
echo.
echo ✓ LocalTunnel iniciado
echo ℹ️  Copie a URL https://xxxxx.loca.lt da janela do LocalTunnel
goto :end

:serveo
echo.
echo Iniciando Serveo...
start "Show Manager - Serveo" cmd /k "title Serveo && echo Iniciando Serveo... && ssh -R 80:localhost:5001 serveo.net"
echo.
echo ✓ Serveo iniciado
echo ℹ️  Copie a URL https://xxxxx.serveo.net da janela do Serveo
goto :end

:cloudflare
echo.
echo Verificando Cloudflare Tunnel...
where cloudflared >nul 2>&1
if errorlevel 1 (
    echo.
    echo ❌ Cloudflare Tunnel nao encontrado
    echo.
    echo Para instalar:
    echo 1. Baixe de: https://github.com/cloudflare/cloudflared/releases
    echo 2. Execute novamente este script
    echo.
    pause
    exit /b 1
)
echo.
echo Iniciando Cloudflare Tunnel...
start "Show Manager - Cloudflare" cmd /k "title Cloudflare Tunnel && echo Iniciando Cloudflare Tunnel... && cloudflared tunnel --url http://localhost:5001"
echo.
echo ✓ Cloudflare Tunnel iniciado
echo ℹ️  Copie a URL https://xxxxx.trycloudflare.com da janela do Cloudflare
goto :end

:local
echo.
echo ==========================================
echo           ACESSO APENAS LOCAL
echo ==========================================
echo.
echo Descobrindo seu IP local...

for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr "IPv4"') do (
    for /f "tokens=1" %%b in ("%%a") do (
        set LOCAL_IP=%%b
    )
)

echo.
echo ✓ Servidor disponivel em:
echo.
echo 🏠 Acesso local: http://localhost:5001
echo 🌐 Acesso na rede: http://%LOCAL_IP%:5001
echo.
echo ℹ️  Compartilhe o segundo link com usuarios na mesma rede WiFi
echo ℹ️  Nao funcionara fora da rede local
goto :end

:end
echo.
echo.
echo ==========================================
echo [OPCIONAL] Iniciando sistema de alertas desktop...
start "Show Manager - Alertas" cmd /k "title Alertas Desktop && echo Sistema de alertas desktop... && python desktop_alerts.py"
echo ✓ Alertas desktop iniciado
echo.
echo ==========================================
echo           ✓ SISTEMA INICIADO!
echo ==========================================
echo.
echo PROXIMOS PASSOS:
echo.
echo 1. Aguarde 30-60 segundos
echo 2. Copie a URL da janela correspondente
echo 3. Compartilhe com todos os usuarios
echo 4. Teste o acesso
echo.
echo CREDENCIAIS DE TESTE:
echo • Usuario: empresario  
echo • Senha: 123456
echo.
echo ℹ️  Mantenha todas as janelas abertas!
echo.
echo ==========================================
echo.

if "%choice%"=="4" (
    echo DICA: Para este computador ter acesso externo,
    echo execute o script novamente e escolha opcao 1 ou 2
    echo.
)

echo Para diagnosticar problemas de conectividade:
echo Execute: diagnose_ngrok.bat
echo.
pause
