import threading
from pynput import keyboard
import keystroke
from facial_expression import facial_expression_monitoring
import multiprocessing
from facialExpressionSummary import calculate_facial_expression_summary
from system_tray import run_tray
from services.database import log_error
import sys

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

    avatar_thread = threading.Thread(target=avatar.run_avatar,daemon=True)
    avatar_thread.start()

    facial_expression_summary_thread = threading.Thread(target=calculate_facial_expression_summary,daemon=True)
    facial_expression_summary_thread.start()

    tray_thread = threading.Thread(target=run_tray,)
    tray_thread.start()
    

    # with keyboard.Listener(on_press=keystroke.on_press, on_release=keystroke.on_release) as listener:
    #     listener.join()


    # try:
    #     with keyboard.Listener(
    #         on_press=keystroke.on_press, 
    #         on_release=keystroke.on_release
    #     ) as listener:
    #         listener.join()
    # except Exception as e:
    #     error = f'[ERROR] main, keyboard listner: {e}'
    #     log_error(error)

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



