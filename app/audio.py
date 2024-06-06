import os
import shutil
import subprocess
import tempfile
import wave
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException
import sounddevice as sd
import numpy as np
from .audio_processor import process_audio

router = APIRouter()

CUSTOM_TEMP_DIR = r"C:\Users\91825\Desktop\GITHUB_AUTH\Temp_Directory_Audio"

@router.post("/record")
async def record_audio(background_tasks: BackgroundTasks):
    fs = 44100
    seconds = 10

    try:
        with tempfile.TemporaryDirectory(dir=CUSTOM_TEMP_DIR) as temp_dir:
            wav_path = os.path.join(temp_dir, "temp.wav")
            recording = sd.rec(int(seconds * fs), samplerate=fs, channels=1, dtype=np.int16)
            sd.wait()
            with wave.open(wav_path, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(fs)
                wf.writeframes(recording.tobytes())

            output_file_path = os.path.join(temp_dir, "output.json")
            background_tasks.add_task(process_audio, wav_path, output_file_path)

            return {"message": "Audio recorded and submitted for processing."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))





