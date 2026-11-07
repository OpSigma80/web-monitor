# Web Monitor Pro

<img width="968" height="590" alt="imagen" src="https://github.com/user-attachments/assets/87ee5c9c-79ee-4f2c-86f8-ead210e64c2d" />

### Telegram Price Alert

<img width="423" height="123" alt="imagen" src="https://github.com/user-attachments/assets/56216f94-7bde-4364-9d82-c54ed499d107" />



A full-stack website monitoring service built with Python, FastAPI, PostgreSQL, Redis, and ARQ.

## Features

- English dashboard with HTTP Basic authentication
- Create, list, check, and delete website monitors
- CSS selector and XPath value extraction
- Scheduled checks every five minutes
- Bitcoin BTC/USD price monitoring example
- Change detection with configurable thresholds
- Telegram change notifications
- Interactive Swagger/OpenAPI documentation

## Tech Stack

- FastAPI and Uvicorn
- SQLModel and PostgreSQL
- Redis and ARQ workers
- HTTPX and BeautifulSoup
- Telegram Bot API
- Docker Compose

## Getting Started

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
docker compose up -d
python scripts/init_db.py
```

Configure `.env` before running:

```env
API_USERNAME=your-username
API_PASSWORD=strong-random-password
DATABASE_URL=postgresql+asyncpg://monitor:monitor_secret@localhost:5432/webmonitor
REDIS_URL=redis://localhost:6379
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id
```

Start the API and worker in separate terminals:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8005 --reload
arq app.workers.tasks.WorkerSettings
```

Open:

- Dashboard: `http://localhost:8005/`
- API documentation: `http://localhost:8005/docs`
- Health check: `http://localhost:8005/health`

## API Authentication

Monitor endpoints require HTTP Basic authentication. Use **Authorize** in Swagger or send the `Authorization` header.

```bash
curl -u "your-username:strong-random-password" \
  http://localhost:8005/api/monitors/
```

## Background Checks

ARQ runs `check_all_due_monitors` at startup and at five-minute intervals. Individual monitors use their configured interval.

## Security Notes

- Never commit `.env`.
- Replace default credentials before deployment.
- Use HTTPS for public deployments.
- Restrict CORS and expose only required ports.
