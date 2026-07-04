
# account growth simulater based on the forex backtester

A specialized Python tool designed to scan historical Gold (XAU/USD) data using Japanese candlesticks and the Relative Strength Index (RSI). It identifies high-probability Supply and Demand zones, simulates virtual trades based on price interaction with these zones, and plots a comprehensive account equity growth curve.

---

## ✨ Key Features
* 🔍 **Automated Zone Detection:** Spots powerful engulfing candlesticks aligned with RSI overbought/oversold momentum criteria.
* 📈 **Built-in Trade Simulator:** Tracks real-time price interaction with discovered zones to simulate entry, take-profit, and stop-loss triggers.
* 💰 **Virtual Portfolio Management:** Computes ongoing cumulative profits and losses, updating your virtual account balance per trade.
* 🎨 **Performance Dashboard:** Automatically generates and saves a dual-chart visual summary showing your equity curve and trade outcome distribution.

---

## 🛠️ Dependencies

Ensure you have the required libraries installed in your Python environment before running the script:

```bash
pip install pandas numpy matplotlib

```

---

## ⚙️ Configuration & Settings

You can customize the strategy rules by modifying the `SETTINGS` dictionary directly inside the script:

| Parameter | Description | Default Value |
| --- | --- | --- |
| `file_path` | Path to your historical market data CSV file | `"gold_5m_full_table.csv"` |
| `rsi_period` | Lookback period used to calculate the RSI indicator | `14` |
| `rsi_oversold` | Oversold threshold used to validate Demand Zones | `35` |
| `rsi_overbought` | Overbought threshold used to validate Supply Zones | `70` |
| `body_multiplier` | Threshold multiplier for candle body size vs. moving average | `1.5` |
| `avg_window` | Moving average window for historical candle body sizes | `20` |
| `initial_balance` | Starting virtual capital for the performance backtest | `1000` |

---

## 🔍 Strategy Logic

### 1. Zone Discovery Conditions:

* 🟢 **Demand Zone (Buy Setup):** Formed when a bullish candlestick closes higher than the previous candle's high with an above-average body size (`body > avg_body * 1.5`), while the RSI is below `35` (oversold).
* 🔴 **Supply Zone (Sell Setup):** Formed when a bearish candlestick closes lower than the previous candle's low with an above-average body size (`body > avg_body * 1.5`), while the RSI is above `70` (overbought).

### 2. Trade Execution Rules:

* **Trigger:** A trade is activated ("Touched") when the price revisits a "Fresh" discovered zone.
* **Take Profit (+ $20):** Achieved when the price moves favorably and breaks past the trigger candle's structural high/low.
* **Stop Loss (- $10):** Hit if the price invalidates the zone by breaking past its structural boundary floor/ceiling.

---

## 🚀 How to Run

1. Place your historical data CSV file named `gold_5m_full_table.csv` in the exact same directory as the script.
2. Ensure your CSV file includes the following standard OHLC column headers: `Open`, `High`, `Low`, and `Close`.
3. Execute the script via your terminal:

```bash
python main.py

```

---

## 📊 Outputs & Reports

Upon a successful run, the script will output:

1. **Terminal Report:** A comprehensive summary detailing total zones detected, winning/losing trade break-downs for both sides, and the final account balance.
2. **Visual Dashboard:** An interactive window will pop up, and a high-resolution chart named `trading_results.png` will be saved locally. It includes:
* **Equity Curve:** Line plot displaying your account growth step-by-step through closed trades.
* **Trade Distribution:** A bar chart comparing winning vs. losing metrics for clear strategy assessment.



```

```