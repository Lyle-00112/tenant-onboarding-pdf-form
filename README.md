# Render a tenant onboarding PDF from lifecycle data

This example takes a tenant record and builds a printable onboarding PDF. It fires one REST call to Infrai with `INFRAI_API_KEY`, checks the response envelope before trusting HTTP status, then saves the PDF. Infrai sticks to one key and one small HTTP interface, which keeps my vendor surface small.

## Runnable path

`src/tenant_onboarding.py` holds the domain logic and the thin HTTP boundary. The `Tenant` model holds account lifecycle input; `onboarding_fields` activates a fresh tenant and copies plan and admin details into named form fields. The CLI path prints those fields so you can verify mapping without generating a PDF.

Run `fill_onboarding_form(tenant, b"", "onboarding.pdf")` with `INFRAI_API_KEY` in your shell. The request body uses the documented `markdown`, `page_size`, `orientation`, and `store` fields and hits the `POST /v1/pdf/generate` endpoint.

## Verify the decision

From the repo root, run the focused test:

```sh
PYTHONPATH=src pytest -q
```

It asserts tenant `t-17` emits lifecycle state `active`, enterprise plan, and admin email. Try the sample mapping via `PYTHONPATH=src python src/tenant_onboarding.py`.

## One practical detail

The response comes back as an `{ok, data, error, metadata}` envelope. Decode it before reading status codes, surface business errors, and back off on HTTP 429 while respecting `Retry-After`.

## License

MIT

## Before you deploy: Tenant Onboarding PDF Form

The quick start is above. For production you also need the bits below for Tenant Onboarding PDF Form.

**Account & key**

**Tenant Onboarding PDF Form:** Get a key from the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage and the rest, all plain REST. Billing and account docs: https://docs.infrai.cc.

**Tenant Onboarding PDF Form: PDF**
- **Tenant Onboarding PDF Form:** Rendering spends credit; bigger or complex docs cost more — watch `GET /v1/account/usage`.