import os
import time
import numpy as np
from unittest.mock import patch, mock_open
import app as brandkit_app


def test_load_config_loads_valid_structure():
    config = brandkit_app.load_config()
    assert "formats" in config
    assert "format_categories" in config
    assert "website" in config["formats"]
    assert "favicon" in config["formats"]
    assert config["formats"]["website"]["width"] == 1200
    assert config["formats"]["website"]["height"] == 630


def test_load_config_missing_file_falls_back():
    with patch("builtins.open", side_effect=FileNotFoundError):
        config = brandkit_app.load_config()
        assert config == brandkit_app.DEFAULT_CONFIG


def test_load_config_invalid_json_falls_back():
    with patch("builtins.open", mock_open(read_data="INVALID_JSON_CONTENT")):
        config = brandkit_app.load_config()
        assert config == brandkit_app.DEFAULT_CONFIG


def test_allowed_file():
    # Valid extensions
    assert brandkit_app.allowed_file("logo.png")
    assert brandkit_app.allowed_file("photo.JPG")
    assert brandkit_app.allowed_file("banner.jpeg")
    assert brandkit_app.allowed_file("animation.gif")
    assert brandkit_app.allowed_file("modern.webp")

    # Invalid extensions and edge cases
    assert not brandkit_app.allowed_file("script.py")
    assert not brandkit_app.allowed_file("exploit.sh")
    assert not brandkit_app.allowed_file("malicious.exe")
    assert not brandkit_app.allowed_file("graphic.svg")
    assert not brandkit_app.allowed_file("no_extension")
    assert not brandkit_app.allowed_file("sneaky.png.exe")


def test_ensure_serializable():
    raw_data = {
        "int": np.int64(42),
        "float": np.float64(3.14),
        "array": np.array([1, 2, 3]),
        "list": [np.int32(10), "hello"],
        "nested": {"key": True},
        "none": None,
    }
    serialized = brandkit_app.ensure_serializable(raw_data)
    assert isinstance(serialized["int"], int)
    assert isinstance(serialized["float"], float)
    assert isinstance(serialized["array"], list)
    assert serialized["array"] == [1, 2, 3]
    assert serialized["list"][0] == 10
    assert serialized["nested"]["key"] is True
    assert serialized["none"] is None


def test_cleanup_old_files(app_instance, tmp_path):
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    cache_dir = upload_dir / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    # 1. Old file (> 24 hours)
    old_file = upload_dir / "old_image.png"
    old_file.write_text("old image data")
    old_mtime = time.time() - (30 * 3600)
    os.utime(str(old_file), (old_mtime, old_mtime))

    # 2. Recent file (< 24 hours)
    recent_file = upload_dir / "recent_image.png"
    recent_file.write_text("recent image data")
    recent_mtime = time.time() - (2 * 3600)
    os.utime(str(recent_file), (recent_mtime, recent_mtime))

    # 3. README.md file (must never be deleted even if old)
    readme_file = upload_dir / "README.md"
    readme_file.write_text("# Uploads directory readme")
    os.utime(str(readme_file), (old_mtime, old_mtime))

    # 4. Old cache file
    old_cache = cache_dir / "old_cached.png"
    old_cache.write_text("old cache")
    os.utime(str(old_cache), (old_mtime, old_mtime))

    brandkit_app.cleanup_old_files(max_age_hours=24)

    assert not old_file.exists()
    assert not old_cache.exists()
    assert recent_file.exists()
    assert readme_file.exists()


def test_cleanup_memory():
    # Should execute without throwing any exception
    res = brandkit_app.cleanup_memory()
    assert res is not None
