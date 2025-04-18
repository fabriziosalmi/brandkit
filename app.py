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

def load_config():
    """Load configuration with proper deep merging of dictionaries"""
    config = DEFAULT_CONFIG.copy()
    try:
        with open('config.json', 'r') as f:
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

# --- End Configuration Loading ---

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def preprocess_image(image, options):
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
    return tuple(max(0, int(c * factor)) for c in color)

def create_radial_gradient(size, center_color, edge_color):
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
    img = image.convert('RGBA').resize((64, 64))
    arr = np.array(img)
    pixels = arr.reshape(-1, 4)
    pixels = pixels[pixels[:, 3] > 0]  # Filter out fully transparent pixels
    if exclude_white:
        pixels = pixels[(pixels[:, 0:3] < 245).any(axis=1)]  # Filter out white pixels
    if len(pixels) == 0:
        return (200, 200, 200)  # Default color if no valid pixels
    colors, counts = np.unique(pixels[:, :3], axis=0, return_counts=True)
    prominent = colors[counts.argmax()]
    return tuple(int(x) for x in prominent)

def has_significant_white_area(image, threshold=0.15):
    img = image.convert('RGBA')
    arr = np.array(img)
    total = arr.shape[0] * arr.shape[1]
    white = ((arr[..., :3] > 245).all(axis=-1)) & (arr[..., 3] > 200)
    transparent = arr[..., 3] < 32
    white_or_transparent = white | transparent
    ratio = np.sum(white_or_transparent) / total
    return ratio > threshold, ratio

@app.route('/')
def index():
    config = load_config()
    return render_template('index.html', config=config, max_upload_mb=app.config['MAX_CONTENT_LENGTH'] // (1024 * 1024))

@app.route('/analyze', methods=['POST'])
def analyze_image_endpoint():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
                file.save(temp_file.name)
                temp_file_path = temp_file.name
            try:
                img_for_analysis = Image.open(temp_file_path)
                prominent_color = get_prominent_color(img_for_analysis)
                has_white_area, white_area_ratio = has_significant_white_area(img_for_analysis)
                analysis_results = {
                    'prominent_color': tuple(int(x) for x in prominent_color),
                    'has_white_area': bool(has_white_area),
                    'white_area_ratio': float(white_area_ratio)
                }
                return jsonify({'success': True, 'analysis': analysis_results})
            except Exception as e:
                print(f"Image analysis failed: {e}")
                return jsonify({'success': False, 'error': 'Failed to analyze image.'}), 500
            finally:
                if temp_file_path and os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
        except Exception as e:
            print(f"Error handling analysis request: {e}")
            return jsonify({'success': False, 'error': 'Server error during analysis.'}), 500
    else:
        return jsonify({'success': False, 'error': 'File type not allowed'}), 400

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
            fill_white_with_prominent = request.form.get('fill_white_with_prominent') == 'true'
            
            # Load configuration
            config = load_config()
            
            # Default to all formats if none selected
            if not selected_formats:
                selected_formats = list(config['formats'].keys())
            
            # Default to PNG if no output format selected
            if not output_formats:
                output_formats = ['png']
                
            # Remove ICO if favicon not selected
            if 'ico' in output_formats and 'favicon' not in selected_formats:
                output_formats.remove('ico')
                if not output_formats:
                    output_formats.append('png')
                    
            # Get preprocessing options from form
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
            
            # Generate unique filename
            original_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'png'
            filename_without_ext = uuid.uuid4().hex
            unique_filename = f"{filename_without_ext}.{original_ext}"
            original_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(original_path)
            
            # Analyze the image for smart background fill feature
            try:
                img_for_analysis = Image.open(original_path)
                prominent_color = get_prominent_color(img_for_analysis)
                has_white_area, white_area_ratio = has_significant_white_area(img_for_analysis)
                analysis_results = {
                    'prominent_color': prominent_color,
                    'has_white_area': has_white_area,
                    'white_area_ratio': white_area_ratio
                }
            except Exception as e:
                print(f"Image analysis failed: {e}")
                analysis_results = None
                
            # Generate formatted images
            results = generate_formats(
                original_path,
                filename_without_ext,
                selected_formats,
                output_formats,
                preprocessing_options,
                variations_mode=variations_mode,
                fill_white_with_prominent=fill_white_with_prominent
            )
            
            # Add original to results
            results['original'] = {
                'path': original_path,
                'url': f"/{app.config['UPLOAD_FOLDER']}/{unique_filename}"
            }
            
            # Add analysis results
            if analysis_results:
                results['analysis'] = analysis_results
                
            # Create and add zip file
            zip_info = create_zip_file(results, filename_without_ext)
            if zip_info:
                results['zip'] = zip_info
                
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
    app.run(host='0.0.0.0', port='8000', debug=is_debug)