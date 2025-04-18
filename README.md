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
*   **Multiple Output Types:** Export assets as PNG, JPG, WEBP, and ICO (for favicons).
*   **Bulk Download:** Download all generated assets conveniently in a single zip file.
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
    git clone https://github.com/your-username/brandkit.git # Replace with your repo URL
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
3.  **Select Formats:** Check the boxes for the desired output dimensions (e.g., `website`, `social`, `favicon`). Descriptions are provided for context. Use "Select All" / "Clear All" for convenience.
4.  **Choose Output Types:** Select the file types you need (PNG, JPG, WEBP, ICO). Note: ICO is only generated if the `favicon` format is selected.
5.  **Enable Variations (Optional):** Toggle "Generate Color Variations" to create multiple styled versions (Grayscale, Inverted, Hue Shifted, etc.) for *each* selected format.
6.  **Generate:** Click the **Generate Brand Kit** button.
7.  **Download:**
    *   Download individual assets using the links provided for each generated format/variation.
    *   Download all generated assets in a structured zip file using the "Download All (.zip)" button.

---

## Configuration (`config.json`)

The `config.json` file defines the available output formats, their dimensions, descriptions, and categories. You can customize this file to add, remove, or modify formats according to your needs.

*   `formats`: Dictionary defining each output format key, width, height, and description.
*   `format_categories`: Groups formats logically for potential UI improvements (currently informational).
*   `output_formats`: Lists the file types the application can export to.
*   `preprocessing_options`: Defines default values for the preprocessing UI controls (currently not dynamically used for defaults in the UI, but planned).

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

## Troubleshooting
- If you get permission errors on uploads, ensure `static/uploads` is writable.
- For custom domains/SSL, use a reverse proxy (e.g., Nginx, Caddy).
- For development, set `FLASK_ENV=development` in docker-compose or your shell.

---

## License
MIT

---

## Credits
- [Flask](https://flask.palletsprojects.com/)
- [Pillow](https://python-pillow.org/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Alpine.js](https://alpinejs.dev/)

---

## Screenshots

![BrandKit UI Screenshot](https://user-images.githubusercontent.com/your-screenshot.png)

---

## Feedback & Contributions

PRs and issues welcome! For feature requests or bug reports, please open an issue.
