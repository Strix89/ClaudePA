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
- **Derivazione chiavi PBKDF2** con 100.000 iterazioni
- **Salt casuali** per ogni utente
- **Password master non recuperabile** (zero-knowledge)
- **Backup crittografati** con password master

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

### Schema di Crittografia

#### 1. Generazione Chiave Utente
```python
# Combinazione password + username per unicità
combined = f"{password}_{username}_ClaudePA_2024"
hash_bytes = hashlib.sha256(combined.encode()).digest()
key = base64.urlsafe_b64encode(hash_bytes)  # Chiave Fernet compatibile
```

#### 2. Crittografia Selettiva
```json
{
  "username": "mario",                    // ❌ NON crittografato
  "password_hash": "abc123...",          // ❌ NON crittografato (hash)
  "created_at": "2024-01-01T10:00:00",   // ❌ NON crittografato
  "passwords": [
    {
      "site": "example.com",             // ❌ NON crittografato
      "username": "mario@email.com",     // ❌ NON crittografato
      "password": "gAAAAABh...",         // ✅ CRITTOGRAFATO (Fernet)
      "notes": "Note in chiaro"          // ❌ NON crittografato
    }
  ]
}
```

#### 3. Backup Sicuri
```python
# Struttura file backup (.pwbak)
[16 bytes: salt casuale] + [payload crittografato con Fernet]

# Derivazione chiave backup
key = derive_key(master_password + "_backup_ClaudePA_2024")
```

### Threat Model

#### ✅ Protetto Contro
- **Accesso fisico al computer** (file crittografati)
- **Malware** che legge file (password crittografate)
- **Backup compromessi** (crittografia con password master)
- **Rainbow table attacks** (salt casuali)
- **Brute force offline** (PBKDF2 con 100k iterazioni)

#### ⚠️ NON Protetto Contro
- **Keylogger** durante inserimento password master
- **Memory dump** durante esecuzione (password in RAM)
- **Screen capture** quando password sono visibili
- **Social engineering** per ottenere password master

---

## 📚 Guida Utente

### 🔑 Primo Utilizzo

#### 1. Registrazione Account
1. Avvia l'applicazione con `python main.py`
2. Clicca **"Crea Nuovo Account"**
3. Inserisci:
   - **Username**: minimo 3 caratteri, univoco
   - **Password Master**: minimo 8 caratteri, sicura
   - **Conferma Password**: deve corrispondere
4. Clicca **"Crea Account"**

#### 2. Primo Login
1. Inserisci username e password master
2. Clicca **"Accedi"**
3. Verrai reindirizzato alla dashboard principale

### 🎯 Gestione Password

#### Aggiungere Nuova Password
1. Nella dashboard, clicca **"➕ Nuova"**
2. Compila i campi:
   - **Sito**: URL o nome servizio
   - **Username**: email o username
   - **Password**: usa il generatore o inserisci manualmente
   - **Note**: informazioni aggiuntive (opzionale)
3. Clicca **"💾 Salva Nuova"**

#### Modificare Password Esistente
1. Seleziona la password dalla lista a sinistra
2. Modifica i campi necessari nell'editor
3. Clicca **"💾 Salva Modifiche"**

#### Eliminare Password
1. Seleziona la password dalla lista
2. Clicca **"🗑️ Elimina"**
3. Conferma l'eliminazione nel dialog

### 🎨 Personalizzazione Tema

#### Cambio Tema Manuale
- Clicca l'icona tema (🌙/☀️) in alto a destra
- I colori si aggiornano automaticamente in tutta l'app

#### Temi Disponibili
- **🌞 Light Mode**: colori chiari per uso diurno
- **🌙 Dark Mode**: colori scuri per uso notturno
- **🖥️ System**: segue automaticamente il tema di sistema

### 💾 Gestione Backup

#### Creare Backup
1. Clicca **"💾 Backup & Restore"**
2. Nella sezione **"📤 Esporta Password"**
3. Clicca **"🔐 Crea Backup Adesso"**
4. Inserisci la password master per conferma
5. Il file `.pwbak` viene salvato in `data/backups/`

