import tkinter as tk
from tkinter import ttk
import alpaca_trade_api as tradeapi

import pandas as pd

import pandas as pd

# קריאת הקובץ תוך ציון הקידוד
sp500_df = pd.read_csv("sp500_symbols.csv", encoding='ISO-8859-1')
print(sp500_df.columns)  # הדפסת שמות העמודות
SP500_SYMBOLS = sp500_df['Symbol'].tolist()  # ודא ששם העמודה נכון

class RonBot:
    def __init__(self, root, api_key, api_secret, base_url, go_back_callback):
        try:
            self.api = tradeapi.REST(api_key, api_secret, base_url, api_version='v2')
            print("API initialized successfully.")
        except Exception as e:
            print("API initialization failed in RonBot:", e)
            self.api = None

        self.root = root
        self.go_back_callback = go_back_callback
        self.frame = tk.Frame(self.root, bg="#2a2d3e")
        self.alerts = []

        self.bots = {
            "בדיקת חיבור API": self.show_test_connection,
            "בוט נפח מסחר": self.show_volume_bot,
            "בוט טרנד": self.show_trend_bot,
            "בוט מומנטום": self.show_momentum_bot,
            "בוט פריצות": self.show_breakout_bot,
            "עמוד התראות": self.show_alerts
        }

        self.create_menu()
        self.create_test_connection_frame()
        self.create_volume_frame()
        self.create_trend_frame()
        self.create_momentum_frame()
        self.create_breakout_frame()
        self.create_alerts_frame()

    def create_menu(self):
        self.topbar = tk.Frame(self.root, bg="#2c3e50", height=60)
        self.topbar.pack(side="top", fill="x")

        button_style = {
            "bg": "#e6e6e6",
            "fg": "black",
            "font": ("Helvetica", 14, "bold"),
            "activebackground": "#d9d9d9",
            "activeforeground": "black",
            "borderwidth": 1,
            "highlightthickness": 1,
            "padx": 10,
            "pady": 5,
        }

        for name, command in self.bots.items():
            tk.Button(self.topbar, text=name, command=command, **button_style).pack(side="left", padx=5, pady=5)

        tk.Button(self.topbar, text="Back", command=self.on_back_button, **button_style).pack(side="right", padx=15, pady=5)

    def on_back_button(self):
        self.hide_all_frames()
        self.topbar.pack_forget()
        self.go_back_callback()

    def hide_all_frames(self):
        for frame in [self.test_frame, self.volume_frame, self.trend_frame, self.momentum_frame, self.breakout_frame, self.alerts_frame]:
            frame.pack_forget()

    # === עמוד בדיקת חיבור API ===
    def create_test_connection_frame(self):
        self.test_frame = tk.Frame(self.root, bg="#1e1e1f")
        label = tk.Label(self.test_frame, text="API Connection Test", font=("Helvetica", 20, "bold"), fg="white", bg="#1e1e1f")
        label.pack(pady=10)
        self.test_output = tk.Label(self.test_frame, text="", font=("Helvetica", 14), fg="white", bg="#1e1e1f")
        self.test_output.pack(pady=10)

    def show_test_connection(self):
        self.hide_all_frames()
        self.test_frame.pack(fill="both", expand=True)
        self.check_api_connection()

    def check_api_connection(self):
        try:
            account = self.api.get_account()
            self.test_output.config(text="API Connection Successful")
            print("Account status:", account.status)
        except Exception as e:
            self.test_output.config(text=f"API Connection Failed: {e}")
            print("Error during API connection test:", e)

    # === עמוד נפח מסחר ===
    def create_volume_frame(self):
        self.volume_frame = tk.Frame(self.root, bg="#1e1e1f")
        label = tk.Label(self.volume_frame, text="High Volume Stocks", font=("Helvetica", 20, "bold"), fg="white", bg="#1e1e1f")
        label.pack(pady=10)
        self.volume_table = ttk.Treeview(self.volume_frame, columns=("Ticker", "Volume", "Avg Volume"), show="headings")
        for col in ["Ticker", "Volume", "Avg Volume"]:
            self.volume_table.heading(col, text=col)
        self.volume_table.pack(pady=10)

    def show_volume_bot(self):
        self.hide_all_frames()
        self.volume_frame.pack(fill="both", expand=True)
        self.update_volume_bot()

    def update_volume_bot(self):
        self.volume_table.delete(*self.volume_table.get_children())
        if not self.api:
            print("API not initialized for volume bot.")
            return
        try:
            print(f"Scanning S&P 500 stocks: {len(SP500_SYMBOLS)} symbols.")

            # קריאה מרוכזת לכל המניות עם 10 ימי מסחר אחרונים
            bars_data = self.api.get_bars(SP500_SYMBOLS, '1Day', limit=10)

            # ארגון הנתונים לפי מניה
            bars_by_symbol = {}
            for bar in bars_data:
                if bar.symbol not in bars_by_symbol:
                    bars_by_symbol[bar.symbol] = []
                bars_by_symbol[bar.symbol].append(bar)

            # מעבר על כל מניה ובדיקה של נפח המסחר
            for symbol, bars in bars_by_symbol.items():
                if len(bars) < 10:
                    print(f"Not enough data for {symbol}")
                    continue

                # חישוב ממוצע נפח המסחר
                avg_volume = sum(bar.v for bar in bars) / len(bars)

                # בדיקה אם הנפח האחרון כפול מהממוצע
                if bars[-1].v >= 2 * avg_volume:
                    self.volume_table.insert("", "end", values=(symbol, bars[-1].v, avg_volume))
                print(f"Fetched data for {symbol}: Volume = {bars[-1].v}, Avg Volume = {avg_volume}")

        except Exception as e:
            print("Error fetching data in volume bot:", e)
    # === עמוד טרנד ===
    def create_trend_frame(self):
        self.trend_frame = tk.Frame(self.root, bg="#1e1e1f")
        label = tk.Label(self.trend_frame, text="Trend Stocks", font=("Helvetica", 20, "bold"), fg="white", bg="#1e1e1f")
        label.pack(pady=10)
        self.trend_table = ttk.Treeview(self.trend_frame, columns=("Ticker", "Change (%)"), show="headings")
        for col in ["Ticker", "Change (%)"]:
            self.trend_table.heading(col, text=col)
        self.trend_table.pack(pady=10)

    def show_trend_bot(self):
        self.hide_all_frames()
        self.trend_frame.pack(fill="both", expand=True)
        self.update_trend_bot()

    def update_volume_bot(self):
        self.volume_table.delete(*self.volume_table.get_children())
        if not self.api:
            print("API not initialized for volume bot.")
            return
        try:
            print(f"Scanning S&P 500 stocks: {len(SP500_SYMBOLS)} symbols.")

            # מעבר על כל סימבול של מניה ב-S&P 500 ובקשת נתוני ברים עבור כל אחד
            for symbol in SP500_SYMBOLS:
                bars = list(self.api.get_bars(symbol, '1Day', limit=10))

                if len(bars) < 10:
                    print(f"Not enough data for {symbol}")
                    continue

                # חישוב ממוצע נפח המסחר
                avg_volume = sum(bar.v for bar in bars) / len(bars)

                # בדיקה אם הנפח האחרון כפול מהממוצע
                if bars[-1].v >= 2 * avg_volume:
                    self.volume_table.insert("", "end", values=(symbol, bars[-1].v, avg_volume))
                print(f"Fetched data for {symbol}: Volume = {bars[-1].v}, Avg Volume = {avg_volume}")

        except Exception as e:
            print("Error fetching data in volume bot:", e)

    # === עמוד מומנטום ===
    def create_momentum_frame(self):
        self.momentum_frame = tk.Frame(self.root, bg="#1e1e1f")
        label = tk.Label(self.momentum_frame, text="Momentum Stocks", font=("Helvetica", 20, "bold"), fg="white", bg="#1e1e1f")
        label.pack(pady=10)
        self.momentum_table = ttk.Treeview(self.momentum_frame, columns=("Ticker", "Momentum (%)"), show="headings")
        for col in ["Ticker", "Momentum (%)"]:
            self.momentum_table.heading(col, text=col)
        self.momentum_table.pack(pady=10)

    def show_momentum_bot(self):
        self.hide_all_frames()
        self.momentum_frame.pack(fill="both", expand=True)
        self.update_momentum_bot()

    def update_momentum_bot(self):
        self.momentum_table.delete(*self.momentum_table.get_children())
        if not self.api:
            print("API not initialized for momentum bot.")
            return
        try:
            assets = self.api.list_assets(status='active')
            for asset in assets:
                bars = self.api.get_bars(asset.symbol, '1Day', limit=5).get(asset.symbol)
                if bars:
                    momentum = (bars[-1].c - bars[0].c) / bars[0].c * 100
                    if momentum > 5:
                        self.momentum_table.insert("", "end", values=(asset.symbol, f"{momentum:.2f}%"))
                    print(f"Fetched momentum data for {asset.symbol}: Momentum = {momentum:.2f}%")
                else:
                    print(f"No data found for {asset.symbol}")
        except Exception as e:
            print("Error fetching data in momentum bot:", e)

    # === עמוד פריצות ===
    def create_breakout_frame(self):
        self.breakout_frame = tk.Frame(self.root, bg="#1e1e1f")
        label = tk.Label(self.breakout_frame, text="Breakout Stocks", font=("Helvetica", 20, "bold"), fg="white", bg="#1e1e1f")
        label.pack(pady=10)
        self.breakout_table = ttk.Treeview(self.breakout_frame, columns=("Ticker", "Price"), show="headings")
        for col in ["Ticker", "Price"]:
            self.breakout_table.heading(col, text=col)
        self.breakout_table.pack(pady=10)

    def show_breakout_bot(self):
        self.hide_all_frames()
        self.breakout_frame.pack(fill="both", expand=True)
        self.update_breakout_bot()

    def update_breakout_bot(self):
        self.breakout_table.delete(*self.breakout_table.get_children())
        if not self.api:
            print("API not initialized for breakout bot.")
            return
        try:
            assets = self.api.list_assets(status='active')
            for asset in assets:
                bars = self.api.get_bars(asset.symbol, '1Day', limit=20).get(asset.symbol)
                if bars:
                    max_price = max(bar.h for bar in bars[:-1])
                    if bars[-1].c > max_price:
                        self.breakout_table.insert("", "end", values=(asset.symbol, bars[-1].c))
                    print(f"Fetched breakout data for {asset.symbol}: Price = {bars[-1].c}, Previous Max = {max_price}")
                else:
                    print(f"No data found for {asset.symbol}")
        except Exception as e:
            print("Error fetching data in breakout bot:", e)

    # === עמוד התראות ===
    def create_alerts_frame(self):
        self.alerts_frame = tk.Frame(self.root, bg="#1e1e1f")
        label = tk.Label(self.alerts_frame, text="Alerts", font=("Helvetica", 20, "bold"), fg="white", bg="#1e1e1f")
        label.pack(pady=10)
        self.alerts_table = ttk.Treeview(self.alerts_frame, columns=("Time", "Ticker", "Alert"), show="headings")
        for col in ["Time", "Ticker", "Alert"]:
            self.alerts_table.heading(col, text=col)
        self.alerts_table.pack(pady=10)

    def show_alerts(self):
        self.hide_all_frames()
        self.alerts_frame.pack(fill="both", expand=True)

    def show(self):
        self.frame.pack(fill="both", expand=True)

    def hide(self):
        self.frame.pack_forget()
