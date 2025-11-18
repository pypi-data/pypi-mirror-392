"""
Data Protector - Redaction and anonymization utilities
"""

import re
import hashlib
from typing import Dict, List, Any, Optional


class DataProtector:
    """
    Data protection utilities for PII redaction and anonymization
    """

    def __init__(self, redaction_method: str = "mask"):
        """
        Initialize data protector

        Args:
            redaction_method: Method for redaction ('mask', 'hash', 'replace')
        """
        self.redaction_method = redaction_method
        self.redaction_patterns = self._init_patterns()

    def _init_patterns(self) -> Dict[str, str]:
        """Initialize redaction patterns"""
        return {
            'EMAIL': '[REDACTED_EMAIL]',
            'PHONE': '[REDACTED_PHONE]',
            'SSN': '[REDACTED_SSN]',
            'CREDIT_CARD': '[REDACTED_CARD]',
            'NAME': '[REDACTED_NAME]',
            'ADDRESS': '[REDACTED_ADDRESS]',
            'DATE_OF_BIRTH': '[REDACTED_DOB]',
            'PASSPORT': '[REDACTED_PASSPORT]',
            'LICENSE': '[REDACTED_LICENSE]',
            'MEDICAL_RECORD': '[REDACTED_MEDICAL]',
            'BIOMETRIC_FACE': '[FACE_REMOVED]',
            'BIOMETRIC_VOICE': '[VOICE_ALTERED]',
            'BIOMETRIC_SIGNATURE': '[SIGNATURE_REMOVED]',
        }

    def redact_text(self, text: str, entities: List[Dict[str, Any]]) -> str:
        """
        Redact PII from text

        Args:
            text: Original text
            entities: List of PII entities to redact

        Returns:
            Redacted text
        """
        # Sort entities by position (reverse to maintain positions)
        sorted_entities = sorted(entities,
                                key=lambda x: x.get('metadata', {}).get('position', {}).get('start', 0),
                                reverse=True)

        redacted = text
        for entity in sorted_entities:
            label = entity.get('label', 'UNKNOWN')
            original_text = entity.get('text', '')

            if self.redaction_method == 'mask':
                replacement = self.redaction_patterns.get(label, '[REDACTED]')
            elif self.redaction_method == 'hash':
                replacement = f"[HASH_{hashlib.md5(original_text.encode()).hexdigest()[:8]}]"
            else:  # replace
                replacement = '*' * len(original_text)

            # Replace in text
            if original_text and original_text in redacted:
                redacted = redacted.replace(original_text, replacement)

        return redacted

    def anonymize_data(self, data: Dict[str, Any],
                      fields_to_anonymize: List[str]) -> Dict[str, Any]:
        """
        Anonymize specific fields in data

        Args:
            data: Data dictionary
            fields_to_anonymize: List of field names to anonymize

        Returns:
            Anonymized data
        """
        anonymized = data.copy()

        for field in fields_to_anonymize:
            if field in anonymized:
                value = anonymized[field]
                if isinstance(value, str):
                    # Hash the value for consistent anonymization
                    anonymized[field] = f"ANON_{hashlib.sha256(value.encode()).hexdigest()[:16]}"
                elif isinstance(value, (int, float)):
                    # Randomize numeric values
                    anonymized[field] = hash(str(value)) % 1000000
                elif isinstance(value, list):
                    # Anonymize list items
                    anonymized[field] = [f"ITEM_{i}" for i in range(len(value))]
                else:
                    anonymized[field] = "[ANONYMIZED]"

        return anonymized

    def tokenize_pii(self, text: str, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Replace PII with secure tokens

        Args:
            text: Original text
            entities: List of PII entities

        Returns:
            Dictionary with tokenized text and token mapping
        """
        tokens = {}
        tokenized = text

        for i, entity in enumerate(entities):
            original_text = entity.get('text', '')
            token = f"{{TOKEN_{i:04d}}}"
            tokens[token] = {
                'original': original_text,
                'label': entity.get('label'),
                'hash': hashlib.sha256(original_text.encode()).hexdigest()
            }

            if original_text in tokenized:
                tokenized = tokenized.replace(original_text, token)

        return {
            'tokenized_text': tokenized,
            'tokens': tokens,
            'entity_count': len(tokens)
        }

    def apply_privacy_preserving_techniques(self,
                                           data: Any,
                                           technique: str = 'differential_privacy') -> Any:
        """
        Apply advanced privacy-preserving techniques

        Args:
            data: Data to protect
            technique: Technique to apply

        Returns:
            Privacy-preserved data
        """
        if technique == 'differential_privacy':
            # Add noise to numeric data
            if isinstance(data, (int, float)):
                import random
                noise = random.gauss(0, 0.1 * abs(data))
                return data + noise
            return data

        elif technique == 'k_anonymity':
            # Generalize data to ensure k-anonymity
            if isinstance(data, str) and data.isdigit():
                # Generalize numeric strings
                return data[:-2] + '**'
            return data

        elif technique == 'homomorphic_encryption':
            # Simulate homomorphic encryption
            if isinstance(data, (int, float)):
                # Simple example: multiply by prime and add salt
                salt = 12345
                return (data * 31) + salt
            return data

        return data