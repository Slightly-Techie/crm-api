import asyncio
import logging
from datetime import datetime

import cloudinary
import cloudinary.uploader
from fastapi import UploadFile

from core.config import settings

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True,
)

logger = logging.getLogger(__name__)


async def upload_file(file: UploadFile, username: str, folder: str) -> str | None:
    try:
        data = await file.read()
        date = datetime.now().strftime("%Y%m%d-%H-%M-%S")
        public_id = f"{username}/{folder}/{date}"
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: cloudinary.uploader.upload(
                data,
                public_id=public_id,
                resource_type="auto",
            ),
        )
        return result["secure_url"]
    except Exception as e:
        logger.error("Cloudinary upload failed: %s", e)
        return None
