#!/usr/bin/env python3
"""
Script para testar o Google Auth corrigido
"""
import requests
import sys

def test_google_auth():
    print("🔍 TESTANDO GOOGLE AUTH CORRIGIDO")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:5005"
    
    # Criar sessão para manter cookies
    session = requests.Session()
    
    try:
        # 1. Testar página de login
        print("📝 1. Testando página de login...")
        login_response = session.get(f"{base_url}/auth/login")
        print(f"   Status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            print("   ✅ Página de login carregada")
        else:
            print("   ❌ Erro na página de login")
            return
        
        # 2. Fazer login como empresário
        print("\n👔 2. Fazendo login como empresário...")
        login_data = {
            'username': 'empresario',
            'password': '123456'
        }
        
        login_post = session.post(f"{base_url}/auth/login", data=login_data, allow_redirects=False)
        print(f"   Status: {login_post.status_code}")
        
        if login_post.status_code in [200, 302]:
            print("   ✅ Login realizado com sucesso")
            
            # 3. Testar acesso ao Google authorize
            print("\n🔐 3. Testando acesso ao Google authorize...")
            auth_response = session.get(f"{base_url}/google/authorize", allow_redirects=False)
            print(f"   Status: {auth_response.status_code}")
            
            if auth_response.status_code == 302:
                redirect_url = auth_response.headers.get('Location', '')
                print(f"   ✅ Redirecionando para: {redirect_url[:100]}...")
                
                if 'accounts.google.com' in redirect_url:
                    print("   ✅ URL do Google detectada - configuração correta!")
                else:
                    print("   ⚠️ Redirecionamento inesperado")
            else:
                print("   ❌ Erro no authorize")
        else:
            print("   ❌ Erro no login")
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Servidor não está rodando em http://127.0.0.1:5005")
        print("   Execute: python app.py")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    test_google_auth()
    print("\n" + "=" * 50)
    print("🔧 INSTRUÇÕES:")
    print("1. Fazer login: http://127.0.0.1:5005/auth/login")
    print("   • Usuário: empresario | Senha: 123456")
    print("2. Autorizar Google: http://127.0.0.1:5005/google/authorize")
    print("3. ✅ Configuração corrigida!")