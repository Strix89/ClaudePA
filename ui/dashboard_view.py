import customtkinter as ctk
import secrets
import string
from typing import Callable, Optional, Dict, Any
from core.components import ThemedFrame, ThemedLabel, ThemedButton, ThemedEntry, show_message
from core.database import PasswordDatabase
from core.password_strength import PasswordValidator, SecurePasswordGenerator

class PasswordStrengthIndicator(ThemedFrame):
    """
    Indicatore visivo della forza della password con barra di progresso colorata
    Analizza in tempo reale la sicurezza della password inserita
    """
    
    def __init__(self, master):
        super().__init__(master, style="surface")
        self.validator = PasswordValidator()
        self._create_ui()
    
    def _create_ui(self):
        """Crea l'interfaccia dell'indicatore di forza password"""
        # Label descrittiva per l'indicatore
        self.strength_label = ThemedLabel(self, text="Forza Password:", style="primary")
        self.strength_label.configure(font=ctk.CTkFont(size=12, weight="bold"))
        self.strength_label.pack(anchor="w", pady=(0, 5))
        
        # Container per barra di progresso e percentuale
        progress_frame = ThemedFrame(self, style="surface")
        progress_frame.pack(fill="x", pady=(0, 5))
        
        # Barra di progresso che cambia colore in base alla forza
        self.progress_bar = ctk.CTkProgressBar(progress_frame, height=12)
        self.progress_bar.pack(fill="x", side="left", expand=True)
        self.progress_bar.set(0)  # Inizializza a 0%
        
        # Label che mostra la percentuale numerica
        self.score_label = ThemedLabel(progress_frame, text="0%", style="secondary")
        self.score_label.configure(font=ctk.CTkFont(size=11))
        self.score_label.pack(side="right", padx=(10, 0))
        
        # Label descrizione forza
        self.description_label = ThemedLabel(self, text="Nessuna password", style="secondary")
        self.description_label.configure(font=ctk.CTkFont(size=11))
        self.description_label.pack(anchor="w", pady=(0, 10))
    
    def update_strength(self, password: str):
        """Aggiorna l'indicatore con una nuova password"""
        analysis = self.validator.analyze_password(password)
        
        # Aggiorna barra di progresso
        progress = analysis.score / 100
        self.progress_bar.set(progress)
        self.progress_bar.configure(progress_color=analysis.color)
        
        # Aggiorna percentuale
        self.score_label.configure(text=f"{analysis.score}%")
        
        # Aggiorna descrizione
        strength_names = {
            0: "Molto Debole",
            1: "Debole", 
            2: "Discreta",
            3: "Buona",
            4: "Forte",
            5: "Molto Forte"
        }
        
        description = strength_names.get(analysis.strength.value, "Sconosciuta")
        self.description_label.configure(text=f"Forza: {description}")

class PasswordListItem(ThemedFrame):
    """Item della lista password"""
    
    def __init__(self, master, password_data: Dict, on_select: Callable):
        super().__init__(master, style="surface")
        
        self.password_data = password_data
        self.on_select = on_select
        
        self._create_ui()
        self._setup_bindings()
    
    def _create_ui(self):
        self.configure(height=60, corner_radius=8)
        
        # Site name
        site_label = ThemedLabel(self, text=self.password_data["site"], style="primary")
        site_label.configure(font=ctk.CTkFont(size=14, weight="bold"))
        site_label.pack(anchor="w", padx=15, pady=(8, 2))
        
        # Username
        username_label = ThemedLabel(self, text=self.password_data["username"], style="secondary")
        username_label.configure(font=ctk.CTkFont(size=12))
        username_label.pack(anchor="w", padx=15, pady=(0, 8))
    
    def _setup_bindings(self):
        """Setup dei binding per il click"""
        self.bind("<Button-1>", lambda e: self.on_select(self.password_data))
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        
        for child in self.winfo_children():
            child.bind("<Button-1>", lambda e: self.on_select(self.password_data))
    
    def _on_enter(self, event):
        from core.theme import theme_manager
        colors = theme_manager.get_colors()
        self.configure(fg_color=colors['hover'])
    
    def _on_leave(self, event):
        from core.theme import theme_manager
        colors = theme_manager.get_colors()
        self.configure(fg_color=colors['surface'])

