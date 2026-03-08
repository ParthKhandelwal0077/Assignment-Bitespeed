# Bitespeed Identity Reconciliation

Identity reconciliation service that links contact records across orders via shared email or phone number.

## Stack

- **Framework:** FastAPI
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Migrations:** Alembic
- **Hosting:** Render / Railway

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL

### Local Development

1. Clone and create a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Configure environment:

   ```bash
   cp .env.example .env
   # Edit .env and set DATABASE_URL
   ```

3. Run migrations:

   ```bash
   alembic upgrade head
   ```

4. Start the server:

   ```bash
   uvicorn app.main:app --reload
   ```

5. API docs: http://localhost:8000/docs

## API

### POST /identify

Reconciles a contact by email and/or phone. Links contacts that share an identifier.

**Request (JSON):**

```json
{
  "email": "optional@example.com",
  "phoneNumber": 123456
}
```

At least one of `email` or `phoneNumber` must be provided.

**Response:**

```json
{
  "contact": {
    "primaryContatctId": 1,
    "emails": ["primary@example.com", "secondary@example.com"],
    "phoneNumbers": ["123456", "717171"],
    "secondaryContactIds": [2, 3]
  }
}
```

### GET /health

Returns `{"status": "ok"}`.

## Deployment

### Render

1. Create a new Web Service, connect your repo.
2. Set `DATABASE_URL` in environment (e.g. from Render PostgreSQL add-on).
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

Or use `render.yaml` for blueprint deployment.

### Railway

1. Create a project, add PostgreSQL, connect your repo.
2. Railway sets `DATABASE_URL` from the PostgreSQL service.
3. Deploy; `railway.json` configures the start command.

## Hosted Endpoint

<!-- Replace with your deployed URL after hosting -->
**Production URL:** `https://your-app.onrender.com` (or your Railway URL)

---

Built for the Bitespeed Backend Task: Identity Reconciliation.
