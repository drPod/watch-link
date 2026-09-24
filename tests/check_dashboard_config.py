import json
import sys
from typing import Any


def redirects(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [item for child in value for item in redirects(child)]
    if isinstance(value, dict):
        own = [value] if value.get("handler") == "static_response" else []
        return own + [item for child in value.values() for item in redirects(child)]
    return []


config = json.load(sys.stdin)
assert any(r.get("status_code") == 303 and r.get("headers", {}).get("Location") == ["/"] for r in redirects(config))
print("Caddy adaptation: private access redirects to dashboard with HTTP 303")
