from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
import os
import uuid
import asyncio
import traceback
from supabase import create_client, Client
from ..dependencies import get_current_user, SUPABASE_URL, SUPABASE_SERVICE_KEY

router = APIRouter(prefix="/media", tags=["media"])

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...), 
    current_user = Depends(get_current_user)
):
    file_extension = (file.filename or "bin").split(".")[-1].lower()
    unique_filename = f"{current_user.id}/{uuid.uuid4()}.{file_extension}"
    file_content = await file.read()

    try:
        bucket_name = "post_images"
        
        # Use an isolated admin client to avoid session conflicts
        admin_supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

        # Upload to Supabase Storage
        await asyncio.to_thread(
            admin_supabase.storage.from_(bucket_name).upload,
            path=unique_filename,
            file=file_content,
            file_options={"content-type": file.content_type or "application/octet-stream", "upsert": "true"},
        )

        public_url = admin_supabase.storage.from_(bucket_name).get_public_url(unique_filename).rstrip("?")
        return {"filename": unique_filename, "url": public_url}

    except Exception as e:
        print(f"[upload] FAILED: {e}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)} — ensure bucket 'post_images' exists in Supabase Storage."
        )
