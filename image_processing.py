import os
import json
import zipfile
import time
import io
import uuid
import hashlib
import logging
import traceback
from datetime import datetime
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont, ImageOps
import numpy as np

from config_utils import load_config, DEFAULT_CONFIG

# Import psutil if available for memory monitoring
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# Import additional libraries for background removal
try:
    from rembg import remove, new_session
    REMBG_AVAILABLE = True
except ImportError:
    REMBG_AVAILABLE = False

# Import cv2 for advanced image processing if available
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False


def _get_upload_folder(upload_folder=None):
    if upload_folder is not None:
        return upload_folder
    try:
        from flask import current_app
        return current_app.config.get('UPLOAD_FOLDER', 'static/uploads')
    except Exception:
        return 'static/uploads'


def shift_hue(img, deg):
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    arr = np.array(img)
    r, g, b, a = arr[..., 0], arr[..., 1], arr[..., 2], arr[..., 3]
    hsv = np.array(Image.fromarray(np.stack([r, g, b], axis=-1)).convert('HSV'))
    hsv[..., 0] = (hsv[..., 0].astype(int) + int(deg / 360 * 255)) % 255
    rgb = Image.fromarray(hsv, 'HSV').convert('RGBA')
    arr2 = np.array(rgb)
    arr2[..., 3] = a
    return Image.fromarray(arr2, 'RGBA')


