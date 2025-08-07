import customtkinter as ctk
from screens.splash import SplashScreen
from win32api import GetSystemMetrics
import time
import socket
# import ctypes

from services.database import (
    create_user_table,
)

def main():
    # Set the appearance of app
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    root2 = ctk.CTk()
    root2.title("WellMind")

    # Get screen resolution
    width = GetSystemMetrics(0)//1.7
    height = GetSystemMetrics(1)//1.7
    root2.geometry(f"{width}x{height}")
    root2.minsize(width, height)

    # Initialize database
    create_user_table()

    # Start Splash screen
    SplashScreen(root2)

    # Launch avatar as floating overlay
    root2.mainloop()


if __name__ == "__main__":
    main()