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
        # Lista di password comuni da evitare (top 100)
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
        """Analizza la forza di una password"""
        if not password:
            return PasswordAnalysis(
                strength=PasswordStrength.VERY_WEAK,
                score=0,
                suggestions=["Inserisci una password"],
                criteria_met={},
                color="#F44336"
            )
        
        criteria = self._check_criteria(password)
        score = self._calculate_score(password, criteria)
        strength = self._determine_strength(score)
        suggestions = self._generate_suggestions(criteria, password)
        color = self._get_color(strength)
        
        return PasswordAnalysis(
            strength=strength,
            score=score,
            suggestions=suggestions,
            criteria_met=criteria,
            color=color
        )
    
    def _check_criteria(self, password: str) -> Dict[str, bool]:
        """Verifica i criteri di sicurezza"""
        return {
            "length_8": len(password) >= 8,
            "length_12": len(password) >= 12,
            "length_16": len(password) >= 16,
            "uppercase": bool(re.search(r'[A-Z]', password)),
            "lowercase": bool(re.search(r'[a-z]', password)),
            "numbers": bool(re.search(r'\d', password)),
            "special_chars": bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password)),
            "no_common": password.lower() not in self.common_passwords,
            "no_repeated": not self._has_repeated_chars(password),
            "no_sequential": not self._has_sequential_chars(password),
            "mixed_case": self._has_mixed_case(password),
            "entropy": self._calculate_entropy(password) > 50
        }
    
    def _calculate_score(self, password: str, criteria: Dict[str, bool]) -> int:
        """Calcola il punteggio della password (0-100)"""
        score = 0
        
        # Lunghezza (max 30 punti)
        if criteria["length_16"]:
            score += 30
        elif criteria["length_12"]:
            score += 20
        elif criteria["length_8"]:
            score += 10
        
        # Varietà caratteri (max 40 punti)
        if criteria["uppercase"]:
            score += 10
        if criteria["lowercase"]:
            score += 10
        if criteria["numbers"]:
            score += 10
        if criteria["special_chars"]:
            score += 10
        
        # Criteri avanzati (max 30 punti)
        if criteria["no_common"]:
            score += 10
        if criteria["no_repeated"]:
            score += 5
        if criteria["no_sequential"]:
            score += 5
        if criteria["mixed_case"]:
            score += 5
        if criteria["entropy"]:
            score += 5
        
        return min(score, 100)
    
    def _determine_strength(self, score: int) -> PasswordStrength:
        """Determina il livello di forza basato sul punteggio"""
        if score >= 90:
            return PasswordStrength.VERY_STRONG
        elif score >= 70:
            return PasswordStrength.STRONG
        elif score >= 50:
            return PasswordStrength.GOOD
        elif score >= 30:
            return PasswordStrength.FAIR
        elif score >= 10:
            return PasswordStrength.WEAK
        else:
            return PasswordStrength.VERY_WEAK
    
    def _generate_suggestions(self, criteria: Dict[str, bool], password: str) -> List[str]:
        """Genera suggerimenti per migliorare la password"""
        suggestions = []
        
        if not criteria["length_8"]:
            suggestions.append("Usa almeno 8 caratteri")
        elif not criteria["length_12"]:
            suggestions.append("Meglio se usi almeno 12 caratteri")
        elif not criteria["length_16"]:
            suggestions.append("Ottimo se usi 16+ caratteri per massima sicurezza")
        
        if not criteria["uppercase"]:
            suggestions.append("Aggiungi lettere maiuscole (A-Z)")
        
        if not criteria["lowercase"]:
            suggestions.append("Aggiungi lettere minuscole (a-z)")
        
        if not criteria["numbers"]:
            suggestions.append("Aggiungi numeri (0-9)")
        
        if not criteria["special_chars"]:
            suggestions.append("Aggiungi caratteri speciali (!@#$%^&*)")
        
        if not criteria["no_common"]:
            suggestions.append("Evita password comuni")
        
        if not criteria["no_repeated"]:
            suggestions.append("Evita caratteri ripetuti consecutivi")
        
        if not criteria["no_sequential"]:
            suggestions.append("Evita sequenze consecutive (123, abc)")
        
        if not suggestions:
            suggestions.append("Password eccellente! 🎉")
        
        return suggestions
    
    def _get_color(self, strength: PasswordStrength) -> str:
        """Ottiene il colore per il livello di forza"""
        colors = {
            PasswordStrength.VERY_WEAK: "#F44336",  # Rosso
            PasswordStrength.WEAK: "#FF5722",       # Rosso arancio
            PasswordStrength.FAIR: "#FF9800",       # Arancione
            PasswordStrength.GOOD: "#FFC107",       # Giallo
            PasswordStrength.STRONG: "#8BC34A",     # Verde chiaro
            PasswordStrength.VERY_STRONG: "#4CAF50" # Verde
        }
        return colors[strength]
    
    def _has_repeated_chars(self, password: str) -> bool:
        """Controlla se ci sono 3+ caratteri consecutivi ripetuti"""
        for i in range(len(password) - 2):
            if password[i] == password[i+1] == password[i+2]:
                return True
        return False
    
    def _has_sequential_chars(self, password: str) -> bool:
        """Controlla sequenze consecutive (123, abc, qwe)"""
        sequences = [
            "0123456789",
            "abcdefghijklmnopqrstuvwxyz",
            "qwertyuiopasdfghjklzxcvbnm"
        ]
        
        password_lower = password.lower()
        for seq in sequences:
            for i in range(len(seq) - 2):
                if seq[i:i+3] in password_lower or seq[i:i+3][::-1] in password_lower:
                    return True
        return False
    
    def _has_mixed_case(self, password: str) -> bool:
        """Controlla se ha maiuscole e minuscole mischiate (non solo all'inizio)"""
        has_upper = any(c.isupper() for c in password[1:])  # Escludi primo carattere
        has_lower = any(c.islower() for c in password)
        return has_upper and has_lower
    
    def _calculate_entropy(self, password: str) -> float:
        """Calcola l'entropia della password"""
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
