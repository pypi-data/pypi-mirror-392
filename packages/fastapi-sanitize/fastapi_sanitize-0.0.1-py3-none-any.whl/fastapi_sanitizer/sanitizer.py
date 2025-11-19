# fastapi_sanitizer/sanitizer.py
import bleach

def sanitize_value(key, value, config):
    """
    Sanitize a single value according to config.
    config: {
      "allowed_tags": [...],
      "script_allowed_fields": [...],
      "whitelist_fields": [...],
    }
    """
    whitelist_fields = set(config.get("whitelist_fields", []))
    script_allowed_fields = set(config.get("script_allowed_fields", []))
    allowed_tags = config.get("allowed_tags", [])

    if key in whitelist_fields:
        return value
    if key in script_allowed_fields:
        return value
    if isinstance(value, str):
        return bleach.clean(value, tags=allowed_tags, strip=True)
    return value


def sanitize_input(data: dict, config: dict):
    clean = {}
    for k, v in data.items():
        clean[k] = sanitize_value(k, v, config)
    return clean


def sanitize_output(data: dict, config: dict):
    # same as input for now (you can customize later)
    return sanitize_input(data, config)
