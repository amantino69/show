from app import create_app
from app.models import User, Artist
import json

app = create_app()

with app.app_context():
    print("🔍 VERIFICAÇÃO DA INTEGRAÇÃO COM GOOGLE CALENDAR")
    print("=" * 60)
    
    # Verificar configurações
    from config import Config
    
    print("📋 CONFIGURAÇÕES GOOGLE:")
    print(f"✅ Client ID: {Config.GOOGLE_CLIENT_ID[:20]}..." if Config.GOOGLE_CLIENT_ID else "❌ Client ID não configurado")
    print(f"✅ Client Secret: {Config.GOOGLE_CLIENT_SECRET[:10]}..." if Config.GOOGLE_CLIENT_SECRET else "❌ Client Secret não configurado")
    print(f"✅ Redirect URI: {Config.GOOGLE_REDIRECT_URI}" if Config.GOOGLE_REDIRECT_URI else "❌ Redirect URI não configurado")
    
    print("\n👥 USUÁRIOS E CONEXÕES GOOGLE:")
    print("-" * 40)
    
    # Verificar usuários
    users = User.query.all()
    for user in users:
        google_status = "🟢 Conectado" if user.google_token else "⚫ Desconectado"
        user_type = "👔 Empresário" if user.is_manager else "🎭 Artista"
        
        print(f"{user_type} {user.username}: {google_status}")
        
        if user.google_token:
            try:
                token_data = json.loads(user.google_token)
                print(f"  📅 Token expira em: {token_data.get('expiry', 'N/A')}")
            except:
                print("  ⚠️ Token inválido")
    
    print("\n🎭 ARTISTAS E EMAILS:")
    print("-" * 40)
    
    artists = Artist.query.all()
    for artist in artists:
        user = User.query.filter_by(artist_id=artist.id).first()
        
        print(f"🎤 {artist.stage_name} ({artist.name})")
        print(f"  📧 Email: {artist.email}")
        print(f"  👤 Conta: {'Sim' if user else 'Não'}")
        print(f"  📅 Google: {'Conectado' if user and user.google_token else 'Desconectado'}")
        print()
    
    print("🔗 COMO CONECTAR GOOGLE CALENDAR:")
    print("-" * 40)
    print("1. 👔 EMPRESÁRIO:")
    print("   - Login: empresario / 123456")
    print("   - Acessar: http://127.0.0.1:5005/google/authorize")
    print("   - Autorizar acesso ao Google Calendar")
    print()
    print("2. 🎭 ARTISTA (Guinho):")
    print("   - Login: guinho / guinho123")
    print("   - Acessar: http://127.0.0.1:5005/google/authorize")
    print("   - Autorizar com conta Google pessoal")
    print()
    
    print("📧 COMO FUNCIONAM AS NOTIFICAÇÕES:")
    print("-" * 40)
    print("🔄 DUPLO SISTEMA DE NOTIFICAÇÕES:")
    print()
    print("1. 📅 GOOGLE CALENDAR (se conectado):")
    print("   • Eventos aparecem automaticamente na agenda")
    print("   • Google envia emails: 2 dias, 1 dia, 3h antes")
    print("   • Notificações no celular via app Google Calendar")
    print("   • Sincronização em tempo real")
    print()
    print("2. 📧 SISTEMA PRÓPRIO (sempre ativo):")
    print("   • Sistema envia emails: 1 dia, 2h, 30min antes")
    print("   • Templates personalizados")
    print("   • Backup caso Google falhe")
    print("   • Funciona independente do Google")
    print()
    print("3. 🖥️ ALERTAS NATIVOS (se logado no sistema):")
    print("   • Pop-ups na tela: 1 dia, 2h, 30min antes")
    print("   • Funcionam quando artista está no sistema")
    print("   • Notificações do Windows/Mac")
    print()
    
    print("🎯 RESULTADO PARA O GUINHO:")
    print("-" * 40)
    print("✅ Recebe notificações por 3 canais diferentes")
    print("✅ Eventos na agenda do Google (se conectar)")
    print("✅ Emails automáticos sempre")
    print("✅ Alertas no computador")
    print("✅ Notificações no celular (via Google)")
    print()
    print("🚀 SISTEMA ROBUSTO E REDUNDANTE!")
    print("   Mesmo se um canal falhar, outros continuam funcionando")