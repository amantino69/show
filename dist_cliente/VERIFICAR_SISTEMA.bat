@echo off
chcp 65001 >nul
echo.
echo ============================================================
echo              VERIFICAÇÃO DO SISTEMA
echo ============================================================
echo.

:: Verificar versão do Windows
echo Verificando sistema operacional...
ver
echo.

:: Verificar espaço em disco
echo Verificando espaço em disco...
dir C:\ | findstr /C:"bytes free"
echo.

:: Verificar se Python está instalado
echo Verificando Python...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    python --version
    echo ✓ Python já está instalado
) else (
    echo ⚠️ Python não está instalado
)
echo.

:: Verificar se pip está disponível
pip --version >nul 2>&1
if %errorlevel% equ 0 (
    pip --version
    echo ✓ pip está disponível
) else (
    echo ⚠️ pip não está disponível
)
echo.

:: Verificar memória RAM
echo Verificando memória RAM...
wmic computersystem get TotalPhysicalMemory /format:value | findstr "="
echo.

:: Verificar arquivos do sistema
echo Verificando arquivos do sistema...
if exist "app.py" (
    echo ✓ app.py encontrado
) else (
    echo ❌ app.py NÃO encontrado
)

if exist "requirements.txt" (
    echo ✓ requirements.txt encontrado
) else (
    echo ❌ requirements.txt NÃO encontrado
)

if exist "INSTALAR_SISTEMA.bat" (
    echo ✓ INSTALAR_SISTEMA.bat encontrado
) else (
    echo ❌ INSTALAR_SISTEMA.bat NÃO encontrado
)

echo.
echo Verificação concluída!
echo.
pause