def adjust_temperature(img, temp):
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    arr = np.array(img).astype(np.int16)
    if temp > 0:
        arr[..., 0] = np.clip(arr[..., 0] + temp, 0, 255)
        arr[..., 2] = np.clip(arr[..., 2] - temp // 2, 0, 255)
    elif temp < 0:
        arr[..., 2] = np.clip(arr[..., 2] + abs(temp), 0, 255)
        arr[..., 0] = np.clip(arr[..., 0] + temp // 2, 0, 255)
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    return Image.fromarray(arr, 'RGBA')


def apply_vignette(img, strength=0.5):
    """Apply vignette effect to image with adjustable strength."""
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    width, height = img.size
    x = np.linspace(-1, 1, width)
    y = np.linspace(-1, 1, height)
    xx, yy = np.meshgrid(x, y)
    distance = np.sqrt(xx**2 + yy**2)
    distance = distance / np.max(distance)
    
    mask = 1 - (distance * strength)
    mask = np.clip(mask, 0, 1)
    
    arr = np.array(img)
    arr[..., :3] = (arr[..., :3] * mask[..., np.newaxis]).astype(np.uint8)
    
    return Image.fromarray(arr, 'RGBA')


def darken_color(color, factor=0.7):
    return tuple(max(0, int(c * factor)) for c in color)


def create_radial_gradient(size, center_color, edge_color):
    width, height = size
    gradient = Image.new('RGBA', (width, height), tuple(edge_color) + (255,))
    cx, cy = width // 2, height // 2
    max_radius = (width**2 + height**2) ** 0.5 / 2
    arr = np.zeros((height, width, 4), dtype=np.uint8)
    for y in range(height):
        for x in range(width):
            dx, dy = x - cx, y - cy
            dist = (dx**2 + dy**2) ** 0.5
            t = min(dist / max_radius, 1.0)
            color = tuple(
                int(center_color[i] * (1 - t) + edge_color[i] * t) for i in range(3)
            )
            arr[y, x, :3] = color
            arr[y, x, 3] = 255
    return Image.fromarray(arr, 'RGBA')


def generate_variations():
    return [
        {'label': 'Original', 'opts': {}},
        {'label': 'Grayscale', 'opts': {'grayscale': True}},
        {'label': 'B&W', 'opts': {'bw': True}},
        {'label': 'Inverted', 'opts': {'invert': True}},
        {'label': 'Hue_+60', 'opts': {'hue_shift': 60}},
        {'label': 'Hue_-60', 'opts': {'hue_shift': -60}},
        {'label': 'Warm', 'opts': {'temperature': 40}},
        {'label': 'Cool', 'opts': {'temperature': -40}},
        {'label': 'Grayscale_Contrast', 'opts': {'grayscale': True, 'enhance_contrast': True}},
        {'label': 'Inverted_Blur', 'opts': {'invert': True, 'apply_blur': True, 'blur_radius': 2}},
    ]


def create_favicon(image, filename_without_ext, upload_folder=None):
    upload_dir = _get_upload_folder(upload_folder)
    favicon_sizes = [16, 32, 48]
    output_filename = f"{filename_without_ext}_favicon.ico"
    output_path = os.path.join(upload_dir, output_filename)
    favicon_images = []
    try:
        for size in favicon_sizes:
            img_copy = image.copy()
            img_copy.thumbnail((size, size), Image.LANCZOS)
            favicon_images.append(img_copy)
        favicon_images[0].save(
            output_path,
            format='ICO',
            sizes=[(img.width, img.height) for img in favicon_images]
        )
        return {
            'path': output_path,
            'url': f"/{upload_dir}/{output_filename}"
        }
    except Exception as e:
        logging.error(f"Error creating favicon: {e}")
        raise ValueError("Failed to create favicon")


def auto_crop_image(image, padding=10):
    """Auto crop image to remove transparent/white areas"""
    try:
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        bbox = image.getbbox()
        
        if bbox:
            left, top, right, bottom = bbox
            left = max(0, left - padding)
            top = max(0, top - padding)
            right = min(image.width, right + padding)
            bottom = min(image.height, bottom + padding)
            
            result = image.crop((left, top, right, bottom))
            return result
        else:
            return image
    except Exception as e:
        logging.error(f"Error auto-cropping image: {e}")
        return image


def add_drop_shadow(image, offset=(5, 5), blur_radius=4, shadow_color=(0, 0, 0), opacity=0.3):
    """Add a drop shadow effect to the image"""
    try:
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        shadow = Image.new('RGBA', 
                          (image.width + abs(offset[0]) + blur_radius * 2, 
                           image.height + abs(offset[1]) + blur_radius * 2), 
                          (0, 0, 0, 0))
        
        shadow_color_with_alpha = shadow_color + (int(255 * opacity),)
        _, _, _, alpha = image.split()
        shadow_layer = Image.new('RGBA', image.size, shadow_color_with_alpha)
        shadow_layer.putalpha(alpha)
        
        shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        
        shadow_x = blur_radius + max(0, offset[0])
        shadow_y = blur_radius + max(0, offset[1])
        shadow.paste(shadow_layer, (shadow_x, shadow_y), shadow_layer)
        
        orig_x = blur_radius + max(0, -offset[0])
        orig_y = blur_radius + max(0, -offset[1])
        shadow.paste(image, (orig_x, orig_y), image)
        
        return shadow
    except Exception as e:
        logging.error(f"Error adding drop shadow: {e}")
        return image


def enhance_image_quality(image):
    """Apply various enhancements to improve image quality"""
    try:
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.1)
        
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(1.05)
        
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.05)
        
        return image
    except Exception:
        return image


def reduce_noise(image, strength=1):
    """Reduce noise in the image using PIL filters"""
    try:
        if strength == 1:
            result = image.filter(ImageFilter.MedianFilter(size=3))
        elif strength == 2:
            result = image.filter(ImageFilter.MedianFilter(size=5))
        else:
            result = image.filter(ImageFilter.SMOOTH_MORE)
        return result
    except Exception:
        return image


def smooth_edges(image, radius=2):
    """Smooth the edges of a transparent image"""
    try:
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        r, g, b, a = image.split()
        smoothed_alpha = a.filter(ImageFilter.GaussianBlur(radius=radius))
        result = Image.merge('RGBA', (r, g, b, smoothed_alpha))
        return result
    except Exception:
        return image


