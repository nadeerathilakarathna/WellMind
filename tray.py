from system_tray import run_tray
import threading


if __name__ == "__main__":
    tray_thread = threading.Thread(target=run_tray, daemon=True)
    tray_thread.start()

