# Contributing to BrandKit

Thank you for your interest in contributing to BrandKit! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Enhancements](#suggesting-enhancements)

## Code of Conduct

This project adheres to the Contributor Covenant [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to fabrizio.salmi@gmail.com.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/brandkit.git
   cd brandkit
   ```
3. Add the upstream repository:
   ```bash
   git remote add upstream https://github.com/fabriziosalmi/brandkit.git
   ```

## Development Setup

### Prerequisites

- Python 3.11 or higher
- pip (Python package installer)
- Git
- Docker and Docker Compose (optional, for containerized development)

### Local Development Environment

1. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```
   The application will be available at [http://localhost:8000](http://localhost:8000)

### Docker Development Environment

1. **Build and run with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

2. **Access the application:**
   Visit [http://localhost:8000](http://localhost:8000)

## How to Contribute

### Branch Naming Convention

Use descriptive branch names following these patterns:
- `feature/description` - For new features
- `fix/description` - For bug fixes
- `docs/description` - For documentation updates
- `refactor/description` - For code refactoring
- `test/description` - For adding or updating tests

Examples:
- `feature/add-svg-support`
- `fix/memory-leak-in-processing`
- `docs/update-api-reference`

### Commit Message Guidelines

Write clear, concise commit messages:
- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests when applicable

Format:
```
type: Brief description

Longer explanation if necessary. Wrap at 72 characters.

Fixes #123
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

## Pull Request Process

1. **Update your fork:**
   ```bash
   git fetch upstream
   git checkout main
   git merge upstream/main
   ```

2. **Create a new branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes:**
   - Write clear, maintainable code
   - Follow the project's coding standards
   - Add or update tests as necessary
   - Update documentation as needed

4. **Test your changes:**
   ```bash
   # Run the application locally
   python app.py
   
   # Test various workflows manually
   # - Upload images
   # - Generate formats
   # - Test preprocessing options
   # - Verify downloads
   ```

5. **Commit your changes:**
   ```bash
   git add .
   git commit -m "feat: Add your feature description"
   ```

6. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Submit a Pull Request:**
   - Go to the original BrandKit repository on GitHub
   - Click "New Pull Request"
   - Select your fork and branch
   - Fill in the PR template with:
     - Clear description of changes
     - Related issue numbers
     - Screenshots (for UI changes)
     - Testing performed

8. **PR Review Process:**
   - Maintainers will review your PR
   - Address any requested changes
   - Once approved, a maintainer will merge your PR

## Coding Standards

### Python Style Guide

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Use 4 spaces for indentation (not tabs)
- Maximum line length: 120 characters
- Use meaningful variable and function names
- Add docstrings to functions and classes

### Code Quality

- Write self-documenting code
- Add comments for complex logic
- Avoid duplicate code (DRY principle)
- Keep functions focused and concise
- Handle errors gracefully

### Example Function Documentation

```python
def process_image(image, width, height, options):
    """
    Process and resize an image with specified options.
    
    Args:
        image (PIL.Image): The source image to process
        width (int): Target width in pixels
        height (int): Target height in pixels
        options (dict): Processing options including quality, effects, etc.
        
    Returns:
        PIL.Image: The processed image
        
    Raises:
        ValueError: If width or height is invalid
        IOError: If image processing fails
    """
    # Implementation
```

## Testing

### Manual Testing

Before submitting a PR, manually test:

1. **Image Upload:**
   - Test with different formats (PNG, JPG, WEBP, GIF)
   - Test with various file sizes
   - Test with transparent images
   - Test with different aspect ratios

2. **Format Generation:**
   - Test individual format selection
   - Test preset selections
   - Test all output formats (PNG, JPG, WEBP, ICO)

3. **Preprocessing Options:**
   - Test each preprocessing effect
   - Test combinations of effects
   - Test background removal (if available)

4. **Download Functionality:**
   - Test individual file downloads
   - Test ZIP download
   - Verify file names and organization

5. **UI/UX:**
   - Test keyboard shortcuts
   - Test responsive design on different screen sizes
   - Test browser compatibility

### Performance Testing

- Test with large images (close to 16MB limit)
- Test generating many formats simultaneously
- Monitor memory usage during processing
- Check for memory leaks with repeated operations

## Reporting Bugs

When reporting bugs, please use the [Bug Report template](.github/ISSUE_TEMPLATE/bug_report.md) and include:

- **Clear title and description:** What is the issue?
- **Steps to reproduce:** Detailed steps to trigger the bug
- **Expected behavior:** What should happen?
- **Actual behavior:** What actually happens?
- **Environment details:**
  - OS (e.g., Ubuntu 22.04, macOS 13, Windows 11)
  - Python version
  - Browser (if relevant)
  - Docker version (if using Docker)
- **Screenshots:** If applicable
- **Error messages:** Complete error logs or stack traces
- **Sample files:** If the bug is related to specific images

## Suggesting Enhancements

When suggesting enhancements, please use the [Feature Request template](.github/ISSUE_TEMPLATE/feature_request.md) and include:

- **Clear title and description:** What feature do you want?
- **Use case:** Why is this feature needed?
- **Proposed solution:** How should it work?
- **Alternatives considered:** Other approaches you've thought about
- **Additional context:** Screenshots, mockups, or examples

## Project Structure

Understanding the project structure will help you navigate the codebase:

```
brandkit/
├── app.py                      # Main Flask application
├── config.json                 # Format and configuration definitions
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker container configuration
├── docker-compose.yml          # Docker Compose setup
├── entrypoint.sh              # Docker entrypoint script
├── static/
│   └── uploads/               # Upload directory for user files
├── templates/
│   └── index.html             # Main UI template
├── README.md                  # Project documentation
├── CONTRIBUTING.md            # This file
├── CODE_OF_CONDUCT.md         # Community guidelines
├── SECURITY.md                # Security policy
└── KEYBOARD_SHORTCUTS.md      # Keyboard shortcuts reference
```

## Key Components

### Backend (`app.py`)
- Flask application setup and configuration
- Security middleware (CSRF, rate limiting, CSP)
- Image upload and validation
- Image preprocessing and effects
- AI-powered background removal
- Format generation and resizing
- ZIP file creation
- Caching and performance optimization
- Memory management and cleanup

### Configuration (`config.json`)
- Format definitions (dimensions, descriptions)
- Format categories for UI organization
- Supported output formats
- Default preprocessing options

### Frontend (`templates/index.html`)
- Alpine.js for interactivity
- Tailwind CSS for styling
- File upload interface
- Format selection UI
- Preprocessing controls
- Background removal controls
- Download management

## Questions or Need Help?

If you have questions or need help:

1. Check existing [issues](https://github.com/fabriziosalmi/brandkit/issues)
2. Review the [README.md](README.md) documentation
3. Open a new issue with the question label
4. Contact the maintainer: fabrizio.salmi@gmail.com

## License

By contributing to BrandKit, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).

---

Thank you for contributing to BrandKit! Your efforts help make this project better for everyone.
