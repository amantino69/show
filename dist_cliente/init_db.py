#!/usr/bin/env python3
"""
Script de inicialização do sistema de gerenciamento de artistas.
Execute este script para configurar o banco de dados e criar dados iniciais.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, Artist, EventType
from werkzeug.security import generate_password_hash

def init_database():
    """Inicializa o banco de dados"""
    app = create_app()
    
    with app.app_context():
        print("Criando banco de dados...")
        db.create_all()
        
        # Criar tipos de eventos padrão
        if EventType.query.count() == 0:
            print("Criando tipos de eventos padrão...")
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
            print("✓ Tipos de eventos criados!")
        
        # Criar usuário empresário padrão
        if not User.query.filter_by(is_manager=True).first():
            print("Criando usuário empresário padrão...")
            manager = User(
                username="empresario",
                email="empresario@exemplo.com",
                is_manager=True
            )
            manager.set_password("123456")  # Mude esta senha!
            db.session.add(manager)
            db.session.commit()
            print("✓ Usuário empresário criado!")
            print("  Usuário: empresario")
            print("  Senha: 123456")
            print("  IMPORTANTE: Altere a senha após o primeiro login!")
        
        print("\n✅ Banco de dados inicializado com sucesso!")
        print("\n🚀 Para iniciar o sistema, execute:")
        print("   python app.py")
        print("\n📝 Configuração necessária:")
        print("   1. Edite o arquivo .env com suas configurações do Gmail")
        print("   2. Configure as credenciais do Google Calendar API")
        print("   3. Altere a senha padrão do empresário")

if __name__ == '__main__':
    init_database()
