import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

# 1. Default Settings
SETTINGS = {
    "file_path": "gold_5m_full_table.csv",
    "rsi_period": 14,
    "rsi_oversold": 35,
    "rsi_overbought": 70,
    "body_multiplier": 1.5,
    "avg_window": 20,
    "initial_balance": 1000  # Virtual initial capital for the equity curve chart
}

class GoldScanner:
    def __init__(self, config):
        self.config = config
        self.df = None
        self.equity_history = [config["initial_balance"]]
        self.results = {
            "demands": [],
            "supplies": [],
            "stats": {
                "buy_win": 0, "buy_fail": 0,
                "sell_win": 0, "sell_fail": 0
            }
        }

    def load_data(self):
        """Loads data from the CSV file and verifies its existence."""
        file_path = self.config["file_path"]
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"❌ File not found: '{file_path}' in the current directory!")
        
        print(f"📊 Loading file: {file_path} ...")
        self.df = pd.read_csv(file_path)
        print(f"✅ Successfully loaded {len(self.df)} rows of data.")

    def apply_indicators(self):
        """Calculates essential technical indicators (RSI and Moving Average)."""
        print("📈 Calculating indicators (RSI, Moving Average)...")
        
        # Calculate RSI changes
        delta = self.df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.config["rsi_period"]).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.config["rsi_period"]).mean()
        rs = gain / (loss + 1e-10)  # Avoid division by zero
        self.df['RSI'] = 100 - (100 / (1 + rs))
        
        # Calculate candle body size and its moving average
        self.df['body'] = (self.df['Close'] - self.df['Open']).abs()
        self.df['avg_body'] = self.df['body'].rolling(window=self.config["avg_window"]).mean()
        
        # Backward fill NaN values caused by the rolling window calculation
        self.df.bfill(inplace=True)

    def scan(self):
        """Main scanning loop to detect supply/demand zones and track trades."""
        print("🔍 Scanning data for supply/demand zones and trade triggers...")
        
        for i in range(1, len(self.df)):
            curr = self.df.iloc[i]
            prev = self.df.iloc[i-1]
            
            # --- Zone Detection Logic ---
            # Example: Bullish engulfing candle with low RSI forms a Demand Zone
            if curr['Close'] > prev['High'] and curr['body'] > (prev['avg_body'] * self.config["body_multiplier"]):
                if curr['RSI'] < self.config["rsi_oversold"]:
                    self.results["demands"].append({
                        "discovery_idx": i, "low": prev['Low'], "high": prev['High'], "status": "Fresh", "t_idx": None
                    })
            
            # Bearish engulfing candle with high RSI forms a Supply Zone
            elif curr['Close'] < prev['Low'] and curr['body'] > (prev['avg_body'] * self.config["body_multiplier"]):
                if curr['RSI'] > self.config["rsi_overbought"]:
                    self.results["supplies"].append({
                        "discovery_idx": i, "low": prev['Low'], "high": prev['High'], "status": "Fresh", "t_idx": None
                    })
            
            # Monitor and update active/triggered trades
            self._update_trades(curr, i)

    def _update_trades(self, curr, i):
        # Buy Logic (Demand Zones)
        for zone in self.results["demands"]:
            if zone["status"] == "Fresh" and i > zone["discovery_idx"]:
                if curr['Low'] <= zone['high']:
                    zone["status"] = "Touched"
                    zone["t_idx"] = i
            
            elif zone["status"] == "Touched" and i > zone["t_idx"]:
                t_high = self.df.iloc[zone["t_idx"]]['High']
                
                if curr['High'] >= t_high:
                    self.results["stats"]["buy_win"] += 1
                    zone["status"] = "Success"
                    self.equity_history.append(self.equity_history[-1] + 20)
                elif curr['Low'] <= zone['low']:
                    self.results["stats"]["buy_fail"] += 1
                    zone["status"] = "Failed"
                    self.equity_history.append(self.equity_history[-1] - 10)

        # Sell Logic (Supply Zones)
        for zone in self.results["supplies"]:
            if zone["status"] == "Fresh" and i > zone["discovery_idx"]:
                if curr['High'] >= zone['low']:
                    zone["status"] = "Touched"
                    zone["t_idx"] = i
            
            elif zone["status"] == "Touched" and i > zone["t_idx"]:
                t_low = self.df.iloc[zone["t_idx"]]['Low']
                
                if curr['Low'] <= t_low:
                    self.results["stats"]["sell_win"] += 1
                    zone["status"] = "Success"
                    self.equity_history.append(self.equity_history[-1] + 20)
                elif curr['High'] >= zone['high']:
                    self.results["stats"]["sell_fail"] += 1
                    zone["status"] = "Failed"
                    self.equity_history.append(self.equity_history[-1] - 10)

    def report(self):
        """Prints a summary text report to the terminal."""
        s = self.results["stats"]
        total_trades = sum(s.values())
        print("\n" + "="*40)
        print("📊 FINAL SCANNER RESULTS REPORT 📊")
        print("="*40)
        print(f"🔹 Total Demand Zones Detected: {len(self.results['demands'])}")
        print(f"🔹 Total Supply Zones Detected: {len(self.results['supplies'])}")
        print(f"🔹 Successful Buy Trades: {s['buy_win']} | Failed: {s['buy_fail']}")
        print(f"🔹 Successful Sell Trades: {s['sell_win']} | Failed: {s['sell_fail']}")
        print(f"💰 Final Account Balance: ${self.equity_history[-1]}")
        print(f"📈 Total Executed Trades: {total_trades}")
        print("="*40)

    def plot_results(self):
        """Generates, saves, and displays the performance dashboard charts."""
        if len(self.equity_history) <= 1:
            print("⚠️ Warning: Not enough closed trades to plot the Equity Curve.")
            return

        print("🎨 Generating charts...")
        plt.style.use('seaborn-v0_8-darkgrid')
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

        # 1. Plot Equity Curve
        trades_count = list(range(len(self.equity_history)))
        ax1.plot(trades_count, self.equity_history, color='#2ecc71', linewidth=2, marker='o', markersize=4)
        ax1.set_title("Equity Curve (Account Growth)", fontsize=12, fontweight='bold')
        ax1.set_xlabel("Number of Closed Trades")
        ax1.set_ylabel("Balance ($)")

        # 2. Plot Trade Outcome Distribution
        s = self.results["stats"]
        labels = ['Buy Win', 'Buy Fail', 'Sell Win', 'Sell Fail']
        values = [s['buy_win'], s['buy_fail'], s['sell_win'], s['sell_fail']]
        colors = ['#27ae60', '#e74c3c', '#2ecc71', '#c0392b']
        
        ax2.bar(labels, values, color=colors)
        ax2.set_title("Trade Distribution", fontsize=12, fontweight='bold')
        ax2.set_ylabel("Count")

        plt.tight_layout()
        
        # Save output image to the current directory
        output_image = "trading_results.png"
        plt.savefig(output_image)
        print(f"💾 Chart successfully saved as: '{output_image}'")
        
        # Open interactive display window
        plt.show()

# --- Execution Block ---
if __name__ == "__main__":
    try:
        # Initialize scanner object with configuration settings
        scanner = GoldScanner(SETTINGS)
        
        # Step-by-step pipeline execution
        scanner.load_data()
        scanner.apply_indicators()
        scanner.scan()
        
        # Output results
        scanner.report()
        scanner.plot_results()
        
        print("\n🚀 Script executed successfully without errors.")
        
    except Exception as e:
        print(f"\n❌ Script crashed due to an unexpected error: {e}") 