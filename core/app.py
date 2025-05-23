# core/app.py
import customtkinter as ctk
from pathlib import Path
from .theme import theme_manager, ThemeMode
from .database import PasswordDatabase
from core.components import ThemedFrame, ThemedLabel, ThemedButton

class PasswordManagerApp(ctk.CTk):
    """Applicazione principale del password manager"""
    
    def __init__(self):
        super().__init__()
        
        # Configurazione finestra
        self.title("Password Manager - Versione Semplificata")
        self.geometry("1000x700")
        self.minsize(800, 600)
        
        # Inizializza variabili
        self.current_user = None
        self.current_view = None
        self.login_view = None
        self.register_view = None
        
        print("Inizializzazione app...")
        
        # Inizializza database
        try:
            data_dir = Path(__file__).parent.parent / "data"
            self.database = PasswordDatabase(str(data_dir))
            print(f"Database inizializzato: {self.database}")
        except Exception as e:
            print(f"Errore inizializzazione database: {e}")
            self.database = None
        
        # Setup UI
        self._setup_ui()
        self._show_login()
        
        # Bind eventi
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _setup_ui(self):
        """Configura l'interfaccia utente principale"""
        # Frame principale per il contenuto
        self.main_frame = ThemedFrame(self, style="background")
        self.main_frame.pack(fill="both", expand=True)

    def _show_login(self):
        """Mostra la vista di login"""
        try:
            self._clear_current_view()
            
            from ui.login_view import LoginView
            self.login_view = LoginView(
                self.main_frame,
                self._on_login_success,
                self._on_register_click
            )
            # Condividi il database
            self.login_view.database = self.database
            self.login_view.pack(fill="both", expand=True)
            self.current_view = self.login_view
            
        except Exception as e:
            print(f"Errore creando login: {e}")

    def _show_register(self):
        """Mostra la vista di registrazione"""
        try:
            self._clear_current_view()
            
            from ui.register_view import RegisterView
            self.register_view = RegisterView(
                self.main_frame,
                self._on_register_success,
                self._on_back_to_login
            )
            # Condividi il database (come fatto per LoginView)
            self.register_view.database = self.database
            self.register_view.pack(fill="both", expand=True)
            self.current_view = self.register_view
            
        except Exception as e:
            print(f"Errore creando registrazione: {e}")
            self._show_login()

    def _show_dashboard(self):
        """Mostra la vista dashboard"""
        try:
            self._clear_current_view()
            
            # Crea la vista dashboard
            from ui.dashboard_view import DashboardView
            dashboard_view = DashboardView(
                self.main_frame,
                self.database,
                self._on_logout
            )
            dashboard_view.pack(fill="both", expand=True)
            self.current_view = dashboard_view
            
            # Rendi accessibile il metodo backup
            dashboard_view.master.master = self
            
        except Exception as e:
            print(f"Errore creando dashboard: {e}")
            self._show_login()

    def _show_backup(self):
        """Mostra la vista backup"""
        try:
            if not self.database or not self.database.current_user:
                self._show_login()
                return
                
            self._clear_current_view()
            
            # Crea la vista backup
            from ui.backup_view import BackupView
            backup_view = BackupView(
                self.main_frame,
                self.database,
                self.database.current_user,
                self._show_dashboard
            )
            backup_view.pack(fill="both", expand=True)
            self.current_view = backup_view
            
        except Exception as e:
            print(f"Errore creando vista backup: {e}")
            self._show_dashboard()

    def _clear_current_view(self):
        """
        Pulisce la vista corrente in modo sicuro per evitare memory leak
        Gestisce la pulizia ricorsiva di tutti i widget e le loro risorse
        """
        try:
            # Forza il completamento di tutte le operazioni pending della GUI
            self.update_idletasks()
            
            # Distrugge tutti i widget figli del frame principale
            for child in list(self.main_frame.winfo_children()):
                try:
                    # Disabilita eventuali callback di scaling per evitare errori durante distruzione
                    if hasattr(child, '_set_scaling'):
                        try:
                            child._set_scaling = lambda x: None
                        except:
                            pass
                    
                    # Esegue distruzione ricorsiva sicura
                    self._destroy_widget_safely(child)
                except Exception as e:
                    # Log degli errori di distruzione per debugging
                    print(f"ERRORE PULIZIA WIDGET: {e}")
                    pass
        except Exception as e:
            print(f"ERRORE PULIZIA VISTA: {e}")
        
        # Reset delle variabili di stato per prevenire riferimenti pendenti
        self.current_view = None
        self.login_view = None
        self.register_view = None
        
        # Forza garbage collection per liberare memoria
        import gc
        gc.collect()
    
    def _destroy_widget_safely(self, widget):
        """Distrugge un widget in modo sicuro"""
        try:
            # Prima distruggi tutti i figli
            for child in list(widget.winfo_children()):
                self._destroy_widget_safely(child)
            
            # Poi distruggi il widget stesso
            widget.destroy()
        except Exception as e:
            print(f"Errore distruggendo widget {widget}: {e}")

    def _on_login_success(self):
        """Callback per login riuscito"""
        try:
            # Verifica che il database abbia current_user impostato
            if not self.database or not self.database.current_user:
                print("Errore: database o current_user non validi dopo login")
                from core.components import show_message
                show_message(self, "Errore", "Errore interno: stato utente non valido", "error")
                self._show_login()
                return
            
            print(f"Login riuscito per utente: {self.database.current_user}")
            self.current_user = self.database.current_user  # Sincronizza
            self._show_dashboard()
            
        except Exception as e:
            print(f"Errore in _on_login_success: {e}")
            self._show_login()

    def _on_register_click(self):
        """Callback per il click su registrazione"""
        self._show_register()

    def _on_register_success(self):
        """Callback per registrazione riuscita"""
        self._show_login()

    def _on_back_to_login(self):
        """Callback per tornare al login dalla registrazione"""
        self._show_login()

    def _on_logout(self):
        """Callback per logout"""
        try:
            print("Eseguendo logout...")
            
            # Pulisci il database
            if self.database:
                self.database.logout()
            
            # Reset variabili
            self.current_user = None
            
            print("Logout completato, tornando al login")
            # Torna al login
            self._show_login()
            
        except Exception as e:
            print(f"Errore durante logout: {e}")
            self._show_login()

    def _on_closing(self):
        """Gestisce la chiusura dell'applicazione"""
        try:
            print("Chiusura applicazione...")
            
            # Cleanup viste
            self._clear_current_view()
            
            # Pulisci CustomTkinter scaling tracker
            try:
                import customtkinter as ctk
                if hasattr(ctk, 'windows') and hasattr(ctk.windows, 'widgets'):
                    if hasattr(ctk.windows.widgets, 'scaling'):
                        scaling_module = ctk.windows.widgets.scaling
                        if hasattr(scaling_module, 'scaling_tracker'):
                            tracker = scaling_module.scaling_tracker.ScalingTracker
                            if hasattr(tracker, 'window_widgets_dict'):
                                tracker.window_widgets_dict.clear()
                            if hasattr(tracker, 'window_dpi_scaling_dict'):
                                tracker.window_dpi_scaling_dict.clear()
            except Exception as e:
                print(f"Errore pulizia CustomTkinter: {e}")
            
            # Chiudi database
            if hasattr(self.database, 'close'):
                self.database.close()
                
        except Exception as e:
            print(f"Errore durante chiusura: {e}")
        finally:
            self.quit()
            self.destroy()