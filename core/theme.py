import customtkinter as ctk
from typing import Dict, Any, Callable, List
from dataclasses import dataclass
from enum import Enum

class ThemeMode(Enum):
    LIGHT = "Light"
    DARK = "Dark"
    SYSTEM = "System"

@dataclass
class ColorScheme:
    """Schema colori per un tema specifico"""
    primary: str
    secondary: str
    background: str
    surface: str
    text: str
    text_secondary: str
    accent: str
    border: str
    hover: str
    success: str
    warning: str
    error: str
    info: str

class ThemeManager:
    """Gestore centralizzato dei temi con observer pattern"""
    
    def __init__(self):
        self.observers = []
        # Inizializza con il tema corrente di CustomTkinter
        current_mode = ctk.get_appearance_mode().lower()
        self.mode = current_mode
        
        # Carica configurazione temi se disponibile
        try:
            from .config import config_manager
            self.config = config_manager
        except ImportError:
            self.config = None
    
    def set_mode(self, mode: str):
        """Imposta la modalità del tema"""
        if mode in ["light", "dark"]:
            self.mode = mode
            # Sincronizza con CustomTkinter
            ctk.set_appearance_mode(mode.capitalize())
            self._notify_observers()
    
    def toggle_mode(self):
        """Cambia tra tema chiaro e scuro"""
        new_mode = "dark" if self.mode == "light" else "light"
        self.set_mode(new_mode)
        return new_mode
    
    def get_current_mode(self):
        """Ottiene la modalità corrente"""
        return self.mode
    
    def get_colors(self):
        """Ottiene i colori del tema corrente"""
        # Prova a caricare colori personalizzati dalla configurazione
        if self.config:
            custom_colors = self.config.get(f'themes.{self.mode}', {})
            if custom_colors:
                return custom_colors
        
        # Colori di default
        if self.mode == "dark":
            return {
                'background': '#1a1a1a',
                'surface': '#2d2d30',
                'secondary': '#3e3e42',
                'primary': '#0d7377',
                'accent': '#14a085',
                'text': '#ffffff',
                'text_secondary': '#cccccc',
                'border': '#404040',
                'hover': '#4a4a4e',
                'error': '#f44336',
                'success': '#4caf50',
                'warning': '#ff9800'
            }
        else:  # light mode
            return {
                'background': '#f8f9fa',
                'surface': '#ffffff',
                'secondary': '#f1f3f4',
                'primary': '#1976d2',
                'accent': '#2196f3',
                'text': '#212529',
                'text_secondary': '#6c757d',
                'border': '#dee2e6',
                'hover': '#e9ecef',
                'error': '#dc3545',
                'success': '#28a745',
                'warning': '#ffc107'
            }
    
    def add_observer(self, callback: Callable):
        """Registra un observer per i cambi di tema"""
        if callback not in self.observers:
            self.observers.append(callback)
    
    def remove_observer(self, callback: Callable):
        """Rimuove un observer"""
        if callback in self.observers:
            self.observers.remove(callback)
    
    def _notify_observers(self):
        """Notifica tutti gli observer del cambio tema"""
        for callback in self.observers[:]:  # Copia la lista per evitare problemi di concorrenza
            try:
                callback()
            except Exception:
                # Rimuovi observer problematici senza log
                self.remove_observer(callback)

# Istanza globale del theme manager
theme_manager = ThemeManager()
