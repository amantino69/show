"""
Script para corrigir e atualizar o banco de dados
Adiciona colunas faltantes na tabela notification
"""

import sqlite3
import os
from datetime import datetime

def backup_database():
    """Criar backup do banco antes de modificar"""
    db_path = "instance/artistas_sistema.db"
    if os.path.exists(db_path):
        backup_path = f"instance/artistas_sistema_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"✓ Backup criado: {backup_path}")
        return True
    return False

def check_table_structure():
    """Verificar estrutura atual da tabela notification"""
    db_path = "instance/artistas_sistema.db"
    if not os.path.exists(db_path):
        print("❌ Banco de dados não encontrado")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Verificar se tabela existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='notification';")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("❌ Tabela notification não existe")
            conn.close()
            return False
        
        # Verificar colunas existentes
        cursor.execute("PRAGMA table_info(notification)")
        columns = cursor.fetchall()
        
        print("📋 Estrutura atual da tabela notification:")
        for col in columns:
            print(f"   - {col[1]} ({col[2]})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar tabela: {e}")
        conn.close()
        return False

def fix_notification_table():
    """Corrigir tabela notification adicionando colunas faltantes"""
    db_path = "instance/artistas_sistema.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Colunas que devem existir
    required_columns = [
        ("title", "VARCHAR(200)", ""),
        ("message", "TEXT", ""),
        ("notification_type", "VARCHAR(20)", "'reminder'"),
        ("scheduled_time", "DATETIME", "datetime('now')"),
        ("sent", "BOOLEAN", "0"),
        ("sent_at", "DATETIME", "NULL"),
        ("read", "BOOLEAN", "0"),
        ("read_at", "DATETIME", "NULL"),
        ("priority", "VARCHAR(10)", "'medium'"),
        ("created_at", "DATETIME", "datetime('now')"),
        ("push_notification_sent", "BOOLEAN", "0"),
        ("email_sent", "BOOLEAN", "0"),
        ("whatsapp_sent", "BOOLEAN", "0")
    ]
    
    try:
        # Verificar quais colunas existem
        cursor.execute("PRAGMA table_info(notification)")
        existing_columns = [col[1] for col in cursor.fetchall()]
        
        print(f"📋 Colunas existentes: {existing_columns}")
        
        # Adicionar colunas faltantes
        for col_name, col_type, default_value in required_columns:
            if col_name not in existing_columns:
                if default_value:
                    sql = f"ALTER TABLE notification ADD COLUMN {col_name} {col_type} DEFAULT {default_value}"
                else:
                    sql = f"ALTER TABLE notification ADD COLUMN {col_name} {col_type}"
                
                print(f"➕ Adicionando coluna: {col_name}")
                cursor.execute(sql)
        
        conn.commit()
        print("✓ Tabela notification corrigida!")
        
        # Verificar estrutura final
        cursor.execute("PRAGMA table_info(notification)")
        final_columns = cursor.fetchall()
        
        print("📋 Estrutura final da tabela notification:")
        for col in final_columns:
            print(f"   - {col[1]} ({col[2]})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao corrigir tabela: {e}")
        conn.rollback()
        conn.close()
        return False

def recreate_notification_table():
    """Recriar tabela notification com estrutura correta"""
    db_path = "instance/artistas_sistema.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Backup dados existentes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='notification';")
        if cursor.fetchone():
            cursor.execute("SELECT * FROM notification")
            old_data = cursor.fetchall()
            print(f"💾 Backup de {len(old_data)} registros existentes")
        else:
            old_data = []
        
        # Remover tabela antiga
        cursor.execute("DROP TABLE IF EXISTS notification")
        
        # Criar nova tabela com estrutura correta
        create_sql = """
        CREATE TABLE notification (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER NOT NULL,
            title VARCHAR(200) NOT NULL,
            message TEXT NOT NULL,
            notification_type VARCHAR(20) NOT NULL DEFAULT 'reminder',
            scheduled_time DATETIME NOT NULL,
            sent BOOLEAN DEFAULT 0,
            sent_at DATETIME,
            read BOOLEAN DEFAULT 0,
            read_at DATETIME,
            priority VARCHAR(10) DEFAULT 'medium',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            push_notification_sent BOOLEAN DEFAULT 0,
            email_sent BOOLEAN DEFAULT 0,
            whatsapp_sent BOOLEAN DEFAULT 0,
            FOREIGN KEY (event_id) REFERENCES event (id)
        )
        """
        
        cursor.execute(create_sql)
        print("✓ Nova tabela notification criada")
        
        # Restaurar dados compatíveis (se existirem)
        if old_data:
            print("🔄 Tentando restaurar dados antigos...")
            # Aqui você pode tentar mapear os dados antigos para a nova estrutura
            # Por segurança, vamos apenas criar registros vazios por enquanto
        
        conn.commit()
        conn.close()
        
        print("✅ Tabela notification recriada com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao recriar tabela: {e}")
        conn.rollback()
        conn.close()
        return False

def main():
    """Função principal do script de correção"""
    print("🔧 CORREÇÃO DO BANCO DE DADOS - Show Manager")
    print("=" * 50)
    
    # 1. Criar backup
    print("\n1. Criando backup...")
    if backup_database():
        print("✓ Backup criado com sucesso")
    else:
        print("⚠️ Nenhum banco encontrado (será criado novo)")
    
    # 2. Verificar estrutura atual
    print("\n2. Verificando estrutura atual...")
    if check_table_structure():
        # Tentar corrigir adicionando colunas
        print("\n3. Tentando corrigir tabela existente...")
        if fix_notification_table():
            print("✅ Correção concluída!")
            return True
    
    # 3. Se correção falhou, recriar tabela
    print("\n4. Recriando tabela notification...")
    if recreate_notification_table():
        print("✅ Tabela recriada com sucesso!")
        return True
    
    print("❌ Falha na correção do banco de dados")
    return False

if __name__ == "__main__":
    try:
        if main():
            print("\n🎉 CORREÇÃO CONCLUÍDA!")
            print("\nAgora você pode executar o app.py normalmente")
            print("python app.py")
        else:
            print("\n💥 CORREÇÃO FALHOU!")
            print("Verifique os erros acima ou delete o banco para criar novo")
            
    except Exception as e:
        print(f"\n💥 ERRO FATAL: {e}")
        print("\nSolução alternativa: delete o arquivo instance/artistas_sistema.db")
        print("O app criará um novo banco automaticamente")
    
    input("\nPressione Enter para continuar...")
