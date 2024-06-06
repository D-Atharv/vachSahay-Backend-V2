# file_manager.py

import os
import uuid
from fastapi import APIRouter, UploadFile, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from google.cloud import storage
from app.auth import verify_access_token
from fastapi import BackgroundTasks
from tempfile import SpooledTemporaryFile
import shutil
from ml_main import process

router = APIRouter()

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'vachsahay-68e83827f56e.json'

storage_client = storage.Client()

def generate_unique_filename(filename):
    filename_without_extension, extension = os.path.splitext(filename)
    return f"{filename_without_extension}_{uuid.uuid4().hex}{extension}"

def create_or_get_folder(bucket, folder_name):
    if not bucket.get_blob(folder_name):
        blob = bucket.blob(folder_name)
        blob.upload_from_string('')
    return folder_name

@router.post("/upload_new_file/")
async def upload_file(user_id: str, file: UploadFile = UploadFile(...)):
    if not file.filename.endswith('.wav'):
        raise HTTPException(status_code=400, detail="Only .wav files are allowed.")

    bucket_name = 'new_vachsahay'
    location = 'asia-south1'

    username = user_id.split('@')[0]
    folder_name = username.strip()

    bucket = storage_client.bucket(bucket_name)
    if not bucket.exists():
        bucket.create(location=location)

    folder_name = create_or_get_folder(bucket, folder_name)

    unique_filename = generate_unique_filename(file.filename)
    blob = bucket.blob(f"{folder_name}/{unique_filename}")
    contents = await file.read()
    blob.upload_from_string(contents)
    return {
        "message": f"File '{file.filename}' uploaded to bucket '{bucket_name}' in folder '{folder_name}' with unique filename '{unique_filename}'."}




@router.get("/download_wav_files/")
async def download_wav_files(user_id: str):
    bucket_name = 'new_vachsahay'

    username = user_id.split('@')[0]
    folder_name = username.strip()

    bucket = storage_client.bucket(bucket_name)

    folder_name = create_or_get_folder(bucket, folder_name)

    local_folder_path = r"C:\Users\91825\Desktop\vach-sahay-backend"
    json_store = r'C:\Users\91825\Desktop\vach-sahay-backend'

    try:
        process_results = process(local_folder_path, json_store, extend_dataset=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error processing files")

    downloaded_files = []

    try:
        for blob in bucket.list_blobs(prefix=folder_name):
            if blob.name.endswith('.wav'):
                filename = os.path.basename(blob.name)
                local_filename = os.path.join(local_folder_path, filename)
                blob.download_to_filename(local_filename)
                downloaded_files.append(local_filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error downloading files")

    return {"downloaded_files": downloaded_files}


