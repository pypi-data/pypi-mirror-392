from fastapi_sanitizer.sanitizer import sanitize_input

def test_basic_strip():
    cfg = {"allowed_tags": ["b"], "whitelist_fields": [], "script_allowed_fields": []}
    data = {"name": "<b>ok</b><script>alert(1)</script>"}
    out = sanitize_input(data, cfg)
    assert out["name"] == "<b>ok</b>alert(1)"
