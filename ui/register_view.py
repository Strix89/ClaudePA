import customtkinter as ctk
from typing import Callable
from pathlib import Path
from core.components import ThemedFrame, ThemedLabel, ThemedButton, ThemedEntry, show_message
from core.database import PasswordDatabase

class RegisterView(ThemedFrame):
    """Vista per la registrazione di nuovi utenti"""
    
    def __init__(self, master, on_register_success: Callable, on_back_to_login: Callable = None):
        super().__init__(master, style="background")
        
        self.on_register_success = on_register_success
        self.on_back_to_login = on_back_to_login or (lambda: None)
        
        # Inizializza database
        data_dir = Path(__file__).parent.parent / "data"
        self.database = PasswordDatabase(str(data_dir))
        
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
        
        # Titolo
        title_label = ThemedLabel(main_container, text="Crea Nuovo Account", style="primary")
        title_label.configure(font=ctk.CTkFont(size=28, weight="bold"))
        title_label.pack(pady=(40, 30))
        
        # Form di registrazione
        form_frame = ThemedFrame(main_container, style="surface")
        form_frame.pack(padx=40, pady=(0, 40))
        
        # Username
        username_label = ThemedLabel(form_frame, text="Nome Utente:", style="primary")
        username_label.pack(anchor="w", pady=(0, 5))
        
        self.username_entry = ThemedEntry(
            form_frame,
            placeholder_text="Inserisci un nome utente",
            width=300,
            height=40
        )
        self.username_entry.pack(pady=(0, 20))
        
        # Password
        password_label = ThemedLabel(form_frame, text="Password Master:", style="primary")
        password_label.pack(anchor="w", pady=(0, 5))
        
        self.password_entry = ThemedEntry(
            form_frame,
            placeholder_text="Inserisci una password sicura",
            show="•",
            width=300,
            height=40
        )
        self.password_entry.pack(pady=(0, 20))
        
        # Conferma password
        confirm_label = ThemedLabel(form_frame, text="Conferma Password:", style="primary")
        confirm_label.pack(anchor="w", pady=(0, 5))
        
        self.confirm_entry = ThemedEntry(
            form_frame,
            placeholder_text="Ripeti la password",
            show="•",
            width=300,
            height=40
        )
        self.confirm_entry.pack(pady=(0, 30))
        
        # Pulsante registrazione
        register_button = ThemedButton(
            form_frame,
            text="Crea Account",
            command=self._handle_register,
            style="primary",
            width=300,
            height=45
        )
        register_button.pack(pady=(0, 20))
        
        # Link al login
        if self.on_back_to_login:
            login_link = ThemedButton(
                form_frame,
                text="← Torna al Login",
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
        """Gestisce il processo di registrazione"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        confirm_password = self.confirm_entry.get()
        
        if not username or not password:
            show_message(self, "Errore", "Inserisci nome utente e password", "error")
            return
        
        if password != confirm_password:
            show_message(self, "Errore", "Le password non coincidono", "error")
            return
        
        if len(password) < 8:
            show_message(self, "Errore", "La password deve essere di almeno 8 caratteri", "error")
            return
        
        try:
            # Registra l'utente
            result = self.database.register_user(username, password)
            
            # Verifica che il risultato sia una tupla
            if result is None:
                show_message(self, "Errore", "Errore interno del database", "error")
                return
            
            if not isinstance(result, tuple) or len(result) != 2:
                show_message(self, "Errore", "Risposta del database non valida", "error")
                return
            
            success, message = result
            
            if success:
                show_message(self, "Successo", "Account creato con successo", "success")
                self.on_register_success()
            else:
                show_message(self, "Errore", message, "error")
                
        except Exception as e:
            print(f"Errore durante la registrazione: {e}")
            show_message(self, "Errore", f"Errore durante la registrazione: {str(e)}", "error")
    
    def clear_form(self):
        """Pulisce il form"""
        self.username_entry.delete(0, "end")
        self.password_entry.delete(0, "end")
        self.confirm_entry.delete(0, "end")
