"""
Show Manager - Aplicativo Desktop para Alertas
Este aplicativo roda em segundo plano e mostra notificações mesmo offline
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import json
import os
from datetime import datetime, timedelta
import sqlite3
from plyer import notification
import requests
import sys

class ShowManagerAlerts:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Show Manager - Alertas")
        self.root.geometry("600x500")
        self.root.withdraw()  # Iniciar minimizado
        
        # Configurações
        self.db_file = "desktop_alerts.db"
        self.api_base = "http://localhost:5001"
        self.check_interval = 30  # segundos
        self.is_running = False
        
        self.setup_database()
        self.create_ui()
        self.create_system_tray()
        self.start_monitoring()
    
    def setup_database(self):
        """Configura banco de dados local para alertas offline"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER,
                title TEXT,
                message TEXT,
                alert_time TEXT,
                alert_type TEXT,
                sent INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_ui(self):
        """Cria interface do usuário"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Título
        title_label = ttk.Label(main_frame, text="Show Manager - Sistema de Alertas", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Status
        self.status_label = ttk.Label(main_frame, text="Status: Parado", 
                                     foreground='red')
        self.status_label.grid(row=1, column=0, columnspan=2, pady=(0, 10))
        
        # Controles
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=2, column=0, columnspan=2, pady=(0, 20))
        
        self.start_btn = ttk.Button(control_frame, text="Iniciar Monitoramento", 
                                   command=self.start_monitoring)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_btn = ttk.Button(control_frame, text="Parar Monitoramento", 
                                  command=self.stop_monitoring)
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        test_btn = ttk.Button(control_frame, text="Testar Notificação", 
                             command=self.test_notification)
        test_btn.pack(side=tk.LEFT)
        
        # Lista de alertas
        ttk.Label(main_frame, text="Próximos Alertas:", font=('Arial', 12, 'bold')).grid(
            row=3, column=0, columnspan=2, sticky=tk.W, pady=(20, 5))
        
        # Treeview para alertas
        columns = ('Data/Hora', 'Evento', 'Tipo', 'Status')
        self.tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        
        self.tree.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=4, column=2, sticky=(tk.N, tk.S))
        self.tree.configure(yscroll=scrollbar.set)
        
        # Configurar redimensionamento
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
    
    def create_system_tray(self):
        """Cria ícone na bandeja do sistema (simplificado)"""
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)
    
    def hide_window(self):
        """Minimiza para bandeja do sistema"""
        self.root.withdraw()
    
    def show_window(self):
        """Mostra janela principal"""
        self.root.deiconify()
        self.root.lift()
    
    def start_monitoring(self):
        """Inicia monitoramento de alertas"""
        if not self.is_running:
            self.is_running = True
            self.status_label.config(text="Status: Executando", foreground='green')
            self.start_btn.config(state='disabled')
            self.stop_btn.config(state='normal')
            
            # Executar em thread separada
            thread = threading.Thread(target=self.monitor_alerts, daemon=True)
            thread.start()
    
    def stop_monitoring(self):
        """Para monitoramento de alertas"""
        self.is_running = False
        self.status_label.config(text="Status: Parado", foreground='red')
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
    
    def monitor_alerts(self):
        """Loop principal de monitoramento"""
        while self.is_running:
            try:
                # Verificar alertas locais
                self.check_local_alerts()
                
                # Sincronizar com servidor (se disponível)
                self.sync_with_server()
                
                # Atualizar interface
                self.root.after(0, self.update_alerts_list)
                
                time.sleep(self.check_interval)
                
            except Exception as e:
                print(f"Erro no monitoramento: {e}")
                time.sleep(60)  # Esperar mais se houver erro
    
    def check_local_alerts(self):
        """Verifica alertas locais pendentes"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        now = datetime.now()
        cursor.execute('''
            SELECT id, title, message, alert_time, alert_type 
            FROM alerts 
            WHERE sent = 0 AND alert_time <= ?
        ''', (now.isoformat(),))
        
        alerts = cursor.fetchall()
        
        for alert in alerts:
            alert_id, title, message, alert_time, alert_type = alert
            
            # Mostrar notificação
            self.show_notification(title, message, alert_type)
            
            # Marcar como enviado
            cursor.execute('UPDATE alerts SET sent = 1 WHERE id = ?', (alert_id,))
        
        conn.commit()
        conn.close()
    
    def sync_with_server(self):
        """Sincroniza alertas com o servidor web"""
        try:
            response = requests.get(f"{self.api_base}/alerts/api/upcoming", 
                                  params={'days': 14}, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    self.save_alerts_locally(data['alerts'])
                    
        except requests.exceptions.RequestException:
            # Servidor offline - usar apenas alertas locais
            pass
    
    def save_alerts_locally(self, alerts):
        """Salva alertas do servidor no banco local"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        for alert in alerts:
            # Verificar se já existe
            cursor.execute('SELECT id FROM alerts WHERE event_id = ? AND alert_time = ?',
                          (alert['event_id'], alert['alert_time']))
            
            if not cursor.fetchone():
                cursor.execute('''
                    INSERT INTO alerts (event_id, title, message, alert_time, alert_type)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    alert['event_id'],
                    alert['event_title'],
                    f"Evento com {alert['artist_name']} em {alert['event_location']}",
                    alert['alert_time'],
                    alert['alert_type']
                ))
        
        conn.commit()
        conn.close()
    
    def show_notification(self, title, message, alert_type):
        """Mostra notificação nativa"""
        try:
            icon_path = None  # Você pode adicionar um ícone aqui
            
            notification.notify(
                title=f"🎵 {title}",
                message=message,
                app_name="Show Manager",
                timeout=10 if alert_type == 'reminder' else 20,
                app_icon=icon_path
            )
            
            print(f"Notificação enviada: {title}")
            
        except Exception as e:
            print(f"Erro ao enviar notificação: {e}")
    
    def test_notification(self):
        """Testa notificação"""
        self.show_notification(
            "Teste - Show Manager",
            "Esta é uma notificação de teste do sistema de alertas!",
            "test"
        )
    
    def update_alerts_list(self):
        """Atualiza lista de alertas na interface"""
        # Limpar lista atual
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Buscar alertas
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT alert_time, title, alert_type, sent 
            FROM alerts 
            WHERE alert_time >= datetime('now', '-1 day')
            ORDER BY alert_time
        ''')
        
        alerts = cursor.fetchall()
        
        for alert in alerts:
            alert_time, title, alert_type, sent = alert
            
            # Formatar data
            try:
                dt = datetime.fromisoformat(alert_time)
                formatted_time = dt.strftime("%d/%m %H:%M")
            except:
                formatted_time = alert_time[:16]
            
            # Status
            status = "Enviado" if sent else "Pendente"
            
            # Tipo
            tipo = "URGENTE" if alert_type == "urgent" else "Lembrete"
            
            self.tree.insert('', 'end', values=(formatted_time, title, tipo, status))
        
        conn.close()
    
    def run(self):
        """Executa aplicação"""
        self.root.mainloop()

def main():
    """Função principal"""
    try:
        app = ShowManagerAlerts()
        app.run()
    except KeyboardInterrupt:
        print("Aplicação interrompida pelo usuário")
    except Exception as e:
        print(f"Erro fatal: {e}")
        messagebox.showerror("Erro", f"Erro fatal: {e}")

if __name__ == "__main__":
    main()
