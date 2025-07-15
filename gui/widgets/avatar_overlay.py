import tkinter as tk
from PIL import Image, ImageTk
from win32api import GetSystemMetrics

class AvatarOverlay(tk.Toplevel):
    def __init__(self, avatar_path, avatar_size=(120, 120), margin=20):
        super().__init__()
        self.avatar_path = avatar_path
        self.avatar_size = avatar_size
        self.margin = margin

        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.wm_attributes("-transparentcolor", "white")

        avatar_img = Image.open(self.avatar_path).resize(self.avatar_size, Image.Resampling.LANCZOS)
        self.avatar_photo = ImageTk.PhotoImage(avatar_img)

        self.label = tk.Label(self, image=self.avatar_photo, bg="white", cursor="hand2")
        self.label.pack()

        # --- Event Bindings ---
        self.label.bind("<Button-1>", self.start_drag)
        self.label.bind("<B1-Motion>", self.do_drag)
        self.label.bind("<ButtonRelease-1>", self.reset_float_origin)  # After dragging
        self.label.bind("<Double-Button-1>", self.on_avatar_click)
        self.label.bind("<Enter>", self.pause_animation)
        self.label.bind("<Leave>", self.resume_animation)

        screen_width = GetSystemMetrics(0)
        screen_height = GetSystemMetrics(1)
        taskbar_offset = 50
        x = screen_width - self.avatar_size[0] - self.margin
        y = screen_height - self.avatar_size[1] - self.margin - taskbar_offset

        self.geometry(f"{self.avatar_size[0]}x{self.avatar_size[1]}+{x}+{y}")

        # Animation variables
        self.float_direction = 1
        self.float_range = 10
        self.float_speed = 2
        self.paused = False
        self.original_y = y  # Used as base for floating
        self.animate_avatar()

    def update_avatar_image(self, new_image_path):
        avatar_img = Image.open(new_image_path).resize(self.avatar_size, Image.Resampling.LANCZOS)
        self.avatar_photo = ImageTk.PhotoImage(avatar_img)
        self.label.configure(image=self.avatar_photo)
        self.label.image = self.avatar_photo

    def start_drag(self, event):
        self.offset_x = event.x
        self.offset_y = event.y
        self.paused = True  # Optional: pause while dragging

    def do_drag(self, event):
        x = self.winfo_pointerx() - self.offset_x
        y = self.winfo_pointery() - self.offset_y
        self.geometry(f"+{x}+{y}")

    def reset_float_origin(self, event=None):
        # Called after dragging ends to update animation origin
        self.original_y = self.winfo_y()
        self.paused = False  # Resume animation

    def pause_animation(self, event=None):
        self.paused = True

    def resume_animation(self, event=None):
        self.paused = False

    def on_avatar_click(self, event):
        print("🧠 Avatar clicked!")

    def animate_avatar(self):
        if not self.paused:
            current_x = self.winfo_x()
            current_y = self.winfo_y()
            new_y = current_y + self.float_direction * self.float_speed

            if abs(new_y - self.original_y) >= self.float_range:
                self.float_direction *= -1
                new_y = current_y + self.float_direction * self.float_speed

            self.geometry(f"+{current_x}+{new_y}")

        self.after(50, self.animate_avatar)
