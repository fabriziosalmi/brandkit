# Security Policy

## Supported Versions

We actively support the latest version of BrandKit with security updates.

| Version | Supported          |
| ------- | ------------------ |
| latest  | :white_check_mark: |
| < 2.0   | :x:                |

## Security Features

BrandKit includes comprehensive security measures:

### Built-in Security
- **CSRF Protection**: Cross-Site Request Forgery protection via Flask-WTF
- **Rate Limiting**: Protection against abuse (200 requests/day, 50 requests/hour default)
- **Content Security Policy (CSP)**: Protection against XSS and other web vulnerabilities
- **Security Headers**: Comprehensive HTTP security headers via Flask-Talisman
- **Input Validation**: Thorough validation of file uploads and user inputs
- **Metadata Stripping**: Optional removal of EXIF data for privacy
- **Memory Safety**: Protection against memory exhaustion attacks
- **Secure File Handling**: Validated file extensions and safe file processing

### Deployment Security Recommendations

1. **Use HTTPS**: Always deploy behind a reverse proxy (Nginx, Caddy) with SSL/TLS
2. **Environment Variables**: Use environment variables for sensitive configuration
3. **Update Dependencies**: Regularly update Python packages: `pip install -r requirements.txt --upgrade`
4. **Container Security**: Keep Docker images updated
5. **Access Control**: Implement authentication for production deployments (e.g., Cloudflare Access)
6. **File Size Limits**: Configure appropriate upload limits via `BRANDKIT_MAX_UPLOAD_MB`
7. **Network Isolation**: Use Docker networks or firewalls to restrict access

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability, please follow these steps:

### How to Report

1. **DO NOT** open a public GitHub issue for security vulnerabilities
2. **Email** the maintainer directly at: **fabrizio.salmi@gmail.com**
3. **Include** the following information:
   - Description of the vulnerability
   - Steps to reproduce the issue
   - Potential impact
   - Suggested fix (if any)
   - Your contact information

### What to Expect

- **Acknowledgment**: Within 48 hours of your report
- **Initial Assessment**: Within 5 business days
- **Progress Updates**: Every 7 days until resolved
- **Resolution**: We aim to fix critical vulnerabilities within 30 days
- **Credit**: We'll acknowledge your contribution (unless you prefer to remain anonymous)

### Response Process

1. We will confirm receipt of your vulnerability report
2. We will investigate and assess the severity
3. We will develop and test a fix
4. We will release a security update
5. We will publicly disclose the vulnerability (with your consent on timing)

### Vulnerability Severity Levels

- **Critical**: Remote code execution, authentication bypass
- **High**: Data exposure, privilege escalation
- **Medium**: XSS, CSRF (not covered by existing protections)
- **Low**: Information disclosure, minor issues

## Security Best Practices for Users

### For Deployment
- Always use the latest version
- Enable all security features
- Use strong, unique secrets for `FLASK_SECRET_KEY`
- Implement proper access controls
- Monitor logs for suspicious activity
- Use container security scanning
- Restrict network access to necessary ports only

### For Development
- Never commit secrets or credentials to version control
- Use `.env` files for local configuration (add to `.gitignore`)
- Keep dependencies updated
- Review code changes for security implications
- Test security features before deploying

### File Upload Security
- Only upload images from trusted sources
- Be aware that uploaded images may contain metadata
- Use the metadata stripping option for privacy-sensitive content
- Implement additional access controls if needed for your use case

## Known Limitations

- The application is designed for internal/trusted use cases
- For public-facing deployments, additional authentication is strongly recommended
- File uploads are not virus-scanned (implement separately if needed)
- Processing user-uploaded images carries inherent risks

## Security Updates

Security updates will be released as needed and announced via:
- GitHub Security Advisories
- Repository README
- CHANGELOG.md

Subscribe to repository notifications to stay informed.

## Disclosure Policy

- We follow responsible disclosure practices
- We will coordinate with reporters on disclosure timing
- We aim for public disclosure within 90 days of a fix
- We will credit security researchers (with permission)

## Contact

For security concerns: **fabrizio.salmi@gmail.com**

For general issues: [GitHub Issues](https://github.com/fabriziosalmi/brandkit/issues)

---

**Thank you for helping keep BrandKit secure!**
