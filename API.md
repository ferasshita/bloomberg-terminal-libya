# API Documentation

Base URL: `http://localhost:8000/api/v1`

## Authentication

Currently, no authentication is required. For production, implement JWT or API key authentication.

## Data Endpoints

### Get Tick Data
```
GET /data/tick
```

Query Parameters:
- `currency_pair` (string, default: "USD/LYD") - Currency pair to query
- `hours` (integer, default: 24) - Hours of history to retrieve

Response:
```json
[
  {
    "id": 1,
    "timestamp": "2024-02-08T12:00:00",
    "currency_pair": "USD/LYD",
    "price": 4.85,
    "price_type": "mid",
    "source_channel": "@EwanLibya",
    "raw_message": "سعر الدولار الآن: 4.85",
    "message_id": 12345
  }
]
```

### Get Daily Data
```
GET /data/daily
```

Query Parameters:
- `currency_pair` (string, default: "USD/LYD")
- `days` (integer, default: 30) - Days of history

Response:
```json
[
  {
    "id": 1,
    "date": "2024-02-01T00:00:00",
    "currency_pair": "USD/LYD",
    "open": 4.80,
    "high": 4.90,
    "low": 4.75,
    "close": 4.85,
    "volume": 100000,
    "source": "fulus.ly"
  }
]
```

### Get Latest Price
```
GET /data/latest-price
```

Query Parameters:
- `currency_pair` (string, default: "USD/LYD")

Response:
```json
{
  "currency_pair": "USD/LYD",
  "price": 4.85,
  "price_type": "mid",
  "timestamp": "2024-02-08T12:00:00",
  "source": "@EwanLibya"
}
```

### Get Telegram Messages
```
GET /data/messages
```

Query Parameters:
- `hours` (integer, default: 24) - Hours of history
- `limit` (integer, default: 100) - Maximum messages to return

Response:
```json
[
  {
    "timestamp": "2024-02-08T12:00:00",
    "channel": "@EwanLibya",
    "text": "سعر الدولار الآن: 4.85",
    "sentiment_score": null,
    "contains_price": true
  }
]
```

## Analysis Endpoints

### Get Complete Analysis
```
GET /analysis/complete
```

Query Parameters:
- `currency_pair` (string, default: "USD/LYD")

Response:
```json
{
  "current_price": 4.85,
  "currency_pair": "USD/LYD",
  "forecast_24h": [
    {
      "timestamp": "2024-02-08T13:00:00",
      "predicted_price": 4.86,
      "lower_bound": 4.80,
      "upper_bound": 4.92,
      "confidence": 0.95
    }
  ],
  "forecast_48h": [...],
  "signal": {
    "signal": "BUY",
    "confidence": 75.5,
    "rsi": 28.5,
    "market_panic_index": 35.2,
    "reasoning": "RSI indicates oversold conditions. Market sentiment is calm."
  },
  "recent_messages": [...],
  "ai_reasoning": "The USD/LYD rate is showing bullish signals..."
}
```

### Get Signal Only
```
GET /analysis/signal
```

Query Parameters:
- `currency_pair` (string, default: "USD/LYD")

Response:
```json
{
  "signal": "BUY",
  "confidence": 75.5,
  "rsi": 28.5,
  "market_panic_index": 35.2,
  "reasoning": "RSI indicates oversold conditions."
}
```

### Get Market Panic Index
```
GET /analysis/panic-index
```

Response:
```json
{
  "market_panic_index": 35.2,
  "timestamp": "2024-02-08T12:00:00"
}
```

## WebSocket Endpoint

### Connect to WebSocket
```
WS /ws
```

The WebSocket endpoint provides real-time updates for:

1. **Price Updates**
```json
{
  "type": "price_update",
  "data": {
    "timestamp": "2024-02-08T12:00:00",
    "currency_pair": "USD/LYD",
    "price": 4.85,
    "price_type": "mid",
    "source_channel": "@EwanLibya"
  }
}
```

2. **Analysis Updates**
```json
{
  "type": "analysis_update",
  "data": {
    "signal": "BUY",
    "confidence": 75.5,
    ...
  }
}
```

### WebSocket Keepalive
Send `"ping"` to keep the connection alive. The server will respond with `"pong"`.

## Error Responses

All errors follow this format:
```json
{
  "detail": "Error message here"
}
```

HTTP Status Codes:
- `200` - Success
- `400` - Bad Request
- `404` - Not Found
- `500` - Internal Server Error

## Rate Limiting

Currently, no rate limiting is implemented. For production, implement rate limiting based on IP or API key.

## CORS

CORS is enabled for the following origins:
- `http://localhost:3000`
- `http://localhost:3001`
- `http://127.0.0.1:3000`

For production, update `CORS_ORIGINS` in the backend configuration.
