import ctypes
import win32con
import win32gui
import win32api
import time

WM_POWERBROADCAST = 0x0218
PBT_APMPOWERSTATUSCHANGE = 0xA

class SYSTEM_POWER_STATUS(ctypes.Structure):
    _fields_ = [
        ("ACLineStatus", ctypes.c_byte),
        ("BatteryFlag", ctypes.c_byte),
        ("BatteryLifePercent", ctypes.c_byte),
        ("Reserved1", ctypes.c_byte),
        ("BatteryLifeTime", ctypes.c_ulong),
        ("BatteryFullLifeTime", ctypes.c_ulong),
    ]

class PowerEventListener:
    def __init__(self):
        message_map = { WM_POWERBROADCAST: self.on_power_broadcast }
        wc = win32gui.WNDCLASS()
        hinst = wc.hInstance = win32api.GetModuleHandle(None)
        wc.lpszClassName = "PowerMonitorWindow"
        wc.lpfnWndProc = message_map
        win32gui.RegisterClass(wc)
        self.hwnd = win32gui.CreateWindow(wc.lpszClassName, "Power Monitor",
                                          0, 0, 0, 0, 0, 0, 0, hinst, None)

    def on_power_broadcast(self, hwnd, msg, wparam, lparam):
        if wparam == PBT_APMPOWERSTATUSCHANGE:
            status = SYSTEM_POWER_STATUS()
            ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(status))
            if status.ACLineStatus == 1:
                print("[🔌] Power Connected")
            elif status.ACLineStatus == 0:
                print("[🔋] Running on Battery")
            if status.BatteryLifePercent < 20:
                print(f"[⚠️] Battery Low: {status.BatteryLifePercent}%")
        return True

    def run(self):
        while True:
            win32gui.PumpWaitingMessages()
            time.sleep(0.1)
