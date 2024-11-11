import os
import tkinter as tk
from tkinter import ttk
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
from real_time_data import RealTimeData  # עמוד מידע בזמן אמת
from ron_bot import RonBot  # עמוד הבוט של רון

# טוען את המפתחות מקובץ .env
load_dotenv()
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')
BASE_URL = 'https://paper-api.alpaca.markets'

# יצירת חלון ראשי
root = tk.Tk()
root.title("Trading Bot Dashboard")
root.geometry("1200x800")
root.config(bg="#2a2d3e")  # רקע כהה יוקרתי

# הגדרת חיבור API עם alpaca
api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL, api_version='v2')

# פונקציה לבדוק את החיבור ל-API
def test_api_connection():
    try:
        account = api.get_account()
        print("API connection successful. Account status:", account.status)
    except Exception as e:
        print("API connection failed:", e)

# קריאה לפונקציה כדי לבדוק את החיבור מיד אחרי ההגדרות
test_api_connection()

# יצירת סגנון כפתור מותאם אישית
style = ttk.Style()
style.configure("TButton", font=("Helvetica", 14, "bold"), padding=10)
style.map("TButton",
          foreground=[("!disabled", "white")],
          background=[("!disabled", "#4CAF50"), ("pressed", "#3e8e41")],
          relief=[("pressed", "flat"), ("!pressed", "raised")
          ])

# פונקציה ליצירת כפתור עם סגנון מותאם
def create_button(master, text, command=None):
    return ttk.Button(
        master,
        text=text,
        command=command,
        style="TButton"
    )

# === מסך פתיחה ===
splash_screen = tk.Frame(root, bg="#2a2d3e")
splash_label = tk.Label(splash_screen, text="Welcome to Ron's Trading Bot 😊", font=("Helvetica", 28, "bold"),
                        fg="#ffffff", bg="#2a2d3e")
splash_label.pack(pady=30)
enter_button = create_button(splash_screen, "Enter", command=lambda: show_main_menu())
enter_button.pack(pady=20)

def show_splash_screen():
    splash_screen.pack(fill="both", expand=True)

def hide_splash_screen():
    splash_screen.pack_forget()

# === תפריט עליון ===
topbar = tk.Frame(root, bg="#1f1f1f", height=60)

def show_topbar():
    if not topbar.winfo_ismapped():  # להציג את התפריט העליון רק אם הוא לא מוצג
        topbar.pack(side="top", fill="x")
        for widget in topbar.winfo_children():  # מנקה את התפריט העליון
            widget.destroy()
        create_button(topbar, "תפריט ראשי", command=show_main_menu).pack(side="left", padx=5)
        create_button(topbar, "בוט של רון", command=show_ron_bot).pack(side="left", padx=5)
        create_button(topbar, "מידע בזמן אמת", command=show_real_time_data).pack(side="left", padx=5)
        create_button(topbar, "Exit", command=root.quit).pack(side="right", padx=10)

# === עמוד ראשי ===
main_menu = tk.Frame(root, bg="#2a2d3e")

def show_main_menu():
    hide_all_frames()
    hide_splash_screen()
    show_topbar()
    main_menu.pack(fill="both", expand=True)

# משתנים כדי לשמור את מופעי הבוטים כך שלא ייווצרו מחדש כל פעם
real_time_data = None
ron_bot = None

# עמוד מידע בזמן אמת
def show_real_time_data():
    global real_time_data
    hide_all_frames()
    if real_time_data is None:
        real_time_data = RealTimeData(root, API_KEY, API_SECRET, BASE_URL, go_back_callback=show_main_menu)
    real_time_data.show()

# עמוד הבוט של רון
# בקובץ main.py
ron_bot = None  # משתנה גלובלי עבור הבוט של רון

def show_ron_bot():
    global ron_bot
    hide_all_frames()  # הסתרת כל העמודים הקודמים
    if ron_bot is None:  # יצירה חד-פעמית של הבוט
        ron_bot = RonBot(root, API_KEY, API_SECRET, BASE_URL, go_back_callback=show_main_menu)
    ron_bot.show()  # הצגת העמוד של הבוט


# עמודי הצבעים
color_frames = {}

def create_color_frame(color_name, color_code):
    frame = tk.Frame(root, bg=color_code)
    tk.Label(frame, text=f"{color_name} Screen", font=("Helvetica", 24, "bold"), fg="white", bg=color_code).pack(
        pady=20)
    create_button(frame, "Back", command=show_main_menu).pack(pady=20)
    color_frames[color_name] = frame

create_color_frame("Red", "#b22222")
create_color_frame("Blue", "#1e90ff")
create_color_frame("Yellow", "#ffd700")

def show_color_screen(color_name):
    hide_all_frames()
    color_frames[color_name].pack(fill="both", expand=True)

# פונקציה הסתרת כל העמודים
def hide_all_frames():
    main_menu.pack_forget()
    if ron_bot is not None:
        ron_bot.hide()
    if real_time_data is not None:
        real_time_data.hide()
    for frame in color_frames.values():
        frame.pack_forget()

# === מבנה תפריט ראשי עם כפתורים מסודרים ומעוצבים ===
def create_main_menu():
    main_menu.pack(fill="both", expand=True)
    label = tk.Label(main_menu, text="Dashboard", font=("Helvetica", 28, "bold"), fg="#ffffff", bg="#2a2d3e")
    label.pack(pady=30)

    create_button(main_menu, "בוט של רון", command=show_ron_bot).pack(pady=10)
    create_button(main_menu, "מידע בזמן אמת", command=show_real_time_data).pack(pady=10)
    create_button(main_menu, "Red Screen", command=lambda: show_color_screen("Red")).pack(pady=10)
    create_button(main_menu, "Blue Screen", command=lambda: show_color_screen("Blue")).pack(pady=10)
    create_button(main_menu, "Yellow Screen", command=lambda: show_color_screen("Yellow")).pack(pady=10)

# הצגת מסך פתיחה בעת הפעלת התוכנה
show_splash_screen()

# הפעלת הלולאה הראשית
root.mainloop()
