import uuid
import os
from transformers import WhisperProcessor, WhisperForConditionalGeneration
import librosa
import torch

import argparse

# Initialize argparse
parser = argparse.ArgumentParser(description="Process a audio file via the command line input.")

# Add an argument for the input file path
parser.add_argument('--FilePath', type=str, required=True, help='Path to the input file')
parser.add_argument('--ConfigProcessor', type=str, required=True, help='Path to the input file')
parser.add_argument('--ConfigModel', type=str, required=True, help='Path to the input file')
# Parse the command-line arguments
args = parser.parse_args()
###====================================================================
# UPLOAD_FOLDER = './tmp_voice'
ALLOWED_EXTENSIONS = {'mp3', 'wav'}

if torch.cuda.is_available():
    device = torch.device("cuda")
    print('There are %d GPU(s) available.' % torch.cuda.device_count())
    print('We will use the "{}".'.format(torch.cuda.get_device_name(0)))
else:
    print('No GPU available, using the CPU instead.')
    device = torch.device("cpu")

processor = WhisperProcessor.from_pretrained(args.ConfigProcessor)
model = WhisperForConditionalGeneration.from_pretrained(args.ConfigModel).to(device)

forced_decoder_ids = processor.get_decoder_prompt_ids(language="persian", task="transcribe")

def whisper_asr(filename):
    try:
        y, sr = librosa.load(filename, sr=16000)
        input_features = processor(y, sampling_rate=sr, return_tensors="pt").input_features.to(device)
        predicted_ids = model.generate(input_features, forced_decoder_ids=forced_decoder_ids)
        transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)
        return transcription
    except:
        return "could not be processed"

if __name__ == '__main__':
    whisper_asr(args.FilePath)
    
    transcription = whisper_asr(args.FilePath)
    print("Transcription:", transcription)