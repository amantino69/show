"""
Script para adicionar as novas tabelas de Marketing ao banco de dados
Este script adiciona as tabelas sem afetar os dados existentes
"""

import sqlite3
import os
from datetime import datetime

def create_marketing_tables():
    """Criar tabelas do módulo de marketing"""
    db_path = "instance/artistas_sistema.db"
    
    if not os.path.exists(db_path):
        print("❌ Banco de dados não encontrado!")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("🔧 Adicionando tabelas do módulo de Marketing...")
        
        # Tabela MediaFile
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS media_file (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename VARCHAR(255) NOT NULL,
            original_filename VARCHAR(255) NOT NULL,
            file_path VARCHAR(500) NOT NULL,
            file_type VARCHAR(20) NOT NULL,
            mime_type VARCHAR(100) NOT NULL,
            file_size INTEGER NOT NULL,
            title VARCHAR(200),
            description TEXT,
            tags VARCHAR(500),
            artist_id INTEGER,
            event_id INTEGER,
            width INTEGER,
            height INTEGER,
            duration INTEGER,
            is_public BOOLEAN DEFAULT 1,
            is_featured BOOLEAN DEFAULT 0,
            uploaded_by INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (artist_id) REFERENCES artist (id),
            FOREIGN KEY (event_id) REFERENCES event (id),
            FOREIGN KEY (uploaded_by) REFERENCES user (id)
        )
        """)
        print("✓ Tabela media_file criada")
        
        # Tabela SocialPost
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS social_post (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title VARCHAR(200) NOT NULL,
            content TEXT NOT NULL,
            platform VARCHAR(50) NOT NULL,
            scheduled_datetime DATETIME NOT NULL,
            status VARCHAR(20) DEFAULT 'draft',
            artist_id INTEGER NOT NULL,
            event_id INTEGER,
            media_file_id INTEGER,
            likes INTEGER DEFAULT 0,
            comments INTEGER DEFAULT 0,
            shares INTEGER DEFAULT 0,
            views INTEGER DEFAULT 0,
            reach INTEGER DEFAULT 0,
            published_at DATETIME,
            external_post_id VARCHAR(255),
            external_url VARCHAR(500),
            hashtags VARCHAR(1000),
            location VARCHAR(200),
            created_by INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (artist_id) REFERENCES artist (id),
            FOREIGN KEY (event_id) REFERENCES event (id),
            FOREIGN KEY (media_file_id) REFERENCES media_file (id),
            FOREIGN KEY (created_by) REFERENCES user (id)
        )
        """)
        print("✓ Tabela social_post criada")
        
        # Tabela PressKit
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS press_kit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            artist_id INTEGER NOT NULL,
            bio_short TEXT,
            bio_long TEXT,
            achievements TEXT,
            profile_photo_id INTEGER,
            banner_photo_id INTEGER,
            website VARCHAR(300),
            instagram VARCHAR(300),
            facebook VARCHAR(300),
            youtube VARCHAR(300),
            spotify VARCHAR(300),
            deezer VARCHAR(300),
            apple_music VARCHAR(300),
            technical_rider TEXT,
            stage_plot TEXT,
            booking_contact VARCHAR(200),
            booking_email VARCHAR(200),
            booking_phone VARCHAR(50),
            is_public BOOLEAN DEFAULT 1,
            template_style VARCHAR(50) DEFAULT 'default',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (artist_id) REFERENCES artist (id),
            FOREIGN KEY (profile_photo_id) REFERENCES media_file (id),
            FOREIGN KEY (banner_photo_id) REFERENCES media_file (id)
        )
        """)
        print("✓ Tabela press_kit criada")
        
        # Tabela SocialMetrics
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS social_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            artist_id INTEGER NOT NULL,
            platform VARCHAR(50) NOT NULL,
            followers_count INTEGER DEFAULT 0,
            following_count INTEGER DEFAULT 0,
            posts_count INTEGER DEFAULT 0,
            period_start DATE NOT NULL,
            period_end DATE NOT NULL,
            total_likes INTEGER DEFAULT 0,
            total_comments INTEGER DEFAULT 0,
            total_shares INTEGER DEFAULT 0,
            total_views INTEGER DEFAULT 0,
            total_reach INTEGER DEFAULT 0,
            followers_growth INTEGER DEFAULT 0,
            engagement_rate REAL DEFAULT 0.0,
            collected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (artist_id) REFERENCES artist (id)
        )
        """)
        print("✓ Tabela social_metrics criada")
        
        # Criar diretório para uploads se não existir
        upload_dir = os.path.join("app", "static", "uploads", "media")
        os.makedirs(upload_dir, exist_ok=True)
        print("✓ Diretório de uploads criado")
        
        conn.commit()
        print("✅ Todas as tabelas de marketing foram criadas com sucesso!")
        
        # Verificar estrutura
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        
        print("\n📋 Tabelas no banco de dados:")
        for table in tables:
            print(f"   - {table[0]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

def main():
    """Função principal"""
    print("🎯 ADICIONANDO MÓDULO DE MARKETING")
    print("=" * 50)
    
    if create_marketing_tables():
        print("\n🎉 MÓDULO DE MARKETING INSTALADO COM SUCESSO!")
        print("\nFuncionalidades adicionadas:")
        print("  📸 Biblioteca de Mídia - Organize fotos, vídeos e documentos")
        print("  📱 Calendário de Posts - Agende posts para redes sociais")
        print("  📄 Press Kit Digital - Crie press kits profissionais")
        print("  📊 Métricas Sociais - Acompanhe engajamento")
        print("\nAcesse: Menu > Marketing")
    else:
        print("\n💥 ERRO na instalação do módulo de marketing")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n💥 ERRO FATAL: {e}")
    
    input("\nPressione Enter para continuar...")
