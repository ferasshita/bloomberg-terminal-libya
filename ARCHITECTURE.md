# System Architecture

## Overview

The Libyan Financial Terminal is a full-stack monorepo application built with a microservices-inspired architecture. It provides real-time monitoring and analysis of Libyan currency markets.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                             │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ Next.js 15  │  │  React 18    │  │  Tailwind    │       │
│  │   (SSR)     │  │  Components  │  │     CSS      │       │
│  └──────┬──────┘  └──────┬───────┘  └──────────────┘       │
│         │                │                                   │
│         └────────┬───────┘                                   │
│                  │  HTTP/REST + WebSocket                    │
└──────────────────┼───────────────────────────────────────────┘
                   │
┌──────────────────┼───────────────────────────────────────────┐
│                  │         Backend (FastAPI)                 │
│  ┌───────────────▼────────────────────────────────┐         │
│  │             API Gateway (FastAPI)              │         │
│  │  ┌──────────────┐  ┌──────────────────────┐   │         │
│  │  │  REST APIs   │  │  WebSocket Handler   │   │         │
│  │  └──────────────┘  └──────────────────────┘   │         │
│  └────┬──────────────────────┬──────────────────┘          │
│       │                      │                              │
│  ┌────▼──────────────────────▼────────────────────┐        │
│  │              Service Layer                      │        │
│  │  ┌─────────────────────────────────────────┐   │        │
│  │  │  TelegramPriceScraper                   │   │        │
│  │  │  - Telethon client                      │   │        │
│  │  │  - Price parsing (Regex)                │   │        │
│  │  │  - Rate limiting                        │   │        │
│  │  └─────────────────────────────────────────┘   │        │
│  │  ┌─────────────────────────────────────────┐   │        │
│  │  │  FulusSyncService                       │   │        │
│  │  │  - Historical data fetching             │   │        │
│  │  │  - Incremental sync                     │   │        │
│  │  └─────────────────────────────────────────┘   │        │
│  │  ┌─────────────────────────────────────────┐   │        │
│  │  │  ForecastingService                     │   │        │
│  │  │  - Prophet model training               │   │        │
│  │  │  - 24h/48h predictions                  │   │        │
│  │  └─────────────────────────────────────────┘   │        │
│  │  ┌─────────────────────────────────────────┐   │        │
│  │  │  AnalysisService                        │   │        │
│  │  │  - RSI calculation                      │   │        │
│  │  │  - Sentiment analysis                   │   │        │
│  │  │  - Signal generation                    │   │        │
│  │  │  - OpenAI integration                   │   │        │
│  │  └─────────────────────────────────────────┘   │        │
│  └─────────────────────────────────────────────────┘       │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│              Database (PostgreSQL + TimescaleDB)            │
│  ┌─────────────────┐  ┌────────────────┐  ┌─────────────┐ │
│  │   tick_data     │  │  daily_data    │  │  telegram_  │ │
│  │  (Hypertable)   │  │ (Hypertable)   │  │  messages   │ │
│  └─────────────────┘  └────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Component Breakdown

### 1. Frontend (Next.js 15)

**Purpose**: User interface for real-time market monitoring

**Key Components**:
- `PriceTicker`: Horizontal scrolling ticker with live prices
- `PriceChart`: Candlestick chart with forecast overlay (lightweight-charts)
- `NewsFeed`: Scrollable feed of Telegram messages with sentiment badges
- `SignalCard`: Buy/Sell/Hold recommendation with confidence metrics
- `AIReasoning`: GPT-4o powered market analysis

**Technology Stack**:
- Next.js 15 (App Router)
- React 18
- TypeScript
- Tailwind CSS
- Shadcn/UI components
- lightweight-charts
- WebSocket client

**Responsive Design**:
- Desktop: 3-column grid layout
- Mobile: Stacked single-column layout

### 2. Backend (FastAPI)

**Purpose**: API server, data processing, and business logic

**Technology Stack**:
- Python 3.11+
- FastAPI (async)
- SQLAlchemy (async ORM)
- Pydantic (data validation)
- Telethon (Telegram API)
- Prophet (forecasting)
- OpenAI API
- TA-Lib (technical analysis)

**Service Architecture**:

#### TelegramPriceScraper
- Connects to Telegram channels via Telethon
- Parses Arabic/English price formats using regex
- Distinguishes buy/sell prices
- Rate limiting (5-second buffer)
- Real-time WebSocket emissions
- Saves to `tick_data` hypertable

#### FulusSyncService
- Fetches historical EOD rates from fulus.ly API
- Incremental sync (only new data)
- Supports multiple currency pairs
- Saves to `daily_data` hypertable
- Periodic sync (24h intervals)

#### ForecastingService
- Trains Prophet models on historical data
- Generates 24h and 48h forecasts
- Returns confidence intervals (95%)
- Handles missing data gracefully

