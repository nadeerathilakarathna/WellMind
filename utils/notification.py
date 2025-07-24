import tkinter as tk
import threading
import time
from screeninfo import get_monitors

def show_modern_notification(rec_id, message, on_like, on_dislike, duration=15):
    def run():
        screen = get_monitors()[0]
        width = 420
        
        # Calculate dynamic height based on message length
        # Estimate characters per line (accounting for wrapping at 380px width)
        chars_per_line = 50  # Approximate for Segoe UI 11pt
        estimated_lines = max(1, len(message) // chars_per_line + (1 if len(message) % chars_per_line else 0))
        
        # Calculate height: header(55) + message(line_height*lines + padding) + buttons(65) + progress(3) + margins
        base_height = 55 + 65 + 3 + 40  # Fixed components height
        message_height = max(30, estimated_lines * 18 + 20)  # Dynamic message area
        height = base_height + message_height
        
        # Ensure minimum and maximum height
        height = max(180, min(height, 400))
        
        x = screen.width - width - 20
        y = screen.height - height - 60

        root = tk.Tk()
        root.overrideredirect(True)
        root.attributes("-topmost", True)
        root.geometry(f"{width}x{height}+{x}+{y}")
        
        # Modern gradient-like background with rounded appearance
        root.configure(bg="#1A1A1A")
        
        # Get current time and determine greeting + colors
        import datetime
        current_hour = datetime.datetime.now().hour
        
        if 5 <= current_hour < 12:
            greeting = "Good Morning! ☀️"
            greeting_color = "#FFB74D"  # Orange for morning
            progress_color = "#FFB74D"  # Same as greeting color
        elif 12 <= current_hour < 17:
            greeting = "Good Afternoon! ⛅"
            greeting_color = "#42A5F5"  # Blue for afternoon
            progress_color = "#42A5F5"  # Same as greeting color
        elif 17 <= current_hour < 21:
            greeting = "Good Evening! 🌅"
            greeting_color = "#FF7043"  # Orange-red for evening
            progress_color = "#FF7043"  # Same as greeting color
        else:
            greeting = "Good Night! 🌙"
            greeting_color = "#9C27B0"  # Purple for night
            progress_color = "#9C27B0"  # Same as greeting color
        
        # Progress bar for auto-close timer - AT THE VERY TOP
        progress_frame = tk.Frame(root, bg="#1A1A1A", height=3)
        progress_frame.pack(side="top", fill="x")
        progress_frame.pack_propagate(False)
        
        progress_bar = tk.Frame(progress_frame, bg=progress_color, height=3)
        progress_bar.pack(side="left", fill="y")
        
        # Add subtle border effect (below progress bar)
        border_frame = tk.Frame(root, bg="#2D2D2D", highlightthickness=0)
        border_frame.pack(fill="both", expand=True, padx=1, pady=1)
        
        # Main content frame with modern spacing
        main_frame = tk.Frame(border_frame, bg="#1A1A1A", highlightthickness=0)
        main_frame.pack(fill="both", expand=True, padx=1, pady=1)

        # Header section with greeting
        header_frame = tk.Frame(main_frame, bg="#1A1A1A", height=40)
        header_frame.pack(fill="x", padx=20, pady=(15, 0))
        header_frame.pack_propagate(False)
        
        # Greeting label with time-based styling
        greeting_label = tk.Label(
            header_frame,
            text=greeting,
            font=("Segoe UI", 11, "bold"),
            fg=greeting_color,
            bg="#1A1A1A"
        )
        greeting_label.pack(side="left", anchor="w")

        # Message content with modern typography - dynamic height
        content_frame = tk.Frame(main_frame, bg="#1A1A1A")
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)

        msg_label = tk.Label(
            content_frame,
            text=message,
            font=("Segoe UI", 11),
            fg="#E8E8E8",
            bg="#1A1A1A",
            wraplength=380,
            justify="left",
            anchor="nw"
        )
        msg_label.pack(fill="both", expand=True, anchor="nw")

        # Modern button section - fixed position at bottom
        action_frame = tk.Frame(main_frame, bg="#1A1A1A", height=50)
        action_frame.pack(side="bottom", fill="x", padx=20, pady=(10, 15))
        action_frame.pack_propagate(False)

        # Button styling function
        def style_button(button, bg_color, hover_color, text_color="#FFFFFF"):
            def on_enter(e):
                button.config(bg=hover_color)
            def on_leave(e):
                button.config(bg=bg_color)
            
            button.bind("<Enter>", on_enter)
            button.bind("<Leave>", on_leave)

        # Like button with green design and rounded corners
        like_btn = tk.Button(
            action_frame,
            text="👍  Like",
            font=("Segoe UI", 10, "bold"),
            bg="#00C851",
            fg="#FFFFFF",
            relief="flat",
            padx=25,
            pady=8,
            cursor="hand2",
            border=0,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: [on_like(), root.destroy()]
        )
        like_btn.pack(side="left", padx=(0, 10))
        
        # Apply rounded corners using a custom style
        like_btn.configure(relief="flat", bd=0)
        
        # Unlike button with red design and rounded corners
        dislike_btn = tk.Button(
            action_frame,
            text="👎  Unlike",
            font=("Segoe UI", 10, "bold"),
            bg="#FF4444",
            fg="#FFFFFF",
            relief="flat",
            padx=25,
            pady=8,
            cursor="hand2",
            border=0,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: [on_dislike(), root.destroy()]
        )
        dislike_btn.pack(side="left")
        
        # Apply rounded corners using a custom style
        dislike_btn.configure(relief="flat", bd=0)
        
        style_button(like_btn, "#00C851", "#00A844", "#FFFFFF")
        style_button(dislike_btn, "#FF4444", "#E53E3E", "#FFFFFF")
        
        # Animate progress bar using tkinter's after method
        def animate_progress(step=0):
            try:
                if step < duration * 10:
                    progress_width = int((width * (duration * 10 - step)) / (duration * 10))
                    progress_bar.config(width=progress_width)
                    root.after(100, lambda: animate_progress(step + 1))
            except tk.TclError:
                print("Tcl Error during progress animation, likely due to window closure. 1st pass.")
                pass
        
        # Slide-in animation
        def slide_in():
            start_x = screen.width
            end_x = screen.width - width - 20
            steps = 20
            
            for i in range(steps + 1):
                current_x = start_x - (start_x - end_x) * (i / steps)
                root.geometry(f"{width}x{height}+{int(current_x)}+{y}")
                root.update()
                time.sleep(0.02)
        
        # Start animations
        root.after(10, slide_in)
        root.after(50, animate_progress)
        
        # Auto close with fade effect
        def fade_and_close():
            def fade_step(alpha=0.8):
                try:
                    if alpha > 0:
                        root.attributes("-alpha", alpha)
                        root.after(50, lambda: fade_step(alpha - 0.2))
                    else:
                        root.withdraw()
                except tk.TclError:
                    print("Tcl Error during fade effect, likely due to window closure. 2nd pass.")
                    pass
            fade_step()

        root.after(duration * 1000, fade_and_close)
        
        # Add subtle shadow effect by adjusting window attributes
        try:
            root.attributes("-alpha", 0.95)
        except:
            pass
            
        root.mainloop()

    threading.Thread(target=run, daemon=True).start()