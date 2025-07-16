import customtkinter as ctk
from screens.splash import SplashScreen
from win32api import GetSystemMetrics
import time
import socket
import ctypes

from services.database import (
    create_user_table,
)

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

    # Start Splash screen
    SplashScreen(root)

    # Launch avatar as floating overlay
    root.mainloop()


if __name__ == "__main__":
    main()