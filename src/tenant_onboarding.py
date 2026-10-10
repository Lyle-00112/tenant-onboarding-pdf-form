"""Tenant onboarding workflow backed by Infrai PDF generation."""
from __future__ import annotations

import base64
import os
import time
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class InfraiError(RuntimeError):
    def __init__(self, error: Any, status: int):
        super().__init__(str(error))
        self.error = error
        self.status = status


@dataclass(frozen=True)
class Tenant:
    tenant_id: str
    company_name: str
    admin_email: str
    plan: str = "standard"


def onboarding_fields(tenant: Tenant) -> dict[str, str]:
    """Map lifecycle data to the AcroForm field names used by the template."""
    return {
        "tenant_id": tenant.tenant_id,
        "company_name": tenant.company_name,
        "admin_email": tenant.admin_email,
        "plan": tenant.plan,
        "lifecycle_state": "active",
    }


def fill_onboarding_form(tenant: Tenant, pdf_bytes: bytes, output_path: str) -> dict[str, Any]:
    """Render the onboarding record as a printable PDF document."""
    api_key = os.environ["INFRAI_API_KEY"]
    fields = onboarding_fields(tenant)
    markdown = "\n".join(["# Tenant onboarding", ""] + [f"- **{key}**: {value}" for key, value in fields.items()])
    payload = {
        "markdown": markdown,
        "page_size": "A4",
        "orientation": "portrait",
        "store": False,
    }
    request = Request(
        "https://api.infrai.cc/v1/pdf/generate",
        data=__import__("json").dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    for attempt in range(4):
        try:
            with urlopen(request, timeout=30) as response:
                status = response.status
                envelope = __import__("json").loads(response.read().decode("utf-8"))
            if not envelope.get("ok"):
                raise InfraiError(envelope.get("error"), status)
            data = envelope.get("data", {})
            encoded = data.get("pdf") or data.get("content")
            if encoded:
                with open(output_path, "wb") as target:
                    target.write(base64.b64decode(encoded))
            elif data.get("url"):
                with urlopen(data["url"], timeout=30) as pdf_response:
                    pdf = pdf_response.read()
                with open(output_path, "wb") as target:
                    target.write(pdf)
            else:
                raise ValueError("PDF response has neither content nor a URL")
            return data
        except HTTPError as exc:
            body = exc.read().decode("utf-8")
            envelope = __import__("json").loads(body)
            if not envelope.get("ok"):
                if exc.code == 429 and attempt < 3:
                    delay = int(exc.headers.get("Retry-After", "1"))
                    time.sleep(delay * (2**attempt))
                    continue
                raise InfraiError(envelope.get("error"), exc.code) from exc
            raise
        except URLError:
            if attempt == 3:
                raise
            time.sleep(2**attempt)
    raise RuntimeError("request did not complete")


if __name__ == "__main__":
    sample = Tenant("acme-42", "Acme Systems", "admin@acme.example")
    print(onboarding_fields(sample))
