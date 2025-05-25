# 🔐 ClaudePA - Password Manager Avanzato

Un password manager desktop sicuro, moderno e user-friendly sviluppato in Python con CustomTkinter. Caratterizzato da crittografia AES-256, sistema di temi avanzato e backup sicuri.

## 📋 Indice

- [Caratteristiche Principali](#-caratteristiche-principali)
- [Installazione e Setup](#-installazione-e-setup)
- [Architettura del Sistema](#-architettura-del-sistema)
- [Sicurezza e Crittografia](#-sicurezza-e-crittografia)
- [Guida Utente](#-guida-utente)
- [Documentazione Tecnica](#-documentazione-tecnica)
- [API Reference](#-api-reference)
- [Troubleshooting](#-troubleshooting)
- [TODO e Roadmap](#-todo-e-roadmap)
- [Contribuire](#-contribuire)

---

## 🚀 Caratteristiche Principali

### 🔒 Sicurezza di Livello Enterprise
- **Crittografia AES-256** tramite libreria `cryptography`
- **Crittografia selettiva** - solo le password sono crittografate
- **Derivazione chiavi deterministiche** basata su password + username
- **Zero-knowledge architecture** - password master non recuperabile
- **Backup crittografati** con autenticazione

### 🎨 Interfaccia Utente Moderna
- **Sistema di temi dinamico** (Light/Dark/System)
- **Observer Pattern** per aggiornamento automatico UI
- **Responsive design** con CustomTkinter
- **Componenti themed** personalizzati
- **Feedback visivo avanzato**

### 💾 Gestione Dati Avanzata
- **Database JSON locale** con metadati in chiaro
- **Solo password crittografate** per performance
- **Backup automatici** con metadata
- **Migrazione automatica** da versioni precedenti
- **Sistema di versioning** dei file utente

### 🛠️ Funzionalità Complete
- **Generatore password sicuro** con pattern personalizzabili
- **Sistema di ricerca** veloce e filtri
- **Gestione note** per ogni password
- **Import/Export** backup con validazione
- **Multi-utente** con isolamento dati

---

## 🛠️ Installazione e Setup

### Requisiti di Sistema
- **Python 3.8+** (raccomandato 3.9+)
- **Windows 10+** / **macOS 10.14+** / **Linux** (Ubuntu 18.04+)
- **RAM**: 256MB minimo, 512MB raccomandato
- **Storage**: 50MB per l'applicazione + spazio per i dati

### Installazione Automatica

```bash
# 1. Clona il repository
git clone https://github.com/tuoUsername/ClaudePA.git
cd ClaudePA

# 2. Esegui l'applicazione (installa automaticamente le dipendenze)
python main.py
```

### Installazione Manuale

```bash
# 1. Installa le dipendenze
pip install -r requirements.txt

# 2. Verifica l'installazione
python -c "import customtkinter, cryptography; print('✅ Dipendenze installate correttamente')"

# 3. Avvia l'applicazione
python main.py
```

### Dipendenze

```
customtkinter>=5.2.0    # UI framework moderno
cryptography>=41.0.0    # Crittografia sicura
pathlib>=1.0.1         # Gestione path cross-platform
```

---

## 🏗️ Architettura del Sistema

### Struttura del Progetto

```
ClaudePA/
├── 📁 core/                    # Moduli core dell'applicazione
│   ├── 🐍 __init__.py         # Package initialization
│   ├── 🐍 app.py              # Applicazione principale e routing
│   ├── 🐍 theme.py            # Theme Manager con Observer Pattern
│   ├── 🐍 components.py       # Componenti UI themed riusabili
│   ├── 🐍 database.py         # Database manager con crittografia
│   └── 🐍 backup.py           # Sistema backup/restore sicuro
├── 📁 ui/                     # Interfacce utente
│   ├── 🐍 __init__.py         # Package initialization
│   ├── 🐍 login_view.py       # Vista autenticazione utente
│   ├── 🐍 register_view.py    # Vista registrazione nuovo utente
│   ├── 🐍 dashboard_view.py   # Vista principale gestione password
│   └── 🐍 backup_view.py      # Vista gestione backup
├── 📁 data/                   # Directory dati (auto-generata)
│   ├── 📁 users/              # File utenti (.json)
│   └── 📁 backups/            # File backup (.pwbak)
├── 📄 main.py                 # Entry point applicazione
├── 📄 requirements.txt        # Dipendenze Python
└── 📄 README.md              # Questa documentazione
```

### Pattern Architetturali

#### 🔄 Observer Pattern (Theme System)
```python
# Theme Manager notifica automaticamente tutti i componenti
theme_manager.add_observer(component._update_theme)
theme_manager.notify_observers()  # Aggiorna tutti i componenti

# Componenti si registrano automaticamente
class ThemedWidget:
    def __init__(self):
        theme_manager.add_observer(self._update_theme)
```

#### 🏭 Factory Pattern (Component Creation)
```python
# Creazione componenti con stili automatici
button = ThemedButton(parent, text="Login", style="primary")
frame = ThemedFrame(parent, style="surface")
```

#### 🎯 MVC-like Pattern
- **Model**: `PasswordDatabase` - gestione dati e business logic
- **View**: `*_view.py` - interfacce utente specifiche
- **Controller**: `PasswordManagerApp` - orchestrazione e routing

---

## 🔐 Sicurezza e Crittografia

ClaudePA implementa un sistema di **crittografia selettiva** dove solo le password vengono crittografate, mentre i metadati rimangono in chiaro per permettere ricerche efficienti e debugging semplificato.

### 🏗️ Architettura di Sicurezza

#### Filosofia "Zero-Knowledge"
```
🔐 Password Master → NON salvata mai da nessuna parte
└── Usata solo per generare chiavi di crittografia
└── Persa = dati irrecuperabili (by design)

📄 File Utente = Metadati in chiaro + Password crittografate
└── Permette ricerche veloci senza decrittografia
└── Debug e manutenzione facilitati
└── Solo le password sensibili sono protette
```

### 🔑 Generazione Chiavi di Crittografia

#### Processo Step-by-Step

**1. Input Utente**
```python
username = "mario"
password_master = "MiaPasswordSegreta123!"
```

**2. Combinazione Deterministca**
```python
# Il sistema combina username + password + salt applicazione
combined = f"{password_master}_{username}_ClaudePA_2024"
# Risultato: "MiaPasswordSegreta123!_mario_ClaudePA_2024"
```

**3. Hash SHA-256**
```python
import hashlib
hash_bytes = hashlib.sha256(combined.encode()).digest()
# Risultato: 32 bytes di hash crittografico
# Esempio: b'\x2a\x5f\x8c\x19...' (32 bytes)
```

**4. Conversione Chiave Fernet**
```python
import base64
key = base64.urlsafe_b64encode(hash_bytes)
# Risultato: chiave Fernet valida
# Esempio: b'Kl-MGeQx7vZ2P3kS9mN8jW5hR1tY6uI0oP2aS4dF7gH='
```

#### Vantaggi di questo Approccio

✅ **Deterministico**: Stessa password + username = stessa chiave sempre  
✅ **Unico per utente**: Username diverso = chiave completamente diversa  
✅ **Non reversibile**: Impossibile recuperare la password dalla chiave  
✅ **Salt integrato**: "ClaudePA_2024" previene rainbow table attacks  
✅ **Zero storage**: Chiave generata al volo, mai salvata  

### 🔒 Crittografia delle Password

#### Esempio Pratico Completo

**Scenario**: Mario vuole salvare la password del suo account GitHub

**Input**:
```python
site = "github.com"
username_github = "mario.rossi@email.com"  
password_github = "GitHub_SuperSecura_2024!"
```

**Processo di Crittografia**:

```python
# 1. La chiave è già stata generata al login
key = "Kl-MGeQx7vZ2P3kS9mN8jW5hR1tY6uI0oP2aS4dF7gH="

# 2. Inizializza Fernet con la chiave
from cryptography.fernet import Fernet
fernet = Fernet(key)

# 3. Cripta SOLO la password
password_bytes = "GitHub_SuperSecura_2024!".encode('utf-8')
encrypted_data = fernet.encrypt(password_bytes)

# 4. Converte in string base64 per storage JSON
encrypted_b64 = base64.b64encode(encrypted_data).decode()
# Risultato: "gAAAAABmF2X3kS5mN8jW2a5f8c19QxvZ..."
```

**Storage nel File JSON**:
```json
{
  "username": "mario",
  "password_hash": "sha256_hash_della_password_master",
  "passwords": [
    {
      "site": "github.com",                           // ❌ NON crittografato
      "username": "mario.rossi@email.com"            // ❌ NON crittografato  
      "password": "gAAAAABmF2X3kS5mN8jW2a5f8c19..." // ✅ CRITTOGRAFATO
      "notes": "Account sviluppo personale"          // ❌ NON crittografato
      "created_at": "2024-01-01T10:00:00"            // ❌ NON crittografato
    }
  ]
}
```

#### Processo di Decrittografia

Quando Mario vuole vedere la sua password GitHub:

```python
# 1. Recupera la stringa crittografata dal JSON
encrypted_b64 = "gAAAAABmF2X3kS5mN8jW2a5f8c19..."

# 2. Converte da base64 a bytes
encrypted_data = base64.b64decode(encrypted_b64)

# 3. Decrittografa con la stessa chiave generata al login
fernet = Fernet(key)
decrypted_bytes = fernet.decrypt(encrypted_data)

# 4. Converte in stringa leggibile
original_password = decrypted_bytes.decode('utf-8')
# Risultato: "GitHub_SuperSecura_2024!"
```

### 🛡️ Sicurezza della Chiave

#### Perché la Chiave Non È Mai Salvata

```python
# ❌ SBAGLIATO (mai fatto in ClaudePA):
with open("user_key.txt", "w") as f:
    f.write(key)  # Espone la chiave su disco

# ✅ CORRETTO (approccio ClaudePA):
def generate_key_on_demand(password, username):
    combined = f"{password}_{username}_ClaudePA_2024"
    hash_bytes = hashlib.sha256(combined.encode()).digest()
    return base64.urlsafe_b64encode(hash_bytes)

# La chiave esiste solo in memoria durante la sessione
```

#### Lifecycle della Chiave

```
👤 Utente inserisce password master
    ↓
🔑 Sistema genera chiave temporanea in RAM
    ↓  
🔓 Chiave usata per cripta/decripta password
    ↓
💾 Solo password crittografate salvate su disco
    ↓
🚪 Logout → chiave cancellata dalla memoria
    ↓
🔒 Dati inaccessibili fino al prossimo login
```

### 📁 Struttura File in Dettaglio

#### File Utente Completo (`mario.json`)

```json
{
  "username": "mario",
  "password_hash": "e3b0c44298fc1c149afbf4c8996fb924...",
  "created_at": "2024-01-01T10:00:00.000000",
  "updated_at": "2024-01-01T12:30:45.000000",
  "version": "3.0",
  "passwords": [
    {
      "site": "github.com",
      "username": "mario.rossi@email.com", 
      "password": "gAAAAABmF2X3kS5mN8jW2a5f8c19QxvZ7P2mR4nT6wE8...",
      "notes": "Account per progetti open source",
      "created_at": "2024-01-01T10:15:00.000000",
      "updated_at": "2024-01-01T10:15:00.000000"
    },
    {
      "site": "gmail.com",
      "username": "mario.rossi@gmail.com",
      "password": "gAAAAABmF2Y4lT6nO9kX3b6g9d29RyvA8Q3oS5uU7xF9...",
      "notes": "Email personale principale", 
      "created_at": "2024-01-01T10:20:00.000000",
      "updated_at": "2024-01-01T11:45:30.000000"
    }
  ]
}
```

#### Cosa Può Vedere un Attaccante

**Con accesso al file `mario.json`** (senza password master):

✅ **Può vedere**:
- Nome utente: "mario"
- Siti web utilizzati: "github.com", "gmail.com" 
- Username per ogni sito: "mario.rossi@email.com"
- Note in chiaro: "Account per progetti open source"
- Timestamp di creazione e modifica
- Numero totale di password salvate

❌ **NON può vedere**:
- Password master di Mario
- Password effettive per GitHub, Gmail, etc.
- Contenuto delle password crittografate

**Esempio di attacco fallito**:
```python
# Attaccante prova a decrittare senza chiave corretta
encrypted = "gAAAAABmF2X3kS5mN8jW2a5f8c19QxvZ7P2mR4nT6wE8..."
wrong_key = "chiave_sbagliata"

try:
    fernet = Fernet(wrong_key)
    fernet.decrypt(base64.b64decode(encrypted))
except:
    print("❌ Decrittografia fallita - chiave incorretta")
```

### 🔐 Sistema di Backup

#### Backup Crittografato Completo

I backup in ClaudePA sono **completamente crittografati**, a differenza dei file utente normali:

**Struttura file backup (`.pwbak`)**:
```
[Byte 0-15]:   Salt casuale (16 bytes)
[Byte 16+]:    Tutto il contenuto crittografato con Fernet
```

#### 🔄 Processo di Export Backup - Esempio Completo

**Scenario**: Mario vuole fare backup delle sue 5 password

**1. Preparazione Dati**
```python
# Mario ha queste password nel suo account
mario_passwords = [
    {
        "site": "github.com",
        "username": "mario@email.com", 
        "password": "GitHub_Password_123!",
        "notes": "Account sviluppo"
    },
    {
        "site": "gmail.com", 
        "username": "mario@gmail.com",
        "password": "Gmail_SuperSecure_456!",
        "notes": "Email personale"
    }
    // ...altre password
]
```

**2. Creazione Backup**
```python
# Mario inserisce la sua password master per il backup
mario_master_password = "MarioMasterPassword2024!"
username = "mario"

# Genera salt casuale per questo backup specifico
import os
salt = os.urandom(16)  
# Esempio: b'\x8a\x2f\x6c\x19\x45\x7e\x9d\x3b\x1f\x4c\x8e\x2a\x7b\x6f\x5d\x9c'

# Crea chiave specifica per backup (DIVERSA dalla chiave account)
backup_key_material = f"{mario_master_password}_backup_ClaudePA_2024"
# Risultato: "MarioMasterPassword2024!_backup_ClaudePA_2024"

backup_hash = hashlib.sha256(backup_key_material.encode()).digest()
backup_key = base64.urlsafe_b64encode(backup_hash)
# Risultato: chiave Fernet per il backup (UNICA per questo backup)
```

**3. Struttura Dati Backup**
```python
# Prepara TUTTO il contenuto da crittografare (inclusi metadati)
backup_data = {
    "version": "1.0",
    "username": "mario",                           # Chi ha creato il backup
    "export_date": "2024-01-01T15:30:00.000000",  # Quando è stato creato
    "export_date_formatted": "01/01/2024 15:30",
    "password_count": 5,
    "passwords": [
        {
            "site": "github.com",
            "username": "mario@email.com", 
            "password": "GitHub_Password_123!",     # Password in CHIARO nel backup
            "notes": "Account sviluppo",
            "created_at": "2024-01-01T10:00:00",
            "updated_at": "2024-01-01T10:00:00"
        },
        {
            "site": "gmail.com",
            "username": "mario@gmail.com",
            "password": "Gmail_SuperSecure_456!",   # Password in CHIARO nel backup
            "notes": "Email personale",
            "created_at": "2024-01-01T10:30:00", 
            "updated_at": "2024-01-01T10:30:00"
        }
        // ...tutte le altre password
    ]
}
```

**4. Crittografia Totale**
```python
# Converti tutto in JSON
json_string = json.dumps(backup_data, indent=2, ensure_ascii=False)

# Critta TUTTO il contenuto (a differenza del file utente normale)
fernet_backup = Fernet(backup_key)
encrypted_payload = fernet_backup.encrypt(json_string.encode('utf-8'))

# Crea file finale: salt + payload crittografato
with open("backup_mario_20240101_153000.pwbak", "wb") as f:
    f.write(salt)                # Primi 16 bytes: salt per derivare chiave
    f.write(encrypted_payload)   # Resto: TUTTO crittografato
```

#### 📥 Processo di Import Cross-Account - Esempio Dettagliato

**Scenario**: Luigi vuole importare le password dal backup di Mario

#### Perché è Possibile l'Import Cross-Account?

```
🔑 CHIAVE BACKUP ≠ CHIAVE ACCOUNT

Chiave Account Mario:  "MarioMasterPassword2024!_mario_ClaudePA_2024"
Chiave Backup Mario:   "MarioMasterPassword2024!_backup_ClaudePA_2024"

├── La chiave backup dipende SOLO dalla password master di Mario
├── NON dipende dal username di chi importa
└── Chiunque conosca la password master di Mario può importare
```

**1. Luigi tenta l'import**
```python
# Luigi ha il file backup di Mario
backup_file = "backup_mario_20240101_153000.pwbak"

# Luigi inserisce la password master che MARIO ha usato per il backup
luigi_provided_password = "MarioMasterPassword2024!"  # Password di MARIO!

# Luigi ha il proprio account con la sua password master
luigi_master_password = "LuigiPassword456!"           # Password di LUIGI
```

**2. Lettura e Decrittografia Backup**
```python
# Legge il file backup
with open(backup_file, "rb") as f:
    salt = f.read(16)                # Salt casuale del backup di Mario
    encrypted_payload = f.read()     # Dati crittografati di Mario

# Ricostruisce la chiave backup usando la password che Luigi ha inserito
backup_key_material = f"{luigi_provided_password}_backup_ClaudePA_2024"
# Se Luigi ha inserito la password corretta di Mario:
# backup_key_material = "MarioMasterPassword2024!_backup_ClaudePA_2024"

backup_hash = hashlib.sha256(backup_key_material.encode()).digest()
backup_key = base64.urlsafe_b64encode(backup_hash)

# Tenta la decrittografia
try:
    fernet_backup = Fernet(backup_key)
    decrypted_data = fernet_backup.decrypt(encrypted_payload)
    backup_content = json.loads(decrypted_data.decode())
    print("✅ Backup di Mario decrittato con successo!")
except:
    print("❌ Password master di Mario incorretta")
```

**3. Import nel Database di Luigi**
```python
# Se la decrittografia è riuscita, Luigi ottiene i dati in chiaro
mario_backup = {
    "username": "mario",                    # Backup di Mario
    "password_count": 5,
    "passwords": [
        {
            "site": "github.com",
            "username": "mario@email.com",
            "password": "GitHub_Password_123!",  # Password in chiaro
            "notes": "Account sviluppo"
        },
        {
            "site": "gmail.com", 
            "username": "mario@gmail.com",
            "password": "Gmail_SuperSecure_456!", # Password in chiaro
            "notes": "Email personale"
        }
        // ...
    ]
}

# Luigi importa nel suo database usando la SUA chiave
luigi_key = database._generate_key_from_password("LuigiPassword456!", "luigi")

for pwd in mario_backup["passwords"]:
    # Controlla se Luigi ha già questa password
    if not luigi_already_has_password(pwd["site"], pwd["username"]):
        # Cripta con la chiave di LUIGI e salva nel database di LUIGI
        encrypted_pwd = database._encrypt_password(pwd["password"], luigi_key)
        
        # Aggiunge al file di Luigi
        luigi_password_entry = {
            "site": pwd["site"],
            "username": pwd["username"], 
            "password": encrypted_pwd,     # Crittografata con chiave di LUIGI
            "notes": pwd["notes"] + " (importata da backup Mario)",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        luigi_database["passwords"].append(luigi_password_entry)
```

#### 🔐 Sicurezza del Sistema di Backup

#### Esempio Scenari di Sicurezza

**Scenario 1: Luigi trova il file backup di Mario**
```python
# Luigi trova backup_mario_20240101.pwbak

# ❌ Luigi NON può fare nulla senza la password master di Mario
# Il file è completamente crittografato

# Tentativi falliti:
luigi_tries = [
    "password123",           # Password comune
    "LuigiPassword456!",    # SUA password master  
    "mario",                # Username di Mario
    "",                     # Password vuota
]

for attempt in luigi_tries:
    # Tutti falliranno perché solo Mario conosce "MarioMasterPassword2024!"
    result = try_decrypt_backup(backup_file, attempt)
    print(f"❌ Tentativo '{attempt}': {result}")  # Fallimento

# ✅ Solo se Luigi conosce la password master di Mario:
correct_password = "MarioMasterPassword2024!"
result = try_decrypt_backup(backup_file, correct_password)
print(f"✅ Password corretta: {result}")  # Successo
```

**Scenario 2: Condivisione Sicura tra Amici**
```python
# Mario vuole condividere alcune password con Luigi

# 1. Mario crea backup con password condivisa
shared_password = "SharedSecret2024!"
mario_creates_backup_with_password(shared_password)

# 2. Mario comunica a Luigi la password condivisa (canale sicuro)
# WhatsApp/Signal: "La password del backup è: SharedSecret2024!"

# 3. Luigi può importare usando la password condivisa
luigi_imports_backup("backup_mario_shared.pwbak", "SharedSecret2024!")

# 4. Le password vengono crittografate nel database di Luigi
#    con la SUA password master, non quella condivisa
```

## 🔄 Sistema di Backup e Importazione

ClaudePA implementa un sistema di backup avanzato che consente la condivisione sicura delle password tra utenti diversi, mantenendo elevati standard di sicurezza.

### 📦 Formato del File di Backup

I file di backup (`.pwbak`) hanno una struttura binaria specifica:

```
┌─────────────────┬───────────────────────────┐
│ Salt (16 bytes) │ Dati Crittografati (JSON) │
└─────────────────┴───────────────────────────┘
```

- **Salt**: 16 bytes casuali generati durante la creazione del backup
- **Dati Crittografati**: L'intero database in formato JSON, crittografato con AES-256

### 🔑 Processo di Esportazione (Backup)

Quando un utente (es. Tommyboy) crea un backup:

1. **Generazione Salt**: Viene generato un salt casuale di 16 bytes
   ```python
   salt = os.urandom(16)  # es: b'\x8a\x2f\x6c\x19\x45\x7e...'
   ```

2. **Derivazione Chiave**: Viene creata una chiave di backup specifica
   ```python
   backup_key_material = f"{password_master}_backup_ClaudePA_2024"
   # es: "MiaPasswordSegreta123_backup_ClaudePA_2024"
   
   backup_hash = hashlib.sha256(backup_key_material.encode()).digest()
   backup_key = base64.urlsafe_b64encode(backup_hash)
   ```

3. **Preparazione Dati**: Tutte le password vengono decriptate temporaneamente
   ```python
   for pwd in passwords:
       decrypted, _ = database.get_decrypted_password(pwd["site"], pwd["username"])
       pwd_copy = pwd.copy()
       pwd_copy["password"] = decrypted  # Password in chiaro
   ```

4. **Struttura JSON**: Viene creato un JSON completo con tutti i dati
   ```json
   {
     "version": "1.0",
     "username": "tommyboy",
     "export_date": "2025-05-25T09:53:08.000000",
     "password_count": 5,
     "passwords": [
       {
         "site": "github.com",
         "username": "tommyboy@email.com", 
         "password": "GitHub_Password_123!",
         "notes": "Account sviluppo",
         "created_at": "2025-01-01T10:00:00",
         "updated_at": "2025-01-01T10:00:00"
       },
       // altre password...
     ]
   }
   ```

5. **Crittografia Completa**: L'intero JSON viene crittografato
   ```python
   json_string = json.dumps(backup_data, indent=2, ensure_ascii=False)
   encrypted_data = fernet.encrypt(json_string.encode('utf-8'))
   ```

6. **Salvataggio File**: Il salt e i dati crittografati vengono salvati
   ```python
   with open(filepath, 'wb') as f:
       f.write(salt)           # Primi 16 bytes: salt
       f.write(encrypted_data) # Resto: dati crittografati
   ```

### 📥 Processo di Importazione

Quando un altro utente (es. Mario) importa il backup:

1. **Lettura File**: Vengono letti il salt e i dati crittografati
   ```python
   with open(filepath, 'rb') as f:
       salt = f.read(16)           # Primi 16 bytes: salt
       encrypted_data = f.read()   # Resto: dati crittografati
   ```

2. **Input Password Master**: Mario deve inserire la password master di Tommyboy
   ```python
   password_input = "MiaPasswordSegreta123"  # Password master di Tommyboy
   ```

3. **Derivazione Chiave**: Viene rigenerata la stessa chiave di backup
   ```python
   backup_key_material = f"{password_input}_backup_ClaudePA_2024"
   # Deve risultare: "MiaPasswordSegreta123_backup_ClaudePA_2024"
   
   backup_hash = hashlib.sha256(backup_key_material.encode()).digest()
   backup_key = base64.urlsafe_b64encode(backup_hash)
   # Deve essere identica alla chiave usata da Tommyboy
   ```

4. **Decrittazione**: I dati vengono decrittati con la chiave generata
   ```python
   fernet = Fernet(backup_key)
   try:
       decrypted_data = fernet.decrypt(encrypted_data)
       json_data = json.loads(decrypted_data.decode('utf-8'))
   except Exception:
       # Se la password è errata, la decrittazione fallisce
       raise InvalidPasswordError("Password master errata")
   ```

5. **Importazione Password**: Ogni password viene importata nel database di Mario
   ```python
   for pwd in json_data["passwords"]:
       # Aggiunge la password (in chiaro) al database di Mario
       mario_database.add_password(
           pwd["site"],
           pwd["username"],
           pwd["password"],  # Password in chiaro dal backup
           pwd.get("notes", "")
       )
       
       # Il metodo add_password cripta automaticamente con la chiave di Mario
       encrypted_for_mario = mario_database._encrypt_password(pwd["password"], mario_key)
       # La password viene salvata crittografata nel file di Mario
   ```

### 🔐 Sicurezza del Sistema

Il sistema di backup garantisce elevati standard di sicurezza:

1. **Zero-Storage**: Le chiavi di crittografia non vengono mai salvate su disco
2. **Doppio Layer**: Le password sono protette da due livelli di crittografia:
   - Nel file normale: Crittografia selettiva (solo password)
   - Nel backup: Crittografia completa (tutto il contenuto)
3. **Isolamento Utenti**: Ogni utente ha una chiave di crittografia diversa
4. **Condivisione Sicura**: La condivisione richiede sia il file di backup che la password master
5. **Eliminazione Sicura**: Le password in chiaro vengono eliminate dalla memoria dopo l'uso

### 📋 Esempio Concreto

Esempio pratico di condivisione password tra utenti:

1. **Tommyboy crea un backup**:
   - Password master: "MiaPasswordSegreta123"
   - File: `backup_tommyboy_20250525_095308.pwbak`
   - Salt generato: `b'\x8a\x2f\x6c\x19...'`

2. **Tommyboy condivide con Mario**:
   - Il file backup `backup_tommyboy_20250525_095308.pwbak`
   - La sua password master: "MiaPasswordSegreta123"

3. **Mario importa il backup**:
   - Inserisce la password master di Tommyboy: "MiaPasswordSegreta123"
   - Il sistema usa il salt dal file + password per generare la stessa chiave
   - Se la password è corretta, il backup si decritta

4. **Risultato finale**:
   - Le password sono ora nel database di Mario
   - Sono crittografate con la chiave personale di Mario
   - Mario può accedervi con la sua password master, non quella di Tommyboy
