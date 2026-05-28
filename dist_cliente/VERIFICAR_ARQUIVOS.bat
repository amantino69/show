@echo off
chcp 65001 >nul
echo Verificando integridade dos arquivos...
echo.
if not exist "app.py" echo ❌ app.py faltando
if not exist "config.py" echo ❌ config.py faltando
if not exist "requirements.txt" echo ❌ requirements.txt faltando
if not exist "INSTALAR_SISTEMA.bat" echo ❌ INSTALAR_SISTEMA.bat faltando
if not exist "INICIAR_SISTEMA.bat" echo ❌ INICIAR_SISTEMA.bat faltando
if not exist ".env" echo ❌ .env faltando
if not exist "app\__init__.py" echo ❌ pasta app incompleta
echo.
echo ✓ Verificação concluída
pause
