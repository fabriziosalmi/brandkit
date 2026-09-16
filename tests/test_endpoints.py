import io
import zipfile
from flask import json


def test_index_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.content_type
    html = response.get_data(as_text=True)
    assert "BrandKit" in html
    assert "csrf_token" in html or "csrf-token" in html or "input type=\"hidden\"" in html


def test_format_info_endpoint(client):
    response = client.get("/format-info")
    assert response.status_code == 200
    assert response.is_json
    data = response.get_json()
    assert data["success"] is True
    assert "categories" in data
    assert "purposes" in data
    assert "recommendations" in data
    assert "Website Essentials" in data["recommendations"]


def test_analyze_endpoint_success(client, sample_png_bytes):
    data = {
        "file": (io.BytesIO(sample_png_bytes), "test_logo.png")
    }
    response = client.post("/analyze", data=data, content_type="multipart/form-data")
    assert response.status_code == 200
    assert response.is_json
    res = response.get_json()
    assert res["success"] is True
    assert "analysis" in res
    analysis = res["analysis"]
    assert "prominent_color" in analysis
    assert "has_white_area" in analysis
    assert "white_area_ratio" in analysis
    assert isinstance(analysis["prominent_color"], list)


def test_upload_endpoint_generates_formats_and_zip(client, sample_png_bytes):
    data = {
        "file": (io.BytesIO(sample_png_bytes), "brand_asset.png"),
        "selected_formats": ["website", "favicon"],
        "output_formats": ["png", "ico"],
        "quality": "90",
    }
    response = client.post("/upload", data=data, content_type="multipart/form-data")
    assert response.status_code == 200
    assert response.is_json
    payload = response.get_json()
    assert payload["success"] is True
    results = payload["results"]
    assert "website" in results
    assert "png" in results["website"]["outputs"]
    assert "original" in results
    assert "zip" in results
    assert results["zip"]["filename"].endswith(".zip")


def test_download_zip_roundtrip(client, sample_png_bytes):
    # 1. Upload to generate zip
    upload_data = {
        "file": (io.BytesIO(sample_png_bytes), "roundtrip.png"),
        "selected_formats": ["website"],
        "output_formats": ["png"],
    }
    upload_res = client.post("/upload", data=upload_data, content_type="multipart/form-data")
    assert upload_res.status_code == 200
    zip_filename = upload_res.get_json()["results"]["zip"]["filename"]

    # 2. Download the generated zip
    download_res = client.get(f"/download-zip/{zip_filename}")
    assert download_res.status_code == 200
    assert download_res.headers.get("Content-Disposition", "").startswith("attachment")
    
    # 3. Verify zip archive is valid and non-empty
    zip_bytes = io.BytesIO(download_res.data)
    with zipfile.ZipFile(zip_bytes, "r") as zf:
        namelist = zf.namelist()
        assert len(namelist) > 0
        assert any("website" in name for name in namelist)
