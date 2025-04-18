# BrandKit Generator ✨

**Generate a complete set of brand assets (logos, banners, icons) in multiple formats and sizes from a single image.**

BrandKit is a web application designed to streamline the creation of brand assets. Upload one source image (like your logo), select desired formats, and BrandKit intelligently resizes, pads, and exports everything you need for websites, web apps, social media, and more. It uses Flask, Pillow, and Alpine.js, and is fully containerized for easy deployment.

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/your-username/brandkit/actions) <!-- Replace with your CI/CD badge -->
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Docker Hub](https://img.shields.io/badge/Docker%20Hub-ready-blue?logo=docker)](https://hub.docker.com/r/your-dockerhub-username/brandkit) <!-- Replace with your Docker Hub badge -->

---

## Key Features

*   **Single Image Source:** Upload one image (PNG, JPG, GIF, WEBP) and generate dozens of assets.
*   **Wide Format Support:** Generate assets for various platforms (web, mobile, social media, favicons, etc.) based on `config.json`.
*   **Smart Background Fill:** Automatically adds a tasteful radial gradient background (based on the image's prominent color) when resizing square images to non-square formats, preventing ugly letterboxing.
*   **Prominent Color Extraction:** Intelligently detects the main color of your image for use in features like background fill.
*   **Image Preprocessing:** Apply effects like grayscale, B&W, inversion, hue shifts, temperature adjustments, contrast enhancement, blur, and watermarking *before* generating assets.
*   **Color Variations:** Optionally generate multiple thematic variations (e.g., Grayscale, Inverted, Warm, Cool) for each selected format.
*   **Format Presets:** Quickly select common format combinations for specific use cases (Social Media Pack, Website Essentials, etc.).
*   **Image Optimization:** Control compression quality and strip metadata (EXIF) for privacy and reduced file sizes.
*   **Multiple Output Types:** Export assets as PNG, JPG, WEBP, and ICO (for favicons).
*   **Bulk Download:** Download all generated assets conveniently in a single zip file.
*   **Keyboard Shortcuts:** Power-user features for faster workflows.
*   **Intelligent Caching:** Improves performance for repeat operations.
*   **Modern UI:** Clean and responsive interface built with Tailwind CSS and Alpine.js.
*   **Containerized:** Easy setup and deployment using Docker and Docker Compose.

---

## Technology Stack

*   **Backend:** Flask (Python)
*   **Image Processing:** Pillow (Python Imaging Library)
*   **Frontend:** Alpine.js, Tailwind CSS
*   **Containerization:** Docker, Docker Compose

---

## Quick Start (Docker Compose)

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/fabriziosalmi/brandkit.git # Replace with your repo URL
    cd brandkit
    ```
2.  **Build and run with Docker Compose:**
    ```sh
    docker-compose up --build -d # Use -d to run in detached mode
    ```
3.  **Open in your browser:**

    Visit [http://localhost:5000](http://localhost:5000)

4.  **Upload an image, select formats/options, and generate your brand kit!**

---

## Usage Guide

1.  **Upload:** Drag and drop an image file (PNG, JPG, GIF, WEBP, max 16MB) onto the upload area, or click to select a file.
2.  **Configure Preprocessing (Optional):** Use the toggles and sliders under "Preprocessing" to apply effects like grayscale, blur, or watermarking to the source image *before* resizing.
3.  **Select Formats:** Check the boxes for the desired output dimensions or use the Format Presets buttons for quick selection of common combinations (e.g., Social Media Pack, Website Essentials).
4.  **Choose Output Types:** Select the file types you need (PNG, JPG, WEBP, ICO). Note: ICO is only generated if the `favicon` format is selected.
5.  **Advanced Options (Optional):** Expand the Advanced Options panel to control image quality and metadata settings.
6.  **Enable Variations (Optional):** Toggle "Generate Color Variations" to create multiple styled versions (Grayscale, Inverted, Hue Shifted, etc.) for *each* selected format.
7.  **Generate:** Click the **Generate Brand Kit** button or use Ctrl+Enter keyboard shortcut.
8.  **Download:**
    *   Download individual assets using the links provided for each generated format/variation.
    *   Download all generated assets in a structured zip file using the "Download All (.zip)" button.

---

## Keyboard Shortcuts

Press `Shift+?` anywhere in the application to view the available keyboard shortcuts:

* `Space` - Open file selector when focused on upload area
* `Ctrl+Enter` or `⌘+Enter` - Generate assets (submit form)
* `Escape` - Reset form or close dialogs
* `Alt+A` - Select all formats
* `Alt+N` - Clear all formats

---

## Configuration (`config.json`)

The `config.json` file defines the available output formats, their dimensions, descriptions, and categories. You can customize this file to add, remove, or modify formats according to your needs.

*   `formats`: Dictionary defining each output format key, width, height, and description.
*   `format_categories`: Groups formats logically for the UI organization.
*   `output_formats`: Lists the file types the application can export to.
*   `preprocessing_options`: Defines default values for the preprocessing UI controls.

---

## File Structure

```
app.py                # Flask backend
config.json           # Format/output config
requirements.txt      # Python dependencies
Dockerfile            # Docker build
entrypoint.sh         # Entrypoint for Docker
static/               # Static files (uploads, css, js)
templates/index.html  # Main UI
```

---

## Development

- Run locally (requires Python 3.11+):
  ```sh
  python3 -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  python app.py
  ```
- App runs at [http://localhost:5000](http://localhost:5000)

---

## Docker Details

- **Build image:**
  ```sh
  docker build -t brandkit .
  ```
- **Run container:**
  ```sh
  docker run -p 5000:5000 -v $(pwd)/static/uploads:/app/static/uploads brandkit
  ```
- **Stop all:**
  ```sh
  docker-compose down
  ```

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
    # Ensure it exposes the port (e.g., 5000) internally
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
    reverse_proxy brandkit:5000 # Proxy requests to the brandkit service on port 5000
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
- If you get permission errors on uploads, ensure `static/uploads` is writable.
- For custom domains/SSL, use a reverse proxy (e.g., Nginx, Caddy).
- For development, set `FLASK_ENV=development` in docker-compose or your shell.

---

## Screenshots

![BrandKit UI Screenshot](https://user-images.githubusercontent.com/your-screenshot.png)

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
