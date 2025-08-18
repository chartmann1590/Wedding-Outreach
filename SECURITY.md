# Security Policy

## Supported Versions

We actively support and provide security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Security Model

### Data Privacy
- **Local Storage Only**: All guest data is stored locally in your database
- **No External APIs**: Facebook integration uses deep links only, no API calls
- **No Data Transmission**: Guest information never leaves your server
- **No Tracking**: No analytics or tracking mechanisms implemented

### Authentication & Authorization
- **Single-User Design**: Currently designed for single-user/family use
- **No Built-in Auth**: Authentication not implemented (intended for private deployment)
- **Session Management**: Uses Flask sessions with secure cookies in production

### Data Protection
- **Database Encryption**: SQLite database stored locally
- **HTTPS Recommended**: Use reverse proxy (nginx/Apache) with SSL in production
- **Secret Key**: Application uses SECRET_KEY for session security
- **Input Validation**: All user inputs are validated and sanitized

## Security Best Practices

### Production Deployment

#### 1. Environment Security
```bash
# Use strong secret key
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"

# Production environment
export FLASK_ENV=production
export DEBUG=false

# Secure database URL
export DATABASE_URL=postgresql://secure_user:strong_password@localhost/wedding_db
```

#### 2. Web Server Configuration
- **Use HTTPS**: Configure SSL/TLS certificates
- **Reverse Proxy**: Deploy behind nginx or Apache
- **Firewall**: Restrict access to necessary ports only
- **Rate Limiting**: Implement request rate limiting

#### 3. Database Security
- **Strong Passwords**: Use complex database passwords
- **User Permissions**: Create dedicated database user with minimal permissions
- **Backups**: Encrypt database backups
- **Access Control**: Restrict database access to application only

#### 4. Container Security (Docker)
```yaml
# docker-compose.yml security considerations
services:
  app:
    # Don't run as root
    user: "1000:1000"
    
    # Read-only root filesystem
    read_only: true
    
    # Temporary filesystem for uploads
    tmpfs:
      - /tmp
    
    # Security options
    security_opt:
      - no-new-privileges:true
    
    # Capability restrictions
    cap_drop:
      - ALL
    cap_add:
      - CHOWN
      - SETGID
      - SETUID
```

### Development Security

#### 1. Dependencies
- **Regular Updates**: Keep all dependencies updated
- **Vulnerability Scanning**: Use `pip audit` to check for known vulnerabilities
- **Minimal Dependencies**: Only include necessary packages

#### 2. Code Security
- **Input Validation**: All user inputs validated
- **SQL Injection Prevention**: Use SQLAlchemy ORM (no raw SQL)
- **XSS Prevention**: Templates auto-escape user content
- **CSRF Protection**: Consider enabling for production

#### 3. File Handling
- **Upload Validation**: CSV files validated before processing
- **Path Sanitization**: File paths sanitized to prevent directory traversal
- **Size Limits**: File upload size limits enforced

## Potential Security Considerations

### Current Limitations
1. **No Authentication**: Application assumes trusted environment
2. **Single User**: Not designed for multi-tenant use
3. **Local Network**: Intended for private/local network deployment
4. **CSV Processing**: File uploads processed without sandboxing

### Risk Assessment
- **Low Risk**: Personal/family use on private networks
- **Medium Risk**: Deployment on shared hosting
- **High Risk**: Public internet exposure without authentication

### Mitigation Strategies

#### For Shared Environments
1. **Add Authentication**: Implement basic auth or OAuth
2. **Network Segmentation**: Deploy on private network/VPN
3. **Access Control**: Use web server authentication
4. **Monitoring**: Implement access logging

#### For Public Deployment
1. **Strong Authentication**: Multi-factor authentication recommended
2. **Rate Limiting**: Prevent abuse and DoS attacks
3. **Security Headers**: Implement comprehensive security headers
4. **Regular Audits**: Periodic security assessments

## Reporting Security Vulnerabilities

### How to Report
If you discover a security vulnerability, please report it responsibly:

1. **Email**: Send details to [your-security-email]
2. **Private Repository**: Create a private repository with details
3. **GitHub Security**: Use GitHub's security advisory feature
4. **Do Not**: Create public issues for security vulnerabilities

### What to Include
- Description of the vulnerability
- Steps to reproduce
- Potential impact assessment
- Suggested fix (if known)

### Response Timeline
- **Initial Response**: Within 48 hours
- **Assessment**: Within 7 days
- **Fix Development**: Varies by severity
- **Public Disclosure**: After fix is available

## Security Checklist

### Pre-Deployment
- [ ] Strong SECRET_KEY generated
- [ ] FLASK_ENV=production set
- [ ] DEBUG=false configured
- [ ] Database secured with strong credentials
- [ ] SSL/TLS certificates configured
- [ ] Firewall rules configured
- [ ] Access logging enabled

### Ongoing Maintenance
- [ ] Regular dependency updates
- [ ] Security scanning with `pip audit`
- [ ] Database backup encryption
- [ ] Log monitoring and rotation
- [ ] Access review and audit

### Incident Response
- [ ] Backup and recovery procedures tested
- [ ] Incident response plan documented
- [ ] Contact information updated
- [ ] Rollback procedures documented

## Security Resources

### Tools and Services
- **Dependency Scanning**: `pip audit`, Snyk, GitHub Dependabot
- **Container Scanning**: Docker Scout, Clair, Trivy
- **SSL Testing**: SSL Labs, testssl.sh
- **Security Headers**: securityheaders.com

### References
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security Guide](https://flask.palletsprojects.com/en/2.0.x/security/)
- [Python Security Best Practices](https://python.org/dev/security/)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)

## Updates and Changes

This security policy is reviewed quarterly and updated as needed. Check back regularly for the latest security guidelines and best practices.

**Last Updated**: August 2024
**Next Review**: November 2024