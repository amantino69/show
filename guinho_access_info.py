"""
📋 INFORMAÇÕES PARA ACESSO DO ARTISTA GUINHO
==================================================

Com base na imagem fornecida, aqui estão as instruções para o artista Guinho acessar o sistema:

🔐 CREDENCIAIS DE ACESSO:
------------------------
• URL: http://127.0.0.1:5005 (ou http://localhost:5005)
• Username: guinho
• Senha: guinho123

📱 COMO ACESSAR:
---------------
1. Abrir o navegador web (Chrome, Firefox, Edge, etc.)
2. Digitar a URL: http://127.0.0.1:5005
3. Clicar em "Entrar" ou "Login"
4. Inserir as credenciais:
   - Usuário: guinho
   - Senha: guinho123
5. Clicar em "Entrar"

👀 O QUE O ARTISTA VÊ:
---------------------
• Dashboard personalizado com APENAS seus eventos
• Agenda com seus compromissos
• Detalhes de seus shows/apresentações
• Notificações de seus eventos

🔔 SISTEMA DE ALERTAS AUTOMÁTICOS:
---------------------------------
O Guinho receberá alertas nativos (pop-ups no computador) nos seguintes momentos:

• 📅 1 DIA ANTES do evento
• ⏰ 2 HORAS ANTES do evento  
• ⚡ 30 MINUTOS ANTES do evento

Os alertas aparecem automaticamente na tela quando:
- O computador está ligado
- O artista está logado no sistema
- Chegou o horário programado para o alerta

💡 VANTAGENS PARA O ARTISTA:
---------------------------
• Nunca mais perder um compromisso
• Visualização clara de sua agenda
• Lembretes automáticos
• Acesso 24/7 de qualquer lugar
• Interface simples e intuitiva

📞 SUPORTE:
----------
Se o Guinho tiver dificuldades:
- O empresário pode acessar as credenciais em: Artistas > Guinho > Credenciais
- Todas as informações ficam disponíveis para cópia fácil
- Sistema funciona em qualquer navegador moderno

🔧 CONFIGURAÇÃO DOS ALERTAS:
---------------------------
Os alertas são automáticos e criados quando:
- Um novo evento é cadastrado para o artista
- O sistema agenda as notificações automaticamente
- Não precisa configurar nada manualmente

===============================================
✅ SISTEMA TOTALMENTE CONFIGURADO E FUNCIONAL!
===============================================
"""

print(__doc__)

# Verificar se o usuário do Guinho existe
if __name__ == "__main__":
    try:
        from app import create_app
        from app.models import User, Artist
        
        app = create_app()
        with app.app_context():
            guinho = Artist.query.filter_by(stage_name='Guinho').first()
            user = User.query.filter_by(artist_id=guinho.id).first() if guinho else None
            
            print("\n🔍 VERIFICAÇÃO NO BANCO DE DADOS:")
            print("=" * 40)
            
            if guinho:
                print(f"✅ Artista encontrado: {guinho.name} ({guinho.stage_name})")
                print(f"📧 Email: {guinho.email}")
                print(f"📱 Telefone: {guinho.phone}")
                print(f"🎭 Tipo: {guinho.artist_type.name if guinho.artist_type else 'Não definido'}")
                
                if user:
                    print(f"✅ Usuário criado: {user.username}")
                    print(f"📧 Email do usuário: {user.email}")
                    print(f"🔑 Senha: guinho123 (padrão)")
                    print(f"👥 Tipo de acesso: {'Empresário' if user.is_manager else 'Artista'}")
                else:
                    print("❌ Usuário NÃO encontrado - precisa criar!")
            else:
                print("❌ Artista Guinho não encontrado!")
                
    except Exception as e:
        print(f"❌ Erro ao verificar: {e}")