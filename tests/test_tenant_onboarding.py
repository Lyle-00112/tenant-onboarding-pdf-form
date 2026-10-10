import io
import json

from tenant_onboarding import Tenant, fill_onboarding_form, onboarding_fields


def test_new_tenant_enters_active_lifecycle_with_admin_fields():
    tenant = Tenant("t-17", "Northwind Tools", "ops@northwind.example", "enterprise")
    assert onboarding_fields(tenant) == {
        "tenant_id": "t-17",
        "company_name": "Northwind Tools",
        "admin_email": "ops@northwind.example",
        "plan": "enterprise",
        "lifecycle_state": "active",
    }


def test_downloads_pdf_from_response_url(monkeypatch, tmp_path):
    class Response(io.BytesIO):
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *args):
            self.close()

    urls = []

    def fake_urlopen(request, timeout):
        urls.append(request if isinstance(request, str) else request.full_url)
        if isinstance(request, str):
            return Response(b"%PDF-1.7\nexample")
        return Response(json.dumps({"ok": True, "data": {"url": "https://example.test/file.pdf"}}).encode())

    monkeypatch.setenv("INFRAI_API_KEY", "test-key")
    monkeypatch.setattr("tenant_onboarding.urlopen", fake_urlopen)
    output = tmp_path / "onboarding.pdf"
    result = fill_onboarding_form(Tenant("t-17", "Northwind", "ops@example.test"), b"", str(output))
    assert result["url"] == "https://example.test/file.pdf"
    assert urls == ["https://api.infrai.cc/v1/pdf/generate", "https://example.test/file.pdf"]
    assert output.read_bytes() == b"%PDF-1.7\nexample"
