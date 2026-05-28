@echo off
chcp 65001 >nul
title Sistema de Gerenciamento de Artistas

echo.
echo ============================================================
echo      SISTEMA DE GERENCIAMENTO DE ARTISTAS - INICIANDO
echo ============================================================
echo.

:: Verificar se Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python não está instalado ou não está no PATH.
    echo Execute primeiro o arquivo: INSTALAR_SISTEMA.bat
    echo.
    pause
    exit /b 1
)

:: Verificar se as dependências estão instaladas
python -c "import flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Dependências não estão instaladas.
    echo Execute primeiro o arquivo: INSTALAR_SISTEMA.bat
    echo.
    pause
    exit /b 1
)

echo ✓ Verificações iniciais aprovadas
echo.

:: Verificar se o banco de dados existe
if not exist "instance\artistas_sistema.db" (
    echo Criando banco de dados...
    python init_db.py
    if %errorlevel% neq 0 (
        echo ❌ Erro ao criar banco de dados.
        pause
        exit /b 1
    )
)

echo Iniciando servidor...
echo.
echo ============================================================
echo                    SISTEMA INICIADO!
echo ============================================================
echo.
echo ✓ O sistema está rodando em: http://localhost:5001
echo.
echo Dados de acesso:
echo   Usuário: empresario
echo   Senha: 123456
echo.
echo ⚠️ MANTENHA ESTA JANELA ABERTA enquanto usar o sistema
echo ⚠️ Para parar o sistema, feche esta janela ou pressione Ctrl+C
echo.
echo Abrindo navegador automaticamente...
echo.

:: Aguardar 3 segundos e abrir navegador
timeout /t 3 /nobreak >nul
start http://localhost:5001

:: Iniciar aplicação Flask
python app.py

echo.
echo Sistema encerrado.
pause
