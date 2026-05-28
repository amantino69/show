@echo off
chcp 65001 >nul
cls
echo.
echo ███████╗██╗███████╗████████╗███████╗███╗   ███╗ █████╗ 
echo ██╔════╝██║██╔════╝╚══██╔══╝██╔════╝████╗ ████║██╔══██╗
echo ███████╗██║███████╗   ██║   █████╗  ██╔████╔██║███████║
echo ╚════██║██║╚════██║   ██║   ██╔══╝  ██║╚██╔╝██║██╔══██║
echo ███████║██║███████║   ██║   ███████╗██║ ╚═╝ ██║██║  ██║
echo ╚══════╝╚═╝╚══════╝   ╚═╝   ╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝
echo.
echo           SISTEMA DE GERENCIAMENTO DE ARTISTAS
echo                  PREPARAÇÃO PARA CLIENTE
echo.
echo ============================================================
echo.

echo 📋 Este script irá preparar o sistema completo para entrega.
echo.
echo ⚠️ ANTES DE CONTINUAR, certifique-se de que:
echo   • Todos os testes foram realizados
echo   • O sistema está funcionando corretamente
echo   • Você tem permissões para criar arquivos
echo.
set /p confirm="Deseja continuar? (S/N): "
if /i not "%confirm%"=="S" (
    echo Operação cancelada.
    pause
    exit /b
)

echo.
echo 🚀 Iniciando preparação...
echo.

:: Executar script de preparação
call PREPARAR_PARA_CLIENTE.bat

echo.
echo ============================================================
echo                    ✅ PREPARAÇÃO CONCLUÍDA!
echo ============================================================
echo.
echo 📦 O sistema foi empacotado e está pronto para entrega!
echo.
echo 📁 LOCALIZAÇÃO: pasta "dist_cliente"
echo.
echo 🎯 PRÓXIMOS PASSOS:
echo   1. Entre na pasta "dist_cliente"
echo   2. Execute "COMPACTAR.bat"
echo   3. Envie o arquivo ZIP para o cliente
echo.
echo 📧 TEMPLATE DE EMAIL: Consulte CHECKLIST_ENTREGA.md
echo.
echo 🔧 SUPORTE: Mantenha-se disponível durante o teste
echo.

set /p open="Deseja abrir a pasta de distribuição? (S/N): "
if /i "%open%"=="S" (
    explorer dist_cliente
)

echo.
echo Obrigado por usar o Sistema de Gerenciamento de Artistas!
echo.
pause
