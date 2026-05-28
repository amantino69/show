// service-worker.js - Para notificações push
self.addEventListener('push', function(event) {
    const options = {
        body: event.data ? event.data.text() : 'Nova notificação',
        icon: '/static/images/icon-192x192.png',
        badge: '/static/images/badge-72x72.png',
        vibrate: [200, 100, 200],
        data: {
            url: '/events'
        },
        actions: [
            {action: 'view', title: 'Ver Evento'},
            {action: 'close', title: 'Fechar'}
        ]
    };

    event.waitUntil(
        self.registration.showNotification('Sistema de Artistas', options)
    );
});

self.addEventListener('notificationclick', function(event) {
    event.notification.close();
    
    if (event.action === 'view') {
        event.waitUntil(
            clients.openWindow('/events')
        );
    }
});
