from app import create_app, db
from app.models import User, Artist, EventType
from app.alert_system import native_alert_system

app = create_app()

def init_db():
    """Inicializa o banco de dados e cria dados padrão"""
    with app.app_context():
        db.create_all()
        
        # Criar tipos de eventos padrão
        if EventType.query.count() == 0:
            event_types = [
                EventType(name="Show", description="Apresentação musical", color="#FF6B6B"),
                EventType(name="Entrevista", description="Entrevista para mídia", color="#4ECDC4"),
                EventType(name="Sessão de Fotos", description="Sessão fotográfica", color="#45B7D1"),
                EventType(name="Gravação", description="Gravação de música/vídeo", color="#96CEB4"),
                EventType(name="Reunião", description="Reunião de planejamento", color="#FFEAA7"),
                EventType(name="Live/Stream", description="Transmissão ao vivo", color="#DDA0DD"),
                EventType(name="Radio/TV", description="Participação em rádio ou TV", color="#FFB347"),
                EventType(name="Evento Promocional", description="Evento de divulgação", color="#87CEEB"),
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
        'native_alert_system': native_alert_system
    }

if __name__ == '__main__':
    init_db()
    # Iniciar sistema de alertas
    start_alert_system()
    app.run(debug=True, host='0.0.0.0', port=5001)
