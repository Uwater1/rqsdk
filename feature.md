## Design Goal

* Build an MCP (Model Context Protocol) server that enables an AI agent to simulate trading stocks using historical data.
* The system maintains a mock portfolio and enforces strict no-lookahead constraints.
* All trading decisions must be made using only information available up to the current simulation date.

---

## Data Source

* Data is stored under `basic/`
* Each stock has its own folder:

  * `price.csv`
  * `financials.csv`
  * `introduction.json`

### price.csv

* Fields:

  * date, open, high, low, close, volume, amount, pctChg, vwap

### financials.csv

* Must include:

  * report_date

---

## Core Constraints

* The agent cannot access future data.

  * Market data limited by `current_date` 
  * Financial reports only available if `report <= current_date` (Except next_report_date)
* All execution is deterministic.
* Simulation advances in discrete trading days.

---

## Portfolio State

* Stored as a JSON object:

```
{
  current_date: string,
  cash: float,
  positions: {
    <stock_code>: {
      quantity: int,
      avg_price: float
    }
  },
  orders: {
    <order_id>: {
      stock_code: string,
      side: "buy" | "sell",
      quantity: int,
      limit_price: float | null,
      status: "pending" | "filled", // (assume no partial fill, cancel instantly delete)
      created_date: string,
      filled_date: string | null,
      filled_price: float | null
    }
  }
}
```

---

## Execution Model

### Order Types

1. Market Order
2. Limit Order (GTC)

### Fill Rules

* Market Order:

  * Executed at next trading day's open price

* Limit Order:

  * Buy: filled if `low <= limit_price`
  * Sell: filled if `high >= limit_price`
  * Fill price = limit_price

* Orders are processed in FIFO order

---

## Time Control

### Command

* `next-day`

### Behavior

1. Advance `current_date`
2. Process all pending orders
3. Update portfolio valuation
4. Unlock new market and financial data

---

## MCP Features

### 1. buy

* Syntax:

  * `buy <stock_code> <quantity> --limit {price}`
* Default:

  * Market order if limit not provided

* Returns:

  * order_id if success (filled or pending)
  * error message if fail (rejected because of insufficient fund)

---

### 2. sell

* Syntax:

  * `sell <stock_code> <quantity> --limit {price}`
* Default:

  * Market order if limit not provided

* Returns:

  * order_id if success (filled or pending)
  * error message if fail (rejected because of insufficient stock)
---

### 3. check-portfolio

* Returns JSON:

```
{
  date: ...,
  cash: ...,
  total_value: ...,
  positions: {...},
  orders: {...}
}
```

---

### 4. cancel-order

* Syntax:

  * `cancel-order <order-id>`

---

### 5. next-day

* Move simulation forward by one trading day

---

### 6. check-price

* Syntax:

  * `check-price <stock_code> <days-ago>`
* Default:

  * days-ago = 1
* Returns:

  * open, high, low, close, volume, amount, pctChg, vwap

---

### 7. check-indicator

* Syntax:

  * `check-indicator <stock_code> <indicator-type> <params> <days-ago>`
* Default:

  * days-ago = 1
* Notes:

  * Uses pandas-ta
  * Must only use data up to current_date

---

### 8. check-financial-report

* Syntax:

  * `check-financial-report <stock_code> <quarters-ago>`
* Default:

  * quarters-ago = 1
* Returns:

  * Financial metrics (revenue, net profit, EPS, etc.)
  * Growth metrics (YoY)
  * Next report publish date

---

### 9. check-stock-info

* Syntax:

  * `check-stock-info <stock_code>`
* Returns:

  * introduction.json content

---

### 10. check-index

* Syntax:

  * `check-index <days-ago>`
* Default:

  * days-ago = 1
* Includes:

  * SSE Composite
  * SZSE Component
  * CSI 300
  * CSI 500
  * CSI 800

---

## Validation Rules

* Reject invalid stock codes
* Reject negative or zero quantity
* Reject orders exceeding available cash or holdings

---

## Logging (Recommended)

* Log each action:

  * timestamp, tool, input, output, state changes ...

---

## Future Extensions

* Transaction costs (fees, slippage)
* Intraday simulation
* Short selling and margin
* Multi-agent environment
