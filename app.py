import os
import json
import zipfile
import io
import uuid
import tempfile
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
from werkzeug.utils import secure_filename
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont, ImageOps
import numpy as np

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# --- Configuration Loading with Environment Variable Overrides ---
DEFAULT_MAX_UPLOAD_MB = 16
try:
    max_upload_mb = int(os.environ.get('BRANDKIT_MAX_UPLOAD_MB', DEFAULT_MAX_UPLOAD_MB))
except ValueError:
    max_upload_mb = DEFAULT_MAX_UPLOAD_MB
app.config['MAX_CONTENT_LENGTH'] = max_upload_mb * 1024 * 1024

# Default config structure if file is missing or invalid
DEFAULT_CONFIG = {
    "formats": {
        "website": {"width": 1200, "height": 630, "description": "Open Graph, Twitter Cards"},
        "webapp": {"width": 512, "height": 512, "description": "Web App Manifest Icon"},
        "mobile": {"width": 1080, "height": 1920, "description": "Mobile Screens"},
        "social": {"width": 1080, "height": 1080, "description": "Social Media Posts"},
        "favicon": {"width": 48, "height": 48, "description": "Browser Favicon (generates .ico)"}
    },
    "format_categories": {},
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
        "watermark_opacity": 0.3
    }
}

# Load configuration from file and apply environment overrides
def load_config():
    config = DEFAULT_CONFIG.copy() # Start with defaults
    try:
        with open('config.json', 'r') as f:
            file_config = json.load(f)
            # Merge file config into defaults (simple merge, not deep)
            config.update(file_config)
    except FileNotFoundError:
        print("Warning: config.json not found. Using default configuration.")
    except json.JSONDecodeError:
        print("Error: config.json is not valid JSON. Using default configuration.")

    # Example: Override a specific preprocessing default via env var
    # config['preprocessing_options']['watermark_text'] = os.environ.get(
    #     'BRANDKIT_WATERMARK_TEXT', config['preprocessing_options']['watermark_text']
    # )
    # Add more overrides here as needed

    return config

# --- End Configuration Loading ---

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def preprocess_image(image, options):
    """Apply preprocessing options to the image"""
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
    return image

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

def darken_color(color, factor=0.7):
    """Return a darker version of the color (factor < 1.0)."""
    return tuple(max(0, int(c * factor)) for c in color)

def create_radial_gradient(size, center_color, edge_color):
    """Create a radial gradient image from center_color to edge_color."""
    width, height = size
    gradient = Image.new('RGBA', (width, height), edge_color + (255,))
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

def create_favicon(image, filename_without_ext):
    favicon_sizes = [16, 32, 48]
    output_filename = f"{filename_without_ext}_favicon.ico"
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
    favicon_images = []
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
        'url': f"/{app.config['UPLOAD_FOLDER']}/{output_filename}"
    }

