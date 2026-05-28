# Backup e Restore do Banco de Dados

Scripts para realizar backup e restore do banco SQLite do sistema de artistas.

## Como Usar

### Backup

1. Execute o script de backup:
   ```bash
   python backup_restore/backup_db.py
   ```
2. O arquivo de backup será salvo na pasta `backup_restore/backups` com data e hora.

### Restore

1. Liste os arquivos de backup na pasta `backup_restore/backups`.
2. Execute o script de restore informando o nome do arquivo:
   ```bash
   python backup_restore/restore_db.py artistas_sistema_backup_YYYYMMDD_HHMMSS.db
   ```
3. O banco será restaurado e sobrescreverá o atual.

## Recomendações
- Sempre faça backup antes de atualizar o sistema ou migrar versões.
- Guarde os arquivos de backup em local seguro.
- O restore sobrescreve o banco atual, use com cautela.
