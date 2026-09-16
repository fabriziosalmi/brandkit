import json
import logging
import os
import numpy as np

logger = logging.getLogger(__name__)

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


def validate_format_spec(name, spec):
    """Validate that a format specification has positive integer width and height."""
    if not isinstance(spec, dict):
        return False
    width = spec.get("width")
    height = spec.get("height")
    if not isinstance(width, int) or isinstance(width, bool) or width <= 0:
        return False
    if not isinstance(height, int) or isinstance(height, bool) or height <= 0:
        return False
    return True


def load_config(config_path='config.json'):
    """Load configuration with proper deep merging and schema validation"""
    config = DEFAULT_CONFIG.copy()
    try:
        with open(config_path, 'r') as f:
            file_config = json.load(f)
            if isinstance(file_config, dict):
                # Validate and merge 'formats'
                if 'formats' in file_config and isinstance(file_config['formats'], dict):
                    if 'formats' not in config:
                        config['formats'] = {}
                    for fmt_name, fmt_spec in file_config['formats'].items():
                        if validate_format_spec(fmt_name, fmt_spec):
                            config['formats'][fmt_name] = {
                                'width': int(fmt_spec['width']),
                                'height': int(fmt_spec['height']),
                                'description': str(fmt_spec.get('description', ''))
                            }
                        else:
                            logger.warning("Invalid format specification for '%s' in %s - skipping", fmt_name, config_path)

                # Validate and merge 'format_categories'
                if 'format_categories' in file_config and isinstance(file_config['format_categories'], dict):
                    if 'format_categories' not in config:
                        config['format_categories'] = {}
                    for cat_name, items in file_config['format_categories'].items():
                        if isinstance(items, list) and all(isinstance(i, str) for i in items):
                            config['format_categories'][cat_name] = list(items)
                        else:
                            logger.warning("Invalid format_categories list for '%s' in %s - skipping", cat_name, config_path)

                # Merge other top-level keys safely
                for key, value in file_config.items():
                    if key in ('formats', 'format_categories'):
                        continue
                    if key in config and isinstance(config[key], dict) and isinstance(value, dict):
                        for sub_k, sub_v in value.items():
                            if isinstance(sub_v, (int, float, str, bool)):
                                config[key][sub_k] = sub_v
                    elif isinstance(value, (dict, list, int, float, str, bool)):
                        config[key] = value
    except FileNotFoundError:
        logger.warning("Configuration file '%s' not found. Using default configuration.", config_path)
    except json.JSONDecodeError as e:
        logger.error("Configuration file '%s' is not valid JSON: %s. Using default configuration.", config_path, e)
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
