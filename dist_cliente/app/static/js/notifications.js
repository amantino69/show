// notifications.js - Sistema de notificações do app
class NotificationManager {
    constructor() {
        this.isSupported = 'Notification' in window;
        this.isServiceWorkerSupported = 'serviceWorker' in navigator;
        this.init();
    }

    async init() {
        if (this.isServiceWorkerSupported) {
            try {
                await navigator.serviceWorker.register('/static/js/service-worker.js');
                console.log('Service Worker registrado com sucesso');
            } catch (error) {
                console.error('Erro ao registrar Service Worker:', error);
            }
        }
    }

    async requestPermission() {
        if (!this.isSupported) {
            console.warn('Notificações não suportadas neste navegador');
            return false;
        }

        let permission = Notification.permission;
        
        if (permission === 'default') {
            permission = await Notification.requestPermission();
        }

        return permission === 'granted';
    }

    async showNotification(title, options = {}) {
        const hasPermission = await this.requestPermission();
        
        if (!hasPermission) {
            console.warn('Permissão para notificações negada');
            return false;
        }

        const defaultOptions = {
            icon: '/static/images/logo.png',
            badge: '/static/images/badge.png',
            vibrate: [200, 100, 200],
            requireInteraction: true,
            ...options
        };

        if (this.isServiceWorkerSupported && 'showNotification' in ServiceWorkerRegistration.prototype) {
            const registration = await navigator.serviceWorker.ready;
            return registration.showNotification(title, defaultOptions);
        } else {
            return new Notification(title, defaultOptions);
        }
    }

    // Notificação específica para eventos
    showEventNotification(event, type = 'reminder') {
        const messages = {
            reminder: `Lembrete: ${event.title} em breve`,
            started: `Evento iniciado: ${event.title}`,
            cancelled: `Evento cancelado: ${event.title}`,
            updated: `Evento atualizado: ${event.title}`
        };

        const colors = {
            reminder: '#ffc107',
            started: '#28a745',
            cancelled: '#dc3545',
            updated: '#17a2b8'
        };

        this.showNotification(messages[type], {
            body: `${event.artist} - ${event.location}\n${event.datetime}`,
            icon: '/static/images/event-icon.png',
            data: {
                eventId: event.id,
                type: type,
                url: `/events/${event.id}`
            },
            actions: [
                {action: 'view', title: '👁️ Ver Evento'},
                {action: 'snooze', title: '⏰ Adiar (10min)'}
            ]
        });
    }

    // Verificar eventos próximos
    async checkUpcomingEvents() {
        try {
            const response = await fetch('/api/upcoming-events');
            const events = await response.json();
            
            events.forEach(event => {
                const eventTime = new Date(event.start_datetime);
                const now = new Date();
                const timeDiff = eventTime - now;
                
                // Notificar 24h, 3h e 30min antes
                if (timeDiff <= 24 * 60 * 60 * 1000 && timeDiff > 23 * 60 * 60 * 1000) {
                    this.showEventNotification(event, 'reminder');
                }
            });
        } catch (error) {
            console.error('Erro ao verificar eventos próximos:', error);
        }
    }

    // Iniciar verificação periódica
    startPeriodicCheck(intervalMinutes = 30) {
        this.checkUpcomingEvents(); // Verificação inicial
        setInterval(() => {
            this.checkUpcomingEvents();
        }, intervalMinutes * 60 * 1000);
    }
}

// Instância global
const notificationManager = new NotificationManager();

// Auto-iniciar quando o usuário estiver logado
document.addEventListener('DOMContentLoaded', function() {
    // Verificar se usuário está logado
    if (document.body.classList.contains('logged-in')) {
        notificationManager.startPeriodicCheck();
    }
});

// Função para testar notificações
function testNotification() {
    notificationManager.showNotification('Teste de Notificação', {
        body: 'O sistema de notificações está funcionando!',
        icon: '/static/images/test-icon.png'
    });
}
