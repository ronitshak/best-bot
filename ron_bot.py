import tkinter as tk
from tkinter import ttk
import alpaca_trade_api as tradeapi

class RonBot:
    def __init__(self, root, api_key, api_secret, base_url, go_back_callback):
        self.api = tradeapi.REST(api_key, api_secret, base_url, api_version='v2')
        self.root = root
        self.go_back_callback = go_back_callback
        self.frame = tk.Frame(self.root, bg="#2a2d3e")  # מסגרת לעמוד של הבוט
        self.alerts = []

        # הגדרת עמודי בוטים ושמותיהם
        self.bots = {
            "בדיקת חיבור API": self.show_test_connection,
            "בוט נפח מסחר": self.show_volume_bot,
            "בוט טרנד": self.show_trend_bot,
            "בוט מומנטום": self.show_momentum_bot,
            "בוט פריצות": self.show_breakout_bot,
            "עמוד התראות": self.show_alerts
        }

        # יצירת תפריט עליון ועמודים
        self.create_menu()
        self.create_test_connection_frame()
        self.create_volume_frame()
        self.create_trend_frame()
        self.create_momentum_frame()
        self.create_breakout_frame()
        self.create_alerts_frame()

    def create_menu(self):
        # תפריט עליון עם כפתורים לכל בוט
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

        # כפתור חזרה
        tk.Button(self.topbar, text="Back", command=self.on_back_button, **button_style).pack(side="right", padx=15, pady=5)

    def on_back_button(self):
        self.hide_all_frames()
        self.topbar.pack_forget()
        self.go_back_callback()

    def hide_all_frames(self):
        # הסתרת כל העמודים
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
        except Exception as e:
            self.test_output.config(text=f"API Connection Failed: {e}")

    # === עמוד נפח מסחר ===
    def create_volume_frame(self):
        self.volume_frame = tk.Frame(self.root, bg="#1e1e1f")
        label = tk.Label(self.volume_frame, text="High Volume Stocks", font=("Helvetica", 20, "bold"), fg="white", bg="#1e1e1f")
        label.pack(pady=10)
        description = tk.Label(self.volume_frame, text="בוט זה מזהה מניות עם נפח מסחר חריג בהשוואה לממוצע", font=("Helvetica", 12), fg="white", bg="#1e1e1f")
        description.pack(pady=5)
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
        for symbol in ["AAPL", "GOOGL", "TSLA"]:
            try:
                bars = self.api.get_barset(symbol, 'day', limit=10)[symbol]
                avg_volume = sum(bar.v for bar in bars) / len(bars)
                if bars[-1].v >= 2 * avg_volume:
                    self.volume_table.insert("", "end", values=(symbol, bars[-1].v, avg_volume))
            except Exception as e:
                print(f"Error fetching data for {symbol}: {e}")

    # === עמוד טרנד ===
    def create_trend_frame(self):
        self.trend_frame = tk.Frame(self.root, bg="#1e1e1f")
        label = tk.Label(self.trend_frame, text="Trend Stocks", font=("Helvetica", 20, "bold"), fg="white", bg="#1e1e1f")
        label.pack(pady=10)
        description = tk.Label(self.trend_frame, text="בוט זה מזהה מניות הנמצאות במגמת עלייה", font=("Helvetica", 12), fg="white", bg="#1e1e1f")
        description.pack(pady=5)
        self.trend_table = ttk.Treeview(self.trend_frame, columns=("Ticker", "Change (%)"), show="headings")
        for col in ["Ticker", "Change (%)"]:
            self.trend_table.heading(col, text=col)
        self.trend_table.pack(pady=10)

    def show_trend_bot(self):
        self.hide_all_frames()
        self.trend_frame.pack(fill="both", expand=True)
        self.update_trend_bot()

    def update_trend_bot(self):
        self.trend_table.delete(*self.trend_table.get_children())
        for symbol in ["AAPL", "GOOGL", "TSLA"]:
            try:
                bars = self.api.get_barset(symbol, 'day', limit=5)[symbol]
                change = (bars[-1].c - bars[0].o) / bars[0].o * 100
                if change > 2:
                    self.trend_table.insert("", "end", values=(symbol, f"{change:.2f}%"))
            except Exception as e:
                print(f"Error fetching data for {symbol}: {e}")

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