class PasswordEditor(ThemedFrame):
    """Editor per le password"""
    
    def __init__(self, master, database: PasswordDatabase, on_save: Callable):
        super().__init__(master, style="surface")
        
        self.database = database
        self.on_save = on_save
        self.current_password: Optional[Dict] = None
        self.edit_mode = False
        self.password_generator = SecurePasswordGenerator()
        
        self._create_ui()
        self.pack_forget()  # Nascondi inizialmente
    
    def _create_ui(self):
        # Titolo
        self.title_label = ThemedLabel(self, text="Nuova Password", style="primary")
        self.title_label.configure(font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.pack(pady=(20, 30))
        
        # Form
        form_frame = ThemedFrame(self, style="surface")
        form_frame.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        
        # Sito
        site_label = ThemedLabel(form_frame, text="Sito/App:", style="primary")
        site_label.pack(anchor="w", pady=(0, 5))
        
        self.site_entry = ThemedEntry(
            form_frame,
            placeholder_text="es. Facebook, Gmail, Amazon",
            height=40
        )
        self.site_entry.pack(fill="x", pady=(0, 15))
        
        # Username
        username_label = ThemedLabel(form_frame, text="Username/Email:", style="primary")
        username_label.pack(anchor="w", pady=(0, 5))
        
        self.username_entry = ThemedEntry(
            form_frame,
            placeholder_text="es. mario.rossi@gmail.com",
            height=40
        )
        self.username_entry.pack(fill="x", pady=(0, 15))
        
        # Password con pulsanti
        password_frame = ThemedFrame(form_frame, style="surface")
        password_frame.pack(fill="x", pady=(0, 5))
        
        password_label = ThemedLabel(password_frame, text="Password:", style="primary")
        password_label.pack(anchor="w", pady=(0, 5))
        
        password_input_frame = ThemedFrame(password_frame, style="surface")
        password_input_frame.pack(fill="x", pady=(0, 5))
        
        self.password_entry = ThemedEntry(
            password_input_frame,
            placeholder_text="Password",
            show="•",
            height=40
        )
        self.password_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # Bind per aggiornamento tempo reale della forza
        self.password_entry.bind("<KeyRelease>", self._on_password_change)
        
        # Pulsanti password
        buttons_frame = ThemedFrame(password_input_frame, style="surface")
        buttons_frame.pack(side="right")
        
        # Menu a tendina per tipo di generazione
        self.gen_type_menu = ctk.CTkOptionMenu(
            buttons_frame,
            values=["Forte (16 car.)", "Forte (20 car.)", "Memorabile", "Personalizza"],
            command=self._on_gen_type_change,
            width=120,
            height=40
        )
        self.gen_type_menu.pack(side="left", padx=(0, 5))
        self.gen_type_menu.set("Forte (16 car.)")
        
        generate_button = ThemedButton(
            buttons_frame,
            text="🎲 Genera",
            command=self._generate_password,
            style="secondary",
            width=100,
            height=40
        )
        generate_button.pack(side="left", padx=(0, 5))
        
        # Pulsante suggerimenti
        self.tips_button = ThemedButton(
            buttons_frame,
            text="💡 Consigli",
            command=self._show_password_tips,
            style="secondary",
            width=100,
            height=40
        )
        self.tips_button.pack(side="left", padx=(0, 5))
        
        # Crea il pulsante copia ma non lo mostra inizialmente
        self.copy_button = ThemedButton(
            buttons_frame,
            text="📋 Copia",
            command=self._copy_password,
            style="secondary",
            width=80,
            height=40
        )
        # Non fare pack inizialmente
        
        # Show password checkbox
        self.show_password_var = ctk.BooleanVar()
        show_password_cb = ctk.CTkCheckBox(
            password_frame,
            text="Mostra password",
            variable=self.show_password_var,
            command=self._toggle_password_visibility
        )
        show_password_cb.pack(anchor="w", pady=(5, 15))
        
        # Indicatore forza password
        self.strength_indicator = PasswordStrengthIndicator(password_frame)
        self.strength_indicator.pack(fill="x", pady=(0, 15))
        
        # Note
        notes_label = ThemedLabel(form_frame, text="Note (opzionale):", style="primary")
        notes_label.pack(anchor="w", pady=(0, 5))
        
        self.notes_text = ctk.CTkTextbox(form_frame, height=80)
        self.notes_text.pack(fill="x", pady=(0, 20))
        
        # Pulsanti azione
        self.action_frame = ThemedFrame(form_frame, style="surface")
        self.action_frame.pack(fill="x", pady=10)
        
        # Frame per pulsanti principali (sempre visibili)
        main_buttons_frame = ThemedFrame(self.action_frame, style="surface")
        main_buttons_frame.pack(fill="x", pady=(0, 5))
        
        self.save_button = ThemedButton(
            main_buttons_frame,
            text="💾 Salva",
            command=self._save_password,
            style="primary",
            height=40
        )
        self.save_button.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        cancel_button = ThemedButton(
            main_buttons_frame,
            text="❌ Annulla",
            command=self._cancel_edit,
            style="secondary",
            height=40
        )
        cancel_button.pack(side="right", fill="x", expand=True, padx=(5, 0))
        
        # Frame per pulsanti secondari (mostrati solo in edit mode)
        self.secondary_buttons_frame = ThemedFrame(self.action_frame, style="surface")
        # Non fare pack inizialmente
        
        # Crea il pulsante elimina nel frame secondario
        self.delete_button = ThemedButton(
            self.secondary_buttons_frame,
            text="🗑️ Elimina Password",
            command=self._delete_password,
            style="danger",
            height=40
        )
        self.delete_button.pack(fill="x")
        
        # Crea il pulsante copia nel frame dei pulsanti password
        self.copy_button = ThemedButton(
            buttons_frame,
            text="📋",
            command=self._copy_password,
            style="secondary",
            width=50,
            height=40
        )
        # Non fare pack inizialmente
    
    def _on_password_change(self, event=None):
        """Callback per aggiornamento in tempo reale della forza password"""
        password = self.password_entry.get()
        self.strength_indicator.update_strength(password)
    
    def _on_gen_type_change(self, value):
        """Callback per cambio tipo di generazione"""
        pass  # Solo per feedback visivo del menu
    
    def _show_password_tips(self):
        """Mostra dialog con consigli per password sicure"""
        tips_dialog = ctk.CTkToplevel(self)
        tips_dialog.title("Consigli per Password Sicure")
        tips_dialog.geometry("800x600")  # Dimensioni fisse più grandi
        tips_dialog.resizable(False, False)
        tips_dialog.transient(self)
        tips_dialog.grab_set()
        
        # Centra dialog
        tips_dialog.update_idletasks()
        width = tips_dialog.winfo_width()
        height = tips_dialog.winfo_height()
        x = (tips_dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (tips_dialog.winfo_screenheight() // 2) - (height // 2)
        tips_dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        frame = ThemedFrame(tips_dialog, style="surface")
        frame.pack(fill="both", expand=True, padx=40, pady=40)
        
        title = ThemedLabel(frame, text="🔒 Come Creare Password Sicure", style="primary")
        title.configure(font=ctk.CTkFont(size=16, weight="bold"))
        title.pack(pady=(0, 25))
        
        tips_text = """✅ CARATTERISTICHE ESSENZIALI:
• Almeno 12-16 caratteri di lunghezza
• Combinazione di maiuscole, minuscole, numeri e simboli
• Non utilizzare informazioni personali (nome, data di nascita)
• Evitare parole del dizionario

❌ DA EVITARE ASSOLUTAMENTE:
• Password comuni come "password", "123456", "qwerty"
• Date di nascita o nomi di familiari/animali
• Sequenze consecutive come "abc123" o "654321"
• La stessa password per più account

💡 STRATEGIE CONSIGLIATE:
• Utilizza frasi facili da ricordare e trasformale
• Sostituisci alcune lettere con numeri o simboli
• Usa il nostro generatore automatico
• Crea una "base" e personalizzala per ogni sito

🔐 ESEMPIO PRATICO:
Frase: "Mi piace la pizza margherita del 2024"
Password: "M1P14c3P1zz4M@rgh3r1t@24!"

🛡️ SICUREZZA AGGIUNTIVA:
• Cambia le password importanti ogni 6-12 mesi
• Attiva l'autenticazione a due fattori quando possibile
• Non condividere mai le tue password
• Utilizza questo password manager per tutto"""
        
        tips_textbox = ctk.CTkTextbox(
            frame,
            font=ctk.CTkFont(size=11),  # Font più piccolo
            height=400,  # Altezza fissa
            wrap="word"
        )
        tips_textbox.pack(fill="both", expand=True, pady=(0, 25))
        tips_textbox.insert("1.0", tips_text)
        tips_textbox.configure(state="disabled")
        
        close_button = ThemedButton(
            frame,
            text="Ho Capito",
            command=tips_dialog.destroy,
            style="primary",
            width=150,
            height=45
        )
        close_button.pack()
    
    def _toggle_password_visibility(self):
        """Mostra/nasconde la password"""
        show = "" if self.show_password_var.get() else "•"
        self.password_entry.configure(show=show)
    
    def _generate_password(self):
        """Genera una password basata sul tipo selezionato"""
        gen_type = self.gen_type_menu.get()
        
        try:
            if gen_type == "Forte (16 car.)":
                password = self.password_generator.generate_strong_password(16, True)
            elif gen_type == "Forte (20 car.)":
                password = self.password_generator.generate_strong_password(20, True)
            elif gen_type == "Memorabile":
                password = self.password_generator.generate_memorable_password()
            elif gen_type == "Personalizza":
                self._show_custom_generator()
                return
            else:
                password = self.password_generator.generate_strong_password(16, True)
            
            self.password_entry.delete(0, "end")
            self.password_entry.insert(0, password)
            
            # Mostra temporaneamente la password
            self.show_password_var.set(True)
            self._toggle_password_visibility()
            
            # Aggiorna indicatore forza
            self._on_password_change()
            
            show_message(self, "Password Generata", f"Password {gen_type.lower()} generata con successo!", "success")
            
        except Exception as e:
            show_message(self, "Errore", f"Errore nella generazione: {str(e)}", "error")
    
    def _show_custom_generator(self):
        """Mostra dialog per generazione personalizzata"""
        custom_dialog = ctk.CTkToplevel(self)
        custom_dialog.title("Generatore Personalizzato")
        custom_dialog.geometry("500x400")  # Dimensioni fisse più grandi
        custom_dialog.resizable(False, False)
        custom_dialog.transient(self)
        custom_dialog.grab_set()
        
        # Centra dialog
        custom_dialog.update_idletasks()
        width = custom_dialog.winfo_width()
        height = custom_dialog.winfo_height()
        x = (custom_dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (custom_dialog.winfo_screenheight() // 2) - (height // 2)
        custom_dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        frame = ThemedFrame(custom_dialog, style="surface")
        frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        title = ThemedLabel(frame, text="Personalizza Password", style="primary")
        title.configure(font=ctk.CTkFont(size=14, weight="bold"))
        title.pack(pady=(0, 25))
        
        # Lunghezza
        length_frame = ThemedFrame(frame, style="surface")
        length_frame.pack(fill="x", pady=10)
        
        length_label = ThemedLabel(length_frame, text="Lunghezza:", style="primary")
        length_label.configure(font=ctk.CTkFont(size=11))
        length_label.pack(side="left")
        
        length_var = ctk.IntVar(value=16)
        length_slider = ctk.CTkSlider(length_frame, from_=8, to=50, number_of_steps=42, variable=length_var, height=20)
        length_slider.pack(side="right", fill="x", expand=True, padx=(15, 0))
        
        length_value_label = ThemedLabel(length_frame, text="16", style="secondary")
        length_value_label.configure(font=ctk.CTkFont(size=11))
        length_value_label.pack(side="right", padx=(10, 0))
        
        def update_length_label(value):
            length_value_label.configure(text=str(int(value)))
        
        length_slider.configure(command=update_length_label)
        
        # Opzioni caratteri
        options_frame = ThemedFrame(frame, style="surface")
        options_frame.pack(fill="x", pady=15)
        
        uppercase_var = ctk.BooleanVar(value=True)
        lowercase_var = ctk.BooleanVar(value=True)
        numbers_var = ctk.BooleanVar(value=True)
        symbols_var = ctk.BooleanVar(value=True)
        
        ctk.CTkCheckBox(options_frame, text="Maiuscole (A-Z)", variable=uppercase_var, height=20, font=ctk.CTkFont(size=11)).pack(anchor="w", pady=3)
        ctk.CTkCheckBox(options_frame, text="Minuscole (a-z)", variable=lowercase_var, height=20, font=ctk.CTkFont(size=11)).pack(anchor="w", pady=3)
        ctk.CTkCheckBox(options_frame, text="Numeri (0-9)", variable=numbers_var, height=20, font=ctk.CTkFont(size=11)).pack(anchor="w", pady=3)
        ctk.CTkCheckBox(options_frame, text="Simboli (!@#$...)", variable=symbols_var, height=20, font=ctk.CTkFont(size=11)).pack(anchor="w", pady=3)
        
        # Pulsanti
        buttons_frame = ThemedFrame(frame, style="surface")
        buttons_frame.pack(fill="x", pady=20)
        
        def generate_custom():
            length = int(length_var.get())
            include_symbols = symbols_var.get()
            
            # Verifica che almeno un'opzione sia selezionata
            if not any([uppercase_var.get(), lowercase_var.get(), numbers_var.get(), symbols_var.get()]):
                show_message(custom_dialog, "Errore", "Seleziona almeno un tipo di carattere", "error")
                return
            
            password = self.password_generator.generate_strong_password(length, include_symbols)
            
            self.password_entry.delete(0, "end")
            self.password_entry.insert(0, password)
            
            self.show_password_var.set(True)
            self._toggle_password_visibility()
            self._on_password_change()
            
            custom_dialog.destroy()
            show_message(self, "Password Generata", "Password personalizzata generata!", "success")
        
        generate_btn = ThemedButton(
            buttons_frame,
            text="Genera",
            command=generate_custom,
            style="primary",
            width=120,
            height=40
        )
        generate_btn.pack(side="left", padx=5)
        
        cancel_btn = ThemedButton(
            buttons_frame,
            text="Annulla",
            command=custom_dialog.destroy,
            style="secondary",
            width=120,
            height=40
        )
        cancel_btn.pack(side="right", padx=5)
    
    def _copy_password(self):
        """Copia la password negli appunti"""
        password = self.password_entry.get()
        if password:
            self.clipboard_clear()
            self.clipboard_append(password)
            show_message(self, "Copiata", "Password copiata negli appunti", "success")
    
    def _save_password(self):
        """Salva la password"""
        site = self.site_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        notes = self.notes_text.get("1.0", "end-1c").strip()
        
        if not site or not username or not password:
            show_message(self, "Errore", "Compila i campi obbligatori", "error")
            return
        
        success, message = self.database.add_password(site, username, password, notes)
        
        if success:
            action = "aggiornata" if self.edit_mode else "salvata"
            show_message(self, "Successo", f"Password {action} con successo", "success")
            self._clear_form_and_hide()
            self.on_save()
        else:
            show_message(self, "Errore", message, "error")
    
    def _delete_password(self):
        """Elimina la password corrente"""
        if not self.current_password:
            return
        
        # Dialog di conferma con dimensioni fisse
        confirm_dialog = ctk.CTkToplevel(self)
        confirm_dialog.title("Conferma Eliminazione")
        confirm_dialog.geometry("600x350")  # Dimensioni fisse
        confirm_dialog.resizable(False, False)
        confirm_dialog.transient(self)
        confirm_dialog.grab_set()
        
        # Centra dialog
        confirm_dialog.update_idletasks()
        width = confirm_dialog.winfo_width()
        height = confirm_dialog.winfo_height()
        x = (confirm_dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (confirm_dialog.winfo_screenheight() // 2) - (height // 2)
        confirm_dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        frame = ThemedFrame(confirm_dialog, style="surface")
        frame.pack(fill="both", expand=True, padx=40, pady=40)
        
        # Icona di avvertimento
        warning_icon = ThemedLabel(frame, text="⚠️", style="primary")
        warning_icon.configure(font=ctk.CTkFont(size=48))
        warning_icon.pack(pady=(0, 20))
        
        # Messaggio in textbox per coerenza
        message_text = f"""Sei sicuro di voler eliminare questa password?

🌐 Sito: {self.current_password['site']}
👤 Username: {self.current_password['username']}

⚠️ Questa operazione non può essere annullata!"""
        
        message_textbox = ctk.CTkTextbox(
            frame,
            font=ctk.CTkFont(size=12),
            wrap="word",
            height=150
        )
        message_textbox.pack(fill="x", pady=(0, 30))
        message_textbox.insert("1.0", message_text)
        message_textbox.configure(state="disabled")
        
        buttons_frame = ThemedFrame(frame, style="surface")
        buttons_frame.pack(fill="x")
        
        cancel_btn = ThemedButton(
            buttons_frame,
            text="❌ Annulla",
            command=confirm_dialog.destroy,
            style="secondary",
            width=140,
            height=45
        )
        cancel_btn.pack(side="left")
        
        delete_btn = ThemedButton(
            buttons_frame,
            text="🗑️ Elimina",
            command=lambda: self._confirm_delete(confirm_dialog),
            style="danger",
            width=140,
            height=45
        )
        delete_btn.pack(side="right")
    
    def _confirm_delete(self, dialog):
        """Conferma ed esegue l'eliminazione"""
        dialog.destroy()
        
        if not self.current_password:
            return
        
        success, message = self.database.delete_password(
            self.current_password["site"],
            self.current_password["username"]
        )
        
        if success:
            show_message(self, "Successo", "Password eliminata con successo", "success")
            self._clear_form_and_hide()
            self.on_save()
        else:
            show_message(self, "Errore", message, "error")
    
    def _cancel_edit(self):
        """Annulla la modifica"""
        try:
            self._clear_form_and_hide()
        except Exception as e:
            print(f"Errore durante annullamento: {e}")
            # Forza il ritorno alla vista welcome
            try:
                self.pack_forget()
                if hasattr(self.master, 'master') and hasattr(self.master.master, '_show_welcome'):
                    self.master.master._show_welcome()
            except:
                pass

    def _clear_form_and_hide(self):
        """Pulisce il form e nasconde l'editor"""
        try:
            self._clear_form()
            self.pack_forget()
            # Rimostra il messaggio di benvenuto
            if hasattr(self.master, 'master') and hasattr(self.master.master, '_show_welcome'):
                try:
                    self.master.master._show_welcome()
                except:
                    pass
        except Exception as e:
            print(f"Errore durante pulizia form: {e}")
            # Forza la chiusura comunque
            try:
                self.pack_forget()
            except:
                pass

    def _clear_form(self):
        """Pulisce il form"""
        try:
            if hasattr(self, 'site_entry') and self.site_entry.winfo_exists():
                self.site_entry.delete(0, "end")
            if hasattr(self, 'username_entry') and self.username_entry.winfo_exists():
                self.username_entry.delete(0, "end")
            if hasattr(self, 'password_entry') and self.password_entry.winfo_exists():
                self.password_entry.delete(0, "end")
            if hasattr(self, 'notes_text') and self.notes_text.winfo_exists():
                self.notes_text.delete("1.0", "end")
            
            if hasattr(self, 'show_password_var'):
                self.show_password_var.set(False)
                self._toggle_password_visibility()
            
            self.current_password = None
            self.edit_mode = False
            
            if hasattr(self, 'strength_indicator'):
                self.strength_indicator.update_strength("")
            
            # Nascondi pulsanti aggiuntivi
            try:
                if hasattr(self, 'copy_button'):
                    self.copy_button.pack_forget()
            except:
                pass
            try:
                if hasattr(self, 'secondary_buttons_frame'):
                    self.secondary_buttons_frame.pack_forget()
            except:
                pass
        except Exception as e:
            print(f"Errore durante pulizia campi: {e}")
    
    def setup_for_new(self):
        """Configura per una nuova password"""
        self._clear_form()
        self.title_label.configure(text="Nuova Password")
        
        # Assicurati che l'editor sia visibile
        self.pack(fill="both", expand=True)
        
        # In modalità "nuova", nascondi i pulsanti aggiuntivi
        self.copy_button.pack_forget()
        self.secondary_buttons_frame.pack_forget()
        
        # Aggiorna testo pulsante salva
        self.save_button.configure(text="💾 Salva Nuova")
        
        # Forza il refresh del layout
        self.update_idletasks()
    
    def setup_for_edit(self, password_data: Dict):
        """Configura per modificare una password esistente"""
        self.current_password = password_data
        self.edit_mode = True
        
        # Assicurati che l'editor sia visibile
        self.pack(fill="both", expand=True)
        
        # Popola i campi
        self.site_entry.delete(0, "end")
        self.site_entry.insert(0, password_data["site"])
        
        self.username_entry.delete(0, "end")
        self.username_entry.insert(0, password_data["username"])
        
        # Ottieni password decriptata
        decrypted, _ = self.database.get_decrypted_password(
            password_data["site"],
            password_data["username"]
        )
        
        if decrypted:
            self.password_entry.delete(0, "end")
            self.password_entry.insert(0, decrypted)
            # Aggiorna indicatore forza
            self._on_password_change()
        
        # Note
        self.notes_text.delete("1.0", "end")
        if "notes" in password_data:
            self.notes_text.insert("1.0", password_data["notes"])
        
        self.title_label.configure(text=f"Modifica: {password_data['site']}")
        
        # Aggiorna testo pulsante salva
        self.save_button.configure(text="💾 Salva Modifiche")
        
        # Usa after per assicurarsi che il layout sia stabile
        self.after(10, self._setup_edit_buttons)

    def _setup_edit_buttons(self):
        """Configura i pulsanti per la modalità edit"""
        # Mostra pulsante copia accanto ai controlli password
        buttons_frame = self.tips_button.master
        self.copy_button.pack(in_=buttons_frame, side="left", padx=(0, 5))
        
        # Mostra frame con pulsante elimina
        self.secondary_buttons_frame.pack(fill="x", pady=(5, 0))
        
        # Forza update del layout
        self.update_idletasks()

class DashboardView(ThemedFrame):
    """Vista principale del dashboard"""
    
    def __init__(self, master, database: PasswordDatabase, on_logout: Callable):
        super().__init__(master, style="background")
        
        # Aggiungi controllo sul database
        if not database or not isinstance(database, PasswordDatabase):
            raise ValueError("Database non valido o mancante")
            
        self.database = database
        self.on_logout = on_logout
        
        self._create_ui()
        self._refresh_password_list()
    
    def _create_ui(self):
        # Header principale con controlli di navigazione
        header_frame = ThemedFrame(self, style="surface")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        # Titolo e informazioni utente
        title_section = ThemedFrame(header_frame, style="surface")
        title_section.pack(side="left", fill="x", expand=True)
        
        main_title = ThemedLabel(title_section, text="🔐 Password Manager", style="primary")
        main_title.configure(font=ctk.CTkFont(size=20, weight="bold"))
        main_title.pack(anchor="w")
        
        user_info = ThemedLabel(
            title_section, 
            text=f"👤 {self.database.current_user or 'Utente'} | 📊 {len(self.database.get_passwords())} password salvate", 
            style="secondary"
        )
        user_info.configure(font=ctk.CTkFont(size=12))
        user_info.pack(anchor="w", pady=(2, 0))
        
        # Controlli di navigazione
        nav_controls = ThemedFrame(header_frame, style="surface")
        nav_controls.pack(side="right")
        
        # Pulsante toggle tema
        from core.components import create_theme_toggle
        theme_toggle = create_theme_toggle(nav_controls)
        theme_toggle.pack(side="left", padx=(0, 15))
        
        backup_button = ThemedButton(
            nav_controls,
            text="💾 Backup & Restore",
            command=self._show_backup,
            style="primary",
            width=160,
            height=40
        )
        backup_button.pack(side="left", padx=(0, 15))
        
        logout_button = ThemedButton(
            nav_controls,
            text="🚪 Logout",
            command=self.on_logout,
            style="secondary",
            width=100,
            height=40
        )
        logout_button.pack(side="left")
        
        # Layout principale a due colonne
        main_container = ThemedFrame(self, style="background")
        main_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        main_container.columnconfigure(0, weight=1)
        main_container.columnconfigure(1, weight=2)
        main_container.rowconfigure(0, weight=1)
        
        # Pannello sinistro - Lista password
        left_panel = ThemedFrame(main_container, style="surface")
        left_panel.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        
        # Header lista password
        list_header = ThemedFrame(left_panel, style="surface")
        list_header.pack(fill="x", padx=20, pady=(20, 10))
        
        list_title = ThemedLabel(list_header, text="📋 Le tue Password", style="primary")
        list_title.configure(font=ctk.CTkFont(size=16, weight="bold"))
        list_title.pack(side="left")
        
        new_button = ThemedButton(
            list_header,
            text="➕ Nuova",
            command=self._new_password,
            style="primary",
            width=100,
            height=35
        )
        new_button.pack(side="right")
        
        # Barra di ricerca
        search_frame = ThemedFrame(left_panel, style="surface")
        search_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        self.search_entry = ThemedEntry(
            search_frame,
            placeholder_text="🔍 Cerca password...",
            height=35
        )
        self.search_entry.pack(fill="x")
        self.search_entry.bind("<KeyRelease>", self._filter_passwords)
        
        # Lista password scrollabile
        self.password_list = ctk.CTkScrollableFrame(left_panel, height=400)
        self.password_list.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Info conteggio password
        self.count_label = ThemedLabel(left_panel, text="", style="secondary")
        self.count_label.configure(font=ctk.CTkFont(size=11))
        self.count_label.pack(pady=(5, 15))
        
        # Pannello destro - Editor
        self.right_panel = ctk.CTkScrollableFrame(main_container, corner_radius=12)
        self.right_panel.grid(row=0, column=1, padx=(10, 0), sticky="nsew")
        
        # Messaggio di benvenuto
        self.welcome_frame = ThemedFrame(self.right_panel, style="surface")
        self.welcome_frame.pack(fill="both", expand=True, pady=50, padx=30)
        
        welcome_content = ThemedFrame(self.welcome_frame, style="surface")
        welcome_content.pack(expand=True)
        
        welcome_icon = ThemedLabel(welcome_content, text="🎯", style="primary")
        welcome_icon.configure(font=ctk.CTkFont(size=48))
        welcome_icon.pack(pady=(20, 10))
        
        welcome_title = ThemedLabel(welcome_content, text="Gestisci le tue Password", style="primary")
        welcome_title.configure(font=ctk.CTkFont(size=18, weight="bold"))
        welcome_title.pack(pady=(0, 15))
        
        welcome_text = """• Seleziona una password dalla lista per modificarla
• Clicca '➕ Nuova' per aggiungere una password
• Usa il generatore per password sicure
• Crea backup per proteggere i tuoi dati"""
        
        welcome_label = ThemedLabel(welcome_content, text=welcome_text, style="secondary")
        welcome_label.configure(font=ctk.CTkFont(size=13), justify="left")
        welcome_label.pack(pady=(0, 20))
        
        # Pulsanti di azione rapida
        quick_actions = ThemedFrame(welcome_content, style="surface")
        quick_actions.pack(pady=10)
        
        quick_new_btn = ThemedButton(
            quick_actions,
            text="➕ Aggiungi Prima Password",
            command=self._new_password,
            style="primary",
            width=200,
            height=40
        )
        quick_new_btn.pack(pady=5)
        
        quick_backup_btn = ThemedButton(
            quick_actions,
            text="💾 Gestisci Backup",
            command=self._show_backup,
            style="secondary",
            width=200,
            height=40
        )
        quick_backup_btn.pack(pady=5)
        
        # Editor password (creato ma inizialmente nascosto)
        self.password_editor = PasswordEditor(self.right_panel, self.database, self._refresh_password_list)
        
        # Mantieni riferimento ai dati originali per il filtro
        self.all_passwords = []
    
    def _filter_passwords(self, event=None):
        """Filtra le password in base al testo di ricerca"""
        search_text = self.search_entry.get().lower().strip()
        
        # Pulisci lista attuale
        for widget in self.password_list.winfo_children():
            widget.destroy()
        
        # Filtra password
        if search_text:
            filtered_passwords = [
                pwd for pwd in self.all_passwords
                if search_text in pwd["site"].lower() or search_text in pwd["username"].lower()
            ]
        else:
            filtered_passwords = self.all_passwords
        
        # Mostra password filtrate
        if not filtered_passwords:
            if search_text:
                no_results = ThemedLabel(
                    self.password_list,
                    text=f"Nessun risultato per '{search_text}'",
                    style="secondary"
                )
                no_results.pack(pady=20)
            else:
                empty_label = ThemedLabel(
                    self.password_list,
                    text="Nessuna password salvata.\nClicca '➕ Nuova' per iniziare.",
                    style="secondary"
                )
                empty_label.pack(pady=40)
        else:
            for password in filtered_passwords:
                item = PasswordListItem(
                    self.password_list,
                    password,
                    self._select_password
                )
                item.pack(fill="x", pady=3, padx=5)
        
        # Aggiorna conteggio
        self._update_count_label(len(filtered_passwords), len(self.all_passwords), search_text)

    def _update_count_label(self, shown_count, total_count, search_text=""):
        """Aggiorna il label del conteggio"""
        if search_text:
            text = f"Mostrate {shown_count} di {total_count} password"
        else:
            text = f"Totale: {total_count} password"
        self.count_label.configure(text=text)

    def _refresh_password_list(self):
        """Aggiorna la lista delle password"""
        self.all_passwords = self.database.get_passwords()
        
        # Aggiorna anche il conteggio nell'header
        if hasattr(self, 'count_label'):
            try:
                user_info = self.master.winfo_children()[0].winfo_children()[0].winfo_children()[0].winfo_children()[1]
                user_info.configure(
                    text=f"👤 {self.database.current_user or 'Utente'} | 📊 {len(self.all_passwords)} password salvate"
                )
            except:
                pass
        
        # Applica il filtro corrente
        self._filter_passwords()
    
    def _select_password(self, password_data: Dict):
        """Seleziona una password per la modifica"""
        # Nascondi messaggio di benvenuto
        self.welcome_frame.pack_forget()
        # Mostra e configura editor per modifica
        self.password_editor.setup_for_edit(password_data)
    
    def _new_password(self):
        """Crea una nuova password"""
        # Nascondi messaggio di benvenuto
        self.welcome_frame.pack_forget()
        # Mostra e configura editor per nuova password
        self.password_editor.setup_for_new()
    
    def _show_welcome(self):
        """Mostra il messaggio di benvenuto e nascondi l'editor"""
        self.password_editor.pack_forget()
        self.welcome_frame.pack(fill="both", expand=True)
    
    def _show_backup(self):
        """Mostra la vista backup"""
        # Passa la richiesta all'app principale
        if hasattr(self.master, 'master') and hasattr(self.master.master, '_show_backup'):
            self.master.master._show_backup()
        else:
            # Fallback: importa e mostra direttamente
            try:
                from ui.backup_view import BackupView
                
                # Crea una finestra popup per il backup
                backup_window = ctk.CTkToplevel(self)
                backup_window.title("Gestione Backup")
                backup_window.geometry("900x700")
                backup_window.transient(self)
                backup_window.grab_set()
                
                # Centra la finestra
                backup_window.update_idletasks()
                width = backup_window.winfo_width()
                height = backup_window.winfo_height()
                x = (backup_window.winfo_screenwidth() // 2) - (width // 2)
                y = (backup_window.winfo_screenheight() // 2) - (height // 2)
                backup_window.geometry(f"{width}x{height}+{x}+{y}")
                
                # Crea la vista backup
                backup_view = BackupView(
                    backup_window,
                    self.database,
                    self.database.current_user or "user",
                    backup_window.destroy
                )
                backup_view.pack(fill="both", expand=True)
                
            except Exception as e:
                show_message(self, "Errore", f"Impossibile aprire la vista backup: {str(e)}", "error")
    
    def destroy(self):
        """Override destroy per pulizia sicura"""
        try:
            # Pulisci eventuali timer o callback
            if hasattr(self, '_search_timer') and self._search_timer:
                self.after_cancel(self._search_timer)
            
            # Pulisci tutti i widget dropdown/optionmenu
            for widget in self.winfo_children():
                try:
                    if hasattr(widget, '_dropdown_menu'):
                        try:
                            widget._dropdown_menu.destroy()
                        except:
                            pass
                except:
                    pass
        except:
            pass
        
        super().destroy()
