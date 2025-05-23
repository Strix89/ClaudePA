import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

class BackupManager:
    """Gestore per backup e restore delle password"""
    
    def __init__(self):
        # Directory per i backup
        self.backup_dir = Path(__file__).parent.parent / "data" / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def _derive_key_from_password(self, password: str, salt: bytes = None) -> bytes:
        """Deriva una chiave di crittografia dalla password master"""
        # Usa lo stesso metodo del database per compatibilità
        import hashlib
        combined = f"{password}_backup_ClaudePA_2024"
        hash_bytes = hashlib.sha256(combined.encode()).digest()
        key = base64.urlsafe_b64encode(hash_bytes)
        return key
    
    def export_passwords(self, username: str, master_password: str, passwords: List[Dict]) -> Tuple[bool, str]:
        """
        Esporta le password in un file di backup crittografato
        
        Args:
            username: Nome utente
            master_password: Password master per la crittografia
            passwords: Lista delle password da esportare
            
        Returns:
            Tuple[bool, str]: (success, filepath_or_error_message)
        """
        try:
            # Crea timestamp per il nome file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"backup_{username}_{timestamp}.pwbak"
            filepath = self.backup_dir / filename
            
            # Genera salt casuale
            salt = os.urandom(16)
            
            # Deriva chiave dalla password master
            key = self._derive_key_from_password(master_password, salt)
            fernet = Fernet(key)
            
            # Prepara i dati per l'export
            backup_data = {
                "version": "1.0",
                "username": username,
                "export_date": datetime.now().isoformat(),
                "export_date_formatted": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "password_count": len(passwords),
                "passwords": []
            }
            
            # Aggiungi le password (già decriptate dal chiamante)
            for pwd in passwords:
                backup_data["passwords"].append({
                    "site": pwd["site"],
                    "username": pwd["username"], 
                    "password": pwd.get("password", ""),  # Password in chiaro
                    "notes": pwd.get("notes", ""),
                    "created_at": pwd.get("created_at", ""),
                    "updated_at": pwd.get("updated_at", "")
                })
            
            # Converti i dati in formato JSON per serializzazione
            json_data = json.dumps(backup_data, indent=2, ensure_ascii=False)
            
            # Cripta i dati utilizzando la chiave derivata dalla password master
            # Usa Fernet per crittografia simmetrica sicura (AES 128 in modalità CBC)
            encrypted_data = fernet.encrypt(json_data.encode('utf-8'))
            
            # Crea il file finale con struttura: [16 bytes salt] + [dati crittografati]
            # Il salt permette di derivare la stessa chiave durante l'import
            with open(filepath, 'wb') as f:
                f.write(salt)           # Primi 16 bytes = salt per derivazione chiave
                f.write(encrypted_data) # Resto = payload crittografato
            
            return True, str(filepath)
            
        except Exception as e:
            # Log errore senza esporre informazioni sensibili
            print(f"ERRORE EXPORT BACKUP: {str(e)}")
            return False, f"Errore durante l'export: {str(e)}"
    
    def import_passwords(self, filepath: str, master_password: str) -> Tuple[bool, str, Dict]:
        """
        Importa le password da un file di backup
        
        Args:
            filepath: Percorso del file di backup
            master_password: Password master per decrittare
            
        Returns:
            Tuple[bool, str, Dict]: (success, message, data)
        """
        try:
            if not os.path.exists(filepath):
                return False, "File di backup non trovato", {}
            
            # Leggi il file
            with open(filepath, 'rb') as f:
                salt = f.read(16)  # Primi 16 bytes = salt
                encrypted_data = f.read()  # Resto = dati crittografati
            
            if len(salt) != 16:
                return False, "File di backup corrotto (salt mancante)", {}
            
            # Deriva la chiave dalla password
            try:
                key = self._derive_key_from_password(master_password, salt)
                fernet = Fernet(key)
            except Exception:
                return False, "Errore nella derivazione della chiave", {}
            
            # Decritta i dati
            try:
                decrypted_data = fernet.decrypt(encrypted_data)
                json_data = decrypted_data.decode('utf-8')
            except Exception:
                return False, "Password master errata o file corrotto", {}
            
            # Parse JSON
            try:
                backup_data = json.loads(json_data)
            except json.JSONDecodeError:
                return False, "Formato del backup non valido", {}
            
            # Valida la struttura
            required_fields = ["version", "username", "export_date", "passwords"]
            for field in required_fields:
                if field not in backup_data:
                    return False, f"Campo obbligatorio mancante: {field}", {}
            
            if not isinstance(backup_data["passwords"], list):
                return False, "Lista password non valida", {}
            
            return True, "Backup importato con successo", backup_data
            
        except Exception as e:
            return False, f"Errore durante l'import: {str(e)}", {}
    
    def list_backups(self) -> List[Dict]:
        """
        Lista tutti i file di backup disponibili
        
        Returns:
            List[Dict]: Lista dei backup con metadata
        """
        backups = []
        
        try:
            for filepath in self.backup_dir.glob("*.pwbak"):
                try:
                    # Ottieni info base dal file
                    stat = filepath.stat()
                    
                    # Prova a leggere metadata (senza decrittare tutto)
                    backup_info = {
                        "filename": filepath.name,
                        "filepath": str(filepath),
                        "size": stat.st_size,
                        "created": datetime.fromtimestamp(stat.st_mtime),
                        "metadata": self._extract_metadata_preview(filepath)
                    }
                    
                    backups.append(backup_info)
                    
                except Exception as e:
                    # Se c'è un errore con un file specifico, continua con gli altri
                    print(f"Errore leggendo backup {filepath}: {e}")
                    continue
            
            # Ordina per data di creazione (più recenti prima)
            backups.sort(key=lambda x: x["created"], reverse=True)
            
        except Exception as e:
            print(f"Errore listando backup: {e}")
        
        return backups
    
    def _extract_metadata_preview(self, filepath: Path) -> Dict:
        """
        Estrae metadata dal nome file e info di base
        Non decritta il contenuto per performance
        """
        try:
            filename = filepath.stem  # Nome senza estensione
            
            # Parse del nome file: backup_username_timestamp
            parts = filename.split('_')
            if len(parts) >= 3 and parts[0] == "backup":
                username = parts[1]
                timestamp_str = '_'.join(parts[2:])
                
                try:
                    # Prova a parsare il timestamp
                    timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                    formatted_date = timestamp.strftime("%d/%m/%Y %H:%M")
                except ValueError:
                    formatted_date = "Data sconosciuta"
                
                return {
                    "username": username,
                    "export_date_formatted": formatted_date,
                    "password_count": "?"  # Non possiamo sapere senza decrittare
                }
            else:
                return {
                    "username": "Sconosciuto",
                    "export_date_formatted": "Data sconosciuta", 
                    "password_count": "?"
                }
                
        except Exception:
            return {
                "username": "Sconosciuto",
                "export_date_formatted": "Data sconosciuta",
                "password_count": "?"
            }
    
    def delete_backup(self, filepath: str) -> Tuple[bool, str]:
        """
        Elimina un file di backup
        
        Args:
            filepath: Percorso del file da eliminare
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            backup_path = Path(filepath)
            
            if not backup_path.exists():
                return False, "File di backup non trovato"
            
            if not backup_path.is_file():
                return False, "Il percorso non è un file valido"
            
            # Controlla che sia nella directory backup per sicurezza
            if not str(backup_path.resolve()).startswith(str(self.backup_dir.resolve())):
                return False, "File non nella directory di backup"
            
            backup_path.unlink()
            return True, "Backup eliminato con successo"
            
        except Exception as e:
            return False, f"Errore durante l'eliminazione: {str(e)}"
    
    def get_backup_info(self, filepath: str, master_password: str) -> Tuple[bool, str, Dict]:
        """
        Ottiene informazioni dettagliate su un backup (decriptandolo)
        
        Args:
            filepath: Percorso del file di backup
            master_password: Password master per decrittare
            
        Returns:
            Tuple[bool, str, Dict]: (success, message, info)
        """
        success, message, data = self.import_passwords(filepath, master_password)
        
        if not success:
            return False, message, {}
        
        # Estrae solo le informazioni, non le password
        info = {
            "version": data.get("version", "Sconosciuta"),
            "username": data.get("username", "Sconosciuto"),
            "export_date": data.get("export_date", ""),
            "export_date_formatted": data.get("export_date_formatted", ""),
            "password_count": data.get("password_count", len(data.get("passwords", [])))
        }
        
        return True, "Info ottenute", info