#### Ripristinare Backup
1. Vai alla sezione **"📥 Importa Password"**
2. Clicca **"📂 Sfoglia"** e seleziona il file `.pwbak`
3. Inserisci la password master del backup
4. Clicca **"📥 Importa dal Backup"**
5. Conferma l'importazione nel dialog

### 🔍 Ricerca e Filtri

#### Ricerca Veloce
- Usa la barra di ricerca sopra la lista password
- Cerca per nome sito o username
- I risultati si aggiornano in tempo reale

#### Conteggio Password
- Visualizza il numero totale di password nell'header
- Mostra risultati filtrati durante la ricerca

---

## 🔧 Documentazione Tecnica

### Database Schema

#### User File Structure (`data/users/{username}.json`)
```json
{
  "username": "mario",
  "password_hash": "sha256_hash_della_password_master",
  "created_at": "2024-01-01T10:00:00.000000",
  "updated_at": "2024-01-01T12:00:00.000000", 
  "version": "3.0",
  "passwords": [
    {
      "site": "github.com",
      "username": "mario@email.com",
      "password": "gAAAAABhZ_encrypted_password_here",
      "notes": "Account sviluppo personale",
      "created_at": "2024-01-01T10:00:00.000000",
      "updated_at": "2024-01-01T10:00:00.000000"
    }
  ]
}
```

#### Backup File Structure (`data/backups/backup_{user}_{timestamp}.pwbak`)
```
[Byte 0-15]:   Salt casuale (16 bytes)
[Byte 16+]:    Payload JSON crittografato con Fernet
```

### Theme System

#### Color Schemes
```python
LIGHT_COLORS = {
    'primary': '#1f538d',      # Blu principale
    'secondary': '#f0f0f0',    # Grigio chiaro
    'surface': '#ffffff',      # Bianco superficie
    'background': '#fafafa',   # Sfondo principale
    'text': '#2b2b2b',        # Testo principale
    'text_secondary': '#666666', # Testo secondario
    'accent': '#0d47a1',      # Accento
    'error': '#d32f2f',       # Errore
    'border': '#e0e0e0',      # Bordi
    'hover': '#e3f2fd'        # Hover
}

DARK_COLORS = {
    'primary': '#90caf9',      # Blu chiaro
    'secondary': '#424242',    # Grigio scuro
    'surface': '#2e2e2e',      # Superficie scura
    'background': '#1e1e1e',   # Sfondo scuro
    'text': '#ffffff',         # Testo bianco
    'text_secondary': '#b0b0b0', # Testo grigio chiaro
    'accent': '#64b5f6',       # Accento chiaro
    'error': '#f44336',        # Errore
    'border': '#555555',       # Bordi scuri
    'hover': '#3e3e3e'         # Hover scuro
}
```

#### Component Styles
```python
# Stili disponibili per i componenti
COMPONENT_STYLES = {
    'primary',    # Colore principale (pulsanti importanti)
    'secondary',  # Colore secondario (pulsanti normali)
    'surface',    # Superficie (frame, card)
    'background', # Sfondo (finestre principali)
    'danger',     # Azioni pericolose (eliminazione)
    'accent'      # Evidenziazione speciale
}
```

### Password Generator

#### Algoritmo di Generazione
```python
CHARACTER_SETS = {
    'lowercase': 'abcdefghijklmnopqrstuvwxyz',
    'uppercase': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 
    'digits': '0123456789',
    'symbols': '!@#$%^&*()_+-=[]{}|;:,.<>?'
}

# Assicura almeno un carattere per ogni set selezionato
# Riempie il resto con selezione casuale da tutti i set
# Shuffle finale per randomizzare posizioni
```

### Memory Management

#### Widget Cleanup
```python
def _clear_current_view(self):
    # 1. Completa operazioni pending
    self.update_idletasks()
    
    # 2. Distruzione ricorsiva widget
    for child in list(self.main_frame.winfo_children()):
        self._destroy_widget_safely(child)
    
    # 3. Reset riferimenti
    self.current_view = None
    
    # 4. Garbage collection
    import gc
    gc.collect()
```

### Error Handling

