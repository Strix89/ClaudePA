import json
import os
import base64
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet

class PasswordDatabase:
    """Database semplificato per la gestione delle password"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.users_dir = self.data_dir / "users"
        self.current_user: Optional[str] = None
        self.current_key: Optional[bytes] = None
        self.user_data: Optional[Dict] = None
        
        # Crea directory se non esistono
        self.data_dir.mkdir(exist_ok=True)
        self.users_dir.mkdir(exist_ok=True)
    
    def _derive_key(self, password: bytes, salt: bytes = None) -> bytes:
        """Deriva una chiave di crittografia dalla password"""
        if salt is None:
            # Genera un salt se non fornito (per compatibilità)
            salt = b'ClaudePA_default_salt_2024'  # Salt fisso per compatibilità
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return kdf.derive(password)

    def _encrypt_data(self, data: str, key: bytes) -> bytes:
        """Cripta i dati usando Fernet"""
        try:
            # Deriva una chiave Fernet dalla chiave PBKDF2
            fernet_key = base64.urlsafe_b64encode(key)
            fernet = Fernet(fernet_key)
            
            # Cripta i dati
            encrypted_data = fernet.encrypt(data.encode())
            return encrypted_data
            
        except Exception as e:
            raise Exception(f"Errore durante la crittografia: {str(e)}")

    def _decrypt_data(self, encrypted_data: bytes, key: bytes) -> str:
        """Decripta i dati usando Fernet"""
        try:
            # Deriva una chiave Fernet dalla chiave PBKDF2
            fernet_key = base64.urlsafe_b64encode(key)
            fernet = Fernet(fernet_key)
            
            # Decripta i dati
            decrypted_data = fernet.decrypt(encrypted_data)
            return decrypted_data.decode()
            
        except Exception as e:
            raise Exception(f"Errore durante la decrittografia: {str(e)}")

    def register_user(self, username: str, password: str) -> Tuple[bool, str]:
        """Registra un nuovo utente"""
        try:
            if not username or not password:
                return False, "Username e password sono obbligatori"
            
            # Controlla se l'utente esiste già
            user_file = self.users_dir / f"{username}.json"
            if user_file.exists():
                return False, "Username già esistente"
            
            # Crea la chiave di crittografia dalla password
            password_bytes = password.encode()
            salt = os.urandom(32)  # Genera un salt random per ogni utente
            key = self._derive_key(password_bytes, salt)
            
            # Crea i dati dell'utente
            user_data = {
                "username": username,
                "created_at": datetime.now().isoformat(),
                "salt": salt.hex(),  # Salva il salt in formato hex
                "passwords": []
            }
            
            # Salva i dati crittografati
            encrypted_data = self._encrypt_data(json.dumps(user_data), key)
            
            with open(user_file, 'wb') as f:
                f.write(encrypted_data)
            
            return True, "Utente registrato con successo"
            
        except Exception as e:
            return False, f"Errore durante la registrazione: {str(e)}"

    def login(self, username: str, password: str) -> Tuple[bool, str]:
        """Autentica un utente"""
        try:
            if not username or not password:
                return False, "Username e password sono obbligatori"
            
            user_file = self.users_dir / f"{username}.json"
            if not user_file.exists():
                return False, "Username non trovato"
            
            password_bytes = password.encode()
            
            # Leggi il file crittografato
            with open(user_file, 'rb') as f:
                encrypted_data = f.read()
            
            # Prima prova con il salt di default per utenti vecchi
            try:
                key = self._derive_key(password_bytes)  # Usa salt di default
                user_data_json = self._decrypt_data(encrypted_data, key)
                user_data = json.loads(user_data_json)
                
                # Se non ha salt, lo aggiungiamo e aggiorniamo il file
                if "salt" not in user_data:
                    salt = os.urandom(32)
                    user_data["salt"] = salt.hex()
                    new_key = self._derive_key(password_bytes, salt)
                    
                    # Ri-critta il file con il nuovo salt
                    new_encrypted_data = self._encrypt_data(json.dumps(user_data), new_key)
                    with open(user_file, 'wb') as f:
                        f.write(new_encrypted_data)
                    
                    # Usa la nuova chiave
                    key = new_key
                
                # Imposta l'utente corrente e la chiave
                self.current_user = username
                self.current_key = key
                self.user_data = user_data
                
                print(f"Login riuscito nel database per: {username}")
                return True, "Login riuscito"
                
            except Exception as first_error:
                # Se fallisce con salt di default, prova con il salt dal file
                print(f"Primo tentativo fallito: {first_error}")
                
                try:
                    # Prova a leggere il salt dal file se il primo tentativo fallisce
                    # Questo potrebbe essere un utente nuovo con salt specifico
                    
                    # Proviamo tutti i salt possibili per compatibilità
                    possible_keys = []
                    
                    # 1. Salt di default
                    possible_keys.append(self._derive_key(password_bytes))
                    
                    # 2. Prova con salt vuoto
                    possible_keys.append(self._derive_key(password_bytes, b''))
                    
                    # 3. Prova con alcuni salt comuni
                    common_salts = [
                        b'ClaudePA_salt',
                        b'default_salt',
                        username.encode()
                    ]
                    for salt in common_salts:
                        possible_keys.append(self._derive_key(password_bytes, salt))
                    
                    user_data = None
                    working_key = None
                    
                    for test_key in possible_keys:
                        try:
                            user_data_json = self._decrypt_data(encrypted_data, test_key)
                            user_data = json.loads(user_data_json)
                            working_key = test_key
                            print(f"Login riuscito con chiave alternativa")
                            break
                        except:
                            continue
                    
                    if user_data and working_key:
                        # Se non ha salt, aggiungilo
                        if "salt" not in user_data:
                            salt = os.urandom(32)
                            user_data["salt"] = salt.hex()
                            new_key = self._derive_key(password_bytes, salt)
                            
                            # Ri-critta il file con il nuovo salt
                            new_encrypted_data = self._encrypt_data(json.dumps(user_data), new_key)
                            with open(user_file, 'wb') as f:
                                f.write(new_encrypted_data)
                        
                        # Imposta l'utente corrente e la chiave
                        self.current_user = username
                        self.current_key = working_key
                        self.user_data = user_data
                        
                        return True, "Login riuscito con chiave alternativa"
                    
                    return False, "Impossibile autenticare l'utente"
                
                except Exception as e:
                    return False, f"Errore durante il login: {str(e)}"

    def debug_user_file(self, username: str) -> str:
        """Debug: verifica lo stato del file utente"""
        try:
            user_file = self.users_dir / f"{username}.json"
            if not user_file.exists():
                return f"File utente {username} non esiste"
            
            file_size = user_file.stat().st_size
            
            # Prova a leggere il file come testo per vedere se è corrotto
            try:
                with open(user_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                return f"File utente {username}: {file_size} bytes, sembra essere testo non crittografato"
            except:
                return f"File utente {username}: {file_size} bytes, sembra essere crittografato correttamente"
                
        except Exception as e:
            return f"Errore debug file {username}: {str(e)}"
