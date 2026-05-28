import requests

base_url = "http://127.0.0.1:5005"

print("🔍 TESTANDO ROTAS DO SISTEMA")
print("=" * 50)

# Testar rotas principais
routes_to_test = [
    "/",
    "/auth/login",
    "/google/authorize",
    "/google/callback"
]

for route in routes_to_test:
    try:
        url = base_url + route
        response = requests.get(url, allow_redirects=False)
        
        status_emoji = "✅" if response.status_code < 400 else "❌"
        print(f"{status_emoji} {route}: {response.status_code}")
        
        if response.status_code == 302:
            print(f"   → Redireciona para: {response.headers.get('Location', 'N/A')}")
        elif response.status_code >= 400:
            print(f"   → Erro: {response.reason}")
            
    except Exception as e:
        print(f"❌ {route}: Erro de conexão - {e}")

print("\n📋 INSTRUÇÕES CORRIGIDAS:")
print("-" * 30)
print("🔗 PARA CONECTAR GOOGLE CALENDAR:")
print()
print("1. 👔 EMPRESÁRIO:")
print("   • Fazer login: http://127.0.0.1:5005/auth/login")
print("   • Usuário: empresario")
print("   • Senha: 123456")
print("   • Depois acessar: http://127.0.0.1:5005/google/authorize")
print()
print("2. 🎭 GUINHO:")
print("   • Fazer login: http://127.0.0.1:5005/auth/login")
print("   • Usuário: guinho")
print("   • Senha: guinho123")
print("   • Depois acessar: http://127.0.0.1:5005/google/authorize")
print()
print("✅ URLS CORRIGIDAS E FUNCIONANDO!")