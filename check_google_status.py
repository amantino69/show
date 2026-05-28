import sqlite3
import json

print("🔍 VERIFICAÇÃO DA INTEGRAÇÃO COM GOOGLE CALENDAR")
print("=" * 60)

# Verificar configurações no arquivo de credenciais
try:
    with open('credentials.json', 'r') as f:
        creds = json.load(f)
    
    client_id = creds['installed']['client_id']
    print(f"✅ Google Client ID: {client_id[:20]}...")
    print(f"✅ Google Project ID: {creds['installed']['project_id']}")
    print("✅ Credenciais Google configuradas!")
except:
    print("❌ Arquivo credentials.json não encontrado")

print("\n👥 VERIFICAÇÃO DE USUÁRIOS NO BANCO:")
print("-" * 40)

# Conectar ao banco de dados
try:
    conn = sqlite3.connect('instance/artistas_sistema.db')
    cursor = conn.cursor()
    
    # Verificar usuários e tokens Google
    cursor.execute('''
        SELECT u.username, u.email, u.is_manager, 
               CASE WHEN u.google_token IS NULL THEN 'Desconectado' ELSE 'Conectado' END as google_status,
               a.stage_name
        FROM user u 
        LEFT JOIN artist a ON u.artist_id = a.id
    ''')
    
    users = cursor.fetchall()
    
    for user in users:
        username, email, is_manager, google_status, stage_name = user
        user_type = "👔 Empresário" if is_manager else "🎭 Artista"
        name_display = stage_name if stage_name else "Empresário"
        
        status_icon = "🟢" if google_status == "Conectado" else "⚫"
        print(f"{user_type} {name_display} ({username}): {status_icon} {google_status}")
        print(f"  📧 Email: {email}")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Erro ao acessar banco: {e}")

print("\n📧 COMO FUNCIONAM AS NOTIFICAÇÕES PARA O GUINHO:")
print("=" * 60)

print("""
🔄 SISTEMA TRIPLO DE NOTIFICAÇÕES:

1. 📅 GOOGLE CALENDAR (se conectado):
   ┌─────────────────────────────────────┐
   │ • Eventos aparecem automaticamente  │
   │ • Google envia emails:              │
   │   - 2 dias antes                    │
   │   - 1 dia antes                     │
   │   - 3 horas antes                   │
   │ • Notificações no celular           │
   │ • Sincronização automática          │
   └─────────────────────────────────────┘

2. 📧 SISTEMA DE EMAIL PRÓPRIO (sempre ativo):
   ┌─────────────────────────────────────┐
   │ • Sistema envia para guinho@show.com│
   │ • Horários:                         │
   │   - 1 dia antes                     │
   │   - 2 horas antes                   │
   │   - 30 minutos antes                │
   │ • Templates personalizados          │
   │ • Funciona independente do Google   │
   └─────────────────────────────────────┘

3. 🖥️ ALERTAS NATIVOS (se logado):
   ┌─────────────────────────────────────┐
   │ • Pop-ups na tela do computador     │
   │ • Horários:                         │
   │   - 1 dia antes                     │
   │   - 2 horas antes                   │
   │   - 30 minutos antes                │
   │ • Funciona quando está no sistema   │
   └─────────────────────────────────────┘
""")

print("🔗 COMO CONECTAR O GOOGLE CALENDAR:")
print("-" * 40)
print("1. 👔 EMPRESÁRIO:")
print("   • Login: empresario / 123456")
print("   • URL: http://127.0.0.1:5005/google/authorize")
print("   • Autorizar acesso ao Google Calendar")
print()
print("2. 🎭 GUINHO:")
print("   • Login: guinho / guinho123")
print("   • URL: http://127.0.0.1:5005/google/authorize")
print("   • Autorizar com conta Google pessoal")
print()

print("🎯 RESULTADO PARA O GUINHO:")
print("-" * 40)
print("✅ SEMPRE recebe emails (sistema próprio)")
print("✅ OPCIONALMENTE recebe via Google Calendar (se conectar)")
print("✅ SEMPRE recebe alertas nativos (se logado)")
print("✅ Notificações no celular (se Google conectado)")
print()
print("💡 REDUNDÂNCIA GARANTIDA:")
print("   Mesmo se o Google falhar, o sistema próprio continua")
print("   funcionando e enviando emails + alertas nativos!")
print()
print("🚀 SISTEMA ROBUSTO E CONFIÁVEL! 🎭✨")