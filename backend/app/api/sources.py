from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse


router = APIRouter(
    prefix="/sources",
    tags=["sources"],
)

DOCUMENT_DIR = Path("app/assets/documents")


@router.get("/{file_name}")
async def get_source(file_name: str):
    file_path = DOCUMENT_DIR / file_name

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        content_disposition_type="inline",
    )