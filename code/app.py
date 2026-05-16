from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from transformers import WhisperProcessor, WhisperForConditionalGeneration
import librosa
import torch
import os
import logging
import time
from datetime import datetime
import shutil
from pathlib import Path
from pydub import AudioSegment
import numpy as np

app = FastAPI()

# Mount the static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create output directory
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

# Create voice archive directory
VOICE_DIR = Path("tmp_voice")
VOICE_DIR.mkdir(exist_ok=True)

# Clean up old files older than 1 hour
def cleanup_old_files():
    current_time = time.time()
    for file in OUTPUT_DIR.iterdir():
        if file.is_file() and (current_time - file.stat().st_mtime) > 3600:
            file.unlink()
            logger.info(f"Deleted old file: {file}")

# Load Whisper model
device = "cuda" if torch.cuda.is_available() else "cpu"
processor_path = os.getenv("WHISPER_PROCESSOR_PATH", "/home/code/whisper_model/processor")
model_path = os.getenv("WHISPER_MODEL_PATH", "/home/code/whisper_model/model")
try:
    processor = WhisperProcessor.from_pretrained(processor_path)
    model = WhisperForConditionalGeneration.from_pretrained(model_path).to(device)
    forced_decoder_ids = processor.get_decoder_prompt_ids(language="persian", task="transcribe")
    logger.info("Whisper model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load Whisper model: {e}")
    raise

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    """Serve the index.html file."""
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """Transcribe an uploaded or recorded audio file."""
    # Validate file extension
    allowed_extensions = {".wav", ".mp3", ".webm"}
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Only WAV, MP3, and WebM files are supported")

    # Generate timestamp-based filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    original_temp_file = OUTPUT_DIR / f"audio_{timestamp}{file_ext}"
    text_file = OUTPUT_DIR / f"transcription_{timestamp}.txt"
    
    # Define path for saving the voice file permanently
    voice_archive_file = VOICE_DIR / f"voice_{timestamp}{file_ext}"

    # List of temporary files to clean up
    temp_files_to_delete = []

    try:
        # Save the uploaded file to the voice archive directory first
        with voice_archive_file.open("wb") as buffer:
            # file.file is a stream, read it once and save content
            shutil.copyfileobj(file.file, buffer)
        # Then, copy the archived file to the temporary processing location
        shutil.copy(voice_archive_file, original_temp_file)
        temp_files_to_delete.append(original_temp_file)
        
        audio_to_process = original_temp_file

        # Preprocess audio with pydub for MP3 robustness
        try:
            audio = AudioSegment.from_file(original_temp_file)
            # Convert to WAV for consistent processing
            wav_file = OUTPUT_DIR / f"audio_{timestamp}.wav"
            audio.export(wav_file, format="wav")
            audio_to_process = wav_file
            temp_files_to_delete.append(wav_file)
        except Exception as e:
            logger.warning(f"Failed to preprocess with pydub: {e}. Falling back to librosa.")

        # Transcribe the audio
        logger.info(f"Transcribing file: {audio_to_process}")
        y, sr = librosa.load(audio_to_process, sr=16000)
        features = processor(y, sampling_rate=sr, return_tensors="pt").to(device)

        predicted_ids = model.generate(
            features.input_features,
            forced_decoder_ids=forced_decoder_ids
        )
        text = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]

        # Save the transcription to a text file
        with text_file.open("w", encoding="utf-8") as f:
            f.write(text)

        # Clean up old files
        cleanup_old_files()

        return {"text": text, "text_filename": text_file.name}
    except Exception as e:
        logger.error(f"Error processing file {file.filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")
    finally:
        # Clean up all temporary audio files
        for temp_file in temp_files_to_delete:
            if temp_file.exists():
                temp_file.unlink()

@app.get("/download/{filename}")
async def download_file(filename: str):
    """Download the transcribed text file."""
    file_path = OUTPUT_DIR / filename
    if not file_path.exists() or file_path.suffix != ".txt":
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, media_type="text/plain", filename=filename)