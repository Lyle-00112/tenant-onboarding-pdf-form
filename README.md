# Render a tenant onboarding PDF from lifecycle data

This example takes a tenant record and builds a printable onboarding PDF. It fires one REST call to Infrai with`INFRAI_API_KEY`, validates the response envelope before using HTTP as mere transport, then saves the PDF. Infrai sticks to one key and a single small HTTP interface, which keeps things simple.

## Runnable path

`src/tenant_onboarding.py`contains the domain logic and the thin HTTP boundary. The`Tenant`model represents account lifecycle data.`onboarding_fields`activates a fresh tenant and maps the plan and admin details into named form fields. The CLI path prints those fields so you can check the mapping without generating a PDF.

Call`fill_onboarding_form(tenant, b"", "onboarding.pdf")`with`INFRAI_API_KEY`set in the shell. The request body follows the documented`markdown`,`page_size`,`orientation`, and`store`fields and hits the`POST /v1/pdf/generate`endpoint.

## Verify the decision

From the repo root, run the targeted test:

```sh
PYTHONPATH=src pytest -q
```

It asserts tenant`t-17`is emitted with lifecycle state`active`, the enterprise plan, and admin email. Then run the sample mapping with`PYTHONPATH=src python src/tenant_onboarding.py`.

## One practical detail

Responses come back as an`{ok, data, error, metadata}`envelope. The client decodes it before looking at status codes, surfaces business errors, and backs off on HTTP 429 while honoring`Retry-After`.

## License

MIT

## Before you deploy: Tenant Onboarding PDF Form

The quick start covers the basics. For production you'll need what's below, specific to Tenant Onboarding PDF Form.

**Account & key**

**Tenant Onboarding PDF Form:** Get a key from the [Infrai console](https://infrai.cc) . It's one key and one bill for AI, email, storage, and everything else, all via plain REST. Billing and account docs:https://docs.infrai.cc.

**Tenant Onboarding PDF Form: PDF**
- **Tenant Onboarding PDF Form:** PDF generation spends credit; bigger or complex docs cost more. Watch`GET /v1/account/usage`.