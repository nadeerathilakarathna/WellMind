import wmi
import time
import threading
import win32gui
import pythoncom

class USBEventListener:
    def __init__(self, on_usb_change=None):
        self.running = True
        self.on_usb_change = on_usb_change

    def handle_usb_events(self):
        pythoncom.CoInitialize()
        wmi_service = wmi.WMI()
        insert_watcher = wmi_service.watch_for(notification_type="Creation", wmi_class="Win32_USBHub")
        remove_watcher = wmi_service.watch_for(notification_type="Deletion", wmi_class="Win32_USBHub")

        while self.running:
            try:
                inserted = insert_watcher(timeout_ms=500)
                print("✅ USB Inserted:", inserted.DeviceID)
                if self.on_usb_change:
                    self.on_usb_change("inserted")
            except wmi.x_wmi_timed_out:
                pass
            except Exception:
                pass

            try:
                removed = remove_watcher(timeout_ms=500)
                print("❌ USB Removed:", removed.DeviceID)
                if self.on_usb_change:
                    self.on_usb_change("removed")
            except wmi.x_wmi_timed_out:
                pass
            except Exception:
                pass

        pythoncom.CoUninitialize()

    def run(self):
        print("🔌 Listening for USB events...")
        threading.Thread(target=self.handle_usb_events, daemon=True).start()