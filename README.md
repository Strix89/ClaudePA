# Password Manager - Versione Semplificata

Una versione semplificata e migliorata del password manager con gestione avanzata del tema.

## Caratteristiche

- 🎨 **Sistema di tema avanzato** con observer pattern
- 🔒 **Crittografia sicura** usando cryptography library
- 🎯 **Architettura semplificata** e modulare
- 📱 **Interfaccia responsive** con CustomTkinter
- 🌓 **Temi Light/Dark/System** con cambio automatico
- 💾 **Backup sicuro** delle password

## Installazione

1. Installa le dipendenze:
```bash
pip install -r requirements.txt
```

2. Avvia l'applicazione:
```bash
python main.py
```

## Struttura del Progetto

```
new_version/
├── main.py              # Entry point dell'applicazione
├── core/                # Moduli core
│   ├── __init__.py
│   ├── app.py          # Applicazione principale
│   ├── theme.py        # Sistema di gestione tema
│   ├── components.py   # Componenti UI con tema automatico
│   └── database.py     # Gestione database e crittografia
├── ui/                 # Interfacce utente
│   ├── __init__.py
│   ├── login_view.py   # Vista login
│   ├── register_view.py # Vista registrazione
│   └── dashboard_view.py # Vista dashboard
├── data/               # Directory dati (creata automaticamente)
│   ├── users/          # File utenti
│   └── backups/        # Backup
├── requirements.txt    # Dipendenze
└── README.md          # Questo file
```

## Miglioramenti Rispetto alla Versione Originale

### 1. Sistema di Tema Avanzato
- **Observer Pattern**: I componenti si aggiornano automaticamente
- **Gestione centralizzata**: Un unico ThemeManager per tutta l'app
- **Colori semantici**: Schema colori più coerente e professionale

### 2. Architettura Migliorata
- **Separazione delle responsabilità**: Core, UI e Data separati
- **Componenti riutilizzabili**: ThemedWidget base per tutti i componenti
- **Gestione automatica dei colori**: Nessun colore hardcoded

### 3. Sicurezza
- **Crittografia moderna**: Uso di cryptography library
- **Derivazione chiavi PBKDF2**: 100,000 iterazioni
- **Salt casuali**: Ogni utente ha un salt unico

### 4. Usabilità
- **Interfaccia semplificata**: Meno opzioni, più chiara
- **Feedback visivo migliore**: Messaggi di stato chiari
- **Generatore password integrato**: Password sicure con un click

## Utilizzo

1. **Primo avvio**: Registra un nuovo account
2. **Login**: Accedi con le tue credenziali
3. **Gestione password**: Aggiungi, modifica, elimina password
4. **Cambio tema**: Usa il selettore in alto a destra

## Note di Sicurezza

- Le password master non possono essere recuperate
- Tutti i dati sono crittografati localmente
- Nessun dato viene inviato online
- Backup consigliati regolarmente
