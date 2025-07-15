import customtkinter as ctk
from screens.splash import SplashScreen
from win32api import GetSystemMetrics
import threading
import time
import socket
import ctypes
from services.database import (
    create_user_table,
    create_preferences_tables,
    import_preferences_from_excel
)
from widgets.avatar_overlay import AvatarOverlay

# Import Listeners
from listeners.usb_listener import USBEventListener
from listeners.power_listener import PowerEventListener, SYSTEM_POWER_STATUS, PBT_APMPOWERSTATUSCHANGE
from listeners.internet_connectivity_listener import InternetEventListener

def main():
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
    create_preferences_tables()
    import_preferences_from_excel()

    # Start Splash screen
    SplashScreen(root)

    # Launch avatar as floating overlay
    threading.Thread(target=launch_avatar_overlay, daemon=True).start()

    # Start system listeners in background
    threading.Thread(target=start_usb_listener, daemon=True).start()
    threading.Thread(target=start_power_listener, daemon=True).start()
    threading.Thread(target=start_internet_listener, daemon=True).start()

    root.mainloop()

# Launch avatar
def launch_avatar_overlay():
    global avatar_overlay_instance
    time.sleep(1.0)
    avatar_overlay_instance = AvatarOverlay("assets/animations/default_avatar.png")
    avatar_overlay_instance.mainloop()

# Event handlers for usb plug and unplug
def on_usb_change(event_type):
    if avatar_overlay_instance:
        if event_type == "inserted":
            avatar_overlay_instance.update_avatar_image("assets/animations/plugged_usb.png")
            time.sleep(5)
            avatar_overlay_instance.update_avatar_image("assets/animations/default_avatar.png")
        elif event_type == "removed":
            avatar_overlay_instance.update_avatar_image("assets/animations/unplugged_usb.png")
            time.sleep(5)
            avatar_overlay_instance.update_avatar_image("assets/animations/default_avatar.png")

# Event handlers for system power battery/plug to the power/battery low
def on_power_change(status):
    if avatar_overlay_instance:
        if status == "on_ac":
            avatar_overlay_instance.update_avatar_image("assets/animations/connect_power.png")
            time.sleep(5)
            avatar_overlay_instance.update_avatar_image("assets/animations/default_avatar.png")
        elif status == "on_battery":
            avatar_overlay_instance.update_avatar_image("assets/animations/disconnect_power.png")
            time.sleep(5)
            avatar_overlay_instance.update_avatar_image("assets/animations/default_avatar.png")
        elif status == "low_battery":
            avatar_overlay_instance.update_avatar_image("assets/animations/battery_low.png")
            time.sleep(5)
            avatar_overlay_instance.update_avatar_image("assets/animations/default_avatar.png")


# Event handlers for internet connection state or unstable
def on_internet_change(status):
    if avatar_overlay_instance:
        if status == "connected":
            avatar_overlay_instance.update_avatar_image("assets/animations/internet_connected.png")
            time.sleep(5)
            avatar_overlay_instance.update_avatar_image("assets/animations/default_avatar.png")
        elif status == "disconnected":
            avatar_overlay_instance.update_avatar_image("assets/animations/internet_disconnected.png")
            time.sleep(5)
            avatar_overlay_instance.update_avatar_image("assets/animations/default_avatar.png")


# Listener wrappers
def start_usb_listener():
    usb = USBEventListener(on_usb_change=on_usb_change)
    usb.run()

def start_power_listener():
    class CustomPowerListener(PowerEventListener):
        def on_power_broadcast(self, hwnd, msg, wparam, lparam):
            if wparam == PBT_APMPOWERSTATUSCHANGE:
                status = SYSTEM_POWER_STATUS()
                ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(status))
                if status.ACLineStatus == 1:
                    print("[🔌] Power Connected")
                    on_power_change("on_ac")
                elif status.ACLineStatus == 0:
                    print("[🔋] Running on Battery")
                    on_power_change("on_battery")
                if status.BatteryLifePercent < 20:
                    print(f"[⚠️] Battery Low: {status.BatteryLifePercent}%")
                    on_power_change("low_battery")
            return True

    def power_loop():
        CustomPowerListener().run()

    # Start it in its own daemon thread
    threading.Thread(target=power_loop, daemon=True).start()

def start_internet_listener():
    internet = InternetEventListener(on_internet_change=on_internet_change)
    internet.start()
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()