def remove_background(image, method='auto'):
    """Remove background from image using various methods"""
    if not REMBG_AVAILABLE:
        logging.warning("Background removal not available - rembg not installed")
        return image
    
    try:
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        if method == 'person':
            session = new_session('u2net_human_seg')
        elif method == 'object':
            session = new_session('u2net')
        elif method == 'anime':
            session = new_session('u2net_anime')
        else:
            session = new_session('u2net')
        
        output = remove(img_bytes.getvalue(), session=session)
        result = Image.open(io.BytesIO(output)).convert('RGBA')
        return result
    except Exception as e:
        logging.error(f"Error removing background: {e}")
        return image


def apply_background_color(image, bg_color="#FFFFFF"):
    """Apply a solid background color to a transparent image"""
    try:
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        if isinstance(bg_color, str):
            bg_color = bg_color.strip()
            if bg_color.startswith('#'):
                hex_color = bg_color[1:]
            else:
                hex_color = bg_color
            
            if len(hex_color) == 3:
                hex_color = ''.join([c * 2 for c in hex_color])
            elif len(hex_color) != 6:
                hex_color = "FFFFFF"
            
            try:
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)
            except ValueError:
                r, g, b = 255, 255, 255
        else:
            r, g, b = bg_color[:3] if len(bg_color) >= 3 else (255, 255, 255)
        
        background = Image.new('RGBA', image.size, (r, g, b, 255))
        result = Image.alpha_composite(background, image)
        return result
    except Exception as e:
        logging.error(f"Error applying background color: {e}")
        return image


def get_prominent_color(image, exclude_white=True):
    img = image.convert('RGBA').resize((64, 64))
    arr = np.array(img)
    pixels = arr.reshape(-1, 4)
    pixels = pixels[pixels[:, 3] > 0]  # Filter out fully transparent pixels
    if exclude_white:
        pixels = pixels[(pixels[:, 0:3] < 245).any(axis=1)]  # Filter out white pixels
    if len(pixels) == 0:
        return [200, 200, 200]
    colors, counts = np.unique(pixels[:, :3], axis=0, return_counts=True)
    prominent = colors[counts.argmax()]
    return [int(x) for x in prominent]


def has_significant_white_area(image, threshold=0.15):
    img = image.convert('RGBA')
    arr = np.array(img)
    total = arr.shape[0] * arr.shape[1]
    white = ((arr[..., :3] > 245).all(axis=-1)) & (arr[..., 3] > 200)
    transparent = arr[..., 3] < 32
    white_or_transparent = white | transparent
    ratio = np.sum(white_or_transparent) / total
    return ratio > threshold, ratio


def optimize_image(img, output_format, quality=95, strip_metadata=False):
    """Apply format-specific optimizations to images"""
    if strip_metadata:
        img = img.copy()
        data = list(img.getdata())
        img_without_exif = Image.new(img.mode, img.size)
        img_without_exif.putdata(data)
        img = img_without_exif
    
    if output_format.lower() in ['jpg', 'jpeg']:
        if img.mode == 'RGBA':
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1])
            img = background
        else:
            img = img.convert('RGB')
        return img, {'quality': quality}
    elif output_format.lower() == 'webp':
        return img, {'quality': quality, 'lossless': False, 'method': 6}
    elif output_format.lower() == 'png':
        return img, {'optimize': True, 'compress_level': 9}
    elif output_format.lower() == 'ico':
        return img, {}
    else:
        return img, {}


