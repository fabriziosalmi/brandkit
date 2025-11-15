# BrandKit Generator ✨

**Generate a complete set of brand assets (logos, banners, icons) in multiple formats and sizes from a single image.**

BrandKit is a web application designed to streamline the creation of brand assets. Upload one source image (like your logo), select desired formats, and BrandKit intelligently resizes, pads, and exports everything you need for websites, web apps, social media, and more. It uses Flask, Pillow, and Alpine.js, and is fully containerized for easy deployment.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg?logo=docker)](https://www.docker.com/)

## Table of Contents

- [Screenshots](#screenshots)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [Quick Start](#quick-start-docker-compose)
- [Usage Guide](#usage-guide)
- [Keyboard Shortcuts](#keyboard-shortcuts)
- [Performance Features](#performance-features)
- [Configuration](#configuration-configjson)
- [File Structure](#file-structure)
- [Development](#development)
- [Docker Details](#docker-details)
- [Security Features](#security-features)
- [Deployment & Security](#deployment--security)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [Changelog](#changelog)
- [License](#license)

## Screenshots

![screenshot1](https://github.com/fabriziosalmi/brandkit/blob/main/screenshot_1.png?raw=true)
![screenshot2](https://github.com/fabriziosalmi/brandkit/blob/main/screenshot_2.png?raw=true)

---

## Key Features

### 🎯 AI-Powered Background Removal
*   **Advanced Background Removal:** Powered by the `rembg` library with multiple AI models for different content types
*   **Smart Method Selection:** Choose from Auto (best guess), Person/Portrait, Object/Product, or Anime/Illustration modes
*   **Background Color Options:** Replace transparent areas with solid colors or keep transparency
*   **Edge Smoothing:** Automatically smooth edges after background removal for professional results

### 🎨 Enhanced Image Processing
*   **Single Image Source:** Upload one image (PNG, JPG, GIF, WEBP) and generate dozens of assets
*   **Advanced Preprocessing:** Apply 15+ effects including grayscale, B&W, inversion, hue shifts, temperature adjustments, contrast enhancement, blur, vignette, saturation, brightness, sharpening, and watermarking
*   **Auto Crop:** Intelligent cropping to remove unnecessary transparent/white areas
*   **Noise Reduction:** Clean up image artifacts for better quality
*   **Drop Shadow Effects:** Add professional drop shadows with customizable opacity and blur
*   **Quality Enhancement:** Automatic sharpness, color, and contrast improvements

### 📐 Format & Output Management
*   **Wide Format Support:** 25+ predefined formats for web, mobile, social media, business documents, and publishing
*   **Smart Background Fill:** Automatically adds tasteful radial gradient backgrounds based on prominent colors
*   **Format Presets:** Quick selection for Social Media Pack, Website Essentials, Mobile App Pack, and Complete Branding
*   **Multiple Output Types:** Export as PNG, JPG, WEBP, and ICO (for favicons)
*   **Bulk Download:** Download all generated assets in organized zip files

### 🚀 User Experience & Performance
*   **Format Search:** Easily find specific formats using the search functionality
*   **Recent Uploads:** Quick access to recently used images
*   **Color Variations:** Generate multiple thematic variations for each format
*   **Keyboard Shortcuts:** Power-user features for faster workflows (Shift+? for help)
*   **Intelligent Caching:** Improved performance for repeat operations
*   **Visual Processing Feedback:** Real-time progress information
*   **Modern UI:** Responsive interface built with Tailwind CSS and Alpine.js

### 🔒 Security & Deployment
*   **Security Hardened:** CSRF protection, rate limiting, CSP headers, and metadata stripping
*   **Memory Management:** Automatic cleanup and optimization for stability
*   **Containerized:** Easy deployment with Docker and Docker Compose
*   **Production Ready:** Optimized for both development and production environments

---

## Technology Stack

*   **Backend:** Flask (Python 3.11+)
*   **AI Background Removal:** rembg library with multiple neural network models
*   **Image Processing:** Pillow (PIL), OpenCV, NumPy
*   **Frontend:** Alpine.js, Tailwind CSS
*   **Security:** Flask-WTF (CSRF), Flask-Limiter (rate limiting), Flask-Talisman (security headers)
*   **Performance:** Flask-Caching, intelligent memory management, psutil monitoring
*   **Containerization:** Docker, Docker Compose

---

## Quick Start (Docker Compose)

The fastest way to get BrandKit running is with Docker Compose:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/fabriziosalmi/brandkit.git
    cd brandkit
    ```

2.  **Build and run with Docker Compose:**
    ```bash
    docker-compose up --build -d
    ```
    The `-d` flag runs containers in detached mode (background).

3.  **Open in your browser:**
    Visit [http://localhost:8000](http://localhost:8000)

4.  **Upload an image, select formats/options, and generate your brand kit!**

5.  **Stop the application:**
    ```bash
    docker-compose down
    ```

**Troubleshooting Docker:**
- Ensure Docker daemon is running
- Check port 8000 is not already in use: `lsof -i :8000` (macOS/Linux) or `netstat -ano | findstr :8000` (Windows)
- View logs: `docker-compose logs -f brandkit`

---

## Usage Guide

### Basic Workflow
1.  **Upload:** Drag and drop an image file (PNG, JPG, GIF, WEBP, max 16MB) onto the upload area, or click to select a file. You can also select from your recent uploads.

### Background Removal (NEW!)
2.  **AI Background Removal:** 
    *   Toggle "🎯 Remove Background" to enable AI-powered background removal
    *   **Method Selection:** Choose the best AI model for your content:
        *   **Auto:** Best general-purpose detection
        *   **Person/Portrait:** Optimized for human subjects
        *   **Object/Product:** Best for products and objects
        *   **Anime/Illustration:** Specialized for anime and illustrations
    *   **Background Color:** Choose what replaces the removed background:
        *   Keep Transparent, White, Black, Gray variations, or custom colors
        *   Color picker available for precise color matching
    *   **Edge Smoothing:** Automatically smooth edges for professional results

### Advanced Preprocessing
3.  **Image Effects (Optional):** Apply 15+ preprocessing effects before generating formats:
    *   **Basic Effects:** Grayscale, B&W, Invert, Contrast Enhancement
    *   **Color Adjustments:** Hue Shift (-180° to +180°), Temperature, Saturation, Brightness
    *   **Quality Enhancement:** Auto Crop, Noise Reduction, Sharpen, Quality Enhancement
    *   **Artistic Effects:** Blur with radius control, Vignette, Drop Shadow
    *   **Watermarking:** Add custom text watermarks with opacity control

### Format Selection & Generation
4.  **Select Formats:** 
    *   **Individual Selection:** Check boxes for specific dimensions
    *   **Format Presets:** Quick selection buttons:
        *   Social Media Pack, Website Essentials, Mobile App Pack, Complete Branding
    *   **Format Search:** Use the search bar to quickly find specific formats
    *   **Categories:** Browse by Web Application, Website, Social Media, Mobile, Business Documents, Publishing

5.  **Output Options:** Select file types (PNG, JPG, WEBP, ICO)

6.  **Advanced Options (Optional):** 
    *   Control image quality (compression)
    *   Strip metadata for privacy
    *   Generate Color Variations (creates themed versions of each format)

7.  **Generate:** Click **Generate Brand Kit** or use Ctrl+Enter

8.  **Download:**
    *   Individual assets via direct links
    *   Bulk download as organized zip file with "Download All (.zip)"

---

## Keyboard Shortcuts

Press `Shift+?` anywhere in the application to view the available keyboard shortcuts:

* `Space` - Open file selector when focused on upload area
* `Ctrl+Enter` or `⌘+Enter` - Generate assets (submit form)
* `Escape` - Reset form or close dialogs

View complete shortcut documentation in [KEYBOARD_SHORTCUTS.md](KEYBOARD_SHORTCUTS.md)

---

## Performance Features

BrandKit includes several performance and reliability optimizations:

* **AI Processing:** GPU-accelerated background removal with multiple specialized models
* **Image Caching:** Processed images are cached and reused when possible, reducing processing time
* **Memory Management:** Intelligent garbage collection, memory monitoring with psutil, automatic cleanup
* **Disk Space Management:** Automatic cleanup of old files to prevent storage issues
* **Processing Progress:** Real-time visual feedback on processing steps and completion status
* **Error Handling:** Robust error handling and fallbacks for all processing steps
* **Batch Operations:** Efficient bulk processing of multiple formats simultaneously

---

## Configuration (`config.json`)

The `config.json` file defines the available output formats, their dimensions, descriptions, and categories. You can customize this file to add, remove, or modify formats according to your needs.

### Configuration Structure:
*   **`formats`:** Dictionary defining each output format with width, height, and description
*   **`format_categories`:** Groups formats logically for UI organization (Web Application, Website, Social Media, Mobile, Business Documents, Publishing)
*   **`output_formats`:** Lists the supported export file types (png, jpg, webp, ico)
*   **`preprocessing_options`:** Defines default values for preprocessing controls

### Available Format Categories:
*   **Web Application:** webapp, favicon, square logos, rectangle logos
*   **Website:** website banners, hero images, backgrounds, blog posts, lightbox images
*   **Social Media:** social posts, Twitter, Instagram, LinkedIn, Facebook, social icons
*   **Mobile:** mobile screens, thumbnails
*   **Business Documents:** email headers, document headers, presentation slides
*   **Publishing:** ebook covers
*   **General Purpose:** square formats (1024x1024) for versatile use

---

## File Structure

```
app.py                     # Flask backend with AI processing
config.json                # Format and output configuration
requirements.txt           # Python dependencies (includes rembg, opencv)
Dockerfile                 # Docker build configuration
docker-compose.yml         # Multi-container setup
entrypoint.sh             # Docker entrypoint script
static/                   # Static assets
  css/                    # Custom stylesheets
  js/                     # JavaScript files
  uploads/                # Generated images and user uploads
    cache/                # Performance cache for processed images
templates/
  index.html              # Main UI with background removal controls
KEYBOARD_SHORTCUTS.md      # Keyboard shortcut documentation
SECURITY.md               # Security guidelines
CODE_OF_CONDUCT.md        # Community guidelines
```

---

## Development

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11 or higher** - [Download Python](https://www.python.org/downloads/)
- **pip** - Python package installer (included with Python 3.11+)
- **Git** - For version control
- **Docker & Docker Compose** (optional) - For containerized deployment
  - [Docker Desktop](https://www.docker.com/products/docker-desktop/) (macOS, Windows)
  - Docker Engine (Linux)

**System Requirements:**
- Minimum 2GB RAM (4GB+ recommended for large images)
- 1GB free disk space (more for AI models and cached images)
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Local Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/fabriziosalmi/brandkit.git
   cd brandkit
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   
   **Note:** On first run, the `rembg` library will download AI models (~100-500MB). This is a one-time download.

4. **Run the application:**
   ```bash
   python app.py
   ```

5. **Access the application:**
   Open your browser and navigate to [http://localhost:8000](http://localhost:8000)

### Local Development Setup
- **Python 3.11+ Required**
- Run locally:
  ```sh
  python3 -m venv venv
  source venv/bin/activate  # On Windows: venv\Scripts\activate
  pip install -r requirements.txt
  python app.py
  ```
- App runs at [http://localhost:8000](http://localhost:8000)

### Key Dependencies
```bash
# Core dependencies
pip install flask pillow werkzeug

# Security and performance
pip install Flask-WTF Flask-Limiter Flask-Caching Flask-Talisman psutil

# AI background removal (optional but recommended)
pip install rembg

# Advanced image processing (optional)
pip install opencv-python numpy
```

### Environment Variables

Configure BrandKit behavior using environment variables:

- `FLASK_ENV=development` - Enable debug mode with auto-reload and detailed error pages
- `FLASK_ENV=production` - Run in production mode with optimizations and scheduled cleanup
- `BRANDKIT_MAX_UPLOAD_MB=16` - Set maximum upload file size in megabytes (default: 16MB)
- `FLASK_SECRET_KEY` - Custom secret key for session management (auto-generated if not set)

**Example:**
```bash
export FLASK_ENV=development
export BRANDKIT_MAX_UPLOAD_MB=32
python app.py
```

---

## Docker Details

- **Build image:**
  ```sh
  docker build -t brandkit .
  ```
- **Run container:**
  ```sh
  docker run -p 8000:8000 -v $(pwd)/static/uploads:/app/static/uploads brandkit
  ```
- **Stop all:**
  ```sh
  docker-compose down
  ```

---

## Security Features

BrandKit includes comprehensive security enhancements:

* **Content Security Policy (CSP):** Protection against XSS and other common web vulnerabilities
* **CSRF Protection:** Cross-site request forgery protection with Flask-WTF
* **Rate Limiting:** Protection against abuse and DoS attacks (200/day, 50/hour default)
* **Security Headers:** Comprehensive security headers via Flask-Talisman
* **Metadata Stripping:** Option to remove EXIF data for privacy protection
* **Input Validation:** Thorough validation of all user inputs and file uploads
* **Memory Safety:** Protection against memory exhaustion attacks
* **Secure File Handling:** Safe file upload and processing with extension validation

---

## Deployment & Security

For exposing the Brand Kit Generator to the internet securely, it's recommended to use a reverse proxy for SSL offloading and potentially a secure tunnel like Cloudflared for Zero Trust access control.

### Reverse Proxy (SSL Offloading)

Running the Flask development server directly exposed is not recommended for production. Use a reverse proxy like Nginx or Caddy to handle HTTPS/SSL termination.

**Using Docker Compose:**

You can integrate Caddy or Nginx into your `docker-compose.yml`.

**Example with Caddy:**

```yaml
# docker-compose.yml (partial)
services:
  brandkit:
    # ... your brandkit service definition ...
    # Ensure it exposes the port (e.g., 8000) internally
    # networks:
    #   - webproxy

  caddy:
    image: caddy:latest
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile # Mount your Caddyfile
      - caddy_data:/data
      - caddy_config:/config
    # networks:
    #   - webproxy

# networks:
#   webproxy:
#     external: true # Or define it here

volumes:
  caddy_data:
  caddy_config:
```

**Example Caddyfile:**

```caddy
# Caddyfile
your-domain.com {
    # Automatic HTTPS via Let's Encrypt
    reverse_proxy brandkit:8000 # Proxy requests to the brandkit service on port 8000
}
```

Refer to the [Caddy Docker documentation](https://hub.docker.com/_/caddy) or [Nginx Proxy Manager](https://nginxproxymanager.com/) for more detailed setup instructions.

### Secure Tunneling (Cloudflared)

To securely expose your Brand Kit Generator without opening firewall ports and add Zero Trust authentication (like Google Workspace or specific email access), you can use Cloudflare Tunnel (cloudflared).

**Using Docker:**

1.  **Set up a Cloudflare Tunnel:** Follow the [Cloudflare Tunnel documentation](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/) to create a tunnel and get your tunnel token.
2.  **Run Cloudflared Container:** Add `cloudflared` to your `docker-compose.yml`.

```yaml
# docker-compose.yml (partial)
services:
  brandkit:
    # ... your brandkit service definition ...
    # No need to expose ports externally if only using the tunnel
    # networks:
    #   - internal_network

  cloudflared:
    image: cloudflare/cloudflared:latest
    restart: unless-stopped
    command: tunnel --no-autoupdate run --token YOUR_TUNNEL_TOKEN # Replace with your token
    # networks:
    #   - internal_network

# networks:
#   internal_network:
```

3.  **Configure DNS:** In your Cloudflare dashboard, point a CNAME record (e.g., `brandkit.your-domain.com`) to your tunnel's UUID `.cfargotunnel.com` address.
4.  **Set up Access Policy:**
    *   Go to Cloudflare Zero Trust dashboard -> Access -> Applications.
    *   Add a "Self-hosted" application.
    *   Configure the subdomain (e.g., `brandkit.your-domain.com`).
    *   Set the "Identity providers" (e.g., enable Google and configure allowed accounts/groups, or set up email authentication).
    *   Create an "Allow" policy, defining who can access (e.g., emails ending in `@yourcompany.com`, specific Gmail addresses, etc.).

This setup ensures only authenticated users can reach your Brand Kit Generator instance through Cloudflare's network.

---

## Troubleshooting

### Common Issues and Solutions

#### Background Removal Not Working

**Problem:** Background removal feature doesn't process images or shows errors.

**Solutions:**
- **Check Installation:** Ensure `rembg` is installed: `pip install rembg`
- **First Run:** On first use, AI models download automatically (100-500MB per model). This may take several minutes depending on your internet connection. Check console output for download progress.
- **Disk Space:** Verify sufficient disk space for AI models (at least 1GB free)
- **Memory:** Background removal requires adequate RAM. For large images, ensure at least 4GB available memory.
- **Permissions:** Ensure the application has write access to the cache directory

**Check Model Installation:**
```bash
python3 -c "from rembg import remove; print('rembg is working')"
```

#### Upload/Permission Errors

**Problem:** "Permission denied" or upload failures.

**Solutions:**
- **Directory Permissions:** Ensure `static/uploads` directory exists and is writable:
  ```bash
  mkdir -p static/uploads
  chmod 755 static/uploads
  ```
- **File Size:** Check if file exceeds the limit (default 16MB). Increase with:
  ```bash
  export BRANDKIT_MAX_UPLOAD_MB=32
  ```
- **File Format:** Verify file is a supported format (PNG, JPG, JPEG, GIF, WEBP)
- **Disk Space:** Ensure sufficient disk space for uploads and processing
- **Docker Volumes:** For Docker, verify volume mounts are correct in `docker-compose.yml`

**Check Permissions:**
```bash
ls -la static/uploads
# Should show rwxr-xr-x or similar
```

#### Memory Issues

**Problem:** Application crashes or becomes unresponsive during processing.

**Solutions:**
- **Monitor Memory:** Check memory usage with built-in psutil monitoring (visible in console logs)
- **Reduce Image Size:** Process smaller images or reduce the number of simultaneous formats
- **Increase Docker Memory:** For Docker deployments, increase container memory limits:
  ```yaml
  # In docker-compose.yml
  services:
    brandkit:
      deploy:
        resources:
          limits:
            memory: 4G
  ```
- **Disable AI Features:** If memory is very limited, process images without background removal
- **Clear Cache:** Remove cached files from `static/uploads/cache/`

**Monitor Memory:**
```bash
# Linux/macOS
top -p $(pgrep -f "python app.py")

# Docker
docker stats brandkit
```

#### Performance Issues

**Problem:** Slow image processing or generation.

**Solutions:**
- **Enable Caching:** Caching is enabled by default. Verify processed images are being cached
- **Use SSD Storage:** Store the application on SSD for faster I/O operations
- **Optimize Images:** Reduce source image size before uploading
- **Adequate RAM:** Ensure at least 2GB RAM available (4GB+ recommended)
- **Reduce Formats:** Generate fewer formats at once to improve speed
- **Background Removal:** AI processing is CPU/memory intensive. Use sparingly for better performance
- **Clean Up:** Regularly clear old files: `rm -rf static/uploads/*` (except README.md)

**Check Cache:**
```bash
ls -lh static/uploads/cache/
# Should show cached processed images
```

#### Security/CSRF Errors

**Problem:** "CSRF token missing" or "CSRF validation failed" errors.

**Solutions:**
- **Secret Key:** Ensure `FLASK_SECRET_KEY` is set (auto-generated if not specified)
- **Cookies:** Enable cookies in your browser
- **Clear Cache:** Clear browser cache and cookies, then reload
- **HTTPS/HTTP Mismatch:** Ensure consistent protocol (both HTTP or both HTTPS)
- **Reload Page:** Refresh the page to get a new CSRF token

**Check CSRF:**
```bash
# Verify CSRF protection is active
curl -X POST http://localhost:8000/upload
# Should return 400 with CSRF error
```

#### Docker/Container Issues

**Problem:** Container fails to start or can't connect.

**Solutions:**
- **Port Conflicts:** Ensure port 8000 is not in use:
  ```bash
  # macOS/Linux
  lsof -i :8000
  
  # Windows
  netstat -ano | findstr :8000
  ```
- **Volume Mounts:** Verify upload directory mounts correctly:
  ```bash
  docker-compose exec brandkit ls -la /app/static/uploads
  ```
- **Container Logs:** Check logs for errors:
  ```bash
  docker-compose logs -f brandkit
  ```
- **Memory Limits:** AI processing requires adequate memory. Increase Docker memory allocation in Docker Desktop settings (recommended: 4GB+)
- **Rebuild Container:** Force rebuild if issues persist:
  ```bash
  docker-compose down
  docker-compose build --no-cache
  docker-compose up
  ```

**Verify Container Health:**
```bash
docker ps
# Should show brandkit container as "Up"

docker-compose exec brandkit python3 -c "print('Container is working')"
```

#### SSL/Custom Domain Issues

**Problem:** SSL errors or can't access via custom domain.

**Solutions:**
- **Use Reverse Proxy:** Don't expose Flask directly. Use Nginx or Caddy for SSL termination
- **Check Certificates:** Verify SSL certificates are valid and properly configured
- **DNS Configuration:** Ensure DNS records point to correct IP address
- **Firewall:** Check firewall rules allow traffic on ports 80/443
- **CSP Headers:** If using custom domains, may need to adjust Content Security Policy in `app.py`

**Example Nginx Configuration:**
```nginx
server {
    listen 443 ssl;
    server_name brandkit.yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Error Messages Reference

| Error Message | Likely Cause | Solution |
|---------------|--------------|----------|
| "File too large" | Exceeds upload limit | Increase `BRANDKIT_MAX_UPLOAD_MB` |
| "Invalid file type" | Unsupported format | Use PNG, JPG, GIF, or WEBP |
| "Permission denied" | Directory not writable | Fix permissions: `chmod 755 static/uploads` |
| "Out of memory" | Insufficient RAM | Reduce image size or increase available memory |
| "CSRF token missing" | Session/cookie issue | Clear cookies and reload page |
| "Port already in use" | Port conflict | Change port or stop conflicting service |
| "rembg not found" | Missing dependency | Install: `pip install rembg` |
| "Module not found" | Missing dependencies | Run: `pip install -r requirements.txt` |

### Getting Additional Help

If your issue isn't listed here:

1. **Check Logs:** Review application logs for detailed error messages
   ```bash
   # Local development
   # Errors appear in console where you ran `python app.py`
   
   # Docker
   docker-compose logs -f brandkit
   ```

2. **Search Issues:** Check [existing GitHub issues](https://github.com/fabriziosalmi/brandkit/issues)

3. **Enable Debug Mode:** Run with `FLASK_ENV=development` for detailed error pages

4. **Open an Issue:** If problem persists, [create a new issue](https://github.com/fabriziosalmi/brandkit/issues/new) with:
   - Detailed description
   - Steps to reproduce
   - Error messages/logs
   - Environment details (OS, Python version, Docker version)
   - Screenshots if applicable

### Performance Optimization Tips

- **Batch Processing:** Generate all formats at once rather than one at a time
- **Cache Utilization:** Reuse preprocessed images by using consistent preprocessing options
- **Image Optimization:** Optimize source images before upload (reduce resolution if very large)
- **Format Selection:** Only generate formats you actually need
- **Output Quality:** Lower quality settings (70-85) reduce file size with minimal visual impact
- **Metadata Stripping:** Enable to reduce output file sizes
- **Regular Cleanup:** Periodically clean upload directory to free disk space

**For custom domains/SSL:**
- Use a reverse proxy (Nginx, Caddy) for production
- Configure proper SSL termination
- Set up security headers appropriately

---

## Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) before submitting a Pull Request.

For bug reports and feature requests, please use the [GitHub Issues](https://github.com/fabriziosalmi/brandkit/issues) page.

For security vulnerabilities, please review our [Security Policy](SECURITY.md).

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed history of changes to this project.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  <a href="https://github.com/fabriziosalmi/brandkit" target="_blank" rel="noopener noreferrer" title="View on GitHub">
    <svg width="32" height="32" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
      <path fill-rule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.036 1.531 1.036.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.026 2.747-1.026.546 1.379.201 2.397.098 2.65.64.7 1.028 1.595 1.028 2.688 0 3.848-2.338 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clip-rule="evenodd" />
    </svg>
  </a>
</p>
