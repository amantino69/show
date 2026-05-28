@echo off
title Show Manager - Servidor Completo
color 0A
echo.
echo ==========================================
echo    SHOW MANAGER - SERVIDOR DIARIO
echo    Sistema de Alertas + Acesso Remoto
echo ==========================================
echo.

REM Verificar se estamos no diretório correto
if not exist "app.py" (
    echo ERRO: Execute este script na pasta do Show Manager
    echo Caminho atual: %CD%
    pause
    exit /b 1
)

echo [1/4] Verificando dependencias...
pip show plyer >nul 2>&1
if errorlevel 1 (
    echo Instalando dependencias necessarias...
    pip install plyer schedule reportlab openpyxl twilio requests
)
echo ✓ Dependencias OK

echo.
echo [2/4] Iniciando servidor Flask...
start "Show Manager - Servidor" cmd /k "title Servidor Flask && echo Servidor Flask rodando na porta 5001... && python app.py"

echo ✓ Servidor iniciado

echo.
echo [3/4] Aguardando servidor inicializar...
timeout /t 10 /nobreak > nul

echo.
echo [4/4] Iniciando Ngrok para acesso remoto...
start "Show Manager - Ngrok" cmd /k "title Ngrok - Acesso Remoto && echo Iniciando Ngrok... && ngrok http 5001"

echo ✓ Ngrok iniciado

echo.
echo [OPCIONAL] Iniciando aplicativo de alertas desktop...
start "Show Manager - Alertas" cmd /k "title Alertas Desktop && echo Sistema de alertas desktop... && python desktop_alerts.py"

echo ✓ Alertas desktop iniciado

echo.
echo ==========================================
echo           ✓ TUDO INICIADO!
echo ==========================================
echo.
echo PROXIMOS PASSOS:
echo.
echo 1. Aguarde 30-60 segundos para tudo carregar
echo.
echo 2. Na janela do Ngrok, procure por:
echo    "Forwarding https://xxxxx.ngrok.io -> http://localhost:5001"
echo.
echo 3. Copie a URL (https://xxxxx.ngrok.io)
echo.
echo 4. Compartilhe essa URL com todos os usuarios
echo.
echo 5. Acesse pelo navegador para testar:
echo    - Usuario: empresario
echo    - Senha: 123456
echo.
echo 6. IMPORTANTE: Mantenha este servidor ligado!
echo    As 3 janelas abertas devem continuar rodando.
echo.
echo ==========================================
echo.
echo Dicas:
echo • Minimize as janelas, mas NAO as feche
echo • O sistema funcionara 24 horas automaticamente
echo • Artistas receberao alertas nos celulares/PCs
echo • Para parar tudo: feche todas as janelas
echo.
echo ==========================================
echo.
pause
