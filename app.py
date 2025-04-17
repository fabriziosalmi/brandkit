import os
import json
import zipfile
import io
import uuid
import tempfile
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
from werkzeug.utils import secure_filename
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont

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
    if options.get('grayscale'):
        image = image.convert('L').convert('RGBA')
    
    if options.get('enhance_contrast'):
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.5)  # Increase contrast by 50%
    
    if options.get('apply_blur'):
        blur_radius = options.get('blur_radius', 2)
        image = image.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    
    if options.get('add_watermark') and options.get('watermark_text'):
        # Create a transparent layer for the watermark
        watermark = Image.new('RGBA', image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(watermark)
        
        # Try to use a system font or fall back to default
        try:
            font = ImageFont.truetype("Arial", 36)
        except IOError:
            font = ImageFont.load_default()
        
        # Get the size of the text
        text_width, text_height = draw.textbbox((0, 0), options.get('watermark_text'), font=font)[2:4]
        
        # Calculate position (bottom right corner with some padding)
        position = (image.width - text_width - 20, image.height - text_height - 20)
        
        # Draw the text with transparency
        opacity = int(255 * float(options.get('watermark_opacity', 0.3)))
        draw.text(position, options.get('watermark_text'), fill=(255, 255, 255, opacity), font=font)
        
        # Composite the watermark with the image
        image = Image.alpha_composite(image.convert('RGBA'), watermark)
    
    return image

def create_favicon(image, filename_without_ext):
    """Generate a favicon.ico file from the processed image"""
    favicon_sizes = [16, 32, 48]
    output_filename = f"{filename_without_ext}_favicon.ico"
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
    
    # Create images for different favicon sizes
    favicon_images = []
    for size in favicon_sizes:
        img_copy = image.copy()
        img_copy.thumbnail((size, size), Image.LANCZOS)
        favicon_images.append(img_copy)
    
    # Save as ICO
    favicon_images[0].save(
        output_path, 
        format='ICO', 
        sizes=[(img.width, img.height) for img in favicon_images]
    )
    
    return {
        'path': output_path,
        'url': f"/{app.config['UPLOAD_FOLDER']}/{output_filename}"
    }

def generate_formats(original_path, filename_without_ext, selected_formats, output_formats, preprocessing_options):
    """Generate different image formats for various platforms"""
    config = load_config()
    formats = config['formats']
    
    # Filter formats based on user selection
    if selected_formats and len(selected_formats) > 0:
        formats = {k: v for k, v in formats.items() if k in selected_formats}
    
    results = {}
    original = Image.open(original_path)
    
    # Preprocess the image
    processed_image = preprocess_image(original.copy(), preprocessing_options)
    
    # Special case for favicon.ico - always create if requested
    if 'favicon' in selected_formats and 'ico' in output_formats:
        results['favicon_ico'] = create_favicon(processed_image, filename_without_ext)
    
    for format_name, format_config in formats.items():
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