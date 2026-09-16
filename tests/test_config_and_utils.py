import json
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


def test_load_config_missing_file_falls_back(caplog):
    with caplog.at_level("WARNING"):
        with patch("builtins.open", side_effect=FileNotFoundError):
            config = brandkit_app.load_config()
            assert config == brandkit_app.DEFAULT_CONFIG
            assert any("not found" in record.message for record in caplog.records)


def test_load_config_invalid_json_falls_back(caplog):
    with caplog.at_level("ERROR"):
        with patch("builtins.open", mock_open(read_data="INVALID_JSON_CONTENT")):
            config = brandkit_app.load_config()
            assert config == brandkit_app.DEFAULT_CONFIG
            assert any("not valid JSON" in record.message for record in caplog.records)


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


def test_validate_format_spec():
    # Valid specs
    assert brandkit_app.validate_format_spec("banner", {"width": 800, "height": 600})
    assert brandkit_app.validate_format_spec("square", {"width": 500, "height": 500, "description": "test"})

    # Invalid specs: non-dict, non-int, negative or zero dimensions, boolean
    assert not brandkit_app.validate_format_spec("bad1", "not a dict")
    assert not brandkit_app.validate_format_spec("bad2", {"width": -100, "height": 200})
    assert not brandkit_app.validate_format_spec("bad3", {"width": 100, "height": 0})
    assert not brandkit_app.validate_format_spec("bad4", {"width": "100", "height": 200})
    assert not brandkit_app.validate_format_spec("bad5", {"width": True, "height": 200})
    assert not brandkit_app.validate_format_spec("bad6", {"width": 100})


def test_load_config_schema_validation_filters_corrupt_formats(tmp_path):
    config_file = tmp_path / "custom_config.json"
    custom_data = {
        "formats": {
            "valid_custom": {"width": 1920, "height": 1080, "description": "Full HD"},
            "corrupt_negative": {"width": -500, "height": 300},
            "corrupt_string": {"width": "bad", "height": "bad"},
            "corrupt_missing": {"description": "no dimensions"}
        },
        "format_categories": {
            "CustomCategory": ["valid_custom"],
            "BadCategory": "not a list"
        }
    }
    config_file.write_text(json.dumps(custom_data))

    cfg = brandkit_app.load_config(str(config_file))
    assert "valid_custom" in cfg["formats"]
    assert cfg["formats"]["valid_custom"]["width"] == 1920
    assert "corrupt_negative" not in cfg["formats"]
    assert "corrupt_string" not in cfg["formats"]
    assert "corrupt_missing" not in cfg["formats"]
    assert "CustomCategory" in cfg["format_categories"]
    assert "BadCategory" not in cfg["format_categories"]

