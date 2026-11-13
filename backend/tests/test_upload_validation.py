import io
import zipfile
import pytest
from fastapi import UploadFile, HTTPException
from app.core.upload_security import validate_and_save_upload, MAX_FILE_SIZE_BYTES

@pytest.mark.asyncio
async def test_png_validation():
    content = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
    file = UploadFile(filename="test.png", file=io.BytesIO(content))
    # In test environment, it should save locally or via configured storage
    unique_name, file_url, size, mime = await validate_and_save_upload(file, subfolder="test")
    assert mime == "image/png"
    assert size == len(content)
    assert unique_name.endswith(".png")

@pytest.mark.asyncio
async def test_jpeg_validation():
    content = b"\xff\xd8\xff" + b"\x00" * 100
    file = UploadFile(filename="test.jpg", file=io.BytesIO(content))
    unique_name, file_url, size, mime = await validate_and_save_upload(file, subfolder="test")
    assert mime == "image/jpeg"
    assert size == len(content)

@pytest.mark.asyncio
async def test_pdf_validation():
    content = b"%PDF-1.4 " + b"\x00" * 100
    file = UploadFile(filename="test.pdf", file=io.BytesIO(content))
    unique_name, file_url, size, mime = await validate_and_save_upload(file, subfolder="test")
    assert mime == "application/pdf"
    assert size == len(content)

@pytest.mark.asyncio
async def test_doc_validation():
    content = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1" + b"\x00" * 100
    file = UploadFile(filename="invoice.doc", file=io.BytesIO(content))
    unique_name, file_url, size, mime = await validate_and_save_upload(file, subfolder="test")
    assert mime == "application/msword"
    assert size == len(content)

@pytest.mark.asyncio
async def test_docx_validation_valid():
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", '<?xml version="1.0" encoding="UTF-8"?>')
        zf.writestr("word/document.xml", '<w:document></w:document>')
    content = zip_buffer.getvalue()
    
    file = UploadFile(filename="receipt.docx", file=io.BytesIO(content))
    unique_name, file_url, size, mime = await validate_and_save_upload(file, subfolder="test")
    assert mime == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    assert size == len(content)

@pytest.mark.asyncio
async def test_docx_validation_arbitrary_zip_rejected():
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("malicious.exe", b"MZ\x90\x00")
    content = zip_buffer.getvalue()
    
    file = UploadFile(filename="spoofed.docx", file=io.BytesIO(content))
    with pytest.raises(HTTPException) as exc_info:
        await validate_and_save_upload(file, subfolder="test")
    assert exc_info.value.status_code == 415
    assert "Office Open XML" in exc_info.value.detail

@pytest.mark.asyncio
async def test_spoofed_extension_rejected():
    content = b"This is plain text pretending to be a PDF"
    file = UploadFile(filename="fake.pdf", file=io.BytesIO(content))
    with pytest.raises(HTTPException) as exc_info:
        await validate_and_save_upload(file, subfolder="test")
    assert exc_info.value.status_code == 415

@pytest.mark.asyncio
async def test_file_size_exceeded_rejected():
    header = b"%PDF-1.4 "
    oversized = header + b"X" * (MAX_FILE_SIZE_BYTES + 1024)
    file = UploadFile(filename="huge.pdf", file=io.BytesIO(oversized))
    with pytest.raises(HTTPException) as exc_info:
        await validate_and_save_upload(file, subfolder="test")
    assert exc_info.value.status_code == 413

