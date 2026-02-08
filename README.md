# Libyan Financial Terminal 🇱🇾📊

A production-ready full-stack Bloomberg-style financial terminal for monitoring Libyan currency markets in real-time.

## Features

- **Real-time Price Monitoring**: Scrapes Telegram channels for USD/LYD, EUR/LYD rates
- **Historical Data**: Syncs with fulus.ly API for daily EOD rates
- **AI-Powered Forecasting**: Uses Meta's Prophet for 24-48h predictions
- **Signal Generation**: RSI-based buy/sell recommendations
- **Sentiment Analysis**: Market panic index from Telegram messages
- **Bloomberg-Style Dashboard**: High-density dark theme interface
- **Real-time Updates**: WebSocket integration for live data

## Stack

- **Frontend**: Next.js 15, React, Tailwind CSS, Shadcn/UI, lightweight-charts
- **Backend**: FastAPI, Python 3.11+
- **Database**: PostgreSQL + TimescaleDB
- **Scraping**: Telethon (Telegram API)
- **Analytics**: Prophet, pandas, numpy
- **Infrastructure**: Docker, docker-compose

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Telegram API credentials (API_ID, API_HASH)
- OpenAI API key (for AI reasoning)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/ferasshita/bloomberg-terminal-libya.git
cd bloomberg-terminal-libya
```

2. Create environment files:

**backend/.env**:
```env
# Database
DATABASE_URL=postgresql://postgres:postgres@db:5432/libyan_terminal

# Telegram
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE=your_phone_number

# OpenAI
OPENAI_API_KEY=your_openai_key

# Fulus.ly
FULUS_API_URL=https://api.fulus.ly/v1
```

**frontend/.env.local**:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

3. Start all services:
```bash
docker-compose up -d
```

4. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Project Structure

```
bloomberg-terminal-libya/
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── models/      # Database models
│   │   ├── services/    # Business logic
│   │   ├── api/         # API routes
│   │   └── core/        # Configuration
│   ├── pyproject.toml
│   └── Dockerfile
├── frontend/            # Next.js application
│   ├── src/
│   │   ├── app/        # Next.js 15 app directory
│   │   ├── components/ # React components
│   │   └── lib/        # Utilities
│   ├── package.json
│   └── Dockerfile
└── docker-compose.yml   # Orchestration
```

## Development

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## License

MIT License - see LICENSE file for details
