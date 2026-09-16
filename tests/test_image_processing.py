import os
import io
import numpy as np
from PIL import Image
import app as brandkit_app


def test_shift_hue():
    img = Image.new("RGBA", (50, 50), (255, 0, 0, 255))
    shifted = brandkit_app.shift_hue(img, 120)
    assert shifted.size == (50, 50)
    assert shifted.mode == "RGBA"
    # Alpha must be preserved
    assert shifted.getchannel("A").getextrema() == (255, 255)
    # Red should have shifted to green/blue hue
    r, g, b, _ = shifted.getpixel((25, 25))
    assert g > 100 or b > 100


def test_adjust_temperature():
    img = Image.new("RGBA", (50, 50), (128, 128, 128, 255))
    
    # Warm temperature boosts red
    warm = brandkit_app.adjust_temperature(img, 40)
    r_w, _, b_w, _ = warm.getpixel((25, 25))
    assert r_w > 128
    assert b_w < 128

    # Cool temperature boosts blue
    cool = brandkit_app.adjust_temperature(img, -40)
    r_c, _, b_c, _ = cool.getpixel((25, 25))
    assert b_c > 128
    assert r_c < 128


def test_apply_vignette():
    img = Image.new("RGBA", (100, 100), (200, 200, 200, 255))
    vignetted = brandkit_app.apply_vignette(img, strength=0.8)
    assert vignetted.size == (100, 100)
    
    center_pixel = vignetted.getpixel((50, 50))[:3]
    corner_pixel = vignetted.getpixel((0, 0))[:3]
    # Center should be brighter than corners
    assert sum(center_pixel) > sum(corner_pixel)


def test_create_radial_gradient():
    gradient = brandkit_app.create_radial_gradient((80, 80), (255, 255, 255), (0, 0, 0))
    assert gradient.size == (80, 80)
    assert gradient.mode == "RGBA"
    
    center = gradient.getpixel((40, 40))[:3]
    corner = gradient.getpixel((0, 0))[:3]
    assert sum(center) > sum(corner)


def test_darken_color():
    color = (100, 200, 50)
    darkened = brandkit_app.darken_color(color, factor=0.5)
    assert darkened == (50, 100, 25)


def test_create_favicon(app_instance, tmp_path):
    img = Image.new("RGBA", (128, 128), (255, 100, 50, 255))
    res = brandkit_app.create_favicon(img, "test_logo")
    assert "path" in res
    assert os.path.exists(res["path"])
    assert res["path"].endswith(".ico")
    
    with Image.open(res["path"]) as ico:
        assert ico.format == "ICO"


def test_auto_crop_image():
    # 100x100 transparent image with 20x20 box in center (from 40 to 60)
    img = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
    for x in range(40, 60):
        for y in range(40, 60):
            img.putpixel((x, y), (255, 0, 0, 255))
    
    cropped = brandkit_app.auto_crop_image(img, padding=5)
    # Target size is 20 + 2*padding = 30x30
    assert cropped.size == (30, 30)


def test_add_drop_shadow():
    img = Image.new("RGBA", (50, 50), (255, 0, 0, 255))
    shadowed = brandkit_app.add_drop_shadow(img, offset=(5, 5), blur_radius=4)
    assert shadowed.width > 50
    assert shadowed.height > 50


def test_enhance_image_quality():
    img = Image.new("RGBA", (50, 50), (100, 150, 200, 255))
    enhanced = brandkit_app.enhance_image_quality(img)
    assert enhanced.size == (50, 50)


def test_get_prominent_color():
    # Mostly green image with white background
    img = Image.new("RGBA", (64, 64), (255, 255, 255, 255))
    for x in range(10, 50):
        for y in range(10, 50):
            img.putpixel((x, y), (0, 200, 50, 255))
            
    color = brandkit_app.get_prominent_color(img)
    assert isinstance(color, list)
    assert color == [0, 200, 50]


def test_has_significant_white_area():
    # All white image
    white_img = Image.new("RGBA", (50, 50), (255, 255, 255, 255))
    has_white, ratio = brandkit_app.has_significant_white_area(white_img)
    assert bool(has_white) is True
    assert ratio > 0.9

    # Dark image
    dark_img = Image.new("RGBA", (50, 50), (20, 20, 20, 255))
    has_white_dark, ratio_dark = brandkit_app.has_significant_white_area(dark_img)
    assert bool(has_white_dark) is False
    assert ratio_dark < 0.1


def test_optimize_image():
    img = Image.new("RGBA", (50, 50), (255, 100, 50, 255))
    
    # JPG conversion strips alpha and adds white background
    jpg_img, jpg_opts = brandkit_app.optimize_image(img, "jpg", quality=85)
    assert jpg_img.mode == "RGB"
    assert jpg_opts["quality"] == 85

    # WebP retains RGBA
    webp_img, webp_opts = brandkit_app.optimize_image(img, "webp", quality=90)
    assert webp_img.mode == "RGBA"
    assert webp_opts["quality"] == 90

    # PNG optimization options
    png_img, png_opts = brandkit_app.optimize_image(img, "png")
    assert png_img.mode == "RGBA"
    assert png_opts["optimize"] is True


def test_preprocess_image():
    img = Image.new("RGBA", (60, 60), (200, 100, 50, 255))
    opts = {
        "grayscale": True,
        "enhance_contrast": True,
        "vignette": True,
        "vignette_strength": 0.5,
        "saturation": 1.2,
        "brightness": 1.1,
    }
    processed = brandkit_app.preprocess_image(img, opts)
    assert processed.size == (60, 60)


def test_generate_variations():
    vars_list = brandkit_app.generate_variations()
    assert isinstance(vars_list, list)
    assert len(vars_list) >= 5
    labels = [v["label"] for v in vars_list]
    assert "Original" in labels
    assert "Grayscale" in labels
    assert "B&W" in labels


def test_save_to_cache_atomic_behavior(tmp_path):
    img = Image.new("RGBA", (32, 32), (10, 20, 30, 255))
    cache_key = "testcachekey123"
    upload_dir = tmp_path / "uploads"
    
    brandkit_app.save_to_cache(img, cache_key, 32, 32, upload_folder=str(upload_dir))
    
    cache_dir = upload_dir / "cache"
    assert cache_dir.exists()
    final_cache_file = cache_dir / f"{cache_key}_32x32.png"
    assert final_cache_file.exists()
    
    # Verify no dangling temporary files remain
    tmp_files = list(cache_dir.glob("*.tmp.*"))
    assert len(tmp_files) == 0
    
    # Verify cached image can be read
    cached_img = brandkit_app.get_from_cache(cache_key, 32, 32, upload_folder=str(upload_dir))
    assert cached_img is not None
    assert cached_img.size == (32, 32)

