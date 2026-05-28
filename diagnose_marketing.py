"""
Script para testar a criação de posts na tabela SocialPost.
Execute este script para verificar se há problemas com a tabela ou os dados.

Uso: python diagnose_marketing.py
"""

import os
import sys
from datetime import datetime, timedelta
from pprint import pprint

# Adicionar o diretório raiz ao sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db
from app.models import Artist, SocialPost, User, MediaFile

app = create_app()

def test_create_post():
    """Testa a criação de um post"""
    with app.app_context():
        # Verificar se há artistas
        artists = Artist.query.filter_by(is_active=True).all()
        if not artists:
            print("⚠️ Não há artistas ativos no sistema. Criando um artista de teste...")
            artist = Artist(
                name="Artista Teste",
                stage_name="Artista Teste",
                email="teste@example.com",
                color="#FF5733",
                is_active=True
            )
            db.session.add(artist)
            db.session.commit()
            artists = [artist]
            print(f"✓ Artista de teste criado com ID {artist.id}")
        
        # Verificar se há usuários
        users = User.query.all()
        if not users:
            print("⚠️ Não há usuários no sistema! Isso é um problema sério.")
            return

        # Criar um post de teste
        artist = artists[0]
        user = users[0]
        
        print(f"\n--- Criando post de teste para artista: {artist.stage_name} (ID: {artist.id}) ---")
        
        try:
            post = SocialPost(
                title="Post de Teste",
                content="Este é um post de teste criado pelo diagnóstico.",
                platform="instagram",
                scheduled_datetime=datetime.utcnow() + timedelta(days=1),
                artist_id=artist.id,
                hashtags="#teste #diagnostico",
                location="Internet",
                status="draft",
                created_by=user.id
            )
            
            db.session.add(post)
            db.session.commit()
            
            print(f"✓ Post criado com sucesso! ID: {post.id}")
            print("Detalhes do post:")
            print(f"  - Título: {post.title}")
            print(f"  - Plataforma: {post.platform}")
            print(f"  - Agendado para: {post.scheduled_datetime}")
            print(f"  - Status: {post.status}")
            
            # Tentar recuperar o post
            retrieved_post = SocialPost.query.get(post.id)
            if retrieved_post:
                print("✓ Post recuperado com sucesso do banco de dados!")
            else:
                print("⚠️ Não foi possível recuperar o post do banco de dados!")
            
            # Limpar
            db.session.delete(post)
            db.session.commit()
            print("✓ Post de teste removido do banco de dados.")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ ERRO ao criar post: {str(e)}")
            print("\nDetalhes do erro:")
            import traceback
            traceback.print_exc()
            
            # Diagnóstico detalhado
            diagnose_database()

def diagnose_database():
    """Realizar diagnóstico mais detalhado do banco de dados"""
    with app.app_context():
        print("\n--- DIAGNÓSTICO DO BANCO DE DADOS ---")
        
        # Verificar tabelas
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"\nTabelas no banco de dados: {tables}")
        
        # Verificar esquema da tabela SocialPost
        if 'social_post' in tables:
            columns = inspector.get_columns('social_post')
            print("\nColunas da tabela social_post:")
            for column in columns:
                print(f"  - {column['name']}: {column['type']} (nullable: {column['nullable']})")
        else:
            print("\n❌ Tabela social_post não existe no banco de dados!")
        
        # Verificar outros dados importantes
        print("\nContagem de registros:")
        print(f"  - Artistas: {Artist.query.count()}")
        print(f"  - Usuários: {User.query.count()}")
        print(f"  - Arquivos de mídia: {MediaFile.query.count()}")
        print(f"  - Posts: {SocialPost.query.count()}")
        
        # Verificar artistas
        artists = Artist.query.all()
        print("\nArtistas disponíveis:")
        for artist in artists:
            print(f"  - ID: {artist.id}, Nome: {artist.stage_name}, Ativo: {artist.is_active}")
        
        # Verificar usuários
        users = User.query.all()
        print("\nUsuários disponíveis:")
        for user in users:
            print(f"  - ID: {user.id}, Username: {user.username}, Email: {user.email}")

if __name__ == "__main__":
    print("=== DIAGNÓSTICO DO MÓDULO DE MARKETING ===\n")
    test_create_post()
    print("\nDiagnóstico concluído.")
