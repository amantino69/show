#!/usr/bin/env python3
"""
Teste rápido do sistema de alertas
"""

try:
    from app.alert_system import native_alert_system
    print("✓ Sistema de alertas importado com sucesso!")
    
    # Testar notificação
    result = native_alert_system.show_desktop_notification(
        "🎵 Teste Show Manager", 
        "Sistema de alertas funcionando!"
    )
    
    if result:
        print("✓ Notificação de teste enviada!")
    else:
        print("⚠️ Erro ao enviar notificação de teste")
        
except Exception as e:
    print(f"❌ Erro: {e}")
