import re
import string
import secrets
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum

class PasswordStrength(Enum):
    VERY_WEAK = 0
    WEAK = 1
    FAIR = 2
    GOOD = 3
    STRONG = 4
    VERY_STRONG = 5

@dataclass
class PasswordAnalysis:
    """Risultato dell'analisi di una password"""
    strength: PasswordStrength
    score: int  # 0-100
    suggestions: List[str]
    criteria_met: Dict[str, bool]
    color: str

class PasswordValidator:
    """Validatore di password basato su standard NIST/OWASP"""
    
    def __init__(self):
        """
        Inizializza il validatore con una lista delle password più comuni
        Questa lista viene utilizzata per penalizzare password facilmente indovinabili
        """
        # Lista delle 100 password più comuni da evitare assolutamente
        # Basata su dataset di violazioni di sicurezza reali
        self.common_passwords = {
            "password", "123456", "123456789", "12345", "qwerty", "abc123",
            "password123", "admin", "letmein", "welcome", "monkey", "1234567890",
            "123123", "password1", "iloveyou", "11111", "000000", "superman",
            "dragon", "sunshine", "princess", "azerty", "trustno1", "123321",
            "passw0rd", "football", "master", "jordan", "mustang", "access",
            "shadow", "baseball", "696969", "12345678", "hottie", "loveme",
            "batman", "trustno1", "zaq12wsx", "qazwsx", "michael", "michelle"
        }
    
    def analyze_password(self, password: str) -> PasswordAnalysis:
        """
        Analizza la forza di una password usando standard di sicurezza moderni
        
        Args:
            password: La password da analizzare
            
        Returns:
            PasswordAnalysis: Oggetto contenente tutti i risultati dell'analisi
        """
        # Gestisce il caso di password vuota
        if not password:
            return PasswordAnalysis(
                strength=PasswordStrength.VERY_WEAK,
                score=0,
                suggestions=["Inserisci una password"],
                criteria_met={},
                color="#F44336"  # Rosso per indicare pericolo
            )
        
        # Esegue tutti i controlli di sicurezza
        criteria = self._check_criteria(password)
        # Calcola un punteggio da 0 a 100 basato sui criteri soddisfatti
        score = self._calculate_score(password, criteria)
        # Determina il livello di forza generale
        strength = self._determine_strength(score)
        # Genera suggerimenti personalizzati per migliorare la password
        suggestions = self._generate_suggestions(criteria, password)
        # Assegna un colore appropriato per la visualizzazione
        color = self._get_color(strength)
        
        return PasswordAnalysis(
            strength=strength,
            score=score,
            suggestions=suggestions,
            criteria_met=criteria,
            color=color
        )
    
    def _check_criteria(self, password: str) -> Dict[str, bool]:
        """
        Verifica tutti i criteri di sicurezza per una password
        Implementa le linee guida NIST e OWASP per la sicurezza delle password
        """
        return {
            # Criteri di lunghezza progressivi
            "length_8": len(password) >= 8,    # Minimo assoluto
            "length_12": len(password) >= 12,  # Raccomandato
            "length_16": len(password) >= 16,  # Ottimale per sicurezza massima
            
            # Varietà di caratteri (aumenta lo spazio delle possibilità)
            "uppercase": bool(re.search(r'[A-Z]', password)),           # Lettere maiuscole
            "lowercase": bool(re.search(r'[a-z]', password)),           # Lettere minuscole  
            "numbers": bool(re.search(r'\d', password)),                # Cifre numeriche
            "special_chars": bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password)),  # Simboli
            
            # Controlli avanzati per evitare pattern prevedibili
            "no_common": password.lower() not in self.common_passwords,    # Non è una password comune
            "no_repeated": not self._has_repeated_chars(password),          # Evita ripetizioni eccessive
            "no_sequential": not self._has_sequential_chars(password),      # Evita sequenze prevedibili
            "mixed_case": self._has_mixed_case(password),                   # Maiuscole e minuscole mischiate
            "entropy": self._calculate_entropy(password) > 50              # Entropia sufficiente
        }
    
    def _calculate_score(self, password: str, criteria: Dict[str, bool]) -> int:
        """
        Calcola un punteggio da 0 a 100 basato sui criteri di sicurezza soddisfatti
        Implementa un sistema di punteggi ponderato che privilegia diversità e lunghezza
        """
        score = 0
        
        # Punteggio per lunghezza (massimo 30 punti)
        # La lunghezza è il fattore più importante per la sicurezza
        if criteria["length_16"]:
            score += 30  # Lunghezza eccellente
        elif criteria["length_12"]:
            score += 20  # Lunghezza buona
        elif criteria["length_8"]:
            score += 10  # Lunghezza minima accettabile
        
        # Punteggio per varietà di caratteri (massimo 40 punti)
        # Ogni tipo di carattere aumenta esponenzialmente lo spazio delle possibilità
        if criteria["uppercase"]:
            score += 10
        if criteria["lowercase"]:
            score += 10
        if criteria["numbers"]:
            score += 10
        if criteria["special_chars"]:
            score += 10
        
        # Punteggio per criteri avanzati (massimo 30 punti)
        # Questi criteri prevengono attacchi basati su pattern comuni
        if criteria["no_common"]:
            score += 10  # Molto importante: evita password da dizionario
        if criteria["no_repeated"]:
            score += 5   # Evita pattern ripetitivi
        if criteria["no_sequential"]:
            score += 5   # Evita sequenze prevedibili
        if criteria["mixed_case"]:
            score += 5   # Migliora la casualità
        if criteria["entropy"]:
            score += 5   # Misura della casualità complessiva
        
        return min(score, 100)  # Assicura che il punteggio non superi 100
    
    def _determine_strength(self, score: int) -> PasswordStrength:
        """
        Converte il punteggio numerico in un livello di forza categorico
        Basato su standard industriali per la classificazione delle password
        """
        if score >= 90:
            return PasswordStrength.VERY_STRONG    # Eccellente (90-100)
        elif score >= 70:
            return PasswordStrength.STRONG         # Forte (70-89)
        elif score >= 50:
            return PasswordStrength.GOOD           # Buona (50-69)
        elif score >= 30:
            return PasswordStrength.FAIR           # Discreta (30-49)
        elif score >= 10:
            return PasswordStrength.WEAK           # Debole (10-29)
        else:
            return PasswordStrength.VERY_WEAK      # Molto debole (0-9)
    
    def _generate_suggestions(self, criteria: Dict[str, bool], password: str) -> List[str]:
        """
        Genera suggerimenti personalizzati basati sui criteri non soddisfatti
        Fornisce consigli specifici e actionable per migliorare la password
        """
        suggestions = []
        
        # Suggerimenti progressivi per la lunghezza
        if not criteria["length_8"]:
            suggestions.append("Usa almeno 8 caratteri")
        elif not criteria["length_12"]:
            suggestions.append("Meglio se usi almeno 12 caratteri")
        elif not criteria["length_16"]:
            suggestions.append("Ottimo se usi 16+ caratteri per massima sicurezza")
        
        # Suggerimenti per diversificare i tipi di caratteri
        if not criteria["uppercase"]:
            suggestions.append("Aggiungi lettere maiuscole (A-Z)")
        
        if not criteria["lowercase"]:
            suggestions.append("Aggiungi lettere minuscole (a-z)")
        
        if not criteria["numbers"]:
            suggestions.append("Aggiungi numeri (0-9)")
        
        if not criteria["special_chars"]:
            suggestions.append("Aggiungi caratteri speciali (!@#$%^&*)")
        
        # Suggerimenti per evitare pattern insicuri
        if not criteria["no_common"]:
            suggestions.append("Evita password comuni")
        
        if not criteria["no_repeated"]:
            suggestions.append("Evita caratteri ripetuti consecutivi")
        
        if not criteria["no_sequential"]:
            suggestions.append("Evita sequenze consecutive (123, abc)")
        
        # Messaggio di congratulazioni per password eccellenti
        if not suggestions:
            suggestions.append("Password eccellente! 🎉")
        
        return suggestions
    
    def _get_color(self, strength: PasswordStrength) -> str:
        """
        Restituisce il codice colore appropriato per visualizzare il livello di forza
        Usa una scala cromatica intuitiva dal rosso (pericoloso) al verde (sicuro)
        """
        colors = {
            PasswordStrength.VERY_WEAK: "#F44336",    # Rosso intenso - Pericolo
            PasswordStrength.WEAK: "#FF5722",         # Rosso arancio - Attenzione
            PasswordStrength.FAIR: "#FF9800",         # Arancione - Migliorabile
            PasswordStrength.GOOD: "#FFC107",         # Giallo - Accettabile
            PasswordStrength.STRONG: "#8BC34A",       # Verde chiaro - Buona
            PasswordStrength.VERY_STRONG: "#4CAF50"   # Verde intenso - Eccellente
        }
        return colors[strength]
    
    def _has_repeated_chars(self, password: str) -> bool:
        """
        Verifica se la password contiene 3 o più caratteri identici consecutivi
        Pattern come 'aaa' o '111' rendono la password più vulnerabile
        """
        for i in range(len(password) - 2):
            if password[i] == password[i+1] == password[i+2]:
                return True
        return False
    
    def _has_sequential_chars(self, password: str) -> bool:
        """
        Cerca sequenze consecutive prevedibili nella password
        Include sequenze numeriche, alfabetiche e di tastiera
        """
        # Definisce le sequenze comuni da evitare
        sequences = [
            "0123456789",                            # Sequenza numerica
            "abcdefghijklmnopqrstuvwxyz",           # Alfabeto
            "qwertyuiopasdfghjklzxcvbnm"            # Layout tastiera QWERTY
        ]
        
        password_lower = password.lower()
        for seq in sequences:
            # Controlla sequenze di 3+ caratteri in entrambe le direzioni
            for i in range(len(seq) - 2):
                substring = seq[i:i+3]
                # Verifica sia la sequenza normale che quella inversa
                if substring in password_lower or substring[::-1] in password_lower:
                    return True
        return False
    
    def _has_mixed_case(self, password: str) -> bool:
        """
        Verifica se la password ha maiuscole e minuscole distribuite
        Non solo la prima lettera maiuscola, ma un mix reale
        """
        # Esclude il primo carattere per evitare il bias della prima lettera maiuscola
        has_upper = any(c.isupper() for c in password[1:])
        has_lower = any(c.islower() for c in password)
        return has_upper and has_lower
    
    def _calculate_entropy(self, password: str) -> float:
        """
        Calcola l'entropia della password (misura della casualità)
        Maggiore entropia = password più difficile da indovinare
        """
        if not password:
            return 0
        
        # Determina il pool di caratteri
        pool_size = 0
        if any(c.islower() for c in password):
            pool_size += 26
        if any(c.isupper() for c in password):
            pool_size += 26
        if any(c.isdigit() for c in password):
            pool_size += 10
        if any(c in "!@#$%^&*(),.?\":{}|<>" for c in password):
            pool_size += 18
        
        # Entropia = log2(pool_size) * lunghezza
        import math
        if pool_size > 0:
            return math.log2(pool_size) * len(password)
        return 0

