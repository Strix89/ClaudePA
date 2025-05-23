import customtkinter as ctk
from typing import Optional, Callable, Any
from .theme import theme_manager
from .config import config_manager

class ThemedWidget:
    """Classe base per widget che supportano il tema automatico"""
    
    def __init__(self):
        self._theme_applied = False
        self._destroyed = False
        theme_manager.add_observer(self._update_theme)
        # Usa after per applicare il tema iniziale
        if hasattr(self, 'after'):
            self.after(1, self._apply_theme)
        else:
            self._apply_theme()
    
    def _apply_theme(self):
        """Applica il tema corrente al widget"""
        if self._destroyed:
            return
        
        try:
            if hasattr(self, '_apply_theme_colors'):
                self._apply_theme_colors()
            self._theme_applied = True
        except Exception as e:
            print(f"Errore applicazione tema: {e}")
    
    def _update_theme(self):
        """
        Callback automatico per aggiornamento tema
        Usa il sistema after() per garantire thread safety
        """
        if self._destroyed:
            return
        
        # Utilizza after() per assicurarsi che l'aggiornamento avvenga nel thread principale
        # Questo previene errori di concorrenza durante il cambio tema
        if hasattr(self, 'after'):
            self.after(1, self._apply_theme)
        else:
            self._apply_theme()
    
    def destroy(self):
        """
        Override del metodo destroy per cleanup automatico
        Rimuove l'observer dal theme manager per evitare memory leak
        """
        self._destroyed = True
        try:
            # Rimuove questo widget dalla lista degli observer del tema
            theme_manager.remove_observer(self._update_theme)
        except:
            # Ignora errori durante la rimozione (widget già rimosso)
            pass
        
        # Chiama il destroy originale se disponibile
        if hasattr(super(), 'destroy'):
            super().destroy()

class ThemedFrame(ThemedWidget, ctk.CTkFrame):
    """Frame con supporto tema automatico"""
    
    def __init__(self, master, style="secondary", **kwargs):
        self.style = style
        
        # Rimuovi fg_color se presente in kwargs per gestirlo automaticamente
        kwargs.pop('fg_color', None)
        
        ctk.CTkFrame.__init__(self, master, **kwargs)
        ThemedWidget.__init__(self)
    
    def _apply_theme_colors(self):
        colors = theme_manager.get_colors()
        color_map = {
            'primary': colors['primary'],
            'secondary': colors['secondary'],
            'surface': colors['surface'],
            'background': colors['background']
        }
        self.configure(fg_color=color_map.get(self.style, colors['secondary']))

class ThemedLabel(ThemedWidget, ctk.CTkLabel):
    """Label con supporto tema automatico"""
    
    def __init__(self, master, text="", style="primary", **kwargs):
        self.style = style
        
        # Rimuovi text_color se presente per gestirlo automaticamente
        kwargs.pop('text_color', None)
        
        ctk.CTkLabel.__init__(self, master, text=text, **kwargs)
        ThemedWidget.__init__(self)
    
    def _apply_theme_colors(self):
        colors = theme_manager.get_colors()
        color_map = {
            'primary': colors['text'],
            'secondary': colors['text_secondary'],
            'accent': colors['accent']
        }
        self.configure(text_color=color_map.get(self.style, colors['text']))

class ThemedButton(ThemedWidget, ctk.CTkButton):
    """Button con supporto tema automatico"""
    
    def __init__(self, master, text="", command=None, style="primary", **kwargs):
        self.style = style
        
        # Rimuovi colori se presenti per gestirli automaticamente
        kwargs.pop('fg_color', None)
        kwargs.pop('hover_color', None)
        kwargs.pop('text_color', None)
        
        ctk.CTkButton.__init__(self, master, text=text, command=command, **kwargs)
        ThemedWidget.__init__(self)
    
    def _apply_theme_colors(self):
        colors = theme_manager.get_colors()
        
        if self.style == "primary":
            self.configure(
                fg_color=colors['primary'],
                hover_color=colors['accent'],
                text_color="white"
            )
        elif self.style == "secondary":
            self.configure(
                fg_color=colors['surface'],
                hover_color=colors['hover'],
                text_color=colors['text'],
                border_width=1,
                border_color=colors['border']
            )
        elif self.style == "danger":
            self.configure(
                fg_color=colors['error'],
                hover_color="#D32F2F",
                text_color="white"
            )

