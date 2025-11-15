# Changelog

All notable changes to BrandKit will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive CONTRIBUTING.md with development guidelines
- CHANGELOG.md for tracking project changes
- Improved documentation consistency across all files

### Changed
- Updated port configuration consistency (8000 across all documentation)
- Improved README badges to reflect accurate project status

### Fixed
- Port mismatch between README and Docker configuration
- Placeholder badges in README

## [2.0.0] - 2024

### Added
- 🎯 AI-powered background removal with rembg library
- Multiple AI model selection (Auto, Person/Portrait, Object/Product, Anime/Illustration)
- Background color replacement options (transparent, white, black, gray, custom colors)
- Edge smoothing for professional background removal results
- 15+ advanced preprocessing effects:
  - Grayscale, B&W, Invert, Contrast Enhancement
  - Hue Shift, Temperature, Saturation, Brightness adjustments
  - Auto Crop, Noise Reduction, Sharpen, Quality Enhancement
  - Blur with radius control, Vignette, Drop Shadow effects
  - Watermarking with custom text and opacity
- Smart radial gradient backgrounds based on prominent colors
- Format search functionality
- Recent uploads quick access
- Color variations generation for each format
- Keyboard shortcuts system (Shift+? for help)
- 25+ predefined formats for various use cases
- Format presets (Social Media Pack, Website Essentials, Mobile App Pack, Complete Branding)
- Multiple output types (PNG, JPG, WEBP, ICO)
- Bulk download as organized ZIP files

### Enhanced
- Security features:
  - CSRF protection with Flask-WTF
  - Rate limiting (200/day, 50/hour default)
  - Content Security Policy (CSP) headers
  - Security headers via Flask-Talisman
  - Metadata stripping for privacy
- Performance optimizations:
  - Intelligent caching with Flask-Caching
  - Memory management with psutil monitoring
  - Automatic cleanup of old files
  - Batch operation efficiency
- UI/UX improvements:
  - Modern responsive interface with Tailwind CSS and Alpine.js
  - Real-time processing feedback
  - Visual progress information
  - Format categorization for better organization

### Technology Stack
- Backend: Flask (Python 3.11+)
- AI: rembg library with neural network models
- Image Processing: Pillow, OpenCV, NumPy
- Frontend: Alpine.js, Tailwind CSS
- Security: Flask-WTF, Flask-Limiter, Flask-Talisman
- Performance: Flask-Caching, psutil
- Containerization: Docker, Docker Compose

## [1.0.0] - Initial Release

### Added
- Basic image upload functionality
- Format generation from single source image
- Multiple format support
- Docker containerization
- Basic UI with format selection
- PNG and JPG output formats
- Simple image resizing and padding
- Upload folder management

---

## Version History Notes

### Versioning Scheme
- **Major version** (X.0.0): Breaking changes or major feature additions
- **Minor version** (0.X.0): New features, backward compatible
- **Patch version** (0.0.X): Bug fixes and minor improvements

### Categories
- **Added**: New features
- **Changed**: Changes to existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security improvements or fixes

[Unreleased]: https://github.com/fabriziosalmi/brandkit/compare/v2.0.0...HEAD
[2.0.0]: https://github.com/fabriziosalmi/brandkit/releases/tag/v2.0.0
[1.0.0]: https://github.com/fabriziosalmi/brandkit/releases/tag/v1.0.0
