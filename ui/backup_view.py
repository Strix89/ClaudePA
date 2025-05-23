import customtkinter as ctk
from tkinter import filedialog
from typing import Callable, List, Dict
from pathlib import Path
from core.components import ThemedFrame, ThemedLabel, ThemedButton, ThemedEntry, show_message
from core.backup import BackupManager
from core.database import PasswordDatabase
from core.config import config_manager

class BackupView(ThemedFrame):
    """Vista per gestire backup e restore delle password"""
    
    def __init__(self, master, database: PasswordDatabase, username: str, on_close: Callable):
        super().__init__(master, style="background")
        
        self.database = database
        self.username = username
        self.on_close = on_close
        self.backup_manager = BackupManager()
        
        self._create_ui()
        self._refresh_backup_list()
    
    def _create_ui(self):
        # Header con titolo e pulsante chiudi - usa configurazione
        header_frame = ThemedFrame(self, style="surface")
        header_frame.pack(fill="x", padx=20, pady=(20, 0))
        
        title_text = config_manager.get('backup.title', '🔄 Gestione Backup')
        close_button_text = config_manager.get('backup.close_button', '✕ Chiudi')
        
        title_label = ThemedLabel(header_frame, text=title_text, style="primary")
        title_label.configure(font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(side="left", pady=15)
        
        close_button = ThemedButton(
            header_frame,
            text=close_button_text,
            command=self.on_close,
            style="secondary",
            width=100,
            height=35
        )
        close_button.pack(side="right", pady=15, padx=15)
        
        # Sottotitolo con informazioni sull'utente corrente e statistiche - usa configurazione
        info_frame = ThemedFrame(self, style="background")
        info_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        user_info_text = config_manager.format_message(
            'backup.user_info_template',
            username=self.username,
            count=len(self.database.get_passwords())
        )
        
        user_info = ThemedLabel(info_frame, text=user_info_text, style="secondary")
        user_info.configure(font=ctk.CTkFont(size=12))
        user_info.pack(anchor="w")
        
        # Frame principale con scrolling per contenuto lungo
        main_scroll = ctk.CTkScrollableFrame(self, corner_radius=0)
        main_scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Container principale che conterrà tutte le sezioni
        container = ThemedFrame(main_scroll, style="background")
        container.pack(fill="both", expand=True)
        
        # Sezione per esportare le password esistenti
        self._create_export_section(container)
        
        # Separatore visivo tra le sezioni
        separator = ThemedFrame(container, style="surface", height=2)
        separator.pack(fill="x", pady=20)
        
        # Sezione per importare backup esistenti
        self._create_import_section(container)
        
        # Altro separatore visivo
        separator2 = ThemedFrame(container, style="surface", height=2)
        separator2.pack(fill="x", pady=20)
        
        # Sezione che mostra la lista dei backup disponibili
        self._create_backup_list_section(container)
    
    def _create_export_section(self, parent):
        """Crea la sezione per l'export"""
        section_frame = ThemedFrame(parent, style="surface")
        section_frame.pack(fill="x", pady=(0, 10))
        
        # Header sezione
        header = ThemedFrame(section_frame, style="surface")
        header.pack(fill="x", padx=20, pady=(15, 10))
        
        title = ThemedLabel(header, text="📤 Esporta Password", style="primary")
        title.configure(font=ctk.CTkFont(size=18, weight="bold"))
        title.pack(side="left")
        
        # Stato export
        passwords = self.database.get_passwords()
        status_text = f"{len(passwords)} password pronte per l'export" if passwords else "Nessuna password da esportare"
        status_color = "primary" if passwords else "secondary"
        
        status = ThemedLabel(header, text=status_text, style=status_color)
        status.configure(font=ctk.CTkFont(size=11))
        status.pack(side="right")
        
        # Contenuto sezione
        content = ThemedFrame(section_frame, style="surface")
        content.pack(fill="x", padx=20, pady=(0, 15))
        
        # Descrizione
        desc = ThemedLabel(
            content,
            text="💡 Crea un backup crittografato di tutte le tue password.\nIl file sarà protetto dalla tua password master e potrà essere importato in futuro.",
            style="secondary"
        )
        desc.configure(font=ctk.CTkFont(size=12), justify="left")
        desc.pack(anchor="w", pady=(0, 15))
        
        # Pulsante export
        export_button = ThemedButton(
            content,
            text="🔐 Crea Backup Adesso",
            command=self._export_passwords,
            style="primary",
            width=250,
            height=45
        )
        export_button.pack(anchor="w")
        
        if not passwords:
            export_button.configure(state="disabled")
    
    def _create_import_section(self, parent):
        """Crea la sezione per l'import"""
        section_frame = ThemedFrame(parent, style="surface")
        section_frame.pack(fill="x", pady=(0, 10))
        
        # Header sezione
        header = ThemedFrame(section_frame, style="surface")
        header.pack(fill="x", padx=20, pady=(15, 10))
        
        title = ThemedLabel(header, text="📥 Importa Password", style="primary")
        title.configure(font=ctk.CTkFont(size=18, weight="bold"))
        title.pack(side="left")
        
        # Contenuto sezione
        content = ThemedFrame(section_frame, style="surface")
        content.pack(fill="x", padx=20, pady=(0, 15))
        
        # Descrizione
        desc = ThemedLabel(
            content,
            text="📂 Ripristina le password da un backup precedente.\nLe password già esistenti verranno saltate automaticamente.",
            style="secondary"
        )
        desc.configure(font=ctk.CTkFont(size=12), justify="left")
        desc.pack(anchor="w", pady=(0, 15))
        
        # Selezione file
        file_section = ThemedFrame(content, style="surface")
        file_section.pack(fill="x", pady=(0, 15))
        
        file_label = ThemedLabel(file_section, text="📁 Seleziona file di backup:", style="primary")
        file_label.configure(font=ctk.CTkFont(size=12, weight="bold"))
        file_label.pack(anchor="w", pady=(0, 8))
        
        file_input_frame = ThemedFrame(file_section, style="surface")
        file_input_frame.pack(fill="x")
        
        self.file_entry = ThemedEntry(
            file_input_frame,
            placeholder_text="Nessun file selezionato...",
            height=40
        )
        self.file_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        browse_button = ThemedButton(
            file_input_frame,
            text="📂 Sfoglia",
            command=self._browse_backup_file,
            style="secondary",
            width=100,
            height=40
        )
        browse_button.pack(side="right")
        
        # Password master
        password_section = ThemedFrame(content, style="surface")
        password_section.pack(fill="x", pady=(0, 15))
        
        pass_label = ThemedLabel(password_section, text="🔑 Password master del backup:", style="primary")
        pass_label.configure(font=ctk.CTkFont(size=12, weight="bold"))
        pass_label.pack(anchor="w", pady=(0, 8))
        
        password_input_frame = ThemedFrame(password_section, style="surface")
        password_input_frame.pack(fill="x")
        
        self.import_password_entry = ThemedEntry(
            password_input_frame,
            placeholder_text="Inserisci la password master del backup...",
            show="•",
            height=40
        )
        self.import_password_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # Checkbox mostra password
        self.show_import_password_var = ctk.BooleanVar()
        show_password_cb = ctk.CTkCheckBox(
            password_input_frame,
            text="👁️",
            variable=self.show_import_password_var,
            command=self._toggle_import_password_visibility,
            width=40
        )
        show_password_cb.pack(side="right")
        
        # Pulsante import
        import_button = ThemedButton(
            content,
            text="📥 Importa dal Backup",
            command=self._import_passwords,
            style="primary",
            width=200,
            height=45
        )
        import_button.pack(anchor="w")
    
    def _create_backup_list_section(self, parent):
        """Crea la sezione con la lista dei backup"""
        section_frame = ThemedFrame(parent, style="surface")
        section_frame.pack(fill="both", expand=True)
        
        # Header sezione
        header = ThemedFrame(section_frame, style="surface")
        header.pack(fill="x", padx=20, pady=(15, 10))
        
        title = ThemedLabel(header, text="📋 Backup Disponibili", style="primary")
        title.configure(font=ctk.CTkFont(size=18, weight="bold"))
        title.pack(side="left")
        
        # Pulsante refresh
        refresh_button = ThemedButton(
            header,
            text="🔄 Aggiorna",
            command=self._refresh_backup_list,
            style="secondary",
            width=100,
            height=30
        )
        refresh_button.pack(side="right")
        
        # Lista backup scrollabile
        list_container = ThemedFrame(section_frame, style="surface")
        list_container.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        self.backup_list_frame = ctk.CTkScrollableFrame(list_container, height=250)
        self.backup_list_frame.pack(fill="both", expand=True, pady=10)
    
    def _toggle_import_password_visibility(self):
        """Mostra/nasconde la password di import"""
        show = "" if self.show_import_password_var.get() else "•"
        self.import_password_entry.configure(show=show)
    
    def _export_passwords(self):
        """Esporta le password in un backup"""
        try:
            passwords = self.database.get_passwords()
            
            if not passwords:
                show_message(self, "Attenzione", "Nessuna password da esportare", "warning")
                return
            
            # Ottieni tutte le password decriptate
            decrypted_passwords = []
            for pwd in passwords:
                decrypted, _ = self.database.get_decrypted_password(pwd["site"], pwd["username"])
                if decrypted:
                    pwd_copy = pwd.copy()
                    pwd_copy["password"] = decrypted
                    decrypted_passwords.append(pwd_copy)
            
            if not decrypted_passwords:
                show_message(self, "Errore", "Impossibile decriptare le password", "error")
                return
            
            # Chiedi la password master
            self._ask_master_password_for_export(decrypted_passwords)
            
        except Exception as e:
            show_message(self, "Errore", f"Errore durante l'export: {str(e)}", "error")
    
    def _ask_master_password_for_export(self, passwords: List[Dict]):
        """Chiede la password master per l'export"""
        password_dialog = ctk.CTkToplevel(self)
        password_dialog.title("🔐 Conferma Password Master")
        password_dialog.geometry("420x200")
        password_dialog.resizable(False, False)
        password_dialog.transient(self)
        password_dialog.grab_set()
        
        # Centra dialog
        password_dialog.update_idletasks()
        width = password_dialog.winfo_width()
        height = password_dialog.winfo_height()
        x = (password_dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (password_dialog.winfo_screenheight() // 2) - (height // 2)
        password_dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        frame = ThemedFrame(password_dialog, style="surface")
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Titolo
        title = ThemedLabel(frame, text="🔒 Conferma Password Master", style="primary")
        title.configure(font=ctk.CTkFont(size=14, weight="bold"))
        title.pack(pady=(0, 15))
        
        # Descrizione migliorata
        desc_text = """Per creare il backup crittografato, inserisci la tua password master.
Questa password proteggerà il file di backup e sarà necessaria
per importare le password in futuro."""
        
        desc = ThemedLabel(frame, text=desc_text, style="secondary")
        desc.configure(
            font=ctk.CTkFont(size=12),
            justify="center",
            wraplength=380
        )
        desc.pack(pady=(0, 20))
        
        # Password entry
        password_entry = ThemedEntry(frame, show="•", height=40)
        password_entry.pack(fill="x", pady=(0, 20))
        password_entry.focus()
        
        def confirm_export():
            master_password = password_entry.get()
            if not master_password:
                show_message(password_dialog, "Errore", "Inserisci la password master per continuare", "error")
                return
            
            password_dialog.destroy()
            
            # Esegui l'export
            success, result = self.backup_manager.export_passwords(
                self.username, master_password, passwords
            )
            
            if success:
                success_message = f"""Backup creato con successo!

📁 Nome file: {Path(result).name}

📍 Posizione: {self.backup_manager.backup_dir}

💡 Conserva questo file in un luogo sicuro e ricorda
la password master utilizzata per proteggerlo."""
                
                show_message(self, "✅ Backup Creato", success_message, "success")
                self._refresh_backup_list()
            else:
                show_message(self, "Errore", f"Errore durante la creazione del backup:\n\n{result}", "error")
        
        # Pulsanti
        buttons_frame = ThemedFrame(frame, style="surface")
        buttons_frame.pack(fill="x")
        
        cancel_btn = ThemedButton(
            buttons_frame,
            text="❌ Annulla",
            command=password_dialog.destroy,
            style="secondary",
            width=120,
            height=35
        )
        cancel_btn.pack(side="left")
        
        export_btn = ThemedButton(
            buttons_frame,
            text="✅ Crea Backup",
            command=confirm_export,
            style="primary",
            width=140,
            height=35
        )
        export_btn.pack(side="right")
        
        # Bind Enter key
        password_entry.bind("<Return>", lambda e: confirm_export())
    
    def _browse_backup_file(self):
        """Apre un dialog per selezionare un file di backup"""
        file_path = filedialog.askopenfilename(
            title="Seleziona file di backup",
            filetypes=[
                ("Password Backup", "*.pwbak"), 
                ("Tutti i file", "*.*")
            ],
            initialdir=str(self.backup_manager.backup_dir)
        )
        
        if file_path:
            self.file_entry.delete(0, "end")
            self.file_entry.insert(0, file_path)
            # Aggiorna placeholder per mostrare solo il nome file
            filename = Path(file_path).name
            self.file_entry.configure(placeholder_text=f"📁 {filename}")
    
    def _import_passwords(self):
        """Importa le password dal backup"""
        filepath = self.file_entry.get().strip()
        password = self.import_password_entry.get().strip()
        
        if not filepath:
            show_message(self, "Errore", "Seleziona un file di backup", "error")
            return
        
        if not password:
            show_message(self, "Errore", "Inserisci la password master", "error")
            return
        
        success, message, data = self.backup_manager.import_passwords(filepath, password)
        
        if not success:
            show_message(self, "Errore", message, "error")
            return
        
        # Mostra dialog di conferma con dettagli
        self._show_import_confirmation_dialog(data)
    
    def _show_import_confirmation_dialog(self, backup_data: Dict):
        """Mostra dialog di conferma per l'import"""
        confirm_dialog = ctk.CTkToplevel(self)
        confirm_dialog.title(config_manager.get('backup.import_section.title', 'Conferma Import'))
        confirm_dialog.geometry("480x350")
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
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Titolo
        title_label = ThemedLabel(frame, text="📥 Conferma Import", style="primary")
        title_label.configure(font=ctk.CTkFont(size=16, weight="bold"))
        title_label.pack(pady=(0, 15))
        
        # Informazioni backup migliorata
        info_text = f"""📊 DETTAGLI DEL BACKUP:

👤 Utente: {backup_data.get('username', 'Sconosciuto')}
📅 Data creazione: {backup_data.get('export_date_formatted', 'N/A')}
🔢 Password contenute: {backup_data.get('password_count', 0)}

⚠️ IMPORTANTE:
• Le password già esistenti nel tuo account verranno saltate
• Solo le nuove password verranno importate
• L'operazione non può essere annullata

Vuoi procedere con l'importazione?"""
        
        info_label = ThemedLabel(frame, text=info_text, style="secondary")
        info_label.configure(
            font=ctk.CTkFont(size=12),
            justify="left",
            wraplength=440
        )
        info_label.pack(pady=(0, 25))
        
        # Pulsanti
        buttons_frame = ThemedFrame(frame, style="surface")
        buttons_frame.pack(fill="x")
        
        cancel_btn = ThemedButton(
            buttons_frame,
            text="❌ Annulla",
            command=confirm_dialog.destroy,
            style="secondary",
            width=140,
            height=40
        )
        cancel_btn.pack(side="left")
        
        import_btn = ThemedButton(
            buttons_frame,
            text="✅ Importa Password",
            command=lambda: self._execute_import(confirm_dialog, backup_data),
            style="primary",
            width=160,
            height=40
        )
        import_btn.pack(side="right")
    
    def _execute_import(self, dialog, backup_data: Dict):
        """Esegue l'import delle password"""
        dialog.destroy()
        
        # Importa le password nel database
        imported_count = 0
        skipped_count = 0
        error_count = 0
        
        try:
            for pwd_data in backup_data['passwords']:
                # Controlla se la password esiste già
                existing = self.database.get_decrypted_password(pwd_data['site'], pwd_data['username'])
                
                if existing[0]:  # Se esiste già
                    skipped_count += 1
                    continue
                
                # Aggiungi la password
                success_add, _ = self.database.add_password(
                    pwd_data['site'],
                    pwd_data['username'],
                    pwd_data['password'],
                    pwd_data.get('notes', '')
                )
                
                if success_add:
                    imported_count += 1
                else:
                    error_count += 1
            
            # Pulisci i campi
            self.file_entry.delete(0, "end")
            self.import_password_entry.delete(0, "end")
            
            # Mostra risultato migliorato
            result_message = f"""✅ IMPORT COMPLETATO CON SUCCESSO!

📊 RIEPILOGO OPERAZIONE:
📥 Password importate: {imported_count}"""
            
            if skipped_count > 0:
                result_message += f"\n⏭️ Password saltate (già esistenti): {skipped_count}"
            if error_count > 0:
                result_message += f"\n❌ Errori durante l'import: {error_count}"
            
            result_message += f"""

💡 Le password sono state importate nel tuo account e sono
ora disponibili nella lista delle password."""
            
            show_message(self, "Import Completato", result_message, "success")
            
        except Exception as e:
            error_msg = f"""Errore durante l'importazione delle password:

{str(e)}

Verifica che il file di backup sia valido e riprova."""
            show_message(self, "Errore Import", error_msg, "error")
    
    def _refresh_backup_list(self):
        """Aggiorna la lista dei backup esistenti"""
        try:
            # Pulisci lista attuale
            for widget in self.backup_list_frame.winfo_children():
                try:
                    widget.destroy()
                except:
                    pass
            
            backups = self.backup_manager.list_backups()
            
            if not backups:
                empty_frame = ThemedFrame(self.backup_list_frame, style="surface")
                empty_frame.pack(fill="x", pady=20, padx=10)
                
                empty_icon = ThemedLabel(empty_frame, text="📂", style="secondary")
                empty_icon.configure(font=ctk.CTkFont(size=24))
                empty_icon.pack(pady=(10, 5))
                
                empty_label = ThemedLabel(
                    empty_frame,
                    text="Nessun backup trovato\nCrea il tuo primo backup utilizzando il pulsante sopra",
                    style="secondary"
                )
                empty_label.configure(font=ctk.CTkFont(size=12), justify="center")
                empty_label.pack(pady=(0, 10))
                return
            
            for backup in backups:
                self._create_backup_item(backup)
                
        except Exception as e:
            print(f"Errore aggiornando lista backup: {e}")
    
    def _create_backup_item(self, backup: Dict):
        """Crea un item per un backup nella lista"""
        item_frame = ThemedFrame(self.backup_list_frame, style="surface")
        item_frame.pack(fill="x", pady=8, padx=10)
        item_frame.configure(height=90, corner_radius=12)
        
        # Frame principale contenuto
        content_frame = ThemedFrame(item_frame, style="surface")
        content_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Info principali (sinistra)
        info_frame = ThemedFrame(content_frame, style="surface")
        info_frame.pack(side="left", fill="both", expand=True)
        
        # Nome file
        filename_label = ThemedLabel(info_frame, text=f"📁 {backup['filename']}", style="primary")
        filename_label.configure(font=ctk.CTkFont(size=13, weight="bold"))
        filename_label.pack(anchor="w")
        
        # Dettagli
        details_text = f"👤 {backup['metadata']['username']} | 🗓️ {backup['metadata']['export_date_formatted']}"
        details_label = ThemedLabel(info_frame, text=details_text, style="secondary")
        details_label.configure(font=ctk.CTkFont(size=11))
        details_label.pack(anchor="w", pady=(2, 0))
        
        # Dimensione file
        size_mb = backup['size'] / (1024 * 1024)
        size_text = f"💾 {size_mb:.2f} MB"
        size_label = ThemedLabel(info_frame, text=size_text, style="secondary")
        size_label.configure(font=ctk.CTkFont(size=10))
        size_label.pack(anchor="w", pady=(2, 0))
        
        # Pulsanti (destra)
        buttons_frame = ThemedFrame(content_frame, style="surface")
        buttons_frame.pack(side="right", padx=(10, 0))
        
        # Pulsante carica
        load_button = ThemedButton(
            buttons_frame,
            text="📋 Carica",
            command=lambda: self._load_backup_to_form(backup['filepath']),
            style="secondary",
            width=80,
            height=32
        )
        load_button.pack(pady=(0, 5))
        
        # Pulsante elimina
        delete_button = ThemedButton(
            buttons_frame,
            text="🗑️ Elimina",
            command=lambda: self._delete_backup(backup),
            style="danger",
            width=80,
            height=32
        )
        delete_button.pack()
    
    def _delete_backup(self, backup: Dict):
        """Elimina un backup dopo conferma"""
        # Dialog di conferma migliorato
        confirm_dialog = ctk.CTkToplevel(self)
        confirm_dialog.title("Conferma Eliminazione")
        confirm_dialog.geometry("380x160")
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
        frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Icona di avvertimento
        warning_label = ThemedLabel(frame, text="⚠️", style="primary")
        warning_label.configure(font=ctk.CTkFont(size=32))
        warning_label.pack(pady=(0, 10))
        
        # Messaggio migliorato
        message_text = f"""Sei sicuro di voler eliminare questo backup?

📁 {backup['filename']}

⚠️ Questa operazione non può essere annullata!"""
        
        label = ThemedLabel(frame, text=message_text, style="primary")
        label.configure(
            font=ctk.CTkFont(size=12),
            justify="center",
            wraplength=350
        )
        label.pack(pady=(0, 20))
        
        buttons_frame = ThemedFrame(frame, style="surface")
        buttons_frame.pack(fill="x")
        
        cancel_btn = ThemedButton(
            buttons_frame,
            text="❌ Annulla",
            command=confirm_dialog.destroy,
            style="secondary",
            width=120,
            height=35
        )
        cancel_btn.pack(side="left")
        
        delete_btn = ThemedButton(
            buttons_frame,
            text="🗑️ Elimina",
            command=lambda: self._confirm_backup_delete(confirm_dialog, backup),
            style="danger",
            width=120,
            height=35
        )
        delete_btn.pack(side="right")
    
    def _load_backup_to_form(self, filepath: str):
        """Carica il percorso del backup nel form di import"""
        try:
            # Inserisce il percorso nel campo file del form di import
            self.file_entry.delete(0, "end")
            self.file_entry.insert(0, filepath)
            
            # Aggiorna il placeholder per mostrare il nome del file
            filename = Path(filepath).name
            
            # Focus sul campo password per guidare l'utente
            self.import_password_entry.focus()
            
            # Mostra messaggio di conferma
            show_message(
                self, 
                "File Caricato", 
                f"File di backup caricato: {filename}\n\nInserisci la password master per importare.", 
                "success"
            )
            
        except Exception as e:
            show_message(self, "Errore", f"Errore caricando il file: {str(e)}", "error")

    def _confirm_backup_delete(self, dialog, backup: Dict):
        """Conferma ed esegue l'eliminazione del backup"""
        try:
            dialog.destroy()
            
            filepath = backup['filepath']
            filename = backup['filename']
            
            # Esegui l'eliminazione
            success, message = self.backup_manager.delete_backup(filepath)
            
            if success:
                show_message(
                    self, 
                    "Backup Eliminato", 
                    f"Il backup '{filename}' è stato eliminato con successo.", 
                    "success"
                )
                # Aggiorna la lista dei backup
                self._refresh_backup_list()
            else:
                show_message(self, "Errore", f"Errore eliminando il backup:\n{message}", "error")
                
        except Exception as e:
            show_message(self, "Errore", f"Errore durante l'eliminazione: {str(e)}", "error")