class ThemedEntry(ThemedWidget, ctk.CTkEntry):
    """Entry con supporto tema automatico"""
    
    def __init__(self, master, **kwargs):
        # Rimuovi border_color se presente per gestirlo automaticamente
        kwargs.pop('border_color', None)
        
        ctk.CTkEntry.__init__(self, master, **kwargs)
        ThemedWidget.__init__(self)
    
    def _apply_theme_colors(self):
        colors = theme_manager.get_colors()
        self.configure(border_color=colors['border'])

class MessageDialog(ThemedWidget):
    """Dialog di messaggio con tema automatico"""
    
    def __init__(self, parent, title: str, message: str, type: str = "info"):
        self.parent = parent
        self.title = title
        self.message = message
        self.type = type
        
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("280x130")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centra il dialog
        self._center_dialog()
        
        # Crea contenuto
        self._create_content()
        
        ThemedWidget.__init__(self)
    
    def _center_dialog(self):
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    def _create_content(self):
        # Frame principale
        self.main_frame = ThemedFrame(self.dialog, style="surface")
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Icona e titolo
        header_frame = ThemedFrame(self.main_frame, style="surface")
        header_frame.pack(fill="x", pady=(0, 8))
        
        # Icona - usa configurazione
        icon_map = {
            "info": config_manager.get('icons.info', 'ℹ️'),
            "success": config_manager.get('icons.success', '✅'),
            "warning": config_manager.get('icons.warning', '⚠️'),
            "error": config_manager.get('icons.error', '❌')
        }
        
        icon_label = ThemedLabel(header_frame, text=icon_map.get(self.type, "ℹ️"))
        icon_label.configure(font=ctk.CTkFont(size=14))
        icon_label.pack(side="left", padx=(0, 8))
        
        title_label = ThemedLabel(header_frame, text=self.title, style="primary")
        title_label.configure(font=ctk.CTkFont(size=13, weight="bold"))
        title_label.pack(side="left")
        
        # Messaggio
        message_label = ThemedLabel(self.main_frame, text=self.message, style="secondary")
        message_label.configure(font=ctk.CTkFont(size=12))
        message_label.pack(pady=(0, 12))
        
        # Pulsante OK
        ok_button = ThemedButton(
            self.main_frame,
            text="OK",
            command=self.dialog.destroy,
            style="primary",
            width=70,
            height=28
        )
        ok_button.pack()

    def _apply_theme_colors(self):
        # I colori vengono gestiti automaticamente dai componenti figli
        pass
    
    def destroy(self):
        theme_manager.remove_observer(self._update_theme)
        self.dialog.destroy()