def generate_formats(original_path, filename_without_ext, selected_formats, output_formats, preprocessing_options, variations_mode=False):
    config = load_config()
    all_available_formats = config['formats']
    formats_to_generate = {k: v for k, v in all_available_formats.items() if k in selected_formats}
    results = {}
    try:
        original = Image.open(original_path)
    except Exception as e:
        print(f"Error opening image: {e}")
        raise ValueError("Could not open or process the uploaded image.")
    # --- Intelligence: get prominent color and check if original is square ---
    prominent_color = get_prominent_color(original)
    is_square = original.width == original.height
    if variations_mode:
        results['variations'] = {}
        variations_list = generate_variations()
        for var in variations_list:
            label = var['label']
            opts = {**preprocessing_options, **var['opts']}
            try:
                processed_image = preprocess_image(original.copy(), opts)
            except Exception as e:
                print(f"Error preprocessing variation '{label}': {e}")
                continue
            results['variations'][label] = {}
            for format_name, format_config in formats_to_generate.items():
                dimensions = (format_config['width'], format_config['height'])
                img_copy = processed_image.copy()
                img_copy.thumbnail(dimensions, Image.LANCZOS)
                # --- Intelligence: fill non-square background for square uploads ---
                if is_square and dimensions[0] != dimensions[1]:
                    # Create radial gradient background
                    center_color = darken_color(prominent_color, 0.7)
                    edge_color = prominent_color
                    bg = create_radial_gradient(dimensions, center_color, edge_color)
                    paste_pos = ((dimensions[0] - img_copy.width) // 2, (dimensions[1] - img_copy.height) // 2)
                    bg.paste(img_copy, paste_pos, img_copy)
                    new_img = bg
                else:
                    new_img = Image.new("RGBA", dimensions, (0, 0, 0, 0))
                    paste_pos = ((dimensions[0] - img_copy.width) // 2, (dimensions[1] - img_copy.height) // 2)
                    if img_copy.mode == 'RGBA':
                        new_img.paste(img_copy, paste_pos, img_copy)
                    else:
                        new_img.paste(img_copy, paste_pos)
                format_results = {}
                for output_format in output_formats:
                    output_format_lower = output_format.lower()
                    if output_format_lower == 'ico' and format_name != 'favicon':
                        continue
                    output_filename = f"{filename_without_ext}_{label}_{format_name}.{output_format_lower}"
                    output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
                    try:
                        if output_format_lower in ['jpg', 'jpeg']:
                            save_img = new_img.convert('RGB')
                            save_img.save(output_path, quality=95)
                        elif output_format_lower == 'webp':
                            save_img = new_img
                            save_img.save(output_path, quality=95, lossless=False)
                        else:
                            new_img.save(output_path)
                        format_results[output_format] = {
                            'path': output_path,
                            'url': f"/{app.config['UPLOAD_FOLDER']}/{output_filename}",
                        }
                    except Exception as e:
                        print(f"Error saving variation {label}/{format_name} as {output_format}: {e}")
                if format_results:
                    results['variations'][label][format_name] = {
                        'outputs': format_results,
                        'dimensions': dimensions,
                        'description': format_config.get('description', '')
                    }
        if 'favicon' in selected_formats and 'ico' in output_formats:
            try:
                base_processed_image = preprocess_image(original.copy(), preprocessing_options)
                results['favicon_ico'] = create_favicon(base_processed_image, filename_without_ext)
            except Exception as e:
                print(f"Error creating main favicon: {e}")
        return results
    try:
        processed_image = preprocess_image(original.copy(), preprocessing_options)
    except Exception as e:
        print(f"Error during initial preprocessing: {e}")
        raise ValueError("Could not preprocess the image with selected options.")
    if 'favicon' in selected_formats and 'ico' in output_formats:
        try:
            results['favicon_ico'] = create_favicon(processed_image.copy(), filename_without_ext)
        except Exception as e:
            print(f"Error creating favicon: {e}")
    for format_name, format_config in formats_to_generate.items():
        if format_name == 'favicon' and 'favicon_ico' in results:
            continue
        dimensions = (format_config['width'], format_config['height'])
        img_copy = processed_image.copy()
        img_copy.thumbnail(dimensions, Image.LANCZOS)
        # --- Intelligence: fill non-square background for square uploads ---
        if is_square and dimensions[0] != dimensions[1]:
            # Create radial gradient background
            center_color = darken_color(prominent_color, 0.7)
            edge_color = prominent_color
            bg = create_radial_gradient(dimensions, center_color, edge_color)
            paste_pos = ((dimensions[0] - img_copy.width) // 2, (dimensions[1] - img_copy.height) // 2)
            bg.paste(img_copy, paste_pos, img_copy)
            new_img = bg
        else:
            new_img = Image.new("RGBA", dimensions, (0, 0, 0, 0))
            paste_pos = ((dimensions[0] - img_copy.width) // 2, (dimensions[1] - img_copy.height) // 2)
            if img_copy.mode == 'RGBA':
                new_img.paste(img_copy, paste_pos, img_copy)
            else:
                new_img.paste(img_copy, paste_pos)
        format_results = {}
        for output_format in output_formats:
            output_format_lower = output_format.lower()
            if output_format_lower == 'ico' and format_name != 'favicon':
                continue
            output_filename = f"{filename_without_ext}_{format_name}.{output_format_lower}"
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
            try:
                if output_format_lower in ['jpg', 'jpeg']:
                    save_img = new_img.convert('RGB')
                    save_img.save(output_path, quality=95)
                elif output_format_lower == 'webp':
                    save_img = new_img
                    save_img.save(output_path, quality=95, lossless=False)
                else:
                    new_img.save(output_path)
                format_results[output_format] = {
                    'path': output_path,
                    'url': f"/{app.config['UPLOAD_FOLDER']}/{output_filename}",
                }
            except Exception as e:
                print(f"Error saving {format_name} as {output_format}: {e}")
        if format_results:
            results[format_name] = {
                'outputs': format_results,
                'dimensions': dimensions,
                'description': format_config.get('description', '')
            }
    return results

def create_zip_file(results, filename_prefix):
    temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
    temp_zip.close()
    added_files = set()
    try:
        with zipfile.ZipFile(temp_zip.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            if 'original' in results and 'path' in results['original']:
                original_path = results['original']['path']
                if os.path.exists(original_path):
                    zip_entry_name = f"original{os.path.splitext(original_path)[1]}"
                    zipf.write(original_path, zip_entry_name)
                    added_files.add(original_path)
            if 'favicon_ico' in results and 'path' in results['favicon_ico']:
                favicon_path = results['favicon_ico']['path']
                if os.path.exists(favicon_path):
                    zipf.write(favicon_path, 'favicon.ico')
                    added_files.add(favicon_path)
            if 'variations' in results:
                for variation_label, variation_data in results['variations'].items():
                    variation_prefix = variation_label.replace(' ', '_').lower()
                    for format_name, format_data in variation_data.items():
                        if 'outputs' in format_data:
                            for output_format, output_data in format_data['outputs'].items():
                                file_path = output_data['path']
                                if os.path.exists(file_path) and file_path not in added_files:
                                    zip_entry_name = f"{variation_prefix}/{format_name}.{output_format.lower()}"
                                    zipf.write(file_path, zip_entry_name)
                                    added_files.add(file_path)
            else:
                for format_name, format_data in results.items():
                    if format_name in ['original', 'favicon_ico', 'zip', 'variations']:
                        continue
                    if 'outputs' in format_data:
                        for output_format, output_data in format_data['outputs'].items():
                            file_path = output_data['path']
                            if os.path.exists(file_path) and file_path not in added_files:
                                clean_name = f"{format_name}.{output_format.lower()}"
                                zipf.write(file_path, clean_name)
                                added_files.add(file_path)
    except Exception as e:
        print(f"Error creating zip file: {e}")
        os.unlink(temp_zip.name)
        return None
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    zip_filename = f"{filename_prefix}_brandkit_{timestamp}.zip"
    zip_path = os.path.join(app.config['UPLOAD_FOLDER'], zip_filename)
    try:
        os.rename(temp_zip.name, zip_path)
    except Exception as e:
        print(f"Error moving temp zip file: {e}")
        try:
            with open(temp_zip.name, 'rb') as f_in, open(zip_path, 'wb') as f_out:
                f_out.write(f_in.read())
            os.unlink(temp_zip.name)
        except Exception as copy_e:
            print(f"Error copying temp zip file: {copy_e}")
            os.unlink(temp_zip.name)
            return None
    return {
        'path': zip_path,
        'url': f"/{app.config['UPLOAD_FOLDER']}/{zip_filename}",
        'filename': zip_filename
    }

def get_prominent_color(image, exclude_white=True):
    """Extract the most prominent color from the image, optionally ignoring white/near-white pixels."""
    img = image.convert('RGBA').resize((64, 64))  # Downsize for speed
    arr = np.array(img)
    pixels = arr.reshape(-1, 4)
    # Remove fully transparent pixels
    pixels = pixels[pixels[:, 3] > 0]
    if exclude_white:
        # Remove near-white pixels
        pixels = pixels[(pixels[:, 0:3] < 245).any(axis=1)]
    if len(pixels) == 0:
        return (200, 200, 200)  # fallback gray
    # Find most common color
    colors, counts = np.unique(pixels[:, :3], axis=0, return_counts=True)
    prominent = colors[counts.argmax()]
    return tuple(int(x) for x in prominent)

def has_significant_white_area(image, threshold=0.15):
    """Detect if the image has a significant white or transparent area (default: >15%)."""
    img = image.convert('RGBA')
    arr = np.array(img)
    total = arr.shape[0] * arr.shape[1]
    # White: all RGB > 245, alpha > 200
    white = ((arr[..., :3] > 245).all(axis=-1)) & (arr[..., 3] > 200)
    # Transparent: alpha < 32
    transparent = arr[..., 3] < 32
    white_or_transparent = white | transparent
    ratio = np.sum(white_or_transparent) / total
    return ratio > threshold, ratio

@app.route('/')
def index():
    config = load_config()
    return render_template('index.html', config=config, max_upload_mb=app.config['MAX_CONTENT_LENGTH'] // (1024 * 1024))

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        try:
            selected_formats = request.form.getlist('selected_formats')
            output_formats = request.form.getlist('output_formats')
            variations_mode = request.form.get('variations_mode') == 'true'
            config = load_config()
            if not selected_formats:
                selected_formats = list(config['formats'].keys())
            if not output_formats:
                output_formats = ['png']
            if 'ico' in output_formats and 'favicon' not in selected_formats:
                output_formats.remove('ico')
                if not output_formats:
                    output_formats.append('png')
            preprocessing_options = {
                'grayscale': request.form.get('grayscale') == 'true',
                'bw': request.form.get('bw') == 'true',
                'invert': request.form.get('invert') == 'true',
                'hue_shift': int(request.form.get('hue_shift', 0)),
                'temperature': int(request.form.get('temperature', 0)),
                'enhance_contrast': request.form.get('enhance_contrast') == 'true',
                'apply_blur': request.form.get('apply_blur') == 'true',
                'blur_radius': float(request.form.get('blur_radius', config.get('preprocessing_options', {}).get('blur_radius', 2.0))),
                'add_watermark': request.form.get('add_watermark') == 'true',
                'watermark_text': request.form.get('watermark_text', config.get('preprocessing_options', {}).get('watermark_text', '© BrandKit')),
                'watermark_opacity': float(request.form.get('watermark_opacity', config.get('preprocessing_options', {}).get('watermark_opacity', 0.3)))
            }
            original_ext = file.filename.rsplit('.', 1)[1].lower()
            filename_without_ext = uuid.uuid4().hex
            unique_filename = f"{filename_without_ext}.{original_ext}"
            original_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(original_path)
            # --- Intelligence: analyze image ---
            try:
                img_for_analysis = Image.open(original_path)
                prominent_color = get_prominent_color(img_for_analysis)
                has_white_area, white_area_ratio = has_significant_white_area(img_for_analysis)
            except Exception as e:
                print(f"Image analysis failed: {e}")
                prominent_color = (200, 200, 200)
                has_white_area = False
                white_area_ratio = 0.0
            results = generate_formats(
                original_path,
                filename_without_ext,
                selected_formats,
                output_formats,
                preprocessing_options,
                variations_mode=variations_mode
            )
            results['original'] = {
                'path': original_path,
                'url': f"/{app.config['UPLOAD_FOLDER']}/{unique_filename}"
            }
            zip_info = create_zip_file(results, filename_without_ext)
            if zip_info:
                results['zip'] = zip_info
            # --- Add intelligence info to response ---
            results['analysis'] = {
                'prominent_color': tuple(int(x) for x in prominent_color),
                'has_white_area': bool(has_white_area),
                'white_area_ratio': float(white_area_ratio)
            }
            return jsonify({
                'success': True,
                'message': 'File processed successfully',
                'results': results
            })
        except ValueError as ve:
            print(f"Value Error during processing: {ve}")
            return jsonify({'error': str(ve)}), 400
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': 'An unexpected error occurred during processing.'}), 500
    return jsonify({'error': 'File type not allowed'}), 400

@app.route('/download-zip/<filename>')
def download_zip(filename):
    zip_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(zip_path):
        return send_file(zip_path, as_attachment=True)
    return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    is_debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', debug=is_debug)