class SecurePasswordGenerator:
    """Generatore di password sicure"""
    
    def __init__(self):
        self.validator = PasswordValidator()
    
    def generate_strong_password(self, length: int = 16, include_symbols: bool = True) -> str:
        """Genera una password forte che rispetta i criteri di sicurezza"""
        # Assicurati lunghezza minima
        length = max(length, 12)
        
        # Pool di caratteri
        lowercase = string.ascii_lowercase
        uppercase = string.ascii_uppercase
        digits = string.digits
        symbols = "!@#$%^&*(),.?\":{}|<>" if include_symbols else ""
        
        # Garantisci almeno un carattere di ogni tipo
        password = [
            secrets.choice(lowercase),
            secrets.choice(uppercase),
            secrets.choice(digits),
        ]
        
        if include_symbols:
            password.append(secrets.choice(symbols))
        
        # Riempie il resto
        all_chars = lowercase + uppercase + digits + symbols
        remaining_length = length - len(password)
        
        for _ in range(remaining_length):
            password.append(secrets.choice(all_chars))
        
        # Mischia la password
        secrets.SystemRandom().shuffle(password)
        
        final_password = ''.join(password)
        
        # Verifica che soddisfi i criteri, altrimenti rigenera
        analysis = self.validator.analyze_password(final_password)
        if analysis.strength.value < PasswordStrength.STRONG.value:
            return self.generate_strong_password(length, include_symbols)
        
        return final_password
    
    def generate_memorable_password(self) -> str:
        """Genera una password memorabile ma sicura usando parole casuali"""
        # Lista di parole comuni ma sicure
        words = [
            "Castle", "Ocean", "Mountain", "Forest", "River", "Thunder", "Lightning",
            "Phoenix", "Dragon", "Tiger", "Eagle", "Wolf", "Bear", "Lion",
            "Crystal", "Diamond", "Ruby", "Emerald", "Silver", "Golden",
            "Storm", "Wind", "Fire", "Ice", "Star", "Moon", "Sun",
            "Magic", "Power", "Energy", "Force", "Spirit", "Dream", "Hope"
        ]
        
        # Seleziona 3-4 parole casuali
        num_words = secrets.randbelow(2) + 3  # 3 o 4 parole
        selected_words = secrets.SystemRandom().sample(words, num_words)
        
        # Aggiungi numeri e simboli
        separator = secrets.choice("!@#$%&*")
        numbers = str(secrets.randbelow(100)).zfill(2)
        
        password = separator.join(selected_words) + numbers + separator
        
        return password
