import threading
from pynput import keyboard
import keystroke
from facial_expression import facial_expression_monitoring
import multiprocessing
from facialExpressionSummary import calculate_facial_expression_summary
from system_tray import run_tray

# import customtkinter as ctk
# import tkinter as tk
# from win32api import GetSystemMetrics
# import threading
# import time
# from widgets.avatar_overlay import AvatarOverlay

import avatar




if __name__ == "__main__":
    multiprocessing.freeze_support()

    facial_expression_thread = threading.Thread(target=facial_expression_monitoring, daemon=True)
    pred_thread = threading.Thread(target=keystroke.predict_and_store, daemon=True)


    facial_expression_thread.start()
    
    pred_thread.start()

    avatar_thread = threading.Thread(target=avatar.run_avatar, daemon=True)
    avatar_thread.start()

    facial_expression_summary_thread = threading.Thread(target=calculate_facial_expression_summary, daemon=True)
    facial_expression_summary_thread.start()

    tray_thread = threading.Thread(target=run_tray,daemon=True)
    tray_thread.start()
    

    with keyboard.Listener(on_press=keystroke.on_press, on_release=keystroke.on_release) as listener:
        listener.join()

    # def start_keyboard_listener():
    #     listener = keyboard.Listener(on_press=keystroke.on_press,on_release=keystroke.on_release)
    #     listener.start()  # non-blocking
    #     listener.join()

    # keyboard_thread = threading.Thread(target=start_keyboard_listener, daemon=True)
    # keyboard_thread.start()

    
    
    

    print("Program ended.")




