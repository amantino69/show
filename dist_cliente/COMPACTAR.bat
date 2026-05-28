@echo off
echo Compactando sistema para distribuição...
powershell -Command "Compress-Archive -Path '.\*' -DestinationPath '..\SistemaGerenciamentoArtistas.zip' -Force"
echo ✓ Arquivo SistemaGerenciamentoArtistas.zip criado!
echo.
echo O arquivo está pronto para envio ao cliente.
pause
