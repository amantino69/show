from app import create_app
from app.models import Event, Artist
from app.alert_system import native_alert_system

app = create_app()

with app.app_context():
    print("🔔 CONFIGURAÇÃO DE ALERTAS PARA O GUINHO")
    print("=" * 50)
    
    # Buscar o artista Guinho
    guinho = Artist.query.filter_by(stage_name='Guinho').first()
    
    if guinho:
        print(f"✅ Artista encontrado: {guinho.stage_name}")
        
        # Buscar eventos do Guinho
        events = Event.query.filter_by(artist_id=guinho.id).all()
        
        if events:
            print(f"📅 Eventos encontrados: {len(events)}")
            
            for event in events:
                print(f"\n🎭 Evento: {event.title}")
                print(f"📅 Data: {event.start_datetime}")
                print(f"📍 Local: {event.location or 'Não informado'}")
                
                # Criar alertas automáticos para este evento
                success = native_alert_system.create_automatic_alerts_for_event(event.id)
                
                if success:
                    print("✅ Alertas automáticos criados!")
                else:
                    print("⚠️ Não foi possível criar alertas (evento já passou?)")
        else:
            print("❌ Nenhum evento encontrado para o Guinho")
            print("💡 Para testar alertas, cadastre um evento futuro para ele")
        
        # Verificar alertas pendentes
        upcoming_alerts = native_alert_system.get_upcoming_alerts(days=30)
        
        if upcoming_alerts:
            print(f"\n🔔 Próximos alertas: {len(upcoming_alerts)}")
            for alert in upcoming_alerts:
                print(f"• {alert['event_title']} - {alert['alert_time']}")
        else:
            print("\n📭 Nenhum alerta pendente")
    else:
        print("❌ Artista Guinho não encontrado!")
    
    print("\n📋 COMO OS ALERTAS FUNCIONAM:")
    print("-" * 40)
    print("1. 🤖 Alertas são criados automaticamente quando um evento é cadastrado")
    print("2. ⏰ Sistema verifica a cada 30 segundos se há alertas para disparar")
    print("3. 🖥️ Alertas aparecem como notificações nativas no desktop")
    print("4. 📱 Funcionam apenas quando o artista está logado no sistema")
    print("5. 🎯 Horários padrão: 1 dia, 2 horas e 30 minutos antes")
    
    print(f"\n🔄 Status do daemon de alertas: {'Ativo' if native_alert_system.is_running else 'Inativo'}")
    
    if not native_alert_system.is_running:
        print("🚀 Iniciando daemon de alertas...")
        native_alert_system.start_alert_daemon()
        print("✅ Daemon iniciado!")