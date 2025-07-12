import threading
from pynput import keyboard
import keystroke


if __name__ == "__main__":
    print("Starting keystroke capture. Press PauseBreak to stop.")

    pred_thread = threading.Thread(target=keystroke.predict_and_store, daemon=True)
    pred_thread.start()

    with keyboard.Listener(on_press=keystroke.on_press, on_release=keystroke.on_release) as listener:
        listener.join()

    print("Program ended.")