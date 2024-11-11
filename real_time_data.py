import tkinter as tk
from tkinter import ttk
import alpaca_trade_api as tradeapi

class RealTimeData:
    def __init__(self, parent, api_key, api_secret, base_url, go_back_callback):
        self.parent = parent
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url
        self.api = tradeapi.REST(api_key, api_secret, base_url, api_version='v2')
        self.go_back_callback = go_back_callback

        # יצירת מסגרת עבור העמוד
        self.frame = tk.Frame(self.parent, bg="#1e1e1f")
        self.create_ui()

    def create_ui(self):
        # כותרת העמוד
        label = tk.Label(self.frame, text="מידע בזמן אמת - מניות מובילות", font=("Helvetica", 20, "bold"), fg="white", bg="#1e1e1f")
        label.pack(pady=10)

        # כפתור חזרה
        tk.Button(self.frame, text="חזור", command=self.go_back_callback, bg="#333", fg="white", font=("Helvetica", 12, "bold")).pack(pady=5)

        # תצוגת מניות עליות
        up_label = tk.Label(self.frame, text="20 מניות שעלו הכי הרבה:", font=("Helvetica", 16), fg="green", bg="#1e1e1f")
        up_label.pack(pady=(20, 5))
        self.up_table = ttk.Treeview(self.frame, columns=("Ticker", "Change (%)"), show="headings", height=10)
        for col in ["Ticker", "Change (%)"]:
            self.up_table.heading(col, text=col)
        self.up_table.pack(pady=10)

        # תצוגת מניות ירידות
        down_label = tk.Label(self.frame, text="20 מניות שירדו הכי הרבה:", font=("Helvetica", 16), fg="red", bg="#1e1e1f")
        down_label.pack(pady=(20, 5))
        self.down_table = ttk.Treeview(self.frame, columns=("Ticker", "Change (%)"), show="headings", height=10)
        for col in ["Ticker", "Change (%)"]:
            self.down_table.heading(col, text=col)
        self.down_table.pack(pady=10)

        # כפתור רענון נתונים
        tk.Button(self.frame, text="רענן נתונים", command=self.refresh_data, bg="blue", fg="white", font=("Helvetica", 12, "bold")).pack(pady=15)

    def show(self):
        self.frame.pack(fill="both", expand=True)
        self.refresh_data()  # טוען נתונים מיד עם הכניסה לעמוד

    def hide(self):
        self.frame.pack_forget()

    def refresh_data(self):
        # מחיקת נתונים קודמים מהטבלאות
        self.up_table.delete(*self.up_table.get_children())
        self.down_table.delete(*self.down_table.get_children())

        try:
            # שליפת הנתונים מה-API של אלפקה
            assets = self.api.list_assets(status='active')
            up_stocks, down_stocks = [], []

            for asset in assets[:100]:  # דוגמה: עובר רק על 100 מניות כדי לחסוך זמן
                bars = self.api.get_barset(asset.symbol, 'day', limit=2)[asset.symbol]
                if len(bars) == 2:
                    change_percent = ((bars[-1].c - bars[-2].c) / bars[-2].c) * 100
                    if change_percent > 0:
                        up_stocks.append((asset.symbol, change_percent))
                    else:
                        down_stocks.append((asset.symbol, change_percent))

            # מיון ובחירת 20 המניות המובילות בעלייה וירידה
            up_stocks = sorted(up_stocks, key=lambda x: x[1], reverse=True)[:20]
            down_stocks = sorted(down_stocks, key=lambda x: x[1])[:20]

            # הוספת הנתונים לטבלאות
            for symbol, change in up_stocks:
                self.up_table.insert("", "end", values=(symbol, f"{change:.2f}%"))
            for symbol, change in down_stocks:
                self.down_table.insert("", "end", values=(symbol, f"{change:.2f}%"))

        except Exception as e:
            print(f"Error fetching real-time data: {e}")