#### Livelli di Error Handling
1. **UI Level**: Messaggi utente user-friendly
2. **Logic Level**: Logging per debugging  
3. **System Level**: Graceful degradation
4. **Critical Level**: Safe shutdown

---

## 📖 API Reference

### Core Classes

#### `PasswordManagerApp`
```python
class PasswordManagerApp(ctk.CTk):
    def __init__(self)
    def _show_login(self)
    def _show_register(self) 
    def _show_dashboard(self)
    def _show_backup(self)
    def _on_login_success(self)
    def _on_logout(self)
```

#### `PasswordDatabase`
```python
class PasswordDatabase:
    def __init__(self, data_dir: str)
    def register_user(self, username: str, password: str) -> Tuple[bool, str]
    def login(self, username: str, password: str) -> Tuple[bool, str]
    def add_password(self, site: str, username: str, password: str, notes: str) -> Tuple[bool, str]
    def get_passwords(self) -> List[Dict]
    def get_decrypted_password(self, site: str, username: str) -> Tuple[str, str]
    def delete_password(self, site: str, username: str) -> Tuple[bool, str]
    def logout(self)
```

#### `ThemeManager`
```python
class ThemeManager:
    def set_mode(self, mode: ThemeMode)
    def toggle_mode(self) -> str
    def get_current_mode(self) -> str
    def get_colors(self) -> Dict[str, str]
    def add_observer(self, callback: Callable)
    def remove_observer(self, callback: Callable)
```

#### `BackupManager`
```python
class BackupManager:
    def export_passwords(self, username: str, master_password: str, passwords: List[Dict]) -> Tuple[bool, str]
    def import_passwords(self, filepath: str, master_password: str) -> Tuple[bool, str, Dict]
    def list_backups(self) -> List[Dict]
    def delete_backup(self, filepath: str) -> Tuple[bool, str]
```

### Themed Components

#### `ThemedWidget` (Base Class)
```python
class ThemedWidget:
    def __init__(self)
    def _apply_theme(self)
    def _update_theme(self)  # Observer callback
    def destroy(self)        # Cleanup automatico
```

#### Component Hierarchy
```
ThemedWidget (base)
├── ThemedFrame
├── ThemedLabel  
├── ThemedButton
├── ThemedEntry
└── MessageDialog
```

---

## 🔧 Troubleshooting

### Problemi Comuni

#### ❌ Errore "ModuleNotFoundError: No module named 'customtkinter'"
```bash
# Soluzione
pip install customtkinter>=5.2.0
```

#### ❌ Errore "ModuleNotFoundError: No module named 'cryptography'"
```bash
# Soluzione
pip install cryptography>=41.0.0

# Su alcuni sistemi potrebbe servire:
pip install --upgrade pip
pip install cryptography
```

#### ❌ Password dimenticata
```
❌ IMPOSSIBILE RECUPERARE
Le password master non sono recuperabili per design.
Dovrai creare un nuovo account.
```

#### ❌ File utente corrotto
```bash
# Verifica integrità
python -c "
from core.database import PasswordDatabase
db = PasswordDatabase()
print(db.debug_user_file('tuo_username'))
"
```

#### ❌ Tema non si applica
```python
# Reset tema manuale
from core.theme import theme_manager
theme_manager.set_mode('light')
theme_manager.notify_observers()
```

#### ❌ Backup corrotto
```bash
# Verifica backup
python -c "
from core.backup import BackupManager
bm = BackupManager()
backups = bm.list_backups()
for b in backups: print(b['filename'], b['size'])
"
```

### Performance Issues

#### 🐌 App lenta all'avvio
- Controlla le dimensioni dei file in `data/users/`
- File >10MB potrebbero indicare problemi
- Prova a ricreare l'account se necessario

#### 🐌 Ricerca lenta
- La ricerca diventa lenta con >1000 password
- Considera di organizzare meglio le password
- Usa nomi siti più specifici

### Logging e Debug

