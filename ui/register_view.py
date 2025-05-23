import customtkinter as ctk
from typing import Callable
from pathlib import Path
from core.components import ThemedFrame, ThemedLabel, ThemedButton, ThemedEntry, show_message
from core.database import PasswordDatabase
from core.config import config_manager

class RegisterView(ThemedFrame):
    """Vista per la registrazione di nuovi utenti"""
    
    def __init__(self, master, on_register_success: Callable, on_back_to_login: Callable = None):
        super().__init__(master, style="background")
        
        self.on_register_success = on_register_success
        self.on_back_to_login = on_back_to_login or (lambda: None)
        
        # Il database sarà assegnato dall'app principale
        self.database = None
        
        self._create_ui()

    def _create_ui(self):
        # Toggle tema in alto a destra
        theme_frame = ThemedFrame(self, style="background")
        theme_frame.pack(fill="x", padx=20, pady=(10, 0))
        
        from core.components import create_theme_toggle
        theme_toggle = create_theme_toggle(theme_frame)
        theme_toggle.pack(side="right")
        
        # Container principale centrato
        main_container = ThemedFrame(self, style="surface")
        main_container.place(relx=0.5, rely=0.5, anchor="center")
        
        # Titolo - usa configurazione
        title_text = config_manager.get('register.title', 'Crea Nuovo Account')
        title_font = config_manager.get_font_config('title')
        
        title_label = ThemedLabel(main_container, text=title_text, style="primary")
        title_label.configure(font=ctk.CTkFont(size=title_font['size'], weight=title_font['weight']))
        title_label.pack(pady=(40, 30))
        
        # Form di registrazione
        form_frame = ThemedFrame(main_container, style="surface")
        form_frame.pack(padx=40, pady=(0, 40))
        
        # Username - usa configurazione
        username_label_text = config_manager.get('register.username_label', 'Nome Utente:')
        username_placeholder = config_manager.get('register.username_placeholder', 'Inserisci un nome utente')
        
        username_label = ThemedLabel(form_frame, text=username_label_text, style="primary")
        username_label.pack(anchor="w", pady=(0, 5))
        
        self.username_entry = ThemedEntry(
            form_frame,
            placeholder_text=username_placeholder,
            width=300,
            height=40
        )
        self.username_entry.pack(pady=(0, 20))
        
        # Password - usa configurazione
        password_label_text = config_manager.get('register.password_label', 'Password Master:')
        password_placeholder = config_manager.get('register.password_placeholder', 'Inserisci una password sicura')
        
        password_label = ThemedLabel(form_frame, text=password_label_text, style="primary")
        password_label.pack(anchor="w", pady=(0, 5))
        
        self.password_entry = ThemedEntry(
            form_frame,
            placeholder_text=password_placeholder,
            show="•",
            width=300,
            height=40
        )
        self.password_entry.pack(pady=(0, 20))
        
        # Conferma password - usa configurazione
        confirm_label_text = config_manager.get('register.confirm_label', 'Conferma Password:')
        confirm_placeholder = config_manager.get('register.confirm_placeholder', 'Ripeti la password')
        
        confirm_label = ThemedLabel(form_frame, text=confirm_label_text, style="primary")
        confirm_label.pack(anchor="w", pady=(0, 5))
        
        self.confirm_entry = ThemedEntry(
            form_frame,
            placeholder_text=confirm_placeholder,
            show="•",
            width=300,
            height=40
        )
        self.confirm_entry.pack(pady=(0, 30))
        
        # Pulsante registrazione - usa configurazione
        register_button_text = config_manager.get('register.register_button', 'Crea Account')
        
        register_button = ThemedButton(
            form_frame,
            text=register_button_text,
            command=self._handle_register,
            style="primary",
            width=300,
            height=45
        )
        register_button.pack(pady=(0, 20))
        
        # Link al login - usa configurazione
        if self.on_back_to_login:
            back_button_text = config_manager.get('register.back_button', '← Torna al Login')
            
            login_link = ThemedButton(
                form_frame,
                text=back_button_text,
                command=self.on_back_to_login,
                style="secondary",
                width=200,
                height=35
            )
            login_link.pack()
        
        # Focus iniziale
        self.username_entry.focus()
        
        # Bind Enter key
        self.username_entry.bind("<Return>", lambda e: self._handle_register())
        self.password_entry.bind("<Return>", lambda e: self._handle_register())
        self.confirm_entry.bind("<Return>", lambda e: self._handle_register())
    
    def _handle_register(self):
        """Gestisce il processo di registrazione con validazione completa"""
        # Recupera e pulisce i dati inseriti dall'utente
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        confirm_password = self.confirm_entry.get()
        
        # Validazione dei campi obbligatori - usa messaggi dalla configurazione
        if not username or not password:
            message = config_manager.get('messages.validation.empty_fields', 'Inserisci nome utente e password')
            show_message(self, "Errore", message, "error")
            return
        
        # Validazione lunghezza username (minimo 3 caratteri)
        if len(username) < 3:
            message = config_manager.get('messages.validation.username_min_length', 'Il nome utente deve essere di almeno 3 caratteri')
            show_message(self, "Errore", message, "error")
            return
        
        # Validazione conferma password
        if password != confirm_password:
            message = config_manager.get('messages.validation.password_mismatch', 'Le password non coincidono')
            show_message(self, "Errore", message, "error")
            return
        
        # Validazione sicurezza password (minimo 8 caratteri)
        if len(password) < 8:
            message = config_manager.get('messages.validation.password_min_length', 'La password deve essere di almeno 8 caratteri')
            show_message(self, "Errore", message, "error")
            return
        
        # Verifica disponibilità del database
        if not self.database:
            message = config_manager.get('messages.validation.database_unavailable', 'Database non disponibile')
            show_message(self, "Errore", message, "error")
            return
        
        try:
            # Tenta la registrazione nel database
            success, message = self.database.register_user(username, password)
            
            if success:
                # Registrazione completata con successo - usa messaggio dalla configurazione
                success_message = config_manager.format_message('messages.success.registration_complete', username=username)
                show_message(self, "Successo", success_message, "success")
                # Pulisce il form e ritorna al login
                self.clear_form()
                self.on_register_success()
            else:
                # Mostra errore specifico dalla registrazione - usa messaggio dalla configurazione
                error_message = config_manager.format_message('messages.errors.registration_failed', message=message)
                show_message(self, "Errore", error_message, "error")
                
        except Exception as e:
            # Gestisce errori imprevisti durante la registrazione
            print(f"ERRORE REGISTRAZIONE: {username} - {str(e)}")
            error_message = config_manager.format_message('messages.errors.database_error', error=str(e))
            show_message(self, "Errore", error_message, "error")
    
    def clear_form(self):
        """Pulisce tutti i campi del form di registrazione"""
        self.username_entry.delete(0, "end")
        self.password_entry.delete(0, "end")
        self.confirm_entry.delete(0, "end")
