import io
import pytest
from flask import json


def test_upload_missing_file_part(client):
    response = client.post("/upload", data={}, content_type="multipart/form-data")
    assert response.status_code == 400
    assert response.is_json
    assert response.get_json()["error"] == "No file part"


def test_upload_empty_filename(client):
    data = {"file": (io.BytesIO(b""), "")}
    response = client.post("/upload", data=data, content_type="multipart/form-data")
    assert response.status_code == 400
    assert response.is_json
    assert response.get_json()["error"] == "No selected file"


def test_upload_disallowed_extension(client):
    data = {"file": (io.BytesIO(b"print('hack')"), "exploit.py")}
    response = client.post("/upload", data=data, content_type="multipart/form-data")
    assert response.status_code == 400
    assert response.is_json
    assert response.get_json()["error"] == "File type not allowed"


def test_upload_corrupt_image_payload(client, corrupt_file_bytes):
    data = {"file": (io.BytesIO(corrupt_file_bytes), "corrupt.png")}
    response = client.post("/upload", data=data, content_type="multipart/form-data")
    assert response.status_code == 400
    assert response.is_json
    assert "Invalid image file" in response.get_json()["error"]


def test_analyze_missing_file_part(client):
    response = client.post("/analyze", data={}, content_type="multipart/form-data")
    assert response.status_code == 400
    assert response.is_json
    assert response.get_json()["success"] is False
    assert response.get_json()["error"] == "No file part"


def test_analyze_empty_filename(client):
    data = {"file": (io.BytesIO(b""), "")}
    response = client.post("/analyze", data=data, content_type="multipart/form-data")
    assert response.status_code == 400
    assert response.is_json
    assert response.get_json()["success"] is False
    assert response.get_json()["error"] == "No selected file"


def test_analyze_disallowed_extension(client):
    data = {"file": (io.BytesIO(b"echo evil"), "danger.sh")}
    response = client.post("/analyze", data=data, content_type="multipart/form-data")
    assert response.status_code == 400
    assert response.is_json
    assert response.get_json()["success"] is False
    assert response.get_json()["error"] == "File type not allowed"


def test_download_zip_non_existent(client):
    response = client.get("/download-zip/nonexistent_file_12345.zip")
    assert response.status_code == 404
    assert response.is_json
    assert response.get_json()["error"] == "File not found"


@pytest.mark.parametrize("traversal_path", [
    "../../app.py",
    "..%2F..%2Fapp.py",
    "....//....//app.py",
    "/etc/passwd",
    "app.py",
    "config.json",
    "test.zip.exe",
])
def test_download_zip_path_traversal_rejection(client, traversal_path):
    response = client.get(f"/download-zip/{traversal_path}")
    assert response.status_code == 404


def test_payload_size_limit_rejection(app_instance):
    # Set a tiny max content length (100 bytes)
    orig_max = app_instance.config.get("MAX_CONTENT_LENGTH")
    app_instance.config["MAX_CONTENT_LENGTH"] = 100
    try:
        client = app_instance.test_client()
        oversized_data = {
            "file": (io.BytesIO(b"X" * 1024), "big.png")
        }
        response = client.post("/upload", data=oversized_data, content_type="multipart/form-data")
        assert response.status_code == 413
    finally:
        app_instance.config["MAX_CONTENT_LENGTH"] = orig_max


def test_csrf_protection_rejects_unauthenticated_post(csrf_client, sample_png_bytes):
    # With CSRF protection enabled, a POST without CSRF token must be rejected with 400
    data = {
        "file": (io.BytesIO(sample_png_bytes), "test.png")
    }
    response = csrf_client.post("/upload", data=data, content_type="multipart/form-data")
    assert response.status_code == 400