#### Abilitare Debug Mode
```python
# In main.py aggiungi:
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### File di Log
- I log vengono stampati su console
- Per salvare su file: `python main.py > app.log 2>&1`

---

## 🚀 TODO e Roadmap

### 📱 Sviluppo Mobile

#### Android App
- [ ] **Kivy/BeeWare** port per Android nativo
- [ ] **Sincronizzazione cloud** sicura (end-to-end encryption)
- [ ] **Biometric authentication** (fingerprint, face unlock)
- [ ] **Auto-fill service** per browser e app Android
- [ ] **Quick access widget** per password frequenti
- [ ] **Secure keyboard** integrata per input password
- [ ] **Play Store** publishing e distribuzione

#### iOS App (Future)
- [ ] **React Native** o **Flutter** implementation
- [ ] **KeyChain** integration per iOS
- [ ] **App Store** compliance e review process

### 💻 Distribuzione Desktop

#### Windows Executable
- [ ] **PyInstaller** bundle completo
- [ ] **Windows Installer** (.msi) con WiX
- [ ] **Code signing** per evitare warning SmartScreen
- [ ] **Auto-updater** integrato
- [ ] **Windows Store** submission
- [ ] **Portable version** senza installazione
- [ ] **Registry integration** per associazioni file

#### macOS App Bundle  
- [ ] **py2app** packaging per macOS
- [ ] **DMG installer** con interfaccia grafica
- [ ] **Apple Developer** certificate e notarization
- [ ] **macOS Big Sur+** compatibility e design guidelines
- [ ] **App Store** submission (sandboxing compliance)
- [ ] **Universal Binary** (Intel + Apple Silicon)

#### Linux Distribution
- [ ] **AppImage** per distribuzione universale
- [ ] **Snap package** per Ubuntu Store
- [ ] **Flatpak** per Flathub
- [ ] **DEB package** per Debian/Ubuntu
- [ ] **RPM package** per RedHat/Fedora
- [ ] **AUR package** per Arch Linux

### 🎨 Migliorie Grafiche e UI/UX

#### Responsive Design
- [ ] **Adaptive layouts** per schermi 4K/8K
- [ ] **Mobile-friendly** touch interface
- [ ] **Tablet mode** con gesture support
- [ ] **High DPI scaling** automatico
- [ ] **Multi-monitor** support migliorato
- [ ] **Window state persistence** (posizione, dimensioni)

#### Accessibilità
- [ ] **Screen reader** compatibility (ARIA labels)
- [ ] **Keyboard navigation** completa
- [ ] **High contrast** themes per ipovedenti
- [ ] **Font scaling** per diverse esigenze visive
- [ ] **Color blind** friendly color schemes
- [ ] **Voice control** integration (Windows Speech)

#### Advanced UI Features
- [ ] **Dashboard widgets** personalizzabili
- [ ] **Password strength visualization** avanzata
- [ ] **Usage analytics** e statistiche personali
- [ ] **Quick actions** toolbar personalizzabile
- [ ] **Drag & drop** per riorganizzare password
- [ ] **Split view** per gestione multi-account
- [ ] **Floating mini-window** per quick access

### 🔐 Sicurezza Avanzata

#### Authentication
- [ ] **Two-factor authentication** (TOTP)
- [ ] **Hardware key** support (YubiKey, FIDO2)
- [ ] **Biometric unlock** (Windows Hello, Touch ID)
- [ ] **Smart card** authentication
- [ ] **SSO integration** con provider enterprise

#### Encryption Enhancements
- [ ] **Post-quantum cryptography** preparedness
- [ ] **Hardware security module** (HSM) support
- [ ] **Secure enclave** utilization dove disponibile
- [ ] **Memory protection** avanzata (mlock, secure_malloc)
- [ ] **Anti-forensics** features

### 🌐 Cloud e Sync

#### Sincronizzazione Sicura
- [ ] **End-to-end encrypted** sync via cloud
- [ ] **Self-hosted server** option (Docker)
- [ ] **Conflict resolution** automatica
- [ ] **Offline-first** architecture
- [ ] **Delta sync** per efficienza bandwidth
- [ ] **Multi-device** session management

#### Cloud Providers
- [ ] **Google Drive** encrypted backup
- [ ] **OneDrive** integration
- [ ] **Dropbox** support
- [ ] **iCloud** per ecosystem Apple
- [ ] **Custom WebDAV** servers

### 📊 Features Avanzate

#### Password Management
- [ ] **Password sharing** sicuro tra utenti
- [ ] **Team/Family** accounts con permessi
- [ ] **Password expiration** notifications
- [ ] **Breach monitoring** con database HaveIBeenPwned
- [ ] **Password history** e versioning
- [ ] **Secure notes** con rich text editor
- [ ] **File attachment** crittografati

#### Automation e Integrazione
- [ ] **Browser extensions** (Chrome, Firefox, Safari)
- [ ] **CLI interface** per scripting
- [ ] **API REST** per integrazioni
- [ ] **SSH key management**
- [ ] **Certificate storage** e management
- [ ] **AWS/Azure** credentials manager

#### Enterprise Features
- [ ] **Active Directory** integration
- [ ] **LDAP authentication**
- [ ] **Group policies** enforcement
- [ ] **Audit logging** avanzato
- [ ] **Compliance reporting** (SOC2, GDPR)
- [ ] **Backup to enterprise** storage

### 🔬 Tecnologie Future

#### AI e Machine Learning
- [ ] **Smart password suggestions** basate su pattern utente
- [ ] **Phishing detection** automatica
- [ ] **Anomaly detection** per accessi sospetti
- [ ] **Password strength prediction** avanzata

#### Emerging Technologies
- [ ] **Blockchain** per timestamping e audit trail
- [ ] **WebAssembly** per performance critiche
- [ ] **Progressive Web App** (PWA) version
- [ ] **Electron alternative** evaluation (Tauri, Neutralino)

---

## 🤝 Contribuire

### 🐛 Segnalazione Bug
1. Controlla i [GitHub Issues](https://github.com/tuoUsername/ClaudePA/issues) esistenti
2. Crea un nuovo issue con:
   - **Descrizione dettagliata** del problema
   - **Steps to reproduce** il bug
   - **Environment info** (OS, Python version, etc.)
   - **Screenshot** se applicabile
   - **Log files** se disponibili

### 💡 Nuove Features
1. **Discussione**: apri un issue per discutere la feature
2. **Design doc**: crea un documento di design se complessa
3. **Implementation**: sviluppa seguendo le convenzioni esistenti
4. **Testing**: aggiungi test appropriati
5. **Documentation**: aggiorna README e documenti

### 🔧 Development Setup
```bash
# 1. Fork del repository
git clone https://github.com/tuoUsername/ClaudePA.git
cd ClaudePA

