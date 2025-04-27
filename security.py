import re
import logging

logger = logging.getLogger(__name__)

def detect_sql_injection(text):
    if not isinstance(text, str):
        return False

    #SQL injection patterns
    sql_patterns = [
        r"(\b|')(\s*)(SELECT|INSERT|UPDATE|DELETE|DROP|ALTER|UNION|CREATE|EXEC)(\s+)",
        r"(\b|')--",
        r"(\b|')\s*OR\s+1\s*=\s*1",
        r"(\b|')\s*;\s*--",
        r"(\b|')\s*;\s*DROP",
    ]

    text_lower = text.lower()
    for pattern in sql_patterns:
        if re.search(pattern, text_lower, re.IGNORECASE):
            logger.warning(f"Potential SQL injection detected: {text}")
            return True

    return False


def sanitize_input(text):
    if not isinstance(text, str):
        return text

    #escape common SQL injection characters
    return text.replace("'", "''").replace(";", "")


def detect_xss(text):
    if not isinstance(text, str):
        return False

    #basic XSS patterns
    xss_patterns = [
        r'<script[^>]*>',
        r'javascript:',
        r'on\w+\s*=',
        r'<iframe',
        r'document\.cookie',
        r'eval\(',
    ]

    for pattern in xss_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            logger.warning(f"Potential XSS attack detected: {text}")
            return True

    return False


def sanitize_html(text):
    if not isinstance(text, str):
        return text

    #replace HTML special characters
    replacements = {
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;',
        '&': '&amp;'
    }

    for char, replacement in replacements.items():
        text = text.replace(char, replacement)

    return text


if __name__ == "__main__":
    # Test SQL injection detection
    sql_tests = [
        "SELECT * FROM users",
        "admin' OR 1=1 --",
        "regular text",
        "1; DROP TABLE users",
        "event'; DROP TABLE users; --"
    ]

    print("TESTING SQL INJECTION DETECTION:")
    for test in sql_tests:
        result = detect_sql_injection(test)
        print(f"'{test}': {'DETECTED' if result else 'safe'}")

        # Also test sanitization
        sanitized = sanitize_input(test)
        print(f"  Sanitized: '{sanitized}'")

    print("\nTESTING XSS DETECTION:")
    xss_tests = [
        "<script>alert('hack')</script>",
        "javascript:alert(document.cookie)",
        "regular text",
        "<img src=x onerror=alert(1)>",
        "event<script>document.cookie</script>"
    ]

    for test in xss_tests:
        result = detect_xss(test)
        print(f"'{test}': {'DETECTED' if result else 'safe'}")

        # Also test sanitization
        sanitized = sanitize_html(test)
        print(f"  Sanitized: '{sanitized}'")