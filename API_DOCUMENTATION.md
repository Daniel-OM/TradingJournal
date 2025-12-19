# Trading Journal - API Documentation

## 🔗 Base URL

```
http://localhost:8000/api/v1
```

## 🔐 Authentication

La API utiliza autenticación basada en Bearer tokens JWT.

### Headers Requeridos
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

---

## 📋 Endpoints

### Auth

#### Register
```
POST /auth/register
```

**Request:**
```json
{
  "username": "usuario",
  "email": "usuario@example.com",
  "password": "securepassword"
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "username": "usuario",
  "email": "usuario@example.com",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### Login
```
POST /auth/login
```

**Request:**
```json
{
  "username": "usuario",
  "password": "securepassword"
}
```

**Response (200):**
```json
{
  "access_token": "jwt_token",
  "refresh_token": "refresh_token",
  "token_type": "bearer"
}
```

---

### Users

#### Get Current User
```
GET /users/me
```

**Headers Required:** Authorization: Bearer <token>

**Response (200):**
```json
{
  "id": "uuid",
  "username": "usuario",
  "email": "usuario@example.com",
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

### Trades

#### Get All Trades
```
GET /trades?skip=0&limit=10&symbol=AAPL&type=LONG
```

**Query Parameters:**
- `skip` (int): Número de resultados a saltar (default: 0)
- `limit` (int): Número de resultados a devolver (default: 10)
- `symbol` (string, opcional): Filtrar por símbolo
- `type` (string, opcional): Filtrar por tipo (LONG/SHORT)

**Response (200):**
```json
{
  "total": 100,
  "items": [
    {
      "id": "uuid",
      "symbol": "AAPL",
      "type": "LONG",
      "entry_price": 150.50,
      "exit_price": 155.00,
      "quantity": 100,
      "pnl": 450.00,
      "commission": 10.00,
      "entry_date": "2024-01-01T10:30:00Z",
      "exit_date": "2024-01-01T14:30:00Z",
      "notes": "Good trade",
      "strategy_id": "uuid",
      "user_id": "uuid"
    }
  ]
}
```

#### Create Trade
```
POST /trades
```

**Request:**
```json
{
  "symbol": "AAPL",
  "type": "LONG",
  "entry_price": 150.50,
  "exit_price": 155.00,
  "quantity": 100,
  "entry_date": "2024-01-01T10:30:00Z",
  "exit_date": "2024-01-01T14:30:00Z",
  "commission": 10.00,
  "notes": "Good trade",
  "strategy_id": "uuid"
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "symbol": "AAPL",
  "type": "LONG",
  "entry_price": 150.50,
  "exit_price": 155.00,
  "quantity": 100,
  "pnl": 450.00,
  "commission": 10.00,
  "entry_date": "2024-01-01T10:30:00Z",
  "exit_date": "2024-01-01T14:30:00Z",
  "notes": "Good trade",
  "strategy_id": "uuid",
  "user_id": "uuid"
}
```

#### Get Trade by ID
```
GET /trades/{trade_id}
```

**Response (200):** Trade object

#### Update Trade
```
PUT /trades/{trade_id}
```

**Request:** Same as Create Trade (send all fields you want to update)

**Response (200):** Updated Trade object

#### Delete Trade
```
DELETE /trades/{trade_id}
```

**Response (204):** No content

---

### Strategies

#### Get All Strategies
```
GET /strategies?skip=0&limit=10
```

**Response (200):**
```json
{
  "total": 50,
  "items": [
    {
      "id": "uuid",
      "name": "Moving Average Crossover",
      "description": "Strategy description",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z",
      "user_id": "uuid",
      "conditions": []
    }
  ]
}
```

#### Create Strategy
```
POST /strategies
```

**Request:**
```json
{
  "name": "Moving Average Crossover",
  "description": "Strategy description",
  "is_active": true
}
```

**Response (201):** Strategy object

#### Get Strategy by ID
```
GET /strategies/{strategy_id}
```

**Response (200):** Strategy object with conditions

#### Update Strategy
```
PUT /strategies/{strategy_id}
```

**Request:** Strategy fields to update

**Response (200):** Updated Strategy object

#### Delete Strategy
```
DELETE /strategies/{strategy_id}
```

**Response (204):** No content

---

### Watchlists

#### Get All Watchlists
```
GET /watchlists?skip=0&limit=10
```

**Response (200):**
```json
{
  "total": 20,
  "items": [
    {
      "id": "uuid",
      "name": "Tech Stocks",
      "description": "Technology stocks to watch",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z",
      "user_id": "uuid",
      "entries": []
    }
  ]
}
```

#### Create Watchlist
```
POST /watchlists
```

**Request:**
```json
{
  "name": "Tech Stocks",
  "description": "Technology stocks to watch",
  "is_active": true
}
```

**Response (201):** Watchlist object

#### Get Watchlist by ID
```
GET /watchlists/{watchlist_id}
```

**Response (200):** Watchlist object with entries

#### Update Watchlist
```
PUT /watchlists/{watchlist_id}
```

**Request:** Watchlist fields to update

**Response (200):** Updated Watchlist object

#### Delete Watchlist
```
DELETE /watchlists/{watchlist_id}
```

**Response (204):** No content

---

### Performance

#### Get Performance Statistics
```
GET /performance/stats?symbol=AAPL&start_date=2024-01-01&end_date=2024-12-31
```

**Query Parameters:**
- `symbol` (string, opcional): Filtrar por símbolo
- `start_date` (date, opcional): Fecha de inicio
- `end_date` (date, opcional): Fecha de fin

**Response (200):**
```json
{
  "total_pnl": 5000.00,
  "win_rate": 0.65,
  "win_count": 65,
  "loss_count": 35,
  "trade_count": 100,
  "profit_factor": 2.5,
  "avg_win": 150.00,
  "avg_loss": -75.00,
  "largest_win": 500.00,
  "largest_loss": -200.00,
  "consecutive_wins": 5,
  "consecutive_losses": 3,
  "sharpe_ratio": 1.5,
  "max_drawdown": 0.15,
  "risk_reward_ratio": 2.0,
  "daily_pnl": 250.00
}
```

#### Get Symbol Performance
```
GET /performance/symbols?symbol=AAPL&start_date=2024-01-01&end_date=2024-12-31
```

**Response (200):**
```json
{
  "best_symbols": [
    {
      "symbol": "AAPL",
      "trade_count": 10,
      "total_pnl": 1000.00,
      "win_rate": 0.7
    }
  ],
  "worst_symbols": [
    {
      "symbol": "TSLA",
      "trade_count": 5,
      "total_pnl": -250.00,
      "win_rate": 0.4
    }
  ]
}
```

---

## 📊 Data Types

### Trade Type
```typescript
type TradeType = "LONG" | "SHORT"
```

### Trade Object
```typescript
interface Trade {
  id: string;
  symbol: string;
  type: "LONG" | "SHORT";
  entry_price: number;
  exit_price: number;
  quantity: number;
  pnl: number;
  commission: number;
  entry_date: string; // ISO 8601
  exit_date: string; // ISO 8601
  notes: string;
  strategy_id?: string;
  user_id: string;
  created_at: string;
  updated_at: string;
}
```

### Strategy Object
```typescript
interface Strategy {
  id: string;
  name: string;
  description: string;
  is_active: boolean;
  user_id: string;
  created_at: string;
  updated_at: string;
  conditions: StrategyCondition[];
}
```

### Watchlist Object
```typescript
interface Watchlist {
  id: string;
  name: string;
  description: string;
  is_active: boolean;
  user_id: string;
  created_at: string;
  updated_at: string;
  entries: WatchlistEntry[];
}
```

---

## ✅ Status Codes

- **200 OK**: Request successful
- **201 Created**: Resource created successfully
- **204 No Content**: Deletion successful
- **400 Bad Request**: Invalid parameters
- **401 Unauthorized**: Missing or invalid token
- **403 Forbidden**: Not authorized to access resource
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server error

---

## 🚀 Getting Started

1. **Register**: `POST /auth/register`
2. **Login**: `POST /auth/login`
3. **Use token**: Include `Authorization: Bearer <token>` in headers
4. **Create trades**: `POST /trades`
5. **View performance**: `GET /performance/stats`

## 📝 Notes

- All timestamps are in ISO 8601 format (UTC)
- P&L (Profit and Loss) is calculated automatically
- Win rate is calculated as: wins / total_trades
- Profit factor is calculated as: total_wins / abs(total_losses)
