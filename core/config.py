import json
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigManager:
    """Gestore centralizzato della configurazione dell'applicazione"""
    
    def __init__(self, config_file: str = None):
        self.config_file = config_file or Path(__file__).parent.parent / "config.json"
        self._config = {}
        self._load_config()
    
    def _load_config(self):
        """Carica la configurazione dal file JSON"""
        try:
            if Path(self.config_file).exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
            else:
                print(f"File di configurazione non trovato: {self.config_file}")
                self._config = self._get_default_config()
        except Exception as e:
            print(f"Errore caricando configurazione: {e}")
            self._config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Configurazione di default in caso di errori"""
        return {
            "app": {
                "title": "Password Manager",
                "geometry": {"width": 1000, "height": 700, "min_width": 800, "min_height": 600}
            },
            "ui": {
                "fonts": {"title": {"size": 28, "weight": "bold"}},
                "spacing": {"small": 5, "medium": 10, "large": 20}
            }
        }
    
    def get(self, path: str, default: Any = None) -> Any:
        """
        Ottiene un valore dalla configurazione usando la notazione punto
        
        Esempi:
        - config.get('app.title') -> "Password Manager"
        - config.get('login.username_label') -> "Nome Utente:"
        """
        try:
            keys = path.split('.')
            value = self._config
            
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return default
            
            return value
        except Exception:
            return default
    
    def format_message(self, path: str, **kwargs) -> str:
        """
        Ottiene un messaggio dalla configurazione e lo formatta con i parametri
        
        Esempio:
        config.format_message('messages.success.registration_complete', username='mario')
        """
        message = self.get(path, "")
        if message and kwargs:
            try:
                return message.format(**kwargs)
            except KeyError:
                return message
        return message
    
    def get_font_config(self, font_type: str = "body") -> Dict[str, Any]:
        """Ottiene la configurazione per un tipo di font"""
        font_config = self.get(f'ui.fonts.{font_type}', {})
        return {
            'size': font_config.get('size', 12),
            'weight': font_config.get('weight', 'normal')
        }
    
    def get_spacing(self, size: str = "medium") -> int:
        """Ottiene un valore di spaziatura"""
        return self.get(f'ui.spacing.{size}', 10)
    
    def get_app_config(self) -> Dict[str, Any]:
        """Ottiene la configurazione dell'applicazione"""
        return self.get('app', {})
    
    def get_icon(self, icon_name: str) -> str:
        """Ottiene un'icona dalla configurazione"""
        return self.get(f'icons.{icon_name}', '●')
    
    def reload(self):
        """Ricarica la configurazione dal file"""
        self._load_config()

# Istanza globale del gestore configurazione
config_manager = ConfigManager()
