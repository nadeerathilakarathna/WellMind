import pystray
import PIL.Image
from services.database import Configuration
import os
from report.report_generator import start_report_generation
import threading
import subprocess
import sys
import subprocess
import os


def visit_dashboard():
    subprocess.Popen(
    'start wellmind',
    shell=True,
    creationflags=subprocess.CREATE_NO_WINDOW,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL)
    print("Dashboard opened")

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

def set_avatar_male():
    configuration.set_avatar("male")
    
def set_avatar_female():
    configuration.set_avatar("female")

def is_avatar_male(item):
    return configuration.get_current_avatar() == "male"

def is_avatar_female(item):
    return configuration.get_current_avatar() == "female"
 

def run_tray():

    # ======= Avatar Submenu ========
    avatar_menu = pystray.Menu(
        pystray.MenuItem("Male", set_avatar_male, checked=is_avatar_male, radio=True),
        pystray.MenuItem("Female", set_avatar_female, checked=is_avatar_female, radio=True)
    )

    # ======= Main Tray Menu ========
    tray_menu = pystray.Menu(
        pystray.MenuItem("WellMind", lambda: visit_dashboard(), default=True),
        pystray.MenuItem("Avatar", avatar_menu),  # Nested Menu
        pystray.MenuItem("Enable Avatar", lambda: configuration.avatar_set_status(not(configuration.avatar_is_running())),checked=lambda item:configuration.avatar_is_running()),
        pystray.MenuItem("Enable Facial Expressions",lambda: configuration.facial_expression_set_status(not(configuration.facial_expression_is_running())),checked=lambda item:configuration.facial_expression_is_running()),
        pystray.MenuItem("Enable Keystroke Dynamics",lambda: configuration.keystroke_dynamics_set_status(not(configuration.keystroke_dynamics_is_running())),checked=lambda item:configuration.keystroke_dynamics_is_running()),
        pystray.MenuItem("Enable Recommendations",lambda: configuration.notifications_set_status(not(configuration.notifications_is_running())),checked=lambda item:configuration.notifications_is_running()),
        pystray.MenuItem("Generate Report", lambda: generate_report()),
        pystray.MenuItem("Exit", lambda: exit_program(icon))  # Exit
    )

    # ======= Run the Tray Icon ========
    icon = pystray.Icon("WellMind", logo, "WellMind Tray", tray_menu)
    icon.run()

# run_tray()