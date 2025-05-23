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
        # Forza la pulizia di tutti i widget CustomTkinter
        import customtkinter as ctk
        # Reset scaling tracker
        if hasattr(ctk.windows.widgets.scaling.scaling_tracker, 'ScalingTracker'):
            ctk.windows.widgets.scaling.scaling_tracker.ScalingTracker.window_widgets_dict.clear()
            ctk.windows.widgets.scaling.scaling_tracker.ScalingTracker.window_dpi_scaling_dict.clear()
    except:
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
        app.mainloop()
        
    except Exception as e:
        print(f"Errore durante l'avvio dell'applicazione: {e}")
        if app:
            try:
                app.destroy()
            except:
                pass
    finally:
        cleanup_on_exit()

if __name__ == "__main__":
    main()
