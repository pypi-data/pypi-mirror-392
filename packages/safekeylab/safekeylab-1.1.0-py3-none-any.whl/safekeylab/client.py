"""
SafeKeyLab Client - Multimodal PII Detection SDK
"""

import requests
import base64
import json
from typing import Dict, List, Any, Optional, Union
from .exceptions import APIError, ValidationError


class SafeKeyLab:
    """
    Main client for SafeKeyLab Multimodal PII Detection API
    """

    def __init__(self, api_key: str, base_url: str = "https://api.safekeylab.com"):
        """
        Initialize SafeKeyLab client

        Args:
            api_key: Your SafeKeyLab API key
            base_url: API endpoint URL
        """
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def detect_text(self, text: str, **kwargs) -> Dict[str, Any]:
        """
        Detect PII in text

        Args:
            text: Text to analyze
            **kwargs: Additional options

        Returns:
            Detection results with PII entities
        """
        return self._make_request("POST", "/detect/text", {
            "content": text,
            "modality": "text",
            **kwargs
        })

    def detect_image(self, image_data: bytes, **kwargs) -> Dict[str, Any]:
        """
        Detect PII in images (faces, text, IDs, signatures)

        Args:
            image_data: Image binary data
            **kwargs: Additional options

        Returns:
            Detection results with visual and text PII
        """
        encoded = base64.b64encode(image_data).decode('utf-8')
        return self._make_request("POST", "/detect/image", {
            "content": encoded,
            "modality": "image",
            **kwargs
        })

    def detect_audio(self, audio_data: bytes, **kwargs) -> Dict[str, Any]:
        """
        Detect PII in audio (voiceprints, spoken information)

        Args:
            audio_data: Audio binary data
            **kwargs: Additional options

        Returns:
            Detection results with voice biometrics and spoken PII
        """
        encoded = base64.b64encode(audio_data).decode('utf-8')
        return self._make_request("POST", "/detect/audio", {
            "content": encoded,
            "modality": "audio",
            **kwargs
        })

    def detect_video(self, video_data: bytes, **kwargs) -> Dict[str, Any]:
        """
        Detect PII in video (faces, audio track, text overlays)

        Args:
            video_data: Video binary data
            **kwargs: Additional options

        Returns:
            Detection results across video timeline
        """
        encoded = base64.b64encode(video_data).decode('utf-8')
        return self._make_request("POST", "/detect/video", {
            "content": encoded,
            "modality": "video",
            **kwargs
        })

    def detect_document(self, file_path: str,
                       modalities: List[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Detect PII in documents (PDFs, Word, Excel)

        Args:
            file_path: Path to document file
            modalities: Specific modalities to check ['text', 'image', 'signature']
            **kwargs: Additional options

        Returns:
            Detection results for document
        """
        with open(file_path, 'rb') as f:
            data = f.read()

        encoded = base64.b64encode(data).decode('utf-8')
        return self._make_request("POST", "/detect/document", {
            "content": encoded,
            "modality": "document",
            "modalities": modalities or ['text', 'image'],
            "filename": file_path.split('/')[-1],
            **kwargs
        })

    def redact_text(self, text: str, **kwargs) -> str:
        """
        Redact PII from text

        Args:
            text: Text to redact
            **kwargs: Redaction options

        Returns:
            Redacted text
        """
        result = self._make_request("POST", "/redact/text", {
            "content": text,
            **kwargs
        })
        return result.get("redacted_text", text)

    def redact_image(self, image_data: bytes, **kwargs) -> bytes:
        """
        Redact PII from images (blur faces, remove text)

        Args:
            image_data: Image binary data
            **kwargs: Redaction options

        Returns:
            Redacted image data
        """
        encoded = base64.b64encode(image_data).decode('utf-8')
        result = self._make_request("POST", "/redact/image", {
            "content": encoded,
            **kwargs
        })
        return base64.b64decode(result.get("redacted_content", encoded))

    def batch_detect(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process multiple files in batch

        Args:
            items: List of items to process
                  [{"file": "path", "type": "text|image|audio|video"}, ...]

        Returns:
            List of detection results
        """
        batch_data = []
        for item in items:
            if item['type'] == 'text':
                with open(item['file'], 'r') as f:
                    content = f.read()
            else:
                with open(item['file'], 'rb') as f:
                    content = base64.b64encode(f.read()).decode('utf-8')

            batch_data.append({
                "content": content,
                "modality": item['type'],
                "filename": item['file'].split('/')[-1]
            })

        return self._make_request("POST", "/batch/detect", {
            "items": batch_data
        })

    def verify_identity(self, face_image: Optional[str] = None,
                       voice_sample: Optional[str] = None,
                       text_sample: Optional[str] = None) -> Dict[str, Any]:
        """
        Cross-modal identity verification

        Args:
            face_image: Path to face image
            voice_sample: Path to voice sample
            text_sample: Text for verification

        Returns:
            Verification results with confidence scores
        """
        data = {}

        if face_image:
            with open(face_image, 'rb') as f:
                data['face'] = base64.b64encode(f.read()).decode('utf-8')

        if voice_sample:
            with open(voice_sample, 'rb') as f:
                data['voice'] = base64.b64encode(f.read()).decode('utf-8')

        if text_sample:
            data['text'] = text_sample

        return self._make_request("POST", "/verify/identity", data)

    def add_custom_rule(self, name: str, pattern: str,
                       confidence: float = 0.9, **kwargs) -> Dict[str, Any]:
        """
        Add custom PII detection rule

        Args:
            name: Rule name
            pattern: Regex pattern
            confidence: Confidence threshold
            **kwargs: Additional rule options

        Returns:
            Rule creation confirmation
        """
        return self._make_request("POST", "/rules/custom", {
            "name": name,
            "pattern": pattern,
            "confidence": confidence,
            **kwargs
        })

    def get_statistics(self, start_date: str = None,
                       end_date: str = None) -> Dict[str, Any]:
        """
        Get usage statistics

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            Usage statistics
        """
        params = {}
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date

        return self._make_request("GET", "/statistics", params=params)

    def _make_request(self, method: str, endpoint: str,
                     data: Dict[str, Any] = None,
                     params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Make API request

        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request body
            params: Query parameters

        Returns:
            API response

        Raises:
            APIError: On API errors
            ValidationError: On validation errors
        """
        url = f"{self.base_url}{endpoint}"

        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers, params=params)
            else:
                response = requests.request(
                    method, url, headers=self.headers,
                    json=data, params=params
                )

            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 400:
                raise ValidationError(f"Validation error: {e.response.text}")
            elif e.response.status_code == 401:
                raise APIError("Invalid API key")
            elif e.response.status_code == 429:
                raise APIError("Rate limit exceeded")
            else:
                raise APIError(f"API error: {e.response.text}")

        except requests.exceptions.RequestException as e:
            raise APIError(f"Request failed: {str(e)}")