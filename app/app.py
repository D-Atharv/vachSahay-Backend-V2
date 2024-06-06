import os
import shutil
import subprocess
import tempfile
import wave
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sounddevice as sd
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the custom temporary directory path
CUSTOM_TEMP_DIR = "C:\\Users\\ASUS\\Desktop\\FAST_API\\temp_directory"

@app.post("/upload/")
async def upload_file(background_tasks: BackgroundTasks, audio_file: UploadFile = File(...)):
    if not audio_file.filename.endswith(".wav"):
        raise HTTPException(status_code=400, detail="Only .wav files are supported.")

    try:
        # Use the custom temporary directory path
        with tempfile.TemporaryDirectory(dir=CUSTOM_TEMP_DIR) as temp_dir:
            file_path = os.path.join(temp_dir, audio_file.filename)
            with open(file_path, 'wb') as buffer:
                shutil.copyfileobj(audio_file.file, buffer)

            output_file_path = os.path.join(temp_dir, "output.json")
            background_tasks.add_task(subprocess.run, ["python", "main1.py", file_path, output_file_path])

            print("Temporary directory:", temp_dir)
            return {"message": "Audio file submitted for processing. Temporary directory: {}".format(temp_dir)}



    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/record")
async def record_audio(background_tasks: BackgroundTasks):
    fs = 44100  # Sample rate
    seconds = 10  # Duration of recording

    try:
        # Use the custom temporary directory path
        with tempfile.TemporaryDirectory(dir=CUSTOM_TEMP_DIR) as temp_dir:
            wav_path = os.path.join(temp_dir, "temp.wav")
            recording = sd.rec(int(seconds * fs), samplerate=fs, channels=1, dtype=np.int16)
            sd.wait()  # Wait for recording to finish
            with wave.open(wav_path, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(fs)
                wf.writeframes(recording.tobytes())

            output_file_path = os.path.join(temp_dir, "output.json")
            background_tasks.add_task(subprocess.run, ["python", "main1.py", wav_path, output_file_path])

            return {"message": "Audio recorded and submitted for processing."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

