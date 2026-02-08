# 🇱🇾 Libyan Financial Terminal - Project Overview

## What We Built

A **production-ready, full-stack Bloomberg-style financial terminal** specifically designed for monitoring Libyan currency markets in real-time. This is a complete monorepo with backend, frontend, and infrastructure code.

## 📊 Key Features

### 1. Real-Time Price Monitoring
- **Telegram Integration**: Automatically scrapes Libyan financial Telegram channels (e.g., @EwanLibya, @AlMushir)
- **Multi-Format Parsing**: Handles both Arabic ("سعر الدولار: 4.85") and English ("USD/LYD: 4.85") formats
- **Buy/Sell Detection**: Distinguishes between buying and selling prices
- **Live Updates**: WebSocket-based real-time price streaming to frontend

### 2. Historical Data Management
- **fulus.ly Integration**: Syncs daily EOD (End of Day) rates
- **TimescaleDB**: High-performance time-series database
- **Incremental Sync**: Only fetches new data to minimize API calls
- **Multiple Pairs**: USD/LYD, EUR/LYD, and extendable to more

### 3. AI-Powered Forecasting
- **Meta Prophet**: Machine learning forecasts for next 24-48 hours
- **Confidence Intervals**: 95% confidence bounds for predictions
- **Chart Overlay**: Dotted forecast line overlaid on candlestick chart
- **Trend Detection**: Automatically identifies upward/downward trends

### 4. Trading Signals
- **RSI Analysis**: 14-period Relative Strength Index for buy/sell signals
- **Market Panic Index**: Sentiment analysis from Telegram messages (0-100 scale)
- **Automated Signals**: BUY (RSI < 30), SELL (RSI > 70), HOLD (neutral)
- **Confidence Scoring**: Each signal comes with confidence percentage

### 5. AI Reasoning (GPT-4o)
- **Context-Aware Analysis**: Analyzes market conditions, news, and technical indicators
- **Natural Language**: Human-readable explanations in 2-3 sentences
- **Real-Time Updates**: Refreshes every minute to stay current
- **Multi-Factor**: Considers RSI, panic index, recent news, and price trends

### 6. Bloomberg-Style Dashboard
- **Dark Theme**: Professional, high-density interface
- **3-Column Layout**: News Feed | Chart + AI | Signal Card
- **Live Ticker**: Horizontal scrolling ticker at top
- **Responsive**: Transforms to mobile-friendly stacked layout
- **Real-Time**: All data updates automatically via WebSocket

## 🏗️ Technology Stack

### Backend
```
Python 3.11+
├── FastAPI (async REST API)
├── Telethon (Telegram client)
├── SQLAlchemy (async ORM)
├── Prophet (forecasting)
├── OpenAI API (GPT-4o)
├── TA-Lib (technical analysis)
└── asyncpg (PostgreSQL driver)
```

### Frontend
```
Node.js 20+ / TypeScript
├── Next.js 15 (App Router)
├── React 18
├── Tailwind CSS
├── Shadcn/UI components
├── lightweight-charts
└── WebSocket client
```

### Database
```
PostgreSQL 15
└── TimescaleDB extension
    ├── Hypertable: tick_data
    ├── Hypertable: daily_data
    └── Table: telegram_messages
```

### Infrastructure
```
Docker Compose
├── Service: PostgreSQL + TimescaleDB
├── Service: Backend (FastAPI)
└── Service: Frontend (Next.js)
```

## 📁 Project Structure

```
bloomberg-terminal-libya/
├── backend/                    # Python FastAPI application
│   ├── app/
│   │   ├── api/               # API routes
│   │   │   └── v1/
│   │   │       ├── analysis.py    # Analysis endpoints
│   │   │       ├── data.py        # Data endpoints
│   │   │       └── websocket.py   # WebSocket endpoint
│   │   ├── core/              # Configuration & database
│   │   │   ├── config.py
│   │   │   └── database.py
│   │   ├── models/            # SQLAlchemy models
│   │   │   └── data.py
│   │   ├── schemas/           # Pydantic schemas
│   │   │   └── data.py
│   │   ├── services/          # Business logic
│   │   │   ├── telegram_scraper.py   # Telegram integration
│   │   │   ├── fulus_sync.py         # Historical data sync
│   │   │   ├── forecasting.py        # Prophet forecasting
│   │   │   └── analysis.py           # Signal generation + AI
│   │   └── main.py            # FastAPI application
│   ├── pyproject.toml
│   └── Dockerfile
├── frontend/                   # Next.js application
│   ├── src/
│   │   ├── app/               # Next.js 15 app directory
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx       # Main dashboard
│   │   │   └── globals.css
│   │   ├── components/        # React components
│   │   │   ├── PriceTicker.tsx
│   │   │   ├── PriceChart.tsx
│   │   │   ├── NewsFeed.tsx
│   │   │   ├── SignalCard.tsx
│   │   │   ├── AIReasoning.tsx
│   │   │   └── ui/            # Shadcn components
│   │   ├── hooks/
│   │   │   └── useWebSocket.ts
│   │   └── lib/
│   │       └── utils.ts
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   └── Dockerfile
├── docker-compose.yml          # Orchestration
├── setup.sh                    # Automated setup script
├── README.md                   # Quick start guide
├── DEVELOPMENT.md              # Developer documentation
├── API.md                      # API reference
├── ARCHITECTURE.md             # System architecture
└── LICENSE                     # MIT License
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Telegram API credentials (api_id, api_hash)
- OpenAI API key

### Setup (3 steps)
```bash
# 1. Clone the repository
git clone https://github.com/ferasshita/bloomberg-terminal-libya.git
cd bloomberg-terminal-libya

