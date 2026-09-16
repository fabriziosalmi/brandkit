import json
import os
import numpy as np

DEFAULT_MAX_UPLOAD_MB = 16
DEFAULT_ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

DEFAULT_CONFIG = {
    "formats": {
        "website": {"width": 1200, "height": 630, "description": "Open Graph, Twitter Cards"},
        "webapp": {"width": 512, "height": 512, "description": "Web App Manifest Icon"},
        "mobile": {"width": 1080, "height": 1920, "description": "Mobile Screens"},
        "social": {"width": 1080, "height": 1080, "description": "Social Media Posts"},
        "favicon": {"width": 48, "height": 48, "description": "Browser Favicon (generates .ico)"},
        "logo_transparent": {"width": 512, "height": 512, "description": "Transparent Logo (PNG only)"},
        "background_desktop": {"width": 1920, "height": 1080, "description": "Desktop Background"},
        "background_mobile": {"width": 1080, "height": 1920, "description": "Mobile Background"},
        "square_1024": {"width": 1024, "height": 1024, "description": "Square Format 1024x1024"},
        "hero_desktop": {"width": 1200, "height": 400, "description": "Website Hero Banner"},
        "hero_mobile": {"width": 800, "height": 600, "description": "Mobile Hero Banner"},
        
        # Social Media Specific
        "instagram": {"width": 1080, "height": 1080, "description": "Instagram Post"},
        "instagram_story": {"width": 1080, "height": 1920, "description": "Instagram Story"},
        "facebook": {"width": 1200, "height": 630, "description": "Facebook Post"},
        "twitter": {"width": 1200, "height": 675, "description": "Twitter Card"},
        "linkedin": {"width": 1200, "height": 627, "description": "LinkedIn Post"},
        "youtube_thumbnail": {"width": 1280, "height": 720, "description": "YouTube Thumbnail"},
        
        # Additional Useful Formats
        "profile_picture": {"width": 400, "height": 400, "description": "Profile Picture"},
        "cover_photo": {"width": 1920, "height": 1080, "description": "Cover Photo"},
        "square_small": {"width": 256, "height": 256, "description": "Small Square Icon"},
        "square_large": {"width": 2048, "height": 2048, "description": "Large Square Format"},
        "business_card": {"width": 1050, "height": 600, "description": "Business Card"},
        "poster": {"width": 1080, "height": 1350, "description": "Poster Format"},
        
        # E-commerce
        "product_square": {"width": 800, "height": 800, "description": "Product Image Square"},
        "product_wide": {"width": 1200, "height": 800, "description": "Product Image Wide"},
        
        # Print-ready
        "print_a4": {"width": 2480, "height": 3508, "description": "A4 Print Ready (300 DPI)"},
        "print_letter": {"width": 2550, "height": 3300, "description": "Letter Print Ready (300 DPI)"}
    },
    "format_categories": {
        "Social Media": ["social", "instagram", "instagram_story", "facebook", "twitter", "linkedin", "youtube_thumbnail"],
        "Website": ["website", "hero_desktop", "hero_mobile", "background_desktop", "cover_photo"],
        "Mobile": ["mobile", "webapp", "background_mobile", "profile_picture"],
        "Branding": ["logo_transparent", "square_1024", "favicon", "square_small", "square_large"],
        "E-commerce": ["product_square", "product_wide", "square_1024"],
        "Print": ["print_a4", "print_letter", "poster", "business_card"]
    },
    "output_formats": ["png", "jpg", "webp", "ico"],
    "preprocessing_options": {
        "grayscale": False,
        "bw": False,
        "invert": False,
        "hue_shift": 0,
        "temperature": 0,
        "enhance_contrast": False,
        "apply_blur": False,
        "blur_radius": 2,
        "add_watermark": False,
        "watermark_text": "© BrandKit",
        "watermark_opacity": 0.3,
        "vignette": False,
        "vignette_strength": 0.5,
        "saturation": 1.0,
        "brightness": 1.0,
        "sharpen": False,
        "sharpen_radius": 1.0,
        "remove_background": False,
        "background_color": "#FFFFFF",
        "edge_smooth": False,
        "noise_reduction": False,
        "auto_crop": False,
        "shadow_effect": False,
        "shadow_opacity": 0.3,
        "shadow_blur": 4
    }
}


def load_config(config_path='config.json'):
    """Load configuration with proper deep merging of dictionaries"""
    config = DEFAULT_CONFIG.copy()
    try:
        with open(config_path, 'r') as f:
            file_config = json.load(f)
            # Deep merge the dictionaries
            for key, value in file_config.items():
                if key in config and isinstance(config[key], dict) and isinstance(value, dict):
                    # Merge nested dictionaries
                    config[key].update(value)
                else:
                    # Replace or add non-dict values
                    config[key] = value
    except FileNotFoundError:
        print("Warning: config.json not found. Using default configuration.")
    except json.JSONDecodeError:
        print("Error: config.json is not valid JSON. Using default configuration.")
    return config


def allowed_file(filename, allowed_extensions=None):
    if allowed_extensions is None:
        allowed_extensions = DEFAULT_ALLOWED_EXTENSIONS
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def ensure_serializable(obj):
    """Ensure objects can be serialized to JSON by converting special types"""
    if isinstance(obj, dict):
        return {k: ensure_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [ensure_serializable(i) for i in obj]
    elif isinstance(obj, (int, float, str, bool, type(None))):
        return obj
    elif isinstance(obj, np.ndarray):
        return ensure_serializable(obj.tolist())
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    else:
        # Convert any other types to string representation
        return str(obj)
