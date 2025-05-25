
from urllib.parse import urlparse
from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from fastapi.concurrency import run_in_threadpool

from app.utils.s3_util import delete_file_from_s3, upload_file_to_s3

router = APIRouter()

@router.post("/upload/image")
async def upload_image(file: UploadFile = File(...)):
    file_bytes = await file.read()
    image_url = await run_in_threadpool(upload_file_to_s3, file_bytes, file.filename, "uploads/post")
    return {"image_url": image_url}

@router.delete("/delete/image")
def delete_image(image_url: str = Query(...)):
    try:
        delete_file_from_s3(image_url)
        return {"message": "File deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))