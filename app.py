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
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Load configuration
def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def preprocess_image(image, options):
    """Apply preprocessing options to the image"""
    # Grayscale
    if options.get('grayscale'):
        image = image.convert('L').convert('RGBA')
    # High-contrast B&W
    if options.get('bw'):
        image = image.convert('L')
        image = image.point(lambda x: 0 if x < 128 else 255, '1').convert('RGBA')
    # Invert
    if options.get('invert'):
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        r, g, b, a = image.split()
        rgb_image = Image.merge('RGB', (r, g, b))
        inverted = ImageOps.invert(rgb_image)
        image = Image.merge('RGBA', (*inverted.split(), a))
    # Hue shift
    if options.get('hue_shift', 0):
        image = shift_hue(image, options.get('hue_shift', 0))
    # Temperature
    if options.get('temperature', 0):
        image = adjust_temperature(image, options.get('temperature', 0))
    # Enhance contrast
    if options.get('enhance_contrast'):
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.5)
    # Blur
    if options.get('apply_blur'):
        blur_radius = options.get('blur_radius', 2)
        image = image.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    # Watermark
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
    r, g, b, a = arr[...,0], arr[...,1], arr[...,2], arr[...,3]
    hsv = np.array(Image.fromarray(np.stack([r,g,b], axis=-1)).convert('HSV'))
    hsv[...,0] = (hsv[...,0].astype(int) + int(deg/360*255)) % 255
    rgb = Image.fromarray(hsv, 'HSV').convert('RGBA')
    arr2 = np.array(rgb)
    arr2[...,3] = a
    return Image.fromarray(arr2, 'RGBA')