#### AnalysisService
- Calculates RSI (14-period)
- Computes Market Panic Index from Telegram sentiment
- Generates Buy/Sell/Hold signals
- OpenAI GPT-4o integration for reasoning
- Combines multiple data sources

### 3. Database (PostgreSQL + TimescaleDB)

**Purpose**: Time-series data storage and querying

**Schema**:

```sql
-- Tick data (real-time updates)
CREATE TABLE tick_data (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    currency_pair VARCHAR(10) NOT NULL,
    price FLOAT NOT NULL,
    price_type VARCHAR(10) NOT NULL,
    source_channel VARCHAR(100) NOT NULL,
    raw_message TEXT NOT NULL,
    message_id INTEGER
);

-- Convert to hypertable
SELECT create_hypertable('tick_data', 'timestamp');

-- Daily OHLCV data
CREATE TABLE daily_data (
    id SERIAL PRIMARY KEY,
    date TIMESTAMP NOT NULL,
    currency_pair VARCHAR(10) NOT NULL,
    open FLOAT NOT NULL,
    high FLOAT NOT NULL,
    low FLOAT NOT NULL,
    close FLOAT NOT NULL,
    volume FLOAT,
    source VARCHAR(50)
);

-- Convert to hypertable
SELECT create_hypertable('daily_data', 'date');

-- Telegram messages (for sentiment)
CREATE TABLE telegram_messages (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    channel VARCHAR(100) NOT NULL,
    message_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    sentiment_score FLOAT,
    contains_price BOOLEAN
);
```

**Indexing Strategy**:
- Composite indexes on (timestamp, currency_pair)
- Single indexes on frequently queried columns
- TimescaleDB compression for older data

## Data Flow

### 1. Real-time Price Updates

```
Telegram → TelegramPriceScraper → Database → WebSocket → Frontend
```

1. Telegram channel posts price update
2. Telethon client receives message
3. Scraper parses price using regex
4. Data saved to `tick_data` table
5. WebSocket broadcasts to connected clients
6. Frontend updates ticker and chart

### 2. Historical Data Sync

```
fulus.ly API → FulusSyncService → Database
```

1. Service checks last sync date
2. Fetches new data from API
3. Saves to `daily_data` table
4. Runs every 24 hours

### 3. Analysis Pipeline

```
Database → ForecastingService → AnalysisService → Frontend
           ↓
       Prophet Model
```

1. Fetch historical data (30 days)
2. Train Prophet model
3. Generate forecasts (24h/48h)
4. Calculate RSI and sentiment
5. Generate trading signal
6. Get AI reasoning from GPT-4o
7. Return complete analysis

## Security Considerations

### Current Implementation
- CORS restricted to localhost origins
- No authentication (development only)
- Environment variables for secrets

### Production Recommendations
1. Implement JWT authentication
2. API rate limiting (Redis)
3. Input validation and sanitization
4. HTTPS/WSS for encrypted connections
5. Database connection pooling
6. Secrets management (AWS Secrets Manager)
7. API key rotation
8. Logging and monitoring

## Scalability

### Current Limitations
- Single instance design
- In-memory WebSocket connections
- Synchronous Telegram scraping

### Scaling Strategies

#### Horizontal Scaling
- Multiple backend instances with load balancer
- Redis for WebSocket pub/sub
- Celery for background tasks
- Distributed caching (Redis/Memcached)

#### Database Scaling
- Read replicas for analytics queries
- Partitioning by time range (TimescaleDB)
- Connection pooling (PgBouncer)
- Continuous aggregates for dashboards

#### Frontend Scaling
- CDN for static assets
- Server-side rendering (Next.js)
- Edge caching
- Service workers for offline support

## Monitoring & Observability

### Recommended Tools
- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **Metrics**: Prometheus + Grafana
- **Tracing**: Jaeger or Zipkin
- **Uptime**: Pingdom or UptimeRobot
- **Error Tracking**: Sentry

### Key Metrics
- API response times
- WebSocket connection count
- Database query performance
- Telegram scraping latency
- Forecast accuracy
- User engagement

## Deployment

### Development
```bash
docker-compose up
```

### Production
1. Use managed services:
   - AWS RDS (PostgreSQL)
   - AWS ECS/EKS (containers)
   - AWS CloudFront (CDN)
   - AWS ElastiCache (Redis)

2. CI/CD pipeline:
   - GitHub Actions
   - Automated testing
   - Blue-green deployment
   - Rollback capability

## Future Enhancements

1. **Multi-language Support**: Arabic/English interface
2. **User Accounts**: Save preferences, watchlists
3. **Alerts**: Price threshold notifications
4. **Mobile Apps**: React Native or Flutter
5. **More Data Sources**: Banks, exchange offices
6. **Advanced Analytics**: ML models, backtesting
7. **Portfolio Tracking**: User portfolios
8. **Social Features**: Community sentiment, discussions
