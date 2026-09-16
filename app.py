import os
import uuid
import tempfile
import logging
import traceback
from datetime import datetime
from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from werkzeug.utils import secure_filename
from werkzeug.exceptions import HTTPException
from PIL import Image
import numpy as np
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from flask_talisman import Talisman

# Decoupled domain modules
from config_utils import (
    DEFAULT_CONFIG,
    DEFAULT_MAX_UPLOAD_MB,
    DEFAULT_ALLOWED_EXTENSIONS,
    load_config,
    allowed_file,
    ensure_serializable,
)
from image_processing import (
    PSUTIL_AVAILABLE,
    REMBG_AVAILABLE,
    CV2_AVAILABLE,
    shift_hue,
    adjust_temperature,
    apply_vignette,
    darken_color,
    create_radial_gradient,
    generate_variations,
    create_favicon,
    auto_crop_image,
    add_drop_shadow,
    enhance_image_quality,
    reduce_noise,
    smooth_edges,
    remove_background,
    apply_background_color,
    get_prominent_color,
    has_significant_white_area,
    optimize_image,
    preprocess_image,
    save_to_cache,
    get_from_cache,
    generate_cache_key,
    generate_formats,
    create_zip_file,
)
from cleanup import (
    cleanup_memory,
    cleanup_old_files,
    _cleanup_settings,
    start_cleanup_thread,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Shared security extensions
csrf = CSRFProtect()
limiter = Limiter(
    get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)
cache = Cache()


def create_app(test_config=None, start_cleanup=True):
    """Application factory for BrandKit"""
    app = Flask(__name__)

    # Secret key initialization
    secret_key = os.environ.get('BRANDKIT_SECRET_KEY') or os.environ.get('FLASK_SECRET_KEY')
    if not secret_key:
        secret_key = os.urandom(24)
        logging.warning(
            "No BRANDKIT_SECRET_KEY set - generating an ephemeral one. Sessions and "
            "CSRF tokens will be invalidated on restart and will not work across "
            "multiple worker processes. Set BRANDKIT_SECRET_KEY in production."
        )
    app.config['SECRET_KEY'] = secret_key
    app.config['UPLOAD_FOLDER'] = 'static/uploads'
    app.config['ALLOWED_EXTENSIONS'] = set(DEFAULT_ALLOWED_EXTENSIONS)

    # Max upload limit
    try:
        max_upload_mb = int(os.environ.get('BRANDKIT_MAX_UPLOAD_MB', DEFAULT_MAX_UPLOAD_MB))
    except ValueError:
        max_upload_mb = DEFAULT_MAX_UPLOAD_MB
    app.config['MAX_CONTENT_LENGTH'] = max_upload_mb * 1024 * 1024

    # Apply test config overrides if provided
    if test_config:
        app.config.update(test_config)

    # Initialize extensions
    csrf.init_app(app)
    limiter.init_app(app)
    cache.init_app(app, config={'CACHE_TYPE': 'SimpleCache'})
    Talisman(app, content_security_policy={
        'default-src': "'self'",
        'img-src': "'self' data: blob:",
        'script-src': "'self' 'unsafe-inline' 'unsafe-eval'",
        'style-src': "'self' 'unsafe-inline'"
    }, force_https=False)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Register HTTP route handlers
    _register_routes(app)

    # Explicit background worker thread initiation
    if start_cleanup and not app.config.get('TESTING', False):
        if os.environ.get('BRANDKIT_CLEANUP_ENABLED', 'true').lower() not in ('0', 'false', 'no'):
            _thread = start_cleanup_thread(upload_folder=app.config['UPLOAD_FOLDER'])
            app.cleanup_thread = _thread

    return app


def _register_routes(app):
    @app.route('/')
    def index():
        config = load_config()
        return render_template(
            'index.html',
            config=config,
            max_upload_mb=app.config['MAX_CONTENT_LENGTH'] // (1024 * 1024),
            csrf_token=generate_csrf()
        )

    @app.route('/format-info', methods=['GET'])
    def format_info():
        config = load_config()
        categories = config.get('format_categories', {})
        
        purposes = {
            "social": ["social", "twitter", "instagram", "linkedin", "facebook"],
            "website": ["website", "hero_desktop", "hero_mobile", "background_desktop", "background_mobile"],
            "icons": ["webapp", "favicon", "square_logo_small", "square_logo_large", "social_icon_small", "social_icon_large"],
            "general": ["square_1024", "mobile"]
        }
        
        recommendations = {
            "Website Essentials": ["website", "favicon", "hero_desktop", "background_desktop"],
            "Social Media Pack": ["social", "twitter", "instagram", "facebook", "social_icon_large"],
            "Complete Branding": ["social", "website", "favicon", "webapp", "background_desktop"],
            "Mobile App Pack": ["webapp", "mobile", "square_logo_small", "square_logo_large"]
        }
        
        return jsonify({
            'success': True,
            'categories': categories,
            'purposes': purposes,
            'recommendations': recommendations
        })

    @app.route('/analyze', methods=['POST'])
    def analyze_image_endpoint():
        try:
            if 'file' not in request.files:
                return jsonify({'success': False, 'error': 'No file part'}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'success': False, 'error': 'No selected file'}), 400
            
            if not allowed_file(file.filename, app.config.get('ALLOWED_EXTENSIONS')):
                return jsonify({'success': False, 'error': 'File type not allowed'}), 400
            
            temp_file_path = None
            try:
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1])
                temp_file_path = temp_file.name
                file.save(temp_file_path)
                temp_file.close()

                with Image.open(temp_file_path) as img:
                    if img.mode != 'RGBA':
                        img = img.convert('RGBA')
                    
                    prominent_color = [200, 200, 200]
                    try:
                        prominent_color = get_prominent_color(img)
                    except Exception as e:
                        logging.error(f"Error getting prominent color: {e}")
                    
                    has_white_area = False
                    white_area_ratio = 0.0
                    try:
                        has_white_area, white_area_ratio = has_significant_white_area(img)
                    except Exception as e:
                        logging.error(f"Error detecting white areas: {e}")
                    
                    analysis_results = {
                        'prominent_color': prominent_color,
                        'has_white_area': bool(has_white_area),
                        'white_area_ratio': float(white_area_ratio)
                    }
                    
                    return jsonify({
                        'success': True,
                        'analysis': analysis_results
                    })
            except HTTPException:
                raise
            except Exception as e:
                logging.error(f"Error analyzing image: {e}")
                return jsonify({
                    'success': False,
                    'error': f'Error analyzing image: {str(e)}'
                }), 500
            finally:
                if temp_file_path and os.path.exists(temp_file_path):
                    try:
                        os.unlink(temp_file_path)
                    except Exception as e:
                        logging.error(f"Error removing temp file: {e}")
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"Unexpected error in analyze endpoint: {e}")
            return jsonify({
                'success': False,
                'error': f'Server error: {str(e)}'
            }), 500

    @app.route('/upload', methods=['POST'])
    @limiter.limit("5 per minute")
    def upload_file():
        try:
            if 'file' not in request.files:
                return jsonify({'error': 'No file part'}), 400
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No selected file'}), 400
            if not allowed_file(file.filename, app.config.get('ALLOWED_EXTENSIONS')):
                return jsonify({'error': 'File type not allowed'}), 400

            filename = secure_filename(file.filename)
            file_id = str(uuid.uuid4())
            filename_without_ext = os.path.splitext(filename)[0]
            
            unique_filename = f"{file_id}_{filename}"
            upload_dir = app.config['UPLOAD_FOLDER']
            file_path = os.path.join(upload_dir, unique_filename)
            file.save(file_path)
            
            # Process image with mandatory metadata stripping
            try:
                with Image.open(file_path) as img:
                    data = list(img.getdata())
                    img_without_exif = Image.new(img.mode, img.size)
                    img_without_exif.putdata(data)
                    img_without_exif.save(file_path)
            except Exception as e:
                logging.error(f"Error processing image: {e}")
                if os.path.exists(file_path):
                    os.remove(file_path)
                return jsonify({'error': 'Invalid image file'}), 400

            try:
                selected_formats = request.form.getlist('selected_formats')
                output_formats = request.form.getlist('output_formats')
                variations_mode = request.form.get('variations_mode') == 'true'
                fill_white_with_prominent = request.form.get('fill_white_with_prominent') == 'true'
                
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
                    'hue_shift': int(float(request.form.get('hue_shift', 0))),
                    'temperature': int(float(request.form.get('temperature', 0))),
                    'enhance_contrast': request.form.get('enhance_contrast') == 'true',
                    'apply_blur': request.form.get('apply_blur') == 'true',
                    'blur_radius': float(request.form.get('blur_radius', config.get('preprocessing_options', {}).get('blur_radius', 2.0))),
                    'add_watermark': request.form.get('add_watermark') == 'true',
                    'watermark_text': request.form.get('watermark_text', config.get('preprocessing_options', {}).get('watermark_text', '© BrandKit')),
                    'watermark_opacity': float(request.form.get('watermark_opacity', config.get('preprocessing_options', {}).get('watermark_opacity', 0.3))),
                    'vignette': request.form.get('vignette') == 'true',
                    'vignette_strength': float(request.form.get('vignette_strength', config.get('preprocessing_options', {}).get('vignette_strength', 0.5))),
                    'saturation': float(request.form.get('saturation', config.get('preprocessing_options', {}).get('saturation', 1.0))),
                    'brightness': float(request.form.get('brightness', config.get('preprocessing_options', {}).get('brightness', 1.0))),
                    'sharpen': request.form.get('sharpen') == 'true',
                    'sharpen_radius': float(request.form.get('sharpen_radius', config.get('preprocessing_options', {}).get('sharpen_radius', 1.0))),
                    'remove_background': request.form.get('remove_background') == 'true',
                    'background_removal_method': request.form.get('background_removal_method', 'auto'),
                    'background_color': request.form.get('background_color', 'transparent'),
                    'edge_smooth': request.form.get('edge_smooth') == 'true',
                    'smooth_radius': float(request.form.get('smooth_radius', 2.0)),
                    'noise_reduction': request.form.get('noise_reduction') == 'true',
                    'noise_strength': int(request.form.get('noise_strength', 1)),
                    'auto_crop': request.form.get('auto_crop') == 'true',
                    'crop_padding': int(request.form.get('crop_padding', 10)),
                    'shadow_effect': request.form.get('shadow_effect') == 'true',
                    'shadow_opacity': float(request.form.get('shadow_opacity', 0.3)),
                    'shadow_blur': int(request.form.get('shadow_blur', 4)),
                    'shadow_offset': (int(request.form.get('shadow_offset_x', 5)), int(request.form.get('shadow_offset_y', 5))),
                    'enhance_quality': request.form.get('enhance_quality') == 'true',
                }
                
                quality = int(request.form.get('quality', 95))
                strip_metadata = request.form.get('strip_metadata') == 'true'
                original_path = file_path
                    
                try:
                    img_for_analysis = Image.open(original_path)
                    prominent_color = get_prominent_color(img_for_analysis)
                    has_white_area, white_area_ratio = has_significant_white_area(img_for_analysis)
                    analysis_results = {
                        'prominent_color': prominent_color,
                        'has_white_area': bool(has_white_area),
                        'white_area_ratio': float(white_area_ratio)
                    }
                except Exception as e:
                    logging.error(f"Image analysis failed: {e}")
                    analysis_results = {
                        'prominent_color': [200, 200, 200],
                        'has_white_area': False,
                        'white_area_ratio': 0.0
                    }
                    
                results = generate_formats(
                    original_path,
                    filename_without_ext,
                    selected_formats,
                    output_formats,
                    preprocessing_options,
                    variations_mode=variations_mode,
                    fill_white_with_prominent=fill_white_with_prominent,
                    quality=quality,
                    strip_metadata=strip_metadata,
                    upload_folder=upload_dir
                )
                
                results['original'] = {
                    'path': original_path,
                    'url': f"/{upload_dir}/{unique_filename}"
                }
                
                if analysis_results:
                    results['analysis'] = analysis_results
                    
                zip_info = create_zip_file(results, filename_without_ext, upload_folder=upload_dir)
                if zip_info:
                    results['zip'] = zip_info
                
                serializable_results = ensure_serializable(results)
                
                if len(selected_formats) > 5 or variations_mode:
                    cleanup_memory()
                
                return jsonify({
                    'success': True,
                    'message': 'File processed successfully',
                    'results': serializable_results
                })
            except ValueError as ve:
                logging.error(f"Value Error during processing: {ve}")
                return jsonify({'error': str(ve)}), 400
            except HTTPException:
                raise
            except Exception as e:
                logging.error(f"An unexpected error occurred: {e}")
                return jsonify({'error': 'An unexpected error occurred during processing.'}), 500
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"Upload error: {e}")
            return jsonify({'error': f'Server error: {str(e)}'}), 500

    @app.route('/download-zip/<filename>')
    def download_zip(filename):
        safe_name = secure_filename(filename)
        if not safe_name or safe_name != filename or not safe_name.endswith('.zip'):
            return jsonify({'error': 'File not found'}), 404

        upload_root = os.path.realpath(app.config['UPLOAD_FOLDER'])
        zip_path = os.path.realpath(os.path.join(upload_root, safe_name))
        if os.path.commonpath([upload_root, zip_path]) != upload_root:
            return jsonify({'error': 'File not found'}), 404

        if os.path.isfile(zip_path):
            return send_file(zip_path, as_attachment=True)
        return jsonify({'error': 'File not found'}), 404


# Top-level WSGI application instance for gunicorn and standalone execution
app = create_app()
_cleanup_thread = getattr(app, 'cleanup_thread', None)


if __name__ == '__main__':
    is_debug = os.environ.get('FLASK_ENV') == 'development'
    port = int(os.environ.get('PORT', 8000))
    app.run(port=port, debug=is_debug)