# 2. Crea virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oppure
venv\Scripts\activate     # Windows

# 3. Installa in development mode
pip install -e .
pip install -r requirements-dev.txt

# 4. Setup pre-commit hooks
pre-commit install

# 5. Run tests
python -m pytest tests/
```

### 📝 Coding Standards
- **PEP 8** compliance per Python code
- **Type hints** obbligatori per funzioni pubbliche
- **Docstrings** in formato Google style
- **Unit tests** per nuove funzionalità
- **Error handling** appropriato con logging

### 🏷️ Versioning
Seguiamo [Semantic Versioning](https://semver.org/):
- **MAJOR**: breaking changes
- **MINOR**: nuove feature backward-compatible
- **PATCH**: bug fixes

---

## 📄 Licenza

Questo progetto è rilasciato sotto licenza **MIT License**.

```
MIT License

Copyright (c) 2024 ClaudePA Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 📞 Supporto e Contatti

- **GitHub Issues**: [Issues](https://github.com/tuoUsername/ClaudePA/issues)
- **Discussions**: [GitHub Discussions](https://github.com/tuoUsername/ClaudePA/discussions)  
- **Email**: support@claudepa.com
- **Discord**: [ClaudePA Community](https://discord.gg/claudepa)

### 🙏 Riconoscimenti

- **CustomTkinter** team per l'eccellente UI framework
- **Cryptography** library developers per la sicurezza
- **Python** community per l'ecosistema fantastico
- Tutti i **beta testers** e **contributors**

---

*Ultimo aggiornamento: Maggio 2025*
*Versione documentazione: 1.0*
