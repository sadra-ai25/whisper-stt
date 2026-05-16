# Whisper STT — Speech-to-Text Service

![Python](https://img.shields.io/badge/Python-3.10-blue) ![Flask](https://img.shields.io/badge/Flask-2.x-lightgrey) ![Whisper](https://img.shields.io/badge/OpenAI_Whisper-Large-orange) ![Nginx](https://img.shields.io/badge/Nginx-HTTPS-green) ![Docker](https://img.shields.io/badge/Docker-Compose-blue)

Self-hosted Persian speech-to-text service powered by OpenAI Whisper. Accepts audio file uploads via a web interface or REST API and returns accurate transcriptions — optimized for Persian (Farsi) speech.

## Features

- **Whisper Large model** — high-accuracy transcription supporting 99 languages including Persian
- **Web interface** — browser-based upload UI with real-time transcription results
- **REST API** — programmatic audio upload and transcription endpoint
- **HTTPS support** — Nginx with SSL/TLS termination via self-signed or custom certificates
- **Multiple audio formats** — supports WAV, MP3, M4A, OGG, FLAC, and more
- **Docker Compose** — single-command deployment, no cloud dependency

## Tech Stack

| Component | Technology |
|---|---|
| STT Model | OpenAI Whisper Large |
| API Server | Flask (Python) |
| Web UI | HTML/CSS/JS (static) |
| Reverse Proxy | Nginx (HTTPS) |
| Containerization | Docker Compose |

## Architecture

```
Browser / API Client
        │
        │  HTTPS (port 443)
        ▼
     Nginx
        │  HTTP proxy
        ▼
   Flask App (:5000)
        │
    Whisper Model
    (local inference)
        │
        ▼
   Transcription Result
   { text: "متن فارسی..." }
```

## Prerequisites

- Docker & Docker Compose
- Whisper Large model files in `code/whisper_model/model/`
- (Optional) Custom SSL certificate files

## Installation & Setup

```bash
# 1. Clone the repository
git clone https://github.com/sadra-ai25/whisper-stt.git
cd whisper-stt

# 2. Download Whisper Large model
# Place model safetensors files in:
mkdir -p code/whisper_model/model
# Copy model-00001-of-00002.safetensors and model-00002-of-00002.safetensors

# 3. (Optional) Add your SSL certificate
cp your_cert.crt nginx/server.crt
cp your_key.key  nginx/server.key

# 4. Start services
docker compose up -d --build
```

The web interface is available at `https://localhost`.

## Usage

### Web Interface

Open `https://localhost` in your browser, upload an audio file, and click **Transcribe**. Results appear on screen within seconds.

### REST API

```bash
# Transcribe an audio file
curl -X POST https://localhost/predict \
  --insecure \
  -F "audio=@/path/to/recording.wav"
```

**Response:**

```json
{
  "text": "سلام، این یک آزمایش تشخیص گفتار است.",
  "language": "fa",
  "duration_seconds": 4.2
}
```

```bash
# Health check
curl -k https://localhost/health
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Web UI (upload form) |
| `POST` | `/predict` | Transcribe uploaded audio file |
| `GET` | `/health` | Service health check |

## Supported Audio Formats

| Format | Extension |
|---|---|
| WAV | `.wav` |
| MP3 | `.mp3` |
| M4A | `.m4a` |
| OGG | `.ogg` |
| FLAC | `.flac` |
| WebM | `.webm` |

## SSL Configuration

The included `openssl.cnf` generates a self-signed certificate for local use:

```bash
openssl req -x509 -newkey rsa:4096 \
  -keyout nginx/server.key \
  -out nginx/server.crt \
  -days 365 -nodes \
  -config openssl.cnf
```

For production, replace with a valid certificate from Let's Encrypt or your CA.

## Contributing

Pull requests are welcome. For major changes, please open an issue first.

## License

MIT