def preprocess_image(image, options):
    """Enhanced preprocessing with background removal and advanced features"""
    if options.get('remove_background') and REMBG_AVAILABLE:
        bg_method = options.get('background_removal_method', 'auto')
        image = remove_background(image, method=bg_method)
    
    if image.mode == 'RGBA':
        alpha_range = image.getchannel('A').getextrema()
        has_transparency = alpha_range[0] < 255
        
        bg_color = options.get('background_color', 'transparent')
        if bg_color and bg_color.lower() != 'transparent' and has_transparency:
            image = apply_background_color(image, bg_color)
    
    if options.get('auto_crop'):
        image = auto_crop_image(image, padding=options.get('crop_padding', 10))
    
    if options.get('noise_reduction'):
        noise_strength = options.get('noise_strength', 1)
        image = reduce_noise(image, strength=noise_strength)
    
    if options.get('edge_smooth') and image.mode == 'RGBA':
        smooth_radius = options.get('smooth_radius', 2)
        image = smooth_edges(image, radius=smooth_radius)
    
    if options.get('grayscale'):
        image = image.convert('L').convert('RGBA')
    if options.get('bw'):
        image = image.convert('L')
        image = image.point(lambda x: 0 if x < 128 else 255, '1').convert('RGBA')
    if options.get('invert'):
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        r, g, b, a = image.split()
        rgb_image = Image.merge('RGB', (r, g, b))
        inverted = ImageOps.invert(rgb_image)
        image = Image.merge('RGBA', (*inverted.split(), a))
    if options.get('hue_shift', 0):
        image = shift_hue(image, options.get('hue_shift', 0))
    if options.get('temperature', 0):
        image = adjust_temperature(image, options.get('temperature', 0))
    if options.get('enhance_contrast'):
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.5)
    if options.get('apply_blur'):
        blur_radius = options.get('blur_radius', 2)
        image = image.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    if options.get('add_watermark') and options.get('watermark_text'):
        watermark = Image.new('RGBA', image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(watermark)
        try:
            font = ImageFont.truetype("Arial", 36)
        except IOError:
            font = ImageFont.load_default()
        text_width, text_height = draw.textbbox((0, 0), options.get('watermark_text'), font=font)[2:4]
        position = (image.width - text_width - 20, image.height - text_height - 20)
        opacity = int(255 * float(options.get('watermark_opacity', 0.3)))
        draw.text(position, options.get('watermark_text'), fill=(255, 255, 255, opacity), font=font)
        image = Image.alpha_composite(image.convert('RGBA'), watermark)
    
    if options.get('vignette'):
        strength = options.get('vignette_strength', 0.5)
        image = apply_vignette(image, strength)
    if options.get('saturation', 1.0) != 1.0:
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(options.get('saturation', 1.0))
    if options.get('brightness', 1.0) != 1.0:
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(options.get('brightness', 1.0))
    if options.get('sharpen'):
        radius = options.get('sharpen_radius', 1.0)
        image = image.filter(ImageFilter.UnsharpMask(radius=radius))
    
    if options.get('shadow_effect'):
        shadow_opacity = options.get('shadow_opacity', 0.3)
        shadow_blur = options.get('shadow_blur', 4)
        shadow_offset = options.get('shadow_offset', (5, 5))
        image = add_drop_shadow(image, offset=shadow_offset, blur_radius=shadow_blur, opacity=shadow_opacity)
    
    if options.get('enhance_quality', False):
        image = enhance_image_quality(image)
    
    return image


def save_to_cache(img, cache_key, width, height, upload_folder=None):
    upload_dir = _get_upload_folder(upload_folder)
    cache_dir = os.path.join(upload_dir, 'cache')
    os.makedirs(cache_dir, exist_ok=True)
    
    cache_path = os.path.join(cache_dir, f"{cache_key}_{width}x{height}.png")
    tmp_cache_path = f"{cache_path}.tmp.{uuid.uuid4().hex}"
    try:
        img.save(tmp_cache_path, "PNG")
        os.replace(tmp_cache_path, cache_path)
    except Exception as e:
        logging.error(f"Error saving to cache: {e}")
        if os.path.exists(tmp_cache_path):
            try:
                os.remove(tmp_cache_path)
            except OSError:
                pass


def get_from_cache(cache_key, width, height, upload_folder=None):
    upload_dir = _get_upload_folder(upload_folder)
    cache_dir = os.path.join(upload_dir, 'cache')
    cache_path = os.path.join(cache_dir, f"{cache_key}_{width}x{height}.png")
    
    if os.path.exists(cache_path):
        try:
            file_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(cache_path))
            if file_age.total_seconds() < 86400:
                return Image.open(cache_path)
        except Exception as e:
            logging.error(f"Error retrieving from cache: {e}")
    return None