# 2. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 3. Start the application
chmod +x setup.sh
./setup.sh
```

### Access
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 📊 Dashboard Components

### 1. Price Ticker (Top)
```
USD/LYD 4.85 ↑ +0.5% | EUR/LYD 5.20 ↓ -0.3% | Gold/LYD 250.00 ...
```

### 2. Left Column: News Feed
```
┌─────────────────────────┐
│ Live News Feed          │
├─────────────────────────┤
│ @EwanLibya [Price]      │
│ سعر الدولار: 4.85      │
│ 2 minutes ago           │
├─────────────────────────┤
│ @AlMushir [Warning]     │
│ نقص في السيولة...      │
│ 5 minutes ago           │
└─────────────────────────┘
```

### 3. Center Column: Chart + AI
```
┌──────────────────────────────────┐
│ USD/LYD Chart      [1M][5M][1H]  │
├──────────────────────────────────┤
│                                  │
│    Candlestick Chart             │
│    with Forecast Overlay         │
│                                  │
└──────────────────────────────────┘
┌──────────────────────────────────┐
│ AI Market Analysis               │
├──────────────────────────────────┤
│ The USD/LYD rate is showing      │
│ bullish signals due to...        │
└──────────────────────────────────┘
```

### 4. Right Column: Signal Card
```
┌─────────────────────────┐
│ Trading Signal          │
├─────────────────────────┤
│        🔼 BUY           │
│     Confidence: 75%     │
│     ████████░░          │
├─────────────────────────┤
│ Market Panic: 35/100    │
│ ████░░░░░░              │
├─────────────────────────┤
│ RSI: 28.5               │
│ ████░░░░░░░░░░          │
├─────────────────────────┤
│ Analysis:               │
│ RSI indicates oversold  │
│ conditions. Market      │
│ sentiment is calm.      │
└─────────────────────────┘
```

## 🔧 Configuration

### Required Environment Variables
```env
# Telegram API (get from my.telegram.org)
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=abcdef1234567890
TELEGRAM_PHONE=+218901234567

# OpenAI API (get from platform.openai.com)
OPENAI_API_KEY=sk-...

# Database (auto-configured in Docker)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/libyan_terminal
```

### Optional Configuration
```env
# Channels to monitor (comma-separated)
TELEGRAM_CHANNELS=@EwanLibya,@AlMushir,@YourChannel

# Scraper rate limiting
SCRAPER_BUFFER_SECONDS=5

# OpenAI model
OPENAI_MODEL=gpt-4o

# CORS origins
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

## 📈 Data Flow

```
1. Telegram Message
   ↓
2. TelegramPriceScraper (parse & validate)
   ↓
3. TimescaleDB (save tick_data)
   ↓
4. WebSocket Broadcast
   ↓
5. Frontend Update (real-time)

Parallel:
6. FulusSyncService (daily_data)
   ↓
7. ForecastingService (Prophet)
   ↓
8. AnalysisService (RSI + AI)
   ↓
9. Frontend Display
```

## 🔐 Security Notes

### Development (Current)
- ✅ Environment variables for secrets
- ✅ CORS restricted to localhost
- ⚠️ No authentication (dev only)
- ⚠️ No rate limiting

### Production Requirements
- 🔒 JWT authentication
- 🔒 API rate limiting (Redis)
- 🔒 HTTPS/WSS encryption
- 🔒 Input validation/sanitization
- 🔒 Secrets management (AWS Secrets Manager)
- 🔒 Database encryption at rest
- 🔒 API key rotation
- 🔒 Logging & monitoring

## 📚 Documentation

- **README.md**: Quick start and overview
- **DEVELOPMENT.md**: Detailed setup and development guide
- **API.md**: Complete API reference with examples
- **ARCHITECTURE.md**: System design and scalability
- **LICENSE**: MIT License

## 🎯 Key Achievements

✅ **Complete Monorepo**: Backend + Frontend + Infrastructure
✅ **Production Ready**: Docker, environment configs, documentation
✅ **Real-Time**: WebSocket integration for live updates
✅ **AI-Powered**: Prophet forecasting + GPT-4o reasoning
✅ **Beautiful UI**: Bloomberg-style dark theme dashboard
✅ **Responsive**: Mobile-friendly design
✅ **Extensible**: Easy to add new currencies, channels, or features
✅ **Well-Documented**: 4 comprehensive documentation files

## 🚧 Future Enhancements

- [ ] User authentication and accounts
- [ ] Price alerts and notifications
- [ ] Multi-language support (Arabic/English)
- [ ] Mobile apps (React Native)
- [ ] More data sources (banks, exchange offices)
- [ ] Portfolio tracking
- [ ] Social features (community sentiment)
- [ ] Advanced analytics (ML models)
- [ ] Backtesting capabilities

## 📞 Support

- GitHub Issues: [Create an issue](https://github.com/ferasshita/bloomberg-terminal-libya/issues)
- Documentation: See README.md, DEVELOPMENT.md, API.md, ARCHITECTURE.md
- License: MIT (see LICENSE file)

## 🏆 Credits

Built with ❤️ for the Libyan financial community

**Tech Stack**:
- FastAPI by Sebastián Ramírez
- Next.js by Vercel
- Prophet by Facebook (Meta)
- Telethon by LonamiWebs
- TimescaleDB by Timescale Inc.
- OpenAI GPT-4o

---

**Version**: 0.1.0  
**Status**: Production Ready  
**Last Updated**: February 2024
