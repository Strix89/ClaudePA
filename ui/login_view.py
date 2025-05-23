import customtkinter as ctk
from typing import Callable
from pathlib import Path
from core.components import ThemedFrame, ThemedLabel, ThemedButton, ThemedEntry, show_message
from core.database import PasswordDatabase

class LoginView(ThemedFrame):
    """Vista per il login degli utenti"""
    
    def __init__(self, master, on_login_success: Callable, on_register_click: Callable = None):
        super().__init__(master, style="background")
        
        self.on_login_success = on_login_success
        self.on_register_click = on_register_click or (lambda: None)
        
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
        
        # Logo/Titolo
        title_label = ThemedLabel(main_container, text="🔐 Password Manager", style="primary")
        title_label.configure(font=ctk.CTkFont(size=32, weight="bold"))
        title_label.pack(pady=(40, 20))
        
        subtitle_label = ThemedLabel(main_container, text="Accedi al tuo account", style="secondary")
        subtitle_label.configure(font=ctk.CTkFont(size=14))
        subtitle_label.pack(pady=(0, 30))
        
        # Form di login
        form_frame = ThemedFrame(main_container, style="surface")
        form_frame.pack(padx=40, pady=(0, 40))
        
        # Username
        username_label = ThemedLabel(form_frame, text="Nome Utente:", style="primary")
        username_label.pack(anchor="w", pady=(0, 5))
        
        self.username_entry = ThemedEntry(
            form_frame,
            placeholder_text="Inserisci il tuo nome utente",
            width=300,
            height=40
        )
        self.username_entry.pack(pady=(0, 20))
        
        # Password
        password_label = ThemedLabel(form_frame, text="Password Master:", style="primary")
        password_label.pack(anchor="w", pady=(0, 5))
        
        self.password_entry = ThemedEntry(
            form_frame,
            placeholder_text="Inserisci la tua password master",
            show="•",
            width=300,
            height=40
        )
        self.password_entry.pack(pady=(0, 30))
        
        # Pulsante login
        login_button = ThemedButton(
            form_frame,
            text="Accedi",
            command=self._handle_login,
            style="primary",
            width=300,
            height=45
        )
        login_button.pack(pady=(0, 20))
        
        # Link alla registrazione
        if self.on_register_click:
            register_text = ThemedLabel(form_frame, text="Non hai un account?", style="secondary")
            register_text.pack(pady=(10, 5))
            
            register_link = ThemedButton(
                form_frame,
                text="Crea nuovo account",
                command=self.on_register_click,
                style="secondary",
                width=200,
                height=35
            )
            register_link.pack()
        
        # Focus iniziale
        self.username_entry.focus()
        
        # Bind Enter key sui singoli widget invece di bind_all
        self.username_entry.bind("<Return>", lambda e: self._handle_login())
        self.password_entry.bind("<Return>", lambda e: self._handle_login())

    def _handle_login(self):
        """Gestisce il processo di login"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            show_message(self, "Errore", "Inserisci nome utente e password", "error")
            return
        
        if not self.database:
            show_message(self, "Errore", "Database non disponibile", "error")
            return
        
        try:
            # Debug: verifica stato file utente
            debug_info = self.database.debug_user_file(username)
            print(f"Debug login - {debug_info}")
            
            result = self.database.login(username, password)
            
            # Verifica che il risultato sia una tupla
            if result is None:
                show_message(self, "Errore di Login", "Errore interno del database", "error")
                return
            
            if not isinstance(result, tuple) or len(result) != 2:
                show_message(self, "Errore di Login", "Risposta del database non valida", "error")
                return
            
            success, message = result
            
            if success:
                print(f"Login riuscito nel LoginView per: {username}")
                self.on_login_success()
            else:
                print(f"Login fallito per {username}: {message}")
                show_message(self, "Errore di Login", message, "error")
                
        except Exception as e:
            print(f"Errore durante il login: {e}")
            show_message(self, "Errore di Login", f"Errore durante il login: {str(e)}", "error")

    def clear_form(self):
        """Pulisce il form"""
        self.username_entry.delete(0, "end")
        self.password_entry.delete(0, "end")
