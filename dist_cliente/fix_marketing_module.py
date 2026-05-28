"""
Script para corrigir problemas no módulo de marketing.
Este script verifica e corrige problemas comuns com o módulo de marketing,
como tabelas faltantes ou incompatíveis.

Uso: python fix_marketing_module.py
"""

import os
import sys
from datetime import datetime, timedelta

# Adicionar o diretório raiz ao sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db
from app.models import Artist, SocialPost, User, MediaFile, SocialMetrics, PressKit

app = create_app()

def check_database():
    """Verifica se as tabelas do módulo de marketing existem"""
    with app.app_context():
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        print("=== VERIFICANDO TABELAS DO MÓDULO DE MARKETING ===")
        
        missing_tables = []
        marketing_tables = ['social_post', 'media_file', 'social_metrics', 'press_kit']
        
        for table in marketing_tables:
            if table in tables:
                print(f"✓ Tabela {table} existe")
            else:
                print(f"✗ Tabela {table} NÃO existe")
                missing_tables.append(table)
        
        if missing_tables:
            print(f"\n⚠️ {len(missing_tables)} tabelas estão faltando. Criando tabelas...")
            
            # Criar tabelas faltantes
            db.create_all()
            
            # Verificar novamente
            new_tables = inspector.get_table_names()
            for table in missing_tables:
                if table in new_tables:
                    print(f"✓ Tabela {table} criada com sucesso")
                else:
                    print(f"✗ FALHA ao criar tabela {table}")
        else:
            print("\n✓ Todas as tabelas necessárias existem")
            
        return missing_tables

def check_tables_structure():
    """Verifica a estrutura das tabelas para garantir que estão corretas"""
    with app.app_context():
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        
        print("\n=== VERIFICANDO ESTRUTURA DAS TABELAS ===")
        
        # Verificar colunas da tabela SocialPost
        if 'social_post' in inspector.get_table_names():
            columns = {c['name']: c for c in inspector.get_columns('social_post')}
            required_columns = [
                'id', 'title', 'content', 'platform', 'scheduled_datetime',
                'artist_id', 'created_by', 'status'
            ]
            
            missing_columns = []
            for col in required_columns:
                if col not in columns:
                    missing_columns.append(col)
                    
            if missing_columns:
                print(f"⚠️ Tabela social_post está faltando colunas: {', '.join(missing_columns)}")
                return False
            else:
                print("✓ Estrutura da tabela social_post parece correta")
                return True
        else:
            print("⚠️ Tabela social_post não existe, não é possível verificar estrutura")
            return False

def create_test_data():
    """Cria dados de teste para garantir que tudo está funcionando"""
    with app.app_context():
        # Verificar se há artistas
        if Artist.query.count() == 0:
            print("\n⚠️ Não há artistas cadastrados. Criando artista de teste...")
            artist = Artist(
                name="Artista Teste",
                stage_name="Artista Teste",
                email="teste@example.com",
                phone="123456789",
                genre="Rock",
                color="#FF5733",
                is_active=True
            )
            db.session.add(artist)
            db.session.commit()
            print(f"✓ Artista de teste criado com ID {artist.id}")
        
        # Verificar se há usuários
        if User.query.count() == 0:
            print("\n⚠️ Não há usuários cadastrados! Isso é um problema sério.")
            return False
        
        # Tentar criar um post de teste
        try:
            artist = Artist.query.first()
            user = User.query.first()
            
            # Verificar se já existe um post de teste
            test_post = SocialPost.query.filter_by(title="Post de Teste (Automático)").first()
            if test_post:
                print(f"✓ Post de teste já existe (ID: {test_post.id})")
            else:
                post = SocialPost(
                    title="Post de Teste (Automático)",
                    content="Este é um post de teste criado pelo sistema de diagnóstico.",
                    platform="instagram",
                    scheduled_datetime=datetime.utcnow() + timedelta(days=1),
                    artist_id=artist.id,
                    hashtags="#teste #sistema",
                    location="Sistema",
                    status="draft",
                    created_by=user.id
                )
                
                db.session.add(post)
                db.session.commit()
                print(f"✓ Post de teste criado com sucesso (ID: {post.id})")
            
            return True
            
        except Exception as e:
            print(f"❌ ERRO ao criar dados de teste: {str(e)}")
            db.session.rollback()
            import traceback
            traceback.print_exc()
            return False

def main():
    print("=== FERRAMENTA DE CORREÇÃO DO MÓDULO DE MARKETING ===\n")
    
    # Verificar tabelas
    missing_tables = check_database()
    
    # Se tabelas existem, verificar estrutura
    if not missing_tables:
        structure_ok = check_tables_structure()
    else:
        structure_ok = False
    
    # Se estrutura está ok, tentar criar dados de teste
    if structure_ok:
        data_ok = create_test_data()
    else:
        data_ok = False
    
    # Resumo
    print("\n=== RESUMO ===")
    if not missing_tables and structure_ok and data_ok:
        print("✓ Módulo de marketing parece estar funcionando corretamente!")
        print("✓ Você deve conseguir criar posts sem problemas agora.")
    else:
        if missing_tables:
            print(f"⚠️ Tabelas faltantes foram criadas: {', '.join(missing_tables)}")
        
        if not structure_ok:
            print("⚠️ Estrutura das tabelas pode ter problemas.")
            print("   Considere fazer backup do banco de dados e recriar as tabelas do módulo de marketing.")
            
        if not data_ok:
            print("⚠️ Não foi possível criar dados de teste.")
            print("   Verifique os erros acima para mais detalhes.")
    
    print("\nProcesso concluído.")

if __name__ == "__main__":
    main()
