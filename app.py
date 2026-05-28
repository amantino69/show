from app import create_app, db
from app.models import User, Artist, EventType, ArtistType
from app.alert_system import native_alert_system

app = create_app()

def init_db():
    """Inicializa o banco de dados e cria dados padrão"""
    with app.app_context():
        db.create_all()
        
        # Criar tipos de artistas padrão
        if ArtistType.query.count() == 0:
            artist_types = [
                ArtistType(name="Cantor/Cantora", description="Artistas musicais e vocais", icon="fas fa-microphone", color="#FF6B6B"),
                ArtistType(name="Influenciador Digital", description="Criadores de conteúdo digital", icon="fas fa-wifi", color="#4ECDC4"),
                ArtistType(name="Modelo", description="Modelos profissionais", icon="fas fa-camera", color="#45B7D1"),
                ArtistType(name="Ator/Atriz", description="Artistas de teatro, cinema e TV", icon="fas fa-theater-masks", color="#96CEB4"),
                ArtistType(name="Dançarino", description="Artistas da dança", icon="fas fa-running", color="#FFEAA7"),
                ArtistType(name="DJ/Produtor", description="DJs e produtores musicais", icon="fas fa-headphones", color="#DDA0DD"),
                ArtistType(name="Comediante", description="Artistas do humor", icon="fas fa-laugh", color="#FFB347"),
                ArtistType(name="Artista Visual", description="Pintores, desenhistas, grafiteiros", icon="fas fa-palette", color="#87CEEB"),
                ArtistType(name="Outros", description="Outros tipos de artistas", icon="fas fa-star", color="#F0A3FF"),
            ]
            
            for artist_type in artist_types:
                db.session.add(artist_type)
            
            db.session.commit()
            print("Tipos de artistas criados!")
        
        # Criar tipos de eventos padrão
        if EventType.query.count() == 0:
            event_types = [
                EventType(name="Show/Performance", description="Apresentação artística", color="#FF6B6B"),
                EventType(name="Entrevista", description="Entrevista para mídia", color="#4ECDC4"),
                EventType(name="Sessão de Fotos", description="Sessão fotográfica", color="#45B7D1"),
                EventType(name="Gravação", description="Gravação de conteúdo", color="#96CEB4"),
                EventType(name="Reunião", description="Reunião de planejamento", color="#FFEAA7"),
                EventType(name="Live/Stream", description="Transmissão ao vivo", color="#DDA0DD"),
                EventType(name="Radio/TV", description="Participação em rádio ou TV", color="#FFB347"),
                EventType(name="Evento Promocional", description="Evento de divulgação", color="#87CEEB"),
                EventType(name="Workshop/Curso", description="Atividade educacional", color="#98FB98"),
                EventType(name="Audição/Casting", description="Processo seletivo", color="#F0A3FF"),
            ]
            
            for event_type in event_types:
                db.session.add(event_type)
            
            db.session.commit()
            print("Tipos de eventos criados!")
        
        # Criar usuário empresário padrão
        if not User.query.filter_by(is_manager=True).first():
            manager = User(
                username="empresario",
                email="claudio.vieiraamantino@gmail.com",  # Usar o email do .env
                is_manager=True
            )
            manager.set_password("123456")  # Senha padrão
            db.session.add(manager)
            db.session.commit()
            print("✓ Usuário empresário criado!")
            print("  Usuário: empresario")
            print("  Senha: 123456")
            print("  IMPORTANTE: Altere a senha após o primeiro login!")
        else:
            print("Usuário empresário já existe.")

def start_alert_system():
    """Inicializa o sistema de alertas automaticamente"""
    try:
        native_alert_system.start_alert_daemon()
        print("✓ Sistema de alertas nativos iniciado!")
    except Exception as e:
        print(f"⚠️ Erro ao iniciar sistema de alertas: {str(e)}")

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db, 
        'User': User, 
        'Artist': Artist, 
        'EventType': EventType,
        'ArtistType': ArtistType,
        'native_alert_system': native_alert_system
    }

if __name__ == '__main__':
    init_db()
    # Iniciar sistema de alertas
    start_alert_system()
    app.run(debug=True, host='0.0.0.0', port=5005)
