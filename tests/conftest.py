import os
import sys
import io
import pytest
from PIL import Image

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Disable background cleanup thread during test execution
os.environ['BRANDKIT_CLEANUP_ENABLED'] = '0'
os.environ['BRANDKIT_SECRET_KEY'] = 'test-secret-key-for-brandkit-testing'

import app as brandkit_app

brandkit_app.limiter.enabled = False


@pytest.fixture
def app_instance(tmp_path):
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    brandkit_app.app.config.update({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
        "RATELIMIT_ENABLED": False,
        "UPLOAD_FOLDER": str(upload_dir),
    })
    return brandkit_app.app


@pytest.fixture
def client(app_instance):
    return app_instance.test_client()


@pytest.fixture
def csrf_client(tmp_path):
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    brandkit_app.app.config.update({
        "TESTING": True,
        "WTF_CSRF_ENABLED": True,
        "UPLOAD_FOLDER": str(upload_dir),
    })
    yield brandkit_app.app.test_client()
    brandkit_app.app.config["WTF_CSRF_ENABLED"] = False


@pytest.fixture
def sample_png_bytes():
    buf = io.BytesIO()
    # 120x120 RGBA image with colored rectangle
    img = Image.new("RGBA", (120, 120), color=(255, 0, 0, 255))
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.getvalue()


@pytest.fixture
def sample_jpg_bytes():
    buf = io.BytesIO()
    img = Image.new("RGB", (100, 100), color=(0, 128, 255))
    img.save(buf, format="JPEG")
    buf.seek(0)
    return buf.getvalue()


@pytest.fixture
def sample_transparent_png_bytes():
    buf = io.BytesIO()
    # 100x100 transparent image with 40x40 solid center
    img = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
    for x in range(30, 70):
        for y in range(30, 70):
            img.putpixel((x, y), (50, 150, 250, 255))
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.getvalue()


@pytest.fixture
def corrupt_file_bytes():
    return b"Corrupted content - definitely not an image file payload"
