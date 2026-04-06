# AetherOS Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.13.x  | :white_check_mark: |
| < 0.13  | :x:                |

We recommend always running the latest stable version to ensure you have the most recent security updates and improvements.

## Reporting a Vulnerability

We take the security of AetherOS seriously. If you believe you've found a security vulnerability, please follow these guidelines:

### **DO NOT** disclose the vulnerability publicly until we've had a chance to address it.

### How to Report

1. **Email**: Send details to security@aetheros.dev (when available) or open a private GitHub Security Advisory
2. **Include**:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)
   - Your contact information for follow-up

### What to Expect

- **Initial Response**: Within 48 hours of your report
- **Status Updates**: Every 7 days while we investigate
- **Resolution Timeline**: Depends on severity (see below)

## Severity Levels

| Severity | Description | Target Resolution |
|----------|-------------|-------------------|
| Critical | Remote code execution, authentication bypass, data breach | 7 days |
| High     | Privilege escalation, sensitive data exposure | 14 days |
| Medium   | CSRF, XSS, information disclosure | 30 days |
| Low      | Minor issues with limited impact | 60 days |

## Security Best Practices for Users

### Installation

- Always download from official sources (GitHub releases or verified packages)
- Verify checksums when provided
- Run installation scripts with appropriate permissions only

### Configuration

- **Never commit secrets**: Keep API keys, passwords, and tokens out of version control
- **Use environment variables**: Store sensitive configuration in `.env` files (gitignored)
- **Restrict network access**: Bind services to localhost unless external access is required
- **Enable authentication**: Don't run the API server without proper authentication in production

### Operation

- **Regular updates**: Keep AetherOS updated to the latest version
- **Monitor logs**: Check `logs/` directory for unusual activity
- **Backup data**: Regularly backup the `data/` directory
- **Limit permissions**: Run with minimal required system permissions

### Memory & Data

- **Encrypt at rest**: Consider encrypting the data directory for sensitive deployments
- **Clear sensitive data**: Use `bin/aether memory --clear` to remove sensitive memories
- **Review entities**: Periodically audit stored entities with `bin/aether memory --entities`

## Security Features

### Built-in Protections

- **Input validation**: All user inputs are sanitized before processing
- **Path traversal prevention**: File operations are restricted to allowed directories
- **Command injection protection**: Shell commands use safe execution methods
- **Memory isolation**: Agent memory spaces are separated

### Governance System

The governance module (`bin/aether governance`) provides:
- Policy enforcement
- Access control profiles
- Audit logging
- Compliance checking

## Known Limitations

- Desktop integration requires trust in the local user session
- Vector database is not encrypted by default
- API authentication is optional in development mode (enable for production)

## Incident Response Process

1. **Detection**: Vulnerability reported or discovered
2. **Triage**: Assess severity and impact
3. **Fix Development**: Create and test patch
4. **Release**: Publish security update
5. **Disclosure**: Public advisory after users have time to update
6. **Post-mortem**: Internal review to prevent recurrence

## Security Updates

Security updates are released as:
- **Patch versions** (0.13.1, 0.13.2, etc.) for critical/high severity
- **Minor versions** (0.14.0, 0.15.0, etc.) for medium/low severity

Subscribe to GitHub release notifications to stay informed.

## For Developers

### Contributing Secure Code

- Follow secure coding practices
- Validate all inputs
- Use parameterized queries (where applicable)
- Implement proper error handling (no sensitive info in errors)
- Write tests for security-critical code

### Code Review Focus Areas

- Authentication and authorization logic
- Data validation and sanitization
- Cryptographic implementations
- Network communication
- File system operations

## Contact

For security-related questions or concerns:
- GitHub Security Advisories (preferred)
- Email: security@aetheros.dev (future)

---

**Remember**: Responsible disclosure helps protect all users. Thank you for helping keep AetherOS secure!
