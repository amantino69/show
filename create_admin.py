"""
Script para criar usuário administrador inicial
Execute este script para criar a primeira conta de empresário
"""
from app import create_app, db
from app.models import User, Artist
from config import Config

def create_initial_users():
    app = create_app()
    
    with app.app_context():
        # Criar tabelas se não existirem
        db.create_all()
        
        print("=== CRIAÇÃO DE USUÁRIO INICIAL ===")
        print("Este script criará o primeiro usuário empresário do sistema.")
        print()
        
        # Verificar se já existe um usuário empresário
        existing_manager = User.query.filter_by(is_manager=True).first()
        if existing_manager:
            print(f"Já existe um usuário empresário: {existing_manager.username}")
            print("Deseja criar outro? (s/n): ", end="")
            choice = input().lower()
            if choice != 's':
                return
        
        # Coletar dados do usuário
        print("Dados do empresário:")
        username = input("Nome de usuário: ")
        email = input("Email: ")
        password = input("Senha: ")
        
        # Verificar se usuário já existe
        if User.query.filter_by(username=username).first():
            print(f"ERRO: Usuário '{username}' já existe!")
            return
        
        if User.query.filter_by(email=email).first():
            print(f"ERRO: Email '{email}' já está cadastrado!")
            return
        
        # Criar usuário empresário
        user = User(
            username=username,
            email=email,
            is_manager=True
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        print(f"\n✅ Usuário empresário '{username}' criado com sucesso!")
        print(f"Email: {email}")
        print(f"Tipo: Empresário")
        print("\nVocê pode fazer login no sistema com essas credenciais.")
        print("\nPara criar artistas, acesse o sistema e vá em 'Artistas' > 'Novo Artista'")

def create_sample_artist():
    """Criar um artista de exemplo"""
    app = create_app()
    
    with app.app_context():
        print("\n=== CRIAR ARTISTA DE EXEMPLO ===")
        print("Deseja criar um artista de exemplo? (s/n): ", end="")
        choice = input().lower()
        
        if choice == 's':
            # Selecionar cor
            colors = Config.ARTIST_COLORS
            color_index = Artist.query.count() % len(colors)
            
            artist = Artist(
                name="João Silva",
                stage_name="João Cantor",
                email="joao.cantor@email.com",
                phone="(11) 99999-9999",
                genre="MPB",
                description="Cantor de MPB com 10 anos de carreira",
                color=colors[color_index]
            )
            
            db.session.add(artist)
            db.session.commit()
            
            print(f"✅ Artista '{artist.stage_name}' criado com sucesso!")
            print(f"Email: {artist.email}")
            print(f"Gênero: {artist.genre}")

if __name__ == "__main__":
    try:
        create_initial_users()
        create_sample_artist()
        print("\n🎉 Configuração inicial concluída!")
        print("\nPara iniciar o sistema, execute: python app.py")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        print("Verifique se todas as dependências estão instaladas.")
