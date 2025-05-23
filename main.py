import os
import sys
import subprocess
import customtkinter as ctk
from pathlib import Path
import atexit

def install_dependencies():
    """Installa le dipendenze mancanti"""
    required_packages = [
        'cryptography',
        'customtkinter'
    ]
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            print(f"Installando {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def cleanup_on_exit():
    """Cleanup quando l'app si chiude"""
    try:
        import customtkinter as ctk
        
        try:
            if hasattr(ctk.windows.widgets.scaling.scaling_tracker, 'ScalingTracker'):
                tracker = ctk.windows.widgets.scaling.scaling_tracker.ScalingTracker
                tracker.window_widgets_dict.clear()
                tracker.window_dpi_scaling_dict.clear()
        except:
            pass
        
        try:
            ctk.CTk._current_height = 600
            ctk.CTk._current_width = 600
        except:
            pass
            
    except Exception:
        pass

# Aggiungi la directory corrente al path per gli import
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Registra cleanup
atexit.register(cleanup_on_exit)

def main():
    """Punto di ingresso principale dell'applicazione"""
    app = None
    try:
        # Installa dipendenze se necessario
        install_dependencies()
        
        # Crea le directory necessarie
        data_dir = current_dir / "data"
        data_dir.mkdir(exist_ok=True)
        (data_dir / "users").mkdir(exist_ok=True)
        (data_dir / "backups").mkdir(exist_ok=True)
        
        # Configura CustomTkinter con tema chiaro iniziale
        ctk.set_appearance_mode("Light")
        ctk.set_default_color_theme("blue")
        
        # Importa e inizializza il theme manager dopo aver configurato CustomTkinter
        from core.theme import theme_manager
        theme_manager.set_mode("light")  # Assicura sincronizzazione
        
        # Importa l'app solo dopo aver configurato tutto
        from core.app import PasswordManagerApp
        
        # Crea e avvia l'applicazione
        app = PasswordManagerApp()
        
        # Gestisci graceful shutdown
        def on_closing():
            try:
                app._on_closing()
            except:
                pass
            
        app.protocol("WM_DELETE_WINDOW", on_closing)
        app.mainloop()
        
    except Exception as e:
        import traceback
        traceback.print_exc()
    finally:
        if app:
            try:
                app.quit()
                app.destroy()
            except:
                pass
        cleanup_on_exit()
        
        import sys
        sys.exit(0)

if __name__ == "__main__":
    main()