def generate_cache_key(original_path, preprocessing_options):
    try:
        file_hash = hashlib.md5(open(original_path, 'rb').read()).hexdigest()
        options_hash = hashlib.md5(json.dumps(preprocessing_options, sort_keys=True).encode()).hexdigest()
        return f"{file_hash}_{options_hash[:10]}"
    except Exception as e:
        logging.error(f"Error generating cache key: {e}")
        return f"fallback_{int(time.time())}"


def generate_formats(original_path, filename_without_ext, selected_formats, output_formats, preprocessing_options, variations_mode=False, fill_white_with_prominent=True, quality=95, strip_metadata=False, upload_folder=None):
    upload_dir = _get_upload_folder(upload_folder)
    config = load_config()
    all_available_formats = config['formats']
    formats_to_generate = {k: v for k, v in all_available_formats.items() if k in selected_formats}
    results = {}
    
    try:
        try:
            original = Image.open(original_path)
            if original.mode != 'RGBA':
                original = original.convert('RGBA')
        except Exception as e:
            raise ValueError(f"Could not open or process the uploaded image: {str(e)}")
            
        is_square = original.width == original.height
        
        try:
            prominent_color = get_prominent_color(original)
        except Exception:
            prominent_color = [200, 200, 200]
        
        if variations_mode:
            variations_results = {}
            variation_definitions = generate_variations()
            
            for variation in variation_definitions:
                variation_label = variation['label']
                try:
                    combined_options = preprocessing_options.copy()
                    for opt_key, opt_value in variation['opts'].items():
                        combined_options[opt_key] = opt_value
                    
                    variation_img = preprocess_image(original.copy(), combined_options)
                    variation_data = {}
                    
                    for format_name, format_config in formats_to_generate.items():
                        try:
                            dimensions = (format_config['width'], format_config['height'])
                            img_copy = variation_img.copy()
                            
                            cache_key = generate_cache_key(original_path, preprocessing_options)
                            cached_img = get_from_cache(cache_key, dimensions[0], dimensions[1], upload_folder=upload_dir)
                            
                            if cached_img:
                                new_img = cached_img
                            else:
                                img_copy.thumbnail(dimensions, Image.LANCZOS)
                                
                                if not is_square and dimensions[0] != dimensions[1] and fill_white_with_prominent:
                                    center_color = darken_color(prominent_color, 0.7)
                                    edge_color = prominent_color
                                    bg = create_radial_gradient(dimensions, center_color, edge_color)
                                    paste_pos = ((dimensions[0] - img_copy.width) // 2, (dimensions[1] - img_copy.height) // 2)
                                    bg.paste(img_copy, paste_pos, img_copy)
                                    new_img = bg
                                else:
                                    if img_copy.mode == 'RGBA':
                                        alpha_range = img_copy.getchannel('A').getextrema()
                                        has_transparency = alpha_range[0] < 255
                                        
                                        if has_transparency:
                                            new_img = Image.new("RGBA", dimensions, (0, 0, 0, 0))
                                            paste_pos = ((dimensions[0] - img_copy.width) // 2, (dimensions[1] - img_copy.height) // 2)
                                            new_img.paste(img_copy, paste_pos, img_copy)
                                        else:
                                            bg_color = img_copy.getpixel((0, 0))[:3]
                                            new_img = Image.new("RGBA", dimensions, bg_color + (255,))
                                            paste_pos = ((dimensions[0] - img_copy.width) // 2, (dimensions[1] - img_copy.height) // 2)
                                            new_img.paste(img_copy, paste_pos)
                                    else:
                                        new_img = Image.new("RGBA", dimensions, (0, 0, 0, 0))
                                        paste_pos = ((dimensions[0] - img_copy.width) // 2, (dimensions[1] - img_copy.height) // 2)
                                        new_img.paste(img_copy, paste_pos)
                                        
                                save_to_cache(new_img, cache_key, dimensions[0], dimensions[1], upload_folder=upload_dir)
                            
                            format_results = {}
                            for output_format in output_formats:
                                try:
                                    output_format_lower = output_format.lower()
                                    if output_format_lower == 'ico' and format_name != 'favicon':
                                        continue
                                    
                                    variation_filename = f"{filename_without_ext}_{variation_label}_{format_name}.{output_format_lower}"
                                    output_path = os.path.join(upload_dir, variation_filename)
                                    
                                    save_img, save_opts = optimize_image(new_img, output_format, quality, strip_metadata)
                                    save_img.save(output_path, **save_opts)
                                    
                                    format_results[output_format] = {
                                        'path': output_path,
                                        'url': f"/{upload_dir}/{variation_filename}",
                                    }
                                except Exception as e:
                                    logging.error(f"Error saving {variation_label} {format_name} as {output_format}: {e}")
                            
                            if format_results:
                                variation_data[format_name] = {
                                    'outputs': format_results,
                                    'dimensions': dimensions,
                                    'description': format_config.get('description', '')
                                }
                        except Exception as e:
                            logging.error(f"Error processing format {format_name} for variation {variation_label}: {e}")
                    
                    if variation_data:
                        variations_results[variation_label] = variation_data
                except Exception as e:
                    logging.error(f"Error processing variation {variation_label}: {e}")
            
            if variations_results:
                results['variations'] = variations_results
            
            if 'favicon' in selected_formats and 'ico' in output_formats:
                try:
                    original_opts = next((v['opts'] for v in variation_definitions if v['label'] == 'Original'), {})
                    favicon_img = preprocess_image(original.copy(), original_opts)
                    results['favicon_ico'] = create_favicon(favicon_img, filename_without_ext, upload_folder=upload_dir)
                except Exception as e:
                    logging.error(f"Error creating favicon in variations mode: {e}")
        else:
            try:
                processed_image = preprocess_image(original.copy(), preprocessing_options)
            except Exception as e:
                raise ValueError(f"Could not preprocess the image with selected options: {str(e)}")
                
            if 'favicon' in selected_formats and 'ico' in output_formats:
                try:
                    results['favicon_ico'] = create_favicon(processed_image.copy(), filename_without_ext, upload_folder=upload_dir)
                except Exception as e:
                    logging.error(f"Error creating favicon: {e}")
                    
            for format_name, format_config in formats_to_generate.items():
                try:
                    if format_name == 'favicon' and 'favicon_ico' in results:
                        continue
                        
                    dimensions = (format_config['width'], format_config['height'])
                    img_copy = processed_image.copy()
                    
                    cache_key = generate_cache_key(original_path, preprocessing_options)
                    cached_img = get_from_cache(cache_key, dimensions[0], dimensions[1], upload_folder=upload_dir)
                    
                    if cached_img:
                        new_img = cached_img
                    else:
                        img_copy.thumbnail(dimensions, Image.LANCZOS)
                        
                        if not is_square and dimensions[0] != dimensions[1] and fill_white_with_prominent:
                            center_color = darken_color(prominent_color, 0.7)
                            edge_color = prominent_color
                            bg = create_radial_gradient(dimensions, center_color, edge_color)
                            paste_pos = ((dimensions[0] - img_copy.width) // 2, (dimensions[1] - img_copy.height) // 2)
                            bg.paste(img_copy, paste_pos, img_copy)
                            new_img = bg
                        else:
                            if img_copy.mode == 'RGBA':
                                alpha_range = img_copy.getchannel('A').getextrema()
                                has_transparency = alpha_range[0] < 255
                                
                                if has_transparency:
                                    new_img = Image.new("RGBA", dimensions, (0, 0, 0, 0))
                                    paste_pos = ((dimensions[0] - img_copy.width) // 2, (dimensions[1] - img_copy.height) // 2)
                                    new_img.paste(img_copy, paste_pos, img_copy)
                                else:
                                    bg_color = img_copy.getpixel((0, 0))[:3]
                                    new_img = Image.new("RGBA", dimensions, bg_color + (255,))
                                    paste_pos = ((dimensions[0] - img_copy.width) // 2, (dimensions[1] - img_copy.height) // 2)
                                    new_img.paste(img_copy, paste_pos)
                            else:
                                new_img = Image.new("RGBA", dimensions, (0, 0, 0, 0))
                                paste_pos = ((dimensions[0] - img_copy.width) // 2, (dimensions[1] - img_copy.height) // 2)
                                paste_pos = ((dimensions[0] - img_copy.width) // 2, (dimensions[1] - img_copy.height) // 2)
                                new_img.paste(img_copy, paste_pos)
                                
                        save_to_cache(new_img, cache_key, dimensions[0], dimensions[1], upload_folder=upload_dir)
                            
                    format_results = {}
                    for output_format in output_formats:
                        try:
                            output_format_lower = output_format.lower()
                            if output_format_lower == 'ico' and format_name != 'favicon':
                                continue
                                
                            output_filename = f"{filename_without_ext}_{format_name}.{output_format_lower}"
                            output_path = os.path.join(upload_dir, output_filename)
                            
                            save_img, save_opts = optimize_image(new_img, output_format, quality, strip_metadata)
                            save_img.save(output_path, **save_opts)
                            
                            format_results[output_format] = {
                                'path': output_path,
                                'url': f"/{upload_dir}/{output_filename}",
                            }
                        except Exception as e:
                            logging.error(f"Error saving {format_name} as {output_format}: {e}")
                            
                    if format_results:
                        results[format_name] = {
                            'outputs': format_results,
                            'dimensions': dimensions,
                            'description': format_config.get('description', '')
                        }
                except Exception as e:
                    logging.error(f"Error processing format {format_name}: {e}")
                
        return results
    except Exception as e:
        logging.error(f"Unhandled error in generate_formats: {e}")
        raise


def create_zip_file(results, filename_without_ext, upload_folder=None):
    """Create a zip file containing all generated assets"""
    upload_dir = _get_upload_folder(upload_folder)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    zip_filename = f"{filename_without_ext}_brandkit_{timestamp}.zip"
    zip_path = os.path.join(upload_dir, zip_filename)
    
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            if 'original' in results:
                original_path = results['original']['path']
                zipf.write(original_path, os.path.basename(original_path))
            
            if 'variations' in results:
                for variation_label, variation_data in results['variations'].items():
                    for format_name, format_data in variation_data.items():
                        for output_format, output_data in format_data['outputs'].items():
                            file_path = output_data['path']
                            zipf.write(file_path, os.path.basename(file_path))
            
            for key, data in results.items():
                if key not in ['original', 'variations', 'zip', 'analysis', 'favicon_ico']:
                    for output_format, output_data in data['outputs'].items():
                        file_path = output_data['path']
                        zipf.write(file_path, os.path.basename(file_path))
            
            if 'favicon_ico' in results:
                file_path = results['favicon_ico']['path']
                zipf.write(file_path, os.path.basename(file_path))
        
        return {
            'path': zip_path,
            'url': f"/{upload_dir}/{zip_filename}",
            'filename': zip_filename
        }
    except Exception as e:
        logging.error(f"Error creating zip file: {e}")
        return None
