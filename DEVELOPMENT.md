# Development Setup Guide

## Prerequisites

1. **Docker & Docker Compose**
   ```bash
   # Install Docker Desktop (macOS/Windows)
   # Or install Docker Engine (Linux)
   ```

2. **Telegram API Credentials**
   - Go to https://my.telegram.org/apps
   - Create a new application
   - Note down your `api_id` and `api_hash`

3. **OpenAI API Key**
   - Go to https://platform.openai.com/api-keys
   - Create a new API key

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/ferasshita/bloomberg-terminal-libya.git
cd bloomberg-terminal-libya
```

### 2. Configure Environment Variables

Copy the example environment files:
```bash
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.local.example frontend/.env.local
```

Edit `.env` and add your credentials:
```env
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE=+218901234567
OPENAI_API_KEY=sk-...
```

### 3. Start the Application

Using the setup script (recommended):
```bash
chmod +x setup.sh
./setup.sh
```

Or manually:
```bash
docker-compose up -d --build
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Development Workflow

### Backend Development

1. **Enter the backend container**:
   ```bash
   docker-compose exec backend bash
   ```

2. **Run database migrations**:
   ```bash
   # Inside container
   alembic upgrade head
   ```

3. **View logs**:
   ```bash
   docker-compose logs -f backend
   ```

### Frontend Development

1. **Local development** (without Docker):
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

2. **View logs**:
   ```bash
   docker-compose logs -f frontend
   ```

### Database Access

```bash
docker-compose exec db psql -U postgres -d libyan_terminal
```

## Features Overview

### 1. Real-time Price Scraping
- Monitors Libyan Telegram channels
- Extracts USD/LYD and EUR/LYD rates
- Handles Arabic and English formats
- Distinguishes buy/sell prices

### 2. Historical Data Sync
- Fetches daily EOD rates from fulus.ly
- Stores in TimescaleDB hypertables
- Automatic incremental sync

### 3. AI-Powered Forecasting
- Uses Meta's Prophet for predictions
- 24h and 48h forecasts with confidence intervals
- Overlays on candlestick charts

### 4. Signal Generation
- RSI-based technical analysis
- Market panic index from sentiment
- Buy/Sell/Hold recommendations

### 5. AI Reasoning
- GPT-4o powered market analysis
- Context-aware explanations
- Real-time sentiment integration

### 6. Bloomberg-Style Dashboard
- High-density dark theme interface
- Real-time price ticker
- Candlestick charts with forecast overlay
- Live news feed with sentiment badges
- Signal card with panic index
- Responsive mobile design

## Troubleshooting

### Database Connection Issues
```bash
# Restart the database
docker-compose restart db

# Check database logs
docker-compose logs db
```

### Telegram Authentication
On first run, you'll need to authenticate with Telegram:
```bash
# View backend logs to see authentication prompts
docker-compose logs -f backend

# You may need to enter a verification code
```

### Port Conflicts
If ports 3000, 8000, or 5432 are already in use:
```bash
# Edit docker-compose.yml to use different ports
# For example, change "3000:3000" to "3001:3000"
```

## Production Deployment

### Environment Variables
Set production values:
```env
DEBUG=false
# Use strong database password
# Use production API URLs
```

### Security Considerations
1. Never commit `.env` files
2. Use secrets management (AWS Secrets Manager, etc.)
3. Enable HTTPS for frontend
4. Restrict database access
5. Rate limit API endpoints

### Scaling
- Use managed PostgreSQL (AWS RDS, etc.)
- Deploy backend on multiple instances
- Use load balancer
- CDN for frontend static assets

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: https://github.com/ferasshita/bloomberg-terminal-libya/issues
- Email: support@example.com
