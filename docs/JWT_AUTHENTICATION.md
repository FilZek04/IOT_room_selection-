# JWT Authentication

JWT authentication secures admin endpoints while keeping public features accessible.

## Quick Start

**1. Configure `.env`:**
```env
JWT_SECRET_KEY="your-secret-key-here"  # openssl rand -hex 32
JWT_ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**2. Create first user (via MongoDB directly):**

The `scripts/create_admin.py` script does not exist. To create the first user, insert directly into MongoDB:

```bash
# Start MongoDB shell
mongosh "mongodb://localhost:27017/iot_room_selection"

# Insert user (password must be bcrypt-hashed)
db.users.insertOne({
    username: "admin",
    email: "admin@example.com",
    hashed_password: "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTtYA.qGZvKG6G",  # "AdminPass123"
    is_active: true,
    created_at: new Date()
})
```

To generate a bcrypt hash, run:
```bash
python -c "import bcrypt; print(bcrypt.hashpw('YourPassword123'.encode(), bcrypt.gensalt()).decode())"
```

**3. Login & use the token:**
```bash
# Get token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=AdminPass123"

# Use token
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/v1/sensors/Room_1/latest
```

## Endpoint Access

| Public (No Token) | Protected (Token Required) |
|-------------------|---------------------------|
| `GET /`, `/health` | `POST /auth/register` |
| `GET /rooms/` | `GET /auth/me` |
| `POST /rank` | `GET /sensors/*` |
| `POST /auth/login` | `GET /calendar/*` |
| `GET /rank/example` | `GET /rooms/{id}` |


## Token Details

- **Algorithm**: HS256
- **Expiration**: 30 minutes (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)
- **Passwords**: Min 8 chars, 1 uppercase, 1 lowercase, 1 digit

## Testing & Troubleshooting

```bash
# Start backend with JWT enabled
cd backend && uvicorn app.main:app --reload

# Login via Swagger UI: http://localhost:8000/docs
# Click "Authorize" and enter: Bearer <token>
```

| Issue | Solution |
|-------|----------|
| 401 Unauthorized | Token expired or not provided - re-login |
| 403 Forbidden | User `is_active` is false |
| "JWT not configured" | Set `JWT_SECRET_KEY` in `.env` |
| "Invalid username or password" | Check credentials or create user in MongoDB |
