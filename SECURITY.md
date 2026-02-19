# Security Guidelines for Fitness MCP Servers

Security best practices for the Garmin and MyFitnessPal MCP servers, based on OWASP MCP Top 10, CIS Controls, and Python security standards.

## Table of Contents

- [Critical MCP Security Controls](#critical-mcp-security-controls)
- [Authentication & Secrets](#authentication--secrets)
- [Input Validation](#input-validation)
- [Python Security](#python-security)
- [Dependencies & Supply Chain](#dependencies--supply-chain)
- [Logging & Monitoring](#logging--monitoring)
- [Deployment Security](#deployment-security)
- [Security Checklist](#security-checklist)

---

## Critical MCP Security Controls

Based on [OWASP MCP Top 10](https://owasp.org/www-project-mcp-top-10/).

### MCP01: Secret Exposure

**Controls:**
- ✅ NEVER hardcode credentials - use environment variables only
- ✅ Load `GARMIN_EMAIL`, `GARMIN_PASSWORD`, `MFP_COOKIE_PATH` from env
- ✅ Never log, print, or return credentials in errors
- ✅ Set token/cookie file permissions to 0600
- ✅ Add credential files to `.gitignore`
- ✅ Rotate credentials quarterly

```python
import os

# CORRECT
garmin_email = os.environ.get("GARMIN_EMAIL")
if not garmin_email:
    raise ValueError("GARMIN_EMAIL not set")

# NEVER DO THIS
# garmin_email = "user@example.com"
```

### MCP04: Supply Chain Attacks

**Controls:**
- ✅ Pin all dependencies to exact versions
- ✅ Run `pip-audit` regularly
- ✅ Monitor security advisories for `garminconnect`, `myfitnesspal`, `mcp`
- ✅ Review changelogs before updating dependencies

```bash
# Scan for vulnerabilities
pip install pip-audit
pip-audit
```

### MCP05: Command Injection

**Controls:**
- ✅ NEVER use `shell=True`, `eval()`, `exec()`, or `compile()`
- ✅ Validate all date parameters match ISO 8601 format
- ✅ Use allowlists for acceptable inputs

```python
import re
from datetime import datetime

def validate_date(date_str: str) -> str:
    """Validate ISO 8601 date (YYYY-MM-DD)."""
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        raise ValueError(f"Invalid date format: {date_str}")
    datetime.fromisoformat(date_str)  # Verify parseable
    return date_str
```

### MCP06: Prompt Injection

**Controls:**
- ✅ Return structured JSON, not natural language
- ✅ Sanitize text from external APIs (food names, activity descriptions)
- ✅ Validate data types before returning to model

### MCP08: Insufficient Logging

**Controls:**
- ✅ Log all tool invocations with parameters (excluding credentials)
- ✅ Log authentication attempts and failures
- ✅ Use structured JSON logging
- ✅ Implement log rotation

```python
import logging
import json

logger = logging.getLogger(__name__)

def log_tool_call(tool: str, args: dict, success: bool):
    """Log tool invocation with sanitized parameters."""
    safe_args = {k: v for k, v in args.items()
                 if k not in ['password', 'token', 'cookie']}
    logger.info(json.dumps({
        'event': 'tool_call',
        'tool': tool,
        'args': safe_args,
        'success': success
    }))
```

---

## Authentication & Secrets

### Garmin Authentication

```python
import os
from garminconnect import Garmin

def get_garmin_client():
    email = os.environ.get("GARMIN_EMAIL")
    password = os.environ.get("GARMIN_PASSWORD")

    if not email or not password:
        raise ValueError("Set GARMIN_EMAIL and GARMIN_PASSWORD")

    try:
        client = Garmin(email, password)
        client.login()
        return client
    except Exception as e:
        # Don't expose credentials in errors
        raise ValueError(f"Auth failed: {type(e).__name__}") from e
```

**Security:**
- Tokens in `~/.garminconnect` must be 0600 permissions
- Library handles token refresh automatically

### MyFitnessPal Authentication

```python
import os

def get_mfp_client():
    cookie_path = os.environ.get("MFP_COOKIE_PATH")

    if not cookie_path or not os.path.exists(cookie_path):
        raise ValueError("Set MFP_COOKIE_PATH to valid file")

    # Verify secure permissions
    if os.stat(cookie_path).st_mode & 0o077:
        raise ValueError(f"Insecure permissions. Run: chmod 600 {cookie_path}")

    # Load and use cookies
    # ...
```

**Security:**
- Cookie file must be 0600 permissions
- Store outside project directory
- Never commit to version control

### .gitignore Requirements

```gitignore
# Credentials
.env
.env.*
*.env

# Tokens & cookies
.garminconnect/
*cookies*.txt
*session*.txt

# Python
__pycache__/
*.pyc
venv/
```

---

## Input Validation

Validate all inputs using allowlists, not blocklists.

```python
import re
from datetime import datetime
from typing import Tuple

def validate_date_range(start: str, end: str) -> Tuple[str, str]:
    """Validate ISO 8601 date range."""
    pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')

    if not pattern.match(start) or not pattern.match(end):
        raise ValueError("Dates must be YYYY-MM-DD format")

    start_dt = datetime.fromisoformat(start)
    end_dt = datetime.fromisoformat(end)

    if start_dt > end_dt:
        raise ValueError("start_date must be <= end_date")

    if (end_dt - start_dt).days > 365:
        raise ValueError("Date range exceeds 365 days")

    return start, end
```

**Principles:**
1. Define what is acceptable, not what is forbidden
2. Validate type, format, and business logic
3. Fail fast with clear errors
4. Never expose internals in error messages

---

## Python Security

Based on [OpenSSF Python Guide](https://best.openssf.org/Secure-Coding-Guide-for-Python/).

### Forbidden Functions

**NEVER use:**
```python
eval()              # Code execution
exec()              # Code execution
compile()           # Code execution
subprocess.run(..., shell=True)  # Command injection
os.system()         # Command injection
pickle.load()       # Deserialization on untrusted data
yaml.load()         # Use yaml.safe_load() instead
```

### Exception Handling

Don't expose sensitive details:

```python
# INCORRECT
try:
    client.login()
except Exception as e:
    return f"Error: {e}"  # May expose credentials

# CORRECT
try:
    client.login()
except Exception as e:
    logger.error(f"Login failed: {type(e).__name__}", exc_info=True)
    return "Authentication failed. Check credentials."
```

### Type Hints

Use type hints to prevent type confusion:

```python
from typing import List, Dict

def get_activities(start: str, end: str) -> List[Dict[str, any]]:
    """Type-checked function signature."""
    start, end = validate_date_range(start, end)
    return client.get_activities(start, end)
```

---

## Dependencies & Supply Chain

Based on [CIS Control 16](https://www.cisecurity.org/controls/application-software-security).

### Pin Exact Versions

```txt
# requirements.txt
mcp==1.0.0
garminconnect==0.2.0
myfitnesspal==1.16.5

# NOT this:
# mcp>=1.0.0
```

### Security Scanning

```bash
# Install tools
pip install pip-audit bandit

# Scan dependencies
pip-audit

# Scan code
bandit -r . -ll

# Check for outdated packages
pip list --outdated
```

### CI/CD Integration

```yaml
# .github/workflows/security.yml
name: Security
on: [push, pull_request]
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install -r requirements.txt
      - run: pip install pip-audit bandit
      - run: pip-audit
      - run: bandit -r . -ll
```

### Update Process

Before updating any dependency:
1. Review changelog and CVE database
2. Test in isolated environment
3. Run full test suite
4. Document reason in commit

---

## Logging & Monitoring

### What to Log

**Always log:**
- Server startup/shutdown
- Authentication attempts
- Tool invocations (sanitized parameters)
- Input validation failures
- Errors and exceptions

**Never log:**
- Passwords, tokens, cookies, API keys
- Health data (unless retention policy defined)

### Structured Logging

```python
from logging.handlers import RotatingFileHandler
import logging

handler = RotatingFileHandler(
    'mcp-server.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[handler, logging.StreamHandler()]
)
```

### Monitoring Alerts

For production, alert on:
- Failed auth attempts (>3 in 5 minutes)
- Error rate spikes
- Dependency vulnerabilities

---

## Deployment Security

### Pre-Deployment Checklist

- [ ] Dependencies scanned with `pip-audit`
- [ ] Code scanned with `bandit` (no high-severity)
- [ ] No hardcoded credentials
- [ ] `.gitignore` configured
- [ ] File permissions: 0600 for credentials
- [ ] Logging configured
- [ ] Input validation implemented
- [ ] Error messages sanitized

### File Permissions

```bash
# Secure credential files
chmod 600 ~/.garminconnect/*
chmod 600 /path/to/mfp-cookies.txt

# Verify
ls -la ~/.garminconnect
```

### Environment Isolation

```bash
# Use virtual environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Verify isolation
which python  # Should be venv/bin/python
```

### Network Security

**stdio transport (local use):**
- No network exposure needed
- Communication over stdin/stdout only

**HTTP transport (production):**
- Use TLS 1.3
- Implement OAuth 2.1 ([MCP Auth](https://mcp-auth.dev/docs))
- Deploy behind reverse proxy
- Enable rate limiting

---

## Security Checklist

### Development
- [ ] No hardcoded credentials
- [ ] Environment variables for all secrets
- [ ] Input validation on all parameters
- [ ] No dangerous functions (eval, shell=True, etc.)
- [ ] Type hints used
- [ ] Errors don't expose internals
- [ ] Dependencies pinned
- [ ] `.gitignore` configured

### Testing
- [ ] `pip-audit` passes
- [ ] `bandit -r . -ll` passes
- [ ] Auth failure handling tested
- [ ] Invalid input handling tested
- [ ] Logs don't contain credentials

### Deployment
- [ ] Absolute paths in MCP config
- [ ] Environment variables configured
- [ ] File permissions: 0600
- [ ] Logging enabled
- [ ] Non-root user account
- [ ] Security docs in README

### Maintenance
- [ ] Monitor security advisories
- [ ] Run `pip-audit` monthly
- [ ] Review logs for suspicious activity
- [ ] Rotate credentials quarterly
- [ ] Update on security patches

---

## Project-Specific Risks

### Garmin
- **Risk:** Unofficial library, no security SLA
- **Mitigation:** Monitor GitHub issues, consider forking if needed

### MyFitnessPal
- **Risk:** Cookie scraping fragile, could break anytime
- **Mitigation:** Isolated server, graceful failure handling, rate limiting

### Health Data Privacy
- **Data:** Heart rate, sleep, nutrition, weight
- **Controls:** No persistent storage, no third-party sharing, encrypted logs

---

## References

### MCP Security
- [OWASP MCP Top 10](https://owasp.org/www-project-mcp-top-10/)
- [MCP Auth](https://mcp-auth.dev/docs)
- [MCP Security Best Practices (TrueFoundry)](https://www.truefoundry.com/blog/mcp-server-security-best-practices)

### Python Security
- [OpenSSF Secure Coding for Python](https://best.openssf.org/Secure-Coding-Guide-for-Python/)
- [Python & OWASP Top 10 (Qwiet)](https://qwiet.ai/appsec-resources/python-and-owasp-top-10-a-developers-guide/)

### Standards
- [CIS Control 16: Application Security](https://www.cisecurity.org/controls/application-software-security)
- [CIS API Security Guide](https://www.cisecurity.org/insights/white-papers/cis-api-security-guide-v1-0-0)

### Tools
- [pip-audit](https://github.com/pypa/pip-audit) - Dependency scanner
- [Bandit](https://github.com/PyCQA/bandit) - Python security linter

---

**Version:** 1.0
**Last Updated:** 2026-02-19
**Review:** Quarterly or after security incidents
