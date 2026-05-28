@echo off
echo Show Manager - Sistema de Alertas Nativos
echo ==========================================
echo.

echo Instalando dependencias necessarias...
pip install plyer schedule reportlab openpyxl twilio requests

echo.
echo Iniciando aplicativo de alertas desktop...
echo Mantenha esta janela aberta para receber notificacoes!
echo.
echo Para parar, pressione Ctrl+C
echo.

python desktop_alerts.py

pause
