# BrandKit Generator

BrandKit is a web app for generating brand assets in multiple formats and sizes from a single image. It uses Flask, Pillow, and Alpine.js, and is fully containerized for easy deployment.

---

## Features
- Upload a single image (PNG, JPG, GIF, WEBP)
- Generate assets in many formats (e.g., 1024x1024, banners, favicons, social, etc.)
- Smart background fill for non-square outputs from square uploads
- Prominent color extraction and intelligent rendering
- Download all assets as a zip
- Modern UI (Tailwind CSS, Alpine.js)
- Docker & docker-compose support

---

## Quick Start (Docker Compose)

1. **Clone the repository:**
   ```sh
git clone <your-repo-url>
cd brandkit
   ```
2. **Build and run with Docker Compose:**
   ```sh
docker-compose up --build
   ```
3. **Open in your browser:**
   
   Visit [http://localhost:5000](http://localhost:5000)

4. **Upload an image and generate your brand kit!**

---

## Example Usage

### Upload and Generate
1. Drag & drop or select an image file (PNG, JPG, GIF, WEBP, max 16MB).
2. Choose the formats you want (defaults to 1024x1024, but you can select more).
3. Choose output file types (defaults to PNG and ICO).
4. Click **Generate Brand Kit**.
5. Download individual assets or the full zip.

### Customization
- Preprocessing: grayscale, B&W, invert, blur, hue shift, temperature, watermark, etc.
- Variations: generate color/contrast variations automatically.
- Smart background: square uploads get a beautiful gradient fill for non-square outputs.

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
