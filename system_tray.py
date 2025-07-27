import pystray
import PIL.Image
from services.database import Configuration
import os
from report.report_generator import start_report_generation
import threading
import subprocess
import sys

logo = PIL.Image.open("assets/logo/logo.png").copy()

configuration = Configuration()

def generate_report():
    report_thread = start_report_generation()
    # report_thread.join()

def exit_program(icon):
    try:
        icon.stop()  # stops the tray icon mainloop cleanly
        sys.exit(0)
    except:
        pass

def run_tray():
    # ======= Main Tray Menu ========
    tray_menu = pystray.Menu(
        pystray.MenuItem("WellMind", lambda: print("App: WellMind"), default=True),
        pystray.MenuItem("Enable Avatar", lambda: configuration.avatar_set_status(not(configuration.avatar_is_running())),checked=lambda item:configuration.avatar_is_running()),
        pystray.MenuItem("Enable Facial Expressions",lambda: configuration.facial_expression_set_status(not(configuration.facial_expression_is_running())),checked=lambda item:configuration.facial_expression_is_running()),
        pystray.MenuItem("Enable Keystroke Dynamics",lambda: configuration.keystroke_dynamics_set_status(not(configuration.keystroke_dynamics_is_running())),checked=lambda item:configuration.keystroke_dynamics_is_running()),
        pystray.MenuItem("Enable Recommendations",lambda: configuration.notifications_set_status(not(configuration.notifications_is_running())),checked=lambda item:configuration.notifications_is_running()),
        pystray.MenuItem("Generate Report", lambda: generate_report()),
        # pystray.MenuItem("Avatar", avatar_menu),  # Nested Menu
        pystray.MenuItem("Exit", lambda: exit_program(icon))  # Exit
    )

    # ======= Run the Tray Icon ========
    icon = pystray.Icon("WellMind", logo, "WellMind Tray", tray_menu)
    icon.run()

# run_tray()