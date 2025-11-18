"""
PII Scanner - Local multimodal scanning capabilities
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from multimodal_pii_detector import MultimodalPIIDetector
from typing import List, Dict, Any, Optional


class PIIScanner:
    """
    Local PII scanner for offline detection
    """

    def __init__(self):
        """Initialize local scanner with multimodal detector"""
        self.detector = MultimodalPIIDetector()

    def scan_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Scan text for PII

        Args:
            text: Text to scan

        Returns:
            List of detected PII entities
        """
        entities = self.detector.detect_text(text)
        return [self._entity_to_dict(e) for e in entities]

    def scan_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Scan file for PII based on file type

        Args:
            file_path: Path to file

        Returns:
            List of detected PII entities
        """
        ext = file_path.lower().split('.')[-1]

        # Determine modality from extension
        if ext in ['txt', 'csv', 'json', 'xml', 'md']:
            with open(file_path, 'r') as f:
                content = f.read()
            return self.scan_text(content)

        elif ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp']:
            with open(file_path, 'rb') as f:
                content = f.read()
            entities = self.detector.detect_image(content, {})
            return [self._entity_to_dict(e) for e in entities]

        elif ext in ['mp3', 'wav', 'm4a', 'ogg']:
            with open(file_path, 'rb') as f:
                content = f.read()
            entities = self.detector.detect_voice(content, {})
            return [self._entity_to_dict(e) for e in entities]

        elif ext in ['mp4', 'avi', 'mov', 'webm']:
            with open(file_path, 'rb') as f:
                content = f.read()
            entities = self.detector.detect_video(content, {})
            return [self._entity_to_dict(e) for e in entities]

        elif ext in ['pdf', 'docx', 'xlsx', 'pptx']:
            with open(file_path, 'rb') as f:
                content = f.read()
            entities = self.detector.detect_document(content, {})
            return [self._entity_to_dict(e) for e in entities]

        else:
            raise ValueError(f"Unsupported file type: {ext}")

    def scan_directory(self, directory: str,
                      recursive: bool = True) -> Dict[str, List[Dict[str, Any]]]:
        """
        Scan directory for PII

        Args:
            directory: Directory path
            recursive: Scan subdirectories

        Returns:
            Dictionary mapping file paths to PII entities
        """
        results = {}

        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    entities = self.scan_file(file_path)
                    if entities:
                        results[file_path] = entities
                except Exception as e:
                    results[file_path] = [{"error": str(e)}]

            if not recursive:
                break

        return results

    def _entity_to_dict(self, entity) -> Dict[str, Any]:
        """Convert entity object to dictionary"""
        return {
            "text": entity.text,
            "label": entity.label,
            "confidence": entity.confidence,
            "modality": entity.modality,
            "metadata": entity.metadata,
            "timestamp": getattr(entity, 'timestamp', None),
            "bbox": getattr(entity, 'bbox', None)
        }