@echo off
title Diagnostico Ngrok - Show Manager
color 0E
echo.
echo ==========================================
echo    DIAGNOSTICO DE CONECTIVIDADE NGROK
echo ==========================================
echo.

echo [INFO] Este script vai diagnosticar por que um computador
echo        nao consegue acessar a URL do ngrok
echo.

REM Solicitar URL do ngrok
set /p NGROK_URL="Digite a URL do ngrok (ex: https://abc123.ngrok.io): "

if "%NGROK_URL%"=="" (
    echo.
    echo ❌ ERRO: URL nao fornecida
    echo.
    echo Execute novamente e digite a URL do ngrok
    pause
    exit /b 1
)

echo.
echo Testando URL: %NGROK_URL%
echo.

echo ==========================================
echo [1/6] Testando conectividade basica...
echo ==========================================

echo.
echo Testando Google...
ping -n 2 google.com > nul 2>&1
if errorlevel 1 (
    echo ❌ ERRO: Sem conectividade com internet
    echo.
    echo PROBLEMA: Computador nao tem acesso a internet
    echo SOLUCAO: Verificar cabo de rede, WiFi ou configuracoes
    echo.
    goto :show_solutions
) else (
    echo ✓ Conectividade com internet OK
)

echo.
echo ==========================================
echo [2/6] Testando DNS...
echo ==========================================

echo.
echo Testando resolucao DNS do ngrok...

REM Extrair dominio da URL
for /f "tokens=3 delims=:/" %%a in ("%NGROK_URL%") do set NGROK_DOMAIN=%%a
if "%NGROK_DOMAIN%"=="" (
    REM Fallback se a extração falhar
    for /f "tokens=2 delims=/" %%a in ("%NGROK_URL%") do set NGROK_DOMAIN=%%a
)

echo Dominio extraido: %NGROK_DOMAIN%
echo.

nslookup %NGROK_DOMAIN% > nul 2>&1
if errorlevel 1 (
    echo ❌ ERRO: DNS nao consegue resolver %NGROK_DOMAIN%
    echo.
    echo PROBLEMA: Servidor DNS nao conhece o dominio ngrok
    echo SOLUCAO: Mudar DNS para servidores publicos
    echo.
    echo Comandos para Windows:
    echo netsh interface ip set dns "Wi-Fi" static 8.8.8.8
    echo netsh interface ip add dns "Wi-Fi" 8.8.4.4 index=2
    echo.
    echo (Substitua "Wi-Fi" pelo nome da sua conexao)
    echo.
    goto :show_solutions
) else (
    echo ✓ DNS OK - Dominio resolve corretamente
)

echo.
echo ==========================================
echo [3/6] Testando conectividade HTTPS...
echo ==========================================

echo.
echo Testando acesso HTTPS ao ngrok...
echo Aguarde...

REM Usar PowerShell para teste HTTP mais confiável
powershell -Command "try { $response = Invoke-WebRequest -Uri '%NGROK_URL%' -Method Head -TimeoutSec 10; Write-Host '✓ HTTP OK - Codigo:' $response.StatusCode } catch { Write-Host '❌ ERRO HTTP:' $_.Exception.Message }" 2>nul
if errorlevel 1 (
    echo.
    echo ❌ ERRO: Nao consegue conectar via HTTPS
    echo.
    echo PROBLEMA: Conexao bloqueada ou filtrada
    echo POSSIVEIS CAUSAS:
    echo - Firewall bloqueando conexoes HTTPS para ngrok
    echo - Antivirus com protecao web ativa
    echo - Proxy corporativo bloqueando tunnels
    echo - Controle parental no roteador
    echo.
) else (
    echo.
    echo ✓ HTTPS OK - Conectividade funcionando!
    echo.
    echo DIAGNOSTICO: Conexao esta funcionando
    echo Se ainda nao consegue acessar pelo navegador:
    echo 1. Limpe o cache do navegador
    echo 2. Tente modo incognito
    echo 3. Tente outro navegador
    echo.
    goto :browser_test
)

echo.
echo ==========================================
echo [4/6] Verificando Firewall/Antivirus...
echo ==========================================

echo.
echo Verificando Firewall do Windows...
for /f "tokens=3" %%a in ('netsh advfirewall show currentprofile ^| findstr "State"') do (
    if "%%a"=="ON" (
        echo ⚠️  Firewall do Windows: ATIVO
        echo   Pode estar bloqueando conexao
    ) else (
        echo ✓ Firewall do Windows: DESATIVADO
    )
)

echo.
echo Verificando processos de antivirus comuns...
tasklist /fi "imagename eq avast*" 2>nul | findstr /i avast >nul && echo ⚠️  Avast detectado
tasklist /fi "imagename eq mcafee*" 2>nul | findstr /i mcafee >nul && echo ⚠️  McAfee detectado  
tasklist /fi "imagename eq kaspersky*" 2>nul | findstr /i kaspersky >nul && echo ⚠️  Kaspersky detectado
tasklist /fi "imagename eq avg*" 2>nul | findstr /i avg >nul && echo ⚠️  AVG detectado

echo.
echo ANTIVIRUS DETECTADOS podem ter protecao web que bloqueia ngrok
echo SOLUCAO: Desabilitar protecao web temporariamente

echo.
echo ==========================================
echo [5/6] Testando navegadores...
echo ==========================================

echo.
echo Testando abertura em diferentes navegadores...

REM Testar se consegue abrir a URL
echo Tentando abrir %NGROK_URL%...

where chrome >nul 2>&1
if %errorlevel% == 0 (
    echo ✓ Chrome encontrado - Abrindo em nova janela...
    start chrome --new-window "%NGROK_URL%"
    timeout /t 2 /nobreak > nul
) else (
    echo ❌ Chrome nao encontrado
)

where firefox >nul 2>&1
if %errorlevel% == 0 (
    echo ✓ Firefox encontrado - Abrindo em nova janela...
    start firefox -new-window "%NGROK_URL%"
    timeout /t 2 /nobreak > nul
) else (
    echo ❌ Firefox nao encontrado
)

echo ✓ Abrindo no navegador padrao...
start "" "%NGROK_URL%"

:browser_test
echo.
echo ==========================================
echo [6/6] Teste manual requerido...
echo ==========================================

echo.
echo TESTE IMPORTANTE: Os navegadores foram abertos
echo.
echo Por favor, verifique:
echo 1. Algum navegador conseguiu carregar a pagina?
echo 2. Apareceu alguma mensagem de erro especifica?
echo 3. A pagina ficou "carregando" infinitamente?
echo.

set /p browser_result="Os navegadores conseguiram acessar? (s/n): "

if /i "%browser_result%"=="s" (
    echo.
    echo ✅ DIAGNOSTICO: Problema resolvido!
    echo A URL do ngrok esta funcionando corretamente
    echo.
    goto :success
) else (
    echo.
    echo ❌ DIAGNOSTICO: Problema confirmado
    echo Vamos identificar a causa...
    echo.
)

:show_solutions
echo.
echo ==========================================
echo           SOLUCOES RECOMENDADAS
echo ==========================================
echo.

echo 🔥 PROBLEMA MAIS COMUM: Firewall/Antivirus
echo SOLUCAO RAPIDA:
echo 1. Desabilitar antivirus temporariamente (5 min)
echo 2. Usar modo incognito do navegador
echo 3. Tentar outro navegador
echo.

echo 🏢 PROBLEMA CORPORATIVO: Proxy/Bloqueio de rede
echo SOLUCAO:
echo 1. Solicitar liberacao de *.ngrok.io no setor de TI
echo 2. Usar VPN pessoal (ProtonVPN, etc)
echo 3. Usar hotspot do celular
echo.

echo 🌐 PROBLEMA DNS:
echo SOLUCAO:
echo 1. Mudar DNS para 8.8.8.8 e 8.8.4.4 (Google)
echo 2. Ou usar 1.1.1.1 e 1.0.0.1 (Cloudflare)
echo 3. Executar: ipconfig /flushdns
echo.

echo 🔄 ALTERNATIVAS AO NGROK:
echo 1. LocalTunnel: npm install -g localtunnel
echo    Depois: lt --port 5001
echo.
echo 2. Serveo: ssh -R 80:localhost:5001 serveo.net
echo.
echo 3. IP local (mesma rede): http://IP_DO_SERVIDOR:5001
echo    Execute no servidor: ipconfig
echo.

echo ⚡ TESTE IMEDIATO:
echo 1. Use hotspot do celular
echo 2. Conecte o computador no hotspot
echo 3. Teste a URL novamente
echo Se funcionar = problema da rede atual
echo.

:success
echo.
echo ==========================================
echo Para executar alternativas automaticas:
echo start_universal_server.bat
echo ==========================================
echo.

echo ARQUIVOS DE AJUDA CRIADOS:
echo - TROUBLESHOOT_NGROK.md (guia completo)
echo - ALTERNATIVAS_NGROK.md (outras opcoes)
echo - start_universal_server.bat (multiplas opcoes)
echo.

echo ==========================================
echo DIAGNOSTICO CONCLUIDO!
echo Mantenha esta janela aberta para consulta
echo ==========================================
echo.
pause
