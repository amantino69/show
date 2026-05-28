from app import create_app
from app.models import User, Artist, db
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # Buscar o artista Guinho
    guinho = Artist.query.filter_by(stage_name='Guinho').first()
    
    if guinho:
        # Verificar se já existe usuário para este artista
        existing_user = User.query.filter_by(artist_id=guinho.id).first()
        
        if not existing_user:
            # Criar usuário para o Guinho
            user = User(
                username='guinho',
                email='guinho@show.com',
                password_hash=generate_password_hash('guinho123'),
                is_manager=False,
                artist_id=guinho.id
            )
            
            db.session.add(user)
            db.session.commit()
            
            print("✅ Usuário criado para Guinho!")
            print(f"👤 Username: guinho")
            print(f"🔑 Senha: guinho123")
            print(f"📧 Email: guinho@show.com")
        else:
            print("ℹ️ Usuário já existe para Guinho:")
            print(f"👤 Username: {existing_user.username}")
            print(f"📧 Email: {existing_user.email}")
    else:
        print("❌ Artista Guinho não encontrado!")