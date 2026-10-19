# ApexiveAI RPA Platform — backend starter

This is the initial platform foundation, not a production deployment approval. It provides department seed data, workflow metadata, safe queued-run records, and audit-log records. It deliberately does not execute browser, ERP, financial, or network actions.

## Windows CMD setup

```bat
cd /d "%USERPROFILE%\Desktop"
mkdir ApexiveAI-RPA-Platform
```

Extract the project archive, then:

```bat
cd /d "%USERPROFILE%\Desktop\ApexiveAI-RPA-Platform\backend"
py -3.12 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
notepad .env
```

Before any deployment, set a long random `JWT_SECRET`, configure a managed PostgreSQL `DATABASE_URL`, restrict `CORS_ORIGINS`, add migrations, and implement/verify authentication and authorization. Do not expose this starter publicly before those controls are implemented.

Start local development:

```bat
uvicorn app.main:app --reload --host 127.0.0.1 --port 8020
```

Open `http://127.0.0.1:8020/docs`.

## Initial API
- `GET /health`
- `GET /api/v1/departments`
- `GET /api/v1/workflows`
- `POST /api/v1/workflows`
- `POST /api/v1/workflows/{workflow_id}/test-run` (only active workflows; queues a safe placeholder, does not run automation)

## Before production
1. Authentication, MFA option, password policy, account recovery and role-based access control.
2. Alembic migrations, PostgreSQL backups/restore drills and retention policies.
3. Durable queue and isolated worker execution with idempotency, timeout, retry limits and cancellation.
4. Encrypted secret vault; never store ERP credentials in workflow definitions.
5. Approval gates for financial, procurement, and write actions.
6. Tamper-resistant audit trail, monitoring, alerting, dependency scanning and security testing.
7. Integration contracts and written authorization from MAX MYANMAR system owners.
