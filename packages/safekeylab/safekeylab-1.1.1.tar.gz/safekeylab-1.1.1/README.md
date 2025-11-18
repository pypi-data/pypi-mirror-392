# SafeKeyLab - Multimodal AI Privacy Shield

[![PyPI version](https://badge.fury.io/py/safekeylab.svg)](https://pypi.org/project/safekeylab/)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

## Enterprise-Grade Multimodal PII Detection & Protection

SafeKeyLab is a comprehensive privacy protection SDK that detects and redacts PII across **multiple modalities**:

- **Text**: Documents, emails, chat messages, code
- **Voice/Audio**: Call recordings, voice memos, podcasts
- **Images**: Photos, scanned documents, screenshots
- **Video**: Meeting recordings, surveillance footage
- **Documents**: PDFs, Word docs, spreadsheets

## Key Features

### 🎯 99% Accuracy Across All Modalities
- State-of-the-art ML models for each data type
- Cross-modal validation for enhanced accuracy
- Real-time detection with <50ms latency

### 🛡️ Comprehensive PII Coverage
- **Biometric Data**: Face detection, voiceprints, signatures
- **Personal Identifiers**: SSN, passport, driver's license
- **Financial Info**: Credit cards, bank accounts, tax IDs
- **Contact Details**: Emails, phones, addresses
- **Healthcare**: Medical records, insurance IDs (HIPAA compliant)
- **100+ PII types** supported out-of-the-box

### 🔒 Enterprise Security & Compliance
- GDPR, CCPA, HIPAA compliant
- SOC2 Type II certified
- End-to-end encryption
- On-premise deployment options

## Quick Start

```python
from safekeylab import SafeKeyLab

# Initialize client
client = SafeKeyLab(api_key="your_api_key")

# Text detection
text_result = client.detect_text("John Doe, SSN: 123-45-6789")

# Image detection (faces, text in images, IDs)
with open("photo.jpg", "rb") as f:
    image_result = client.detect_image(f.read())

# Audio detection (voiceprints, spoken PII)
with open("call_recording.wav", "rb") as f:
    audio_result = client.detect_audio(f.read())

# Video detection (faces, audio, overlays)
with open("meeting.mp4", "rb") as f:
    video_result = client.detect_video(f.read())

# Automatic redaction
redacted_text = client.redact_text("Contact me at john@email.com")
# Output: "Contact me at [REDACTED_EMAIL]"
```

## Advanced Features

### Multimodal Analysis
```python
# Analyze document with embedded images
result = client.detect_document("contract.pdf",
                                modalities=['text', 'image', 'signature'])

# Cross-modal verification
verified = client.verify_identity(
    face_image="id_photo.jpg",
    voice_sample="voice.wav",
    text_sample="John Smith"
)
```

### Batch Processing
```python
# Process multiple files efficiently
results = client.batch_detect([
    {"file": "doc1.txt", "type": "text"},
    {"file": "image1.jpg", "type": "image"},
    {"file": "audio1.mp3", "type": "audio"}
])
```

### Custom PII Rules
```python
# Add industry-specific patterns
client.add_custom_rule(
    name="employee_id",
    pattern=r"EMP-\d{6}",
    confidence=0.95
)
```

## Installation

```bash
pip install safekeylab
```

## Supported File Formats

- **Text**: .txt, .csv, .json, .xml, .html, .md
- **Documents**: .pdf, .docx, .xlsx, .pptx
- **Images**: .jpg, .png, .gif, .bmp, .tiff
- **Audio**: .mp3, .wav, .m4a, .ogg, .flac
- **Video**: .mp4, .avi, .mov, .webm, .mkv

## Performance

- **Latency**: <50ms for text, <200ms for images
- **Throughput**: 10,000+ requests/second
- **Accuracy**: 99% F1 score across modalities
- **Scale**: Process TB of data daily

## Use Cases

- **Healthcare**: Protect patient data in medical records, imaging, recordings
- **Finance**: Secure customer data in documents, call centers, video KYC
- **Legal**: Redact sensitive info in contracts, depositions, evidence
- **HR**: Anonymize resumes, interview recordings, ID documents
- **Customer Service**: Clean chat logs, call recordings, support tickets

## Documentation

- [API Reference](https://docs.safekeylab.com/api)
- [Integration Guides](https://docs.safekeylab.com/guides)
- [Best Practices](https://docs.safekeylab.com/best-practices)
- [Compliance Guide](https://docs.safekeylab.com/compliance)

## Support

- Email: support@safekeylab.com
- Documentation: https://docs.safekeylab.com
- Enterprise: enterprise@safekeylab.com

---

**SafeKeyLab** - Protecting Privacy Across Every Modality