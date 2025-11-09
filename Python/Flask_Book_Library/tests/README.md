# XSS Protection Tests

## Running Tests

```bash
# Run all tests
python run_tests.py

# Or with pytest
python -m pytest tests/test_xss_protection.py -v
```

## What's Tested

### XSS Attack Vectors
- `<script>alert('XSS')</script>` - Script injection
- `<img src=x onerror="alert(1)">` - Event handler injection
- `<svg/onload=alert(1)>` - SVG-based XSS
- `<iframe src="evil.com">` - IFrame injection

### Protection Mechanisms
- Input escaping with `markupsafe.escape()`
- CSP headers configured
- SQL injection prevention
- Safe JSON output

## Expected Result
All tests should **PASS** 

