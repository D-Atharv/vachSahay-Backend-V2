import os
import uuid
from fastapi import FastAPI, UploadFile, HTTPException, APIRouter
from google.cloud import storage
from ml_main import process
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

router = APIRouter()

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'vachsahay-68e83827f56e.json'
# os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

storage_client = storage.Client()

def generate_unique_filename(filename):
    filename_without_extension, extension = os.path.splitext(filename)
    return f"{filename_without_extension}_{uuid.uuid4().hex}{extension}"

def create_or_get_folder(bucket, folder_name):
    if not bucket.get_blob(folder_name):
        blob = bucket.blob(folder_name)
        blob.upload_from_string('')
    return folder_name

@router.post("/upload_file/")
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


@router.get("/downloading_wav_files/")
async def download_wav_files(user_id: str):
    bucket_name = 'new_vachsahay'

    username = user_id.split('@')[0]
    folder_name = username.strip()

    bucket = storage_client.bucket(bucket_name)

    folder_name = create_or_get_folder(bucket, folder_name)

    local_folder_path = r"C:\Users\91825\Desktop\vach-sahay-backend\downloaded_audio_files"
    json_store = r'C:\Users\91825\Desktop\vach-sahay-backend\json_store'

    process_results = process(local_folder_path, json_store, extend_dataset=True)

    downloaded_files = []

    for blob in bucket.list_blobs(prefix=folder_name):
        if blob.name.endswith('.wav'):
            filename = os.path.basename(blob.name)
            local_filename = os.path.join(local_folder_path, filename)
            blob.download_to_filename(local_filename)
            downloaded_files.append(local_filename)

    return {"downloaded_files": downloaded_files}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="127.0.0.1", port=8000)