def show_message(parent, title: str, message: str, message_type: str = "info"):
    """
    Mostra un messaggio in un dialog personalizzato con testo formattato
    
    Args:
        parent: Widget genitore
        title: Titolo del dialog
        message: Messaggio da mostrare
        message_type: Tipo di messaggio ("info", "success", "warning", "error")
    """
    import customtkinter as ctk
    
    # Crea dialog
    dialog = ctk.CTkToplevel(parent)
    dialog.title(title)
    dialog.resizable(False, False)
    dialog.transient(parent)
    dialog.grab_set()
    
    # Dimensioni fisse più grandi per tutti i tipi di dialog
    if message_type in ["error", "warning"]:
        # Dialog di errore - dimensioni molto grandi
        dialog_width = 900
        dialog_height = 500
        font_size = 11
        title_font_size = 16
        icon_size = 40
        button_width = 150
        button_height = 50
        padding = 50
    else:
        # Dialog normali - dimensioni grandi
        dialog_width = 700
        dialog_height = 400
        font_size = 12
        title_font_size = 18
        icon_size = 32
        button_width = 120
        button_height = 45
        padding = 40
    
    # Imposta dimensioni fisse
    dialog.geometry(f"{dialog_width}x{dialog_height}")
    
    # Centra dialog
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (dialog_width // 2)
    y = (dialog.winfo_screenheight() // 2) - (dialog_height // 2)
    dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
    
    # Ottieni i colori del tema corrente
    colors = theme_manager.get_colors()
    
    # Configura i colori del dialog
    dialog.configure(fg_color=colors['background'])
    
    # Frame principale con padding generoso
    main_frame = ThemedFrame(dialog, style="surface")
    main_frame.pack(fill="both", expand=True, padx=padding, pady=padding)
    
    # Icona e colore basati sul tipo
    icons = {
        "info": "ℹ️",
        "success": "✅", 
        "warning": "⚠️",
        "error": "❌"
    }
    
    type_colors = {
        "info": "#3498db",
        "success": "#2ecc71",
        "warning": "#f39c12", 
        "error": "#e74c3c"
    }
    
    icon = icons.get(message_type, "ℹ️")
    type_color = type_colors.get(message_type, "#3498db")
    
    # Header con icona e titolo
    header_frame = ThemedFrame(main_frame, style="surface")
    header_frame.pack(fill="x", pady=(0, 30))
    
    # Icona
    icon_label = ThemedLabel(header_frame, text=icon, style="primary")
    icon_label.configure(font=ctk.CTkFont(size=icon_size))
    icon_label.pack(side="left", padx=(0, 25))
    
    # Titolo
    title_label = ThemedLabel(header_frame, text=title, style="primary")
    title_label.configure(
        font=ctk.CTkFont(size=title_font_size, weight="bold"),
        text_color=type_color
    )
    title_label.pack(side="left", fill="x", expand=True, anchor="w")
    
    # Messaggio - sempre usa textbox per migliore leggibilità
    message_frame = ThemedFrame(main_frame, style="surface")
    message_frame.pack(fill="both", expand=True, pady=(0, 30))
    
    # Calcola altezza del textbox in base alle dimensioni del dialog
    if message_type in ["error", "warning"]:
        textbox_height = 300  # Altezza fissa grande per errori
    else:
        textbox_height = 200  # Altezza fissa media per altri
    
    message_textbox = ctk.CTkTextbox(
        message_frame,
        font=ctk.CTkFont(size=font_size),
        wrap="word",
        height=textbox_height,
        fg_color=colors['secondary'],
        text_color=colors['text'],
        border_color=colors['border'],
        border_width=1
    )
    message_textbox.pack(fill="both", expand=True)
    
    # Formatta il messaggio per una migliore leggibilità
    formatted_message = message.strip()
    
    # Inserisci il messaggio
    message_textbox.insert("1.0", formatted_message)
    message_textbox.configure(state="disabled")
    
    # Pulsante OK
    button_frame = ThemedFrame(main_frame, style="surface")
    button_frame.pack(fill="x")
    
    ok_button = ThemedButton(
        button_frame,
        text="OK",
        command=dialog.destroy,
        style="primary",
        width=button_width,
        height=button_height
    )
    ok_button.configure(font=ctk.CTkFont(size=font_size + 1, weight="bold"))
    ok_button.pack(anchor="center")
    
    # Focus sul pulsante OK
    ok_button.focus()
    
    # Bind Enter e Escape
    dialog.bind("<Return>", lambda e: dialog.destroy())
    dialog.bind("<Escape>", lambda e: dialog.destroy())

def create_theme_toggle(parent):
    """Crea un toggle per cambiare tema"""
    import customtkinter as ctk
    
    def toggle_theme():
        # Usa il theme manager per cambiare tema
        new_mode = theme_manager.toggle_mode()
        
        # Aggiorna il testo del pulsante - usa configurazione
        button_text = (config_manager.get('dashboard.theme_toggle_light', '🌙 Tema Scuro') 
                      if new_mode == "light" 
                      else config_manager.get('dashboard.theme_toggle_dark', '☀️ Tema Chiaro'))
        toggle_button.configure(text=button_text)
    
    # Determina il testo iniziale del pulsante basato sulla modalità corrente
    current_mode = theme_manager.get_current_mode()
    button_text = (config_manager.get('dashboard.theme_toggle_light', '🌙 Tema Scuro') 
                  if current_mode == "light" 
                  else config_manager.get('dashboard.theme_toggle_dark', '☀️ Tema Chiaro'))
    
    toggle_button = ThemedButton(
        parent,
        text=button_text,
        command=toggle_theme,
        style="secondary",
        width=140,
        height=35
    )
    
    return toggle_button
