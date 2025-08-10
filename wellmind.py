import threading
import multiprocessing
from services.database import log_error
import sys

from services.database import create_user_table, fetch_latest_user




import customtkinter as ctk
from screens.splash import SplashScreen
from win32api import GetSystemMetrics
import time
import socket
# import ctypes

from services.database import (
    create_user_table,
)


def dashboard():
    # Set the appearance of app
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    root.title("WellMind")

    # Get screen resolution
    width = GetSystemMetrics(0)//1.7
    height = GetSystemMetrics(1)//1.7
    root.geometry(f"{width}x{height}")
    root.minsize(width, height)


    # Initialize database
    create_user_table()

    # Start Splash screen
    SplashScreen(root)

    # Launch avatar as floating overlay
    root.mainloop()


if __name__ == "__main__":
    multiprocessing.freeze_support()
    print(sys.argv)
    if len(sys.argv) == 2 and sys.argv[1].lower() == 'start':
        print(sys.argv[1])
        create_user_table()
        if fetch_latest_user() is None:
            from system_tray import run_tray
            tray_thread = threading.Thread(target=run_tray,)
            tray_thread.start()


            dashboard_thread = threading.Thread(target=dashboard,)
            dashboard_thread.start()
            dashboard_thread.join()

            from pynput import keyboard
            import keystroke
            from facial_expression import facial_expression_monitoring
            from facialExpressionSummary import calculate_facial_expression_summary
            import avatar


            while fetch_latest_user() is None:
                time.sleep(1)

            facial_expression_thread = threading.Thread(target=facial_expression_monitoring, daemon=True)
            pred_thread = threading.Thread(target=keystroke.predict_and_store, daemon=True)

            facial_expression_thread.start()
            
            pred_thread.start()

            avatar_thread = threading.Thread(target=avatar.run_avatar,daemon=True)
            avatar_thread.start()

            facial_expression_summary_thread = threading.Thread(target=calculate_facial_expression_summary,daemon=True)
            facial_expression_summary_thread.start()

            try:
                listener = keyboard.Listener(
                    on_press=keystroke.on_press,
                    on_release=keystroke.on_release
                )

                # Wrap listener.start() and keep thread alive
                thread = threading.Thread(target=listener.run, daemon=True)  # make it a daemon thread
                thread.start()

            except Exception as e:
                error = f'[ERROR] main, keyboard listener: {e}'
                log_error(error)

            tray_thread.join()
            
            print("Program ended.")
            sys.exit(0)

        else:

            from pynput import keyboard
            import keystroke
            from facial_expression import facial_expression_monitoring
            from facialExpressionSummary import calculate_facial_expression_summary
            from system_tray import run_tray
            import avatar


            facial_expression_thread = threading.Thread(target=facial_expression_monitoring, daemon=True)
            pred_thread = threading.Thread(target=keystroke.predict_and_store, daemon=True)

            facial_expression_thread.start()
            
            pred_thread.start()

            

            avatar_thread = threading.Thread(target=avatar.run_avatar,daemon=True)
            avatar_thread.start()

            facial_expression_summary_thread = threading.Thread(target=calculate_facial_expression_summary,daemon=True)
            facial_expression_summary_thread.start()

            tray_thread = threading.Thread(target=run_tray,)
            tray_thread.start()

            
            

            try:
                listener = keyboard.Listener(
                    on_press=keystroke.on_press,
                    on_release=keystroke.on_release
                )

                # Wrap listener.start() and keep thread alive
                thread = threading.Thread(target=listener.run, daemon=True)  # make it a daemon thread
                thread.start()

            except Exception as e:
                error = f'[ERROR] main, keyboard listener: {e}'
                log_error(error)

            tray_thread.join()
            
            print("Program ended.")
            sys.exit(0)
    else:
        dashboard()
