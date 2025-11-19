import re
import base64
from typing import Tuple, Dict, List
from urllib.parse import unquote

class InputValidator:
    """Validates input for suspicious patterns and characteristics"""
    
    DANGEROUS_PATTERNS = [
        r"ignore\s+(previous|above|all)\s+(instructions?|prompts?|rules?)",
        r"disregard\s+(previous|above|all)",
        r"forget\s+(everything|all|previous)",
        r"system\s*[:：]\s*",
        r"you\s+are\s+now",
        r"new\s+instructions?",
        r"roleplay\s+as",
        r"pretend\s+(you\s+are|to\s+be)",
        r"<\s*\|im_start\|>",
        r"<\s*\|im_end\|>",
        r"###\s*Instruction",
        r"\[SYSTEM\]",
        r"\[INST\]",
        r"</s>",
        r"<s>",
    ]
    
    ENCODING_PATTERNS = [
        r"(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?",  # Base64
        r"\\x[0-9a-fA-F]{2}",  # Hex encoding
        r"\\u[0-9a-fA-F]{4}",  # Unicode escape
        r"%[0-9a-fA-F]{2}",    # URL encoding
        r"&#\d+;",              # HTML entities
    ]
    
    def __init__(self, config: 'GuardConfig'):
        self.config = config
        self.compiled_patterns = [re.compile(p, re.IGNORECASE) for p in self.DANGEROUS_PATTERNS]
        
    def validate(self, text: str) -> Tuple[bool, Dict]:
        """
        Validate input text for suspicious characteristics
        Returns: (is_valid, details_dict)
        """
        details = {
            "length_check": True,
            "pattern_check": True,
            "encoding_check": True,
            "char_ratio_check": True,
            "detected_patterns": [],
            "suspicious_encodings": []
        }
        
        # Length check
        if not (self.config.min_length <= len(text) <= self.config.max_length):
            details["length_check"] = False
            return False, details
        
        # Pattern matching
        if self.config.enable_pattern_matching:
            for pattern in self.compiled_patterns:
                if pattern.search(text):
                    details["pattern_check"] = False
                    details["detected_patterns"].append(pattern.pattern)
        
        # Check for custom blacklist
        text_lower = text.lower()
        for blacklisted in self.config.custom_blacklist:
            if blacklisted.lower() in text_lower:
                details["pattern_check"] = False
                details["detected_patterns"].append(f"custom: {blacklisted}")
        
        # Encoding detection
        if self.config.enable_encoding_detection:
            suspicious_encodings = self._detect_encodings(text)
            if suspicious_encodings:
                details["encoding_check"] = False
                details["suspicious_encodings"] = suspicious_encodings
        
        # Special character ratio
        special_chars = sum(not c.isalnum() and not c.isspace() for c in text)
        ratio = special_chars / len(text) if len(text) > 0 else 0
        if ratio > self.config.max_special_char_ratio:
            details["char_ratio_check"] = False
        
        is_valid = all([
            details["length_check"],
            details["pattern_check"],
            details["encoding_check"],
            details["char_ratio_check"]
        ])
        
        return is_valid, details
    
    def _detect_encodings(self, text: str) -> List[str]:
        """Detect suspicious encoding attempts"""
        encodings = []
        
        # Check for base64
        if self._looks_like_base64(text):
            try:
                decoded = base64.b64decode(text).decode('utf-8', errors='ignore')
                if any(pattern.search(decoded) for pattern in self.compiled_patterns):
                    encodings.append("base64")
            except:
                pass
        
        # Check for URL encoding
        if '%' in text:
            try:
                decoded = unquote(text)
                if decoded != text:
                    encodings.append("url_encoding")
            except:
                pass
        
        # Check for hex/unicode escapes
        if re.search(r'\\[xu]', text):
            encodings.append("escape_sequences")
        
        return encodings
    
    def _looks_like_base64(self, text: str) -> bool:
        """Check if text looks like base64"""
        if len(text) < 20:
            return False
        base64_chars = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=')
        return len(set(text) - base64_chars) / len(text) < 0.1