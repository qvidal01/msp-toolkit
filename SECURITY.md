# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to: security@aiqso.io

You should receive a response within 48 hours. If for some reason you do not, please follow up via email to ensure we received your original message.

Please include the following information:

- Type of issue (e.g., buffer overflow, SQL injection, cross-site scripting, etc.)
- Full paths of source file(s) related to the manifestation of the issue
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

## Security Best Practices

When using MSP Toolkit:

- **Never commit credentials** to version control
- **Use environment variables** for sensitive configuration
- **Enable encryption** for data at rest
- **Use HTTPS** for all API communications
- **Rotate credentials** regularly
- **Keep dependencies updated** (`pip install --upgrade`)
- **Review logs** for suspicious activity
- **Limit access** using principle of least privilege

## Security Features

MSP Toolkit includes:

- Secure credential management via OS keyring
- Input validation and sanitization
- Log sanitization (credential masking)
- Rate limiting
- Audit logging
- Type-safe data models (Pydantic)

## Disclosure Policy

When we receive a security bug report, we will:

1. Confirm the problem and determine affected versions
2. Audit code to find similar problems
3. Prepare fixes for all supported versions
4. Release patched versions as soon as possible

Thank you for helping keep MSP Toolkit secure!
