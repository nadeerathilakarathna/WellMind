import tkinter as tk
from PIL import Image, ImageTk
import threading
import time
from screeninfo import get_monitors
import os


def show_modern_notification(rec_id, message, on_like, on_dislike, duration=15):
    def run():
        screen = get_monitors()[0]
        width, height = 500, 250
        x = screen.width - width - 20
        y = screen.height - height - 60

        root = tk.Tk()
        root.overrideredirect(True)
        root.attributes("-topmost", True)
        root.geometry(f"{width}x{height}+{x}+{y}")
        root.configure(bg="#333333")

        frame = tk.Frame(root, bg="#333333")
        frame.pack(expand=True, fill="both", padx=10, pady=10)

        title = tk.Label(frame, text=f"Recommendation [{rec_id}]", font=("Segoe UI", 10, "bold"),
                         fg="#00FFCC", bg="#333333", anchor="w")
        title.pack(fill="x")

        msg = tk.Label(frame, text=message, font=("Segoe UI", 10),
                       fg="#FFFFFF", bg="#333333", wraplength=500, justify="left")
        msg.pack(fill="x", pady=(5, 10))

        btn_frame = tk.Frame(frame, bg="#333333")
        btn_frame.pack()

        # Load icons
        icon_path = os.path.join("assets", "icons")
        like_img = Image.open(os.path.join(icon_path, "thumb_up.png")).resize((24, 24))
        dislike_img = Image.open(os.path.join(icon_path, "thumb_down.png")).resize((24, 24))

        like_photo = ImageTk.PhotoImage(like_img)
        dislike_photo = ImageTk.PhotoImage(dislike_img)

        # Keep references
        root.like_photo = like_photo
        root.dislike_photo = dislike_photo

        like_btn = tk.Button(
            btn_frame,
            image=like_photo,
            text=" Like",
            compound="left",
            font=("Segoe UI", 10, "bold"),
            bg="white",
            fg="black",
            relief="flat",
            padx=10,
            pady=5,
            command=lambda: [on_like(), root.destroy()]
        )
        like_btn.pack(side="left", padx=20)

        dislike_btn = tk.Button(
            btn_frame,
            image=dislike_photo,
            text=" Unlike",
            compound="left",
            font=("Segoe UI", 10, "bold"),
            bg="white",
            fg="black",
            relief="flat",
            padx=10,
            pady=5,
            command=lambda: [on_dislike(), root.destroy()]
        )
        dislike_btn.pack(side="right", padx=20)

        def auto_close():
            time.sleep(duration)
            try:
                root.destroy()
            except:
                pass

        threading.Thread(target=auto_close, daemon=True).start()
        root.mainloop()

    threading.Thread(target=run, daemon=True).start()
