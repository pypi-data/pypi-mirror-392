# fastapi-sanitizer-example

A configurable FastAPI middleware that sanitizes JSON request/response fields using bleach.

## Quick usage

```python
from fastapi import FastAPI
from fastapi_sanitizer import SanitizerMiddleware

app = FastAPI()

app.add_middleware(
    SanitizerMiddleware,
    allowed_tags=["b", "i", "u"],
    script_allowed_fields=["code_snippet"],
    whitelist_fields=["system_status"],
)

@app.post("/demo")
def demo(data: dict):
    return {"received": data}