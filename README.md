# BrandKit Generator ✨

**Generate a complete set of brand assets (logos, banners, icons) in multiple formats and sizes from a single image.**

BrandKit is a web application designed to streamline the creation of brand assets. Upload one source image (like your logo), select desired formats, and BrandKit intelligently resizes, pads, and exports everything you need for websites, web apps, social media, and more. It uses Flask, Pillow, and Alpine.js, and is fully containerized for easy deployment.

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/your-username/brandkit/actions) <!-- Replace with your CI/CD badge -->
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Docker Hub](https://img.shields.io/badge/Docker%20Hub-ready-blue?logo=docker)](https://hub.docker.com/r/your-dockerhub-username/brandkit) <!-- Replace with your Docker Hub badge -->

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

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/fabriziosalmi/brandkit.git
    cd brandkit
    ```
2.  **Build and run with Docker Compose:**
    ```sh
    docker-compose up --build -d # Use -d to run in detached mode
    ```
3.  **Open in your browser:**

    Visit [http://localhost:8000](http://localhost:8000)

4.  **Upload an image, select formats/options, and generate your brand kit!**

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
- `FLASK_ENV=development` - Enable debug mode
- `BRANDKIT_MAX_UPLOAD_MB=16` - Set max upload size (default: 16MB)

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

**Background Removal Not Working:**
- Install rembg: `pip install rembg`
- On first use, models will download automatically (may take a few minutes)
- Ensure sufficient disk space for AI models (~100-500MB per model)

**Upload/Permission Errors:**
- Ensure `static/uploads` directory is writable
- Check file size limits (default 16MB, configurable via `BRANDKIT_MAX_UPLOAD_MB`)
- Verify file format is supported (PNG, JPG, JPEG, GIF, WEBP)

**Memory Issues:**
- Monitor memory usage with built-in psutil monitoring
- Reduce image size or number of simultaneous formats
- Increase Docker memory limits if using containers

**Performance Issues:**
- Enable caching for better performance on repeated operations
- Use SSD storage for faster image processing
- Ensure adequate RAM for large images and AI processing

**Security/CSRF Errors:**
- Check that `FLASK_SECRET_KEY` is properly set
- Verify CSRF token is included in form submissions
- Clear browser cache and cookies

**Docker/Container Issues:**
- Ensure proper volume mounts for persistent uploads
- Check container memory limits for AI processing
- Verify port mappings (default 8000)

**For custom domains/SSL:**
- Use a reverse proxy (Nginx, Caddy) for production
- Configure proper SSL termination
- Set up security headers appropriately

---

## Feedback & Contributions

PRs and issues welcome! For feature requests or bug reports, please open an issue.

---

<p align="center">
  <a href="https://github.com/fabriziosalmi/brandkit" target="_blank" rel="noopener noreferrer" title="View on GitHub">
    <svg width="32" height="32" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
      <path fill-rule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.036 1.531 1.036.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.026 2.747-1.026.546 1.379.201 2.397.098 2.65.64.7 1.028 1.595 1.028 2.688 0 3.848-2.338 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clip-rule="evenodd" />
    </svg>
  </a>
</p>