def adjust_temperature(img, temp):
    # temp: -100 (cool) to +100 (warm)
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    arr = np.array(img).astype(np.int16)
    if temp > 0:
        arr[...,0] = np.clip(arr[...,0] + temp, 0, 255) # more red
        arr[...,2] = np.clip(arr[...,2] - temp//2, 0, 255) # less blue
    elif temp < 0:
        arr[...,2] = np.clip(arr[...,2] + abs(temp), 0, 255) # more blue
        arr[...,0] = np.clip(arr[...,0] + temp//2, 0, 255) # less red
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    return Image.fromarray(arr, 'RGBA')

def generate_variations():
    return [
        {'label': 'Original', 'opts': {}},
        {'label': 'Grayscale', 'opts': {'grayscale': True}},
        {'label': 'B&W', 'opts': {'bw': True}},
        {'label': 'Inverted', 'opts': {'invert': True}},
        {'label': 'Hue +60°', 'opts': {'hue_shift': 60}},
        {'label': 'Hue -60°', 'opts': {'hue_shift': -60}},
        {'label': 'Warm', 'opts': {'temperature': 40}},
        {'label': 'Cool', 'opts': {'temperature': -40}},
        {'label': 'Grayscale+Contrast', 'opts': {'grayscale': True, 'enhance_contrast': True}},
        dimensions = (format_config['width'], format_config['height'])
        
        # Create a copy to avoid modifying the original during resizing
        img_copy = processed_image.copy()
        
        # Resize the image while preserving aspect ratio
        img_copy.thumbnail(dimensions, Image.LANCZOS)
        
        # Create a new image with the exact dimensions and paste the resized image centered
        new_img = Image.new("RGBA", dimensions, (255, 255, 255, 0))
        
        # Calculate position to paste (centered)
        paste_pos = ((dimensions[0] - img_copy.width) // 2,
                     (dimensions[1] - img_copy.height) // 2)
        
        # Paste the resized image
        if img_copy.mode == 'RGBA':
            new_img.paste(img_copy, paste_pos, img_copy)
        else:
            new_img.paste(img_copy, paste_pos)
        
        format_results = {}
        
        # Save in each requested output format
        for output_format in output_formats:
            # Skip ICO format for non-favicon images (handled separately)
            if output_format.lower() == 'ico' and format_name != 'favicon':
                continue
                
            # Save the new image
            output_filename = f"{filename_without_ext}_{format_name}.{output_format}"
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
            
            # Convert mode for saving in different formats
            if output_format.lower() == 'jpg' or output_format.lower() == 'jpeg':
                save_img = new_img.convert('RGB')
                save_img.save(output_path, quality=95)
            elif output_format.lower() == 'webp':
                save_img = new_img.convert('RGBA')
                save_img.save(output_path, quality=95)
            elif output_format.lower() == 'ico' and format_name == 'favicon':
                # For favicon format, we use a specialized method
                continue  # Skip as it's handled separately
            else:  # PNG
                new_img.save(output_path)
            
            format_results[output_format] = {
                'path': output_path,
                'url': f"/{app.config['UPLOAD_FOLDER']}/{output_filename}",
            }
        
        results[format_name] = {
            'outputs': format_results,
            'dimensions': dimensions,
            'description': format_config.get('description', '')
        }
    
    return results

def create_zip_file(results, filename_prefix):
    """Create a ZIP file containing all generated images"""
    # Create a temporary file
    temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
    temp_zip.close()
    
    # Create a ZIP file
    with zipfile.ZipFile(temp_zip.name, 'w') as zipf:
        # Add original image
        if 'original' in results:
            original_path = results['original']['path']
            zipf.write(original_path, os.path.basename(original_path))
        
        # Add special favicon.ico if present
        if 'favicon_ico' in results:
            favicon_path = results['favicon_ico']['path']
            zipf.write(favicon_path, 'favicon.ico')
        
        # Add all other generated images
        for format_name, format_data in results.items():
            if format_name in ['original', 'favicon_ico']:
                continue
                
            if 'outputs' in format_data:
                for output_format, output_data in format_data['outputs'].items():
                    file_path = output_data['path']
                    # Use a clean filename in the ZIP
                    clean_name = f"{format_name}.{output_format}"
                    zipf.write(file_path, clean_name)
    
    # Save the ZIP file to the uploads folder
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    zip_filename = f"{filename_prefix}_brandkit_{timestamp}.zip"
    zip_path = os.path.join(app.config['UPLOAD_FOLDER'], zip_filename)
    
    # Copy the temporary ZIP to the uploads folder
    with open(temp_zip.name, 'rb') as f_in:
        with open(zip_path, 'wb') as f_out:
            f_out.write(f_in.read())
    
    # Clean up the temporary file
    os.unlink(temp_zip.name)
    
    return {
        'path': zip_path,
        'url': f"/{app.config['UPLOAD_FOLDER']}/{zip_filename}"
    }

@app.route('/')
def index():
    config = load_config()
    return render_template('index.html', config=config)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        # Parse form data
        selected_formats = request.form.getlist('formats')
        output_formats = request.form.getlist('output_formats')
        
        # Default to all formats if none selected
        if not selected_formats:
            config = load_config()
            selected_formats = list(config['formats'].keys())
        
        # Default to PNG if no output format is selected
        if not output_formats:
            output_formats = ['png']
        
        # Get preprocessing options
        preprocessing_options = {
            'grayscale': request.form.get('grayscale') == 'true',
            'enhance_contrast': request.form.get('enhance_contrast') == 'true',
            'apply_blur': request.form.get('apply_blur') == 'true',
            'blur_radius': float(request.form.get('blur_radius', 2)),
            'add_watermark': request.form.get('add_watermark') == 'true',
            'watermark_text': request.form.get('watermark_text', '© BrandKit'),
            'watermark_opacity': float(request.form.get('watermark_opacity', 0.3))
        }
        
        # Generate a unique filename
        original_ext = file.filename.rsplit('.', 1)[1].lower()
        filename_without_ext = uuid.uuid4().hex
        unique_filename = f"{filename_without_ext}.{original_ext}"
        
        # Save the uploaded file
        original_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(original_path)
        
        # Generate different formats
        results = generate_formats(
            original_path, 
            filename_without_ext, 
            selected_formats, 
            output_formats, 
            preprocessing_options
        )
        
        # Add the original file info to results
        results['original'] = {
            'path': original_path,
            'url': f"/{app.config['UPLOAD_FOLDER']}/{unique_filename}"
        }
        
        # Create a ZIP file with all generated images
        zip_info = create_zip_file(results, filename_without_ext)
        results['zip'] = zip_info
        
        return jsonify({
            'success': True,
            'message': 'File uploaded successfully',
            'results': results
        })
    
    return jsonify({'error': 'File type not allowed'}), 400

@app.route('/download-zip/<filename>')
def download_zip(filename):
    """Download a ZIP file"""
    zip_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(zip_path):
        return send_file(zip_path, as_attachment=True)
    return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)