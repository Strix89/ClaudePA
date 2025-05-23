import json
import os
import base64
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from cryptography.fernet import Fernet

class PasswordDatabase:
    """Database con crittografia selettiva - solo le password vengono crittografate"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.users_dir = self.data_dir / "users"
        self.current_user: Optional[str] = None
        self.current_key: Optional[bytes] = None
        self.user_data: Optional[Dict] = None
        
        # Crea directory se non esistono
        self.data_dir.mkdir(exist_ok=True)
        self.users_dir.mkdir(exist_ok=True)
    
    def _generate_key_from_password(self, password: str, username: str = "") -> bytes:
        """Genera una chiave Fernet dalla password"""
        # Combina password e username per creare una chiave unica
        combined = f"{password}_{username}_ClaudePA_2024"
        
        # Usa SHA256 per creare un hash di 32 bytes
        hash_bytes = hashlib.sha256(combined.encode()).digest()
        
        # Converti in chiave Fernet valida
        key = base64.urlsafe_b64encode(hash_bytes)
        return key

    def _encrypt_password(self, password: str, key: bytes) -> str:
        """Cripta una singola password e restituisce la stringa base64"""
        try:
            fernet = Fernet(key)
            encrypted_data = fernet.encrypt(password.encode())
            return base64.b64encode(encrypted_data).decode()
        except Exception as e:
            raise Exception(f"Errore durante la crittografia: {str(e)}")

    def _decrypt_password(self, encrypted_password: str, key: bytes) -> str:
        """Decripta una singola password dalla stringa base64"""
        try:
            fernet = Fernet(key)
            encrypted_data = base64.b64decode(encrypted_password)
            decrypted_data = fernet.decrypt(encrypted_data)
            return decrypted_data.decode()
        except Exception as e:
            raise Exception(f"Errore durante la decrittografia: {str(e)}")

    def register_user(self, username: str, password: str) -> Tuple[bool, str]:
        """Registra un nuovo utente"""
        try:
            if not username or not password:
                return False, "Username e password sono obbligatori"
            
            # Pulisci username
            username = username.strip().lower()
            if len(username) < 3:
                return False, "Username deve essere di almeno 3 caratteri"
            
            # Controlla se l'utente esiste già
            user_file = self.users_dir / f"{username}.json"
            if user_file.exists():
                return False, "Username già esistente"
            
            # Crea i dati dell'utente (NON crittografati)
            user_data = {
                "username": username,
                "password_hash": hashlib.sha256(password.encode()).hexdigest(),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "version": "3.0",
                "passwords": []
            }
            
            # Salva il file JSON in chiaro (solo i metadati)
            with open(user_file, 'w', encoding='utf-8') as f:
                json.dump(user_data, f, indent=2, ensure_ascii=False)
            
            print(f"Utente {username} registrato con successo")
            return True, "Utente registrato con successo"
            
        except Exception as e:
            print(f"Errore durante registrazione: {e}")
            return False, f"Errore durante la registrazione: {str(e)}"

    def login(self, username: str, password: str) -> Tuple[bool, str]:
        """Autentica un utente"""
        try:
            if not username or not password:
                return False, "Username e password sono obbligatori"
            
            # Pulisci username
            username = username.strip().lower()
            
            user_file = self.users_dir / f"{username}.json"
            if not user_file.exists():
                return False, "Username non trovato"
            
            # Prova a leggere il file come JSON
            try:
                with open(user_file, 'r', encoding='utf-8') as f:
                    user_data = json.load(f)
                
                # Verifica hash password
                expected_hash = hashlib.sha256(password.encode()).hexdigest()
                stored_hash = user_data.get("password_hash")
                
                if not stored_hash:
                    return False, "File utente corrotto (hash mancante)"
                
                if stored_hash != expected_hash:
                    return False, "Password errata"
                
                # Genera chiave per decrittare le password
                key = self._generate_key_from_password(password, username)
                
                # Imposta l'utente corrente
                self.current_user = username
                self.current_key = key
                self.user_data = user_data
                
                print(f"Login riuscito per: {username}")
                return True, "Login riuscito"
                
            except json.JSONDecodeError:
                # Il file potrebbe essere nel vecchio formato crittografato
                return self._try_legacy_login(username, password, user_file)
                
        except Exception as e:
            print(f"Errore durante il login: {e}")
            return False, f"Errore durante il login: {str(e)}"

    def _try_legacy_login(self, username: str, password: str, user_file: Path) -> Tuple[bool, str]:
        """Prova a fare login con il vecchio formato crittografato e migra al nuovo"""
        try:
            print(f"Tentativo migrazione file legacy per {username}")
            
            # Prova a leggere come file binario crittografato (vecchio formato)
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
            
            with open(user_file, 'rb') as f:
                encrypted_data = f.read()
            
            # Prova diverse chiavi per compatibilità
            password_bytes = password.encode()
            
            # Metodo 1: Salt di default vecchio
            salt = b'ClaudePA_default_salt_2024'
            kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000)
            key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
            
            try:
                fernet = Fernet(key)
                decrypted_data = fernet.decrypt(encrypted_data)
                user_data = json.loads(decrypted_data.decode())
                
                print(f"Migrazione riuscita per {username}")
                
                # Migra al nuovo formato
                user_data["password_hash"] = hashlib.sha256(password.encode()).hexdigest()
                user_data["version"] = "3.0"
                user_data["updated_at"] = datetime.now().isoformat()
                
                # Salva nel nuovo formato (JSON in chiaro)
                with open(user_file, 'w', encoding='utf-8') as f:
                    json.dump(user_data, f, indent=2, ensure_ascii=False)
                
                # Imposta l'utente corrente
                new_key = self._generate_key_from_password(password, username)
                self.current_user = username
                self.current_key = new_key
                self.user_data = user_data
                
                print(f"File migrato con successo per {username}")
                return True, "Login riuscito (file migrato al nuovo formato)"
                
            except Exception as e:
                print(f"Fallimento migrazione: {e}")
                return False, "Password errata o file corrotto"
                
        except Exception as e:
            print(f"Errore durante migrazione legacy: {e}")
            return False, "File utente non leggibile"

    def _save_user_data(self) -> Tuple[bool, str]:
        """
        Salva i dati dell'utente corrente nel file JSON
        Aggiorna automaticamente il timestamp di ultima modifica
        """
        if not self.current_user or not self.user_data:
            return False, "Dati utente non disponibili"
        
        try:
            # Determina il percorso del file utente
            user_file = self.users_dir / f"{self.current_user}.json"
            
            # Aggiorna il timestamp di ultima modifica per tracking delle modifiche
            self.user_data["updated_at"] = datetime.now().isoformat()
            
            # Salva i dati come JSON leggibile (solo le password sono crittografate)
            # Questo permette debug più facile e migrazione futura
            with open(user_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_data, f, indent=2, ensure_ascii=False)
            
            return True, "Dati salvati"
            
        except Exception as e:
            # Log dell'errore per debugging, senza esporre dati sensibili
            print(f"ERRORE SALVATAGGIO DATI utente {self.current_user}: {str(e)}")
            return False, f"Errore salvando dati: {str(e)}"

    def get_passwords(self) -> List[Dict]:
        """Ottiene la lista delle password dell'utente corrente"""
        if not self.user_data:
            return []
        
        return self.user_data.get("passwords", [])

    def add_password(self, site: str, username: str, password: str, notes: str = "") -> Tuple[bool, str]:
        """Aggiunge una nuova password"""
        if not self.current_user or not self.current_key or not self.user_data:
            return False, "Utente non autenticato"
        
        try:
            # Controlla se esiste già
            for pwd in self.user_data["passwords"]:
                if pwd["site"] == site and pwd["username"] == username:
                    return False, "Password già esistente per questo sito e username"
            
            # Cripta SOLO la password
            encrypted_password = self._encrypt_password(password, self.current_key)
            
            # Aggiungi ai dati (tutto in chiaro tranne la password)
            password_entry = {
                "site": site,
                "username": username,
                "password": encrypted_password,  # Solo questo è crittografato
                "notes": notes,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            self.user_data["passwords"].append(password_entry)
            
            # Salva
            success, message = self._save_user_data()
            if success:
                return True, "Password aggiunta con successo"
            else:
                return False, f"Errore salvando: {message}"
                
        except Exception as e:
            return False, f"Errore aggiungendo password: {str(e)}"

    def get_decrypted_password(self, site: str, username: str) -> Tuple[str, str]:
        """Ottiene una password decriptata"""
        if not self.current_user or not self.current_key or not self.user_data:
            return "", "Utente non autenticato"
        
        try:
            for pwd in self.user_data["passwords"]:
                if pwd["site"] == site and pwd["username"] == username:
                    # Decripta SOLO la password
                    decrypted_password = self._decrypt_password(pwd["password"], self.current_key)
                    return decrypted_password, "Successo"
            
            return "", "Password non trovata"
            
        except Exception as e:
            return "", f"Errore decrittando: {str(e)}"

    def delete_password(self, site: str, username: str) -> Tuple[bool, str]:
        """Elimina una password"""
        if not self.current_user or not self.current_key or not self.user_data:
            return False, "Utente non autenticato"
        
        try:
            passwords = self.user_data["passwords"]
            
            for i, pwd in enumerate(passwords):
                if pwd["site"] == site and pwd["username"] == username:
                    passwords.pop(i)
                    success, message = self._save_user_data()
                    if success:
                        return True, "Password eliminata con successo"
                    else:
                        return False, f"Errore salvando: {message}"
            
            return False, "Password non trovata"
            
        except Exception as e:
            return False, f"Errore eliminando password: {str(e)}"

    def debug_user_file(self, username: str) -> str:
        """Debug: verifica lo stato del file utente"""
        try:
            username = username.strip().lower()
            user_file = self.users_dir / f"{username}.json"
            if not user_file.exists():
                return f"File utente {username} non esiste"
            
            file_size = user_file.stat().st_size
            
            # Prova a leggere come JSON
            try:
                with open(user_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                version = data.get("version", "legacy")
                password_count = len(data.get("passwords", []))
                return f"File utente {username}: {file_size} bytes, versione {version}, {password_count} password"
            except:
                return f"File utente {username}: {file_size} bytes, formato legacy crittografato"
                
        except Exception as e:
            return f"Errore debug file {username}: {str(e)}"

    def logout(self):
        """Logout dell'utente corrente"""
        self.current_user = None
        self.current_key = None
        self.user_data = None
        print("Logout completato")
