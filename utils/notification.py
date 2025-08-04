import tkinter as tk
import threading
import time
from screeninfo import get_monitors

def show_modern_notification(rec_id, message, on_like, on_dislike, duration=15):
    def run():
        screen = get_monitors()[0]
        width = 420
        
        # Calculate dynamic height based on message length
        chars_per_line = 50
        estimated_lines = max(1, len(message) // chars_per_line + (1 if len(message) % chars_per_line else 0))
        
        base_height = 55 + 65 + 3 + 40
        message_height = max(30, estimated_lines * 18 + 20)
        height = base_height + message_height
        height = max(180, min(height, 400))
        
        x = screen.width - width - 20
        y = screen.height - height - 60

        root = tk.Tk()
        root.overrideredirect(True)
        root.attributes("-topmost", True)
        root.geometry(f"{width}x{height}+{x}+{y}")
        root.configure(bg="#1A1A1A")
        
        # Flags to track window state and prevent multiple operations
        window_destroyed = threading.Event()
        animation_running = threading.Event()
        
        # Get current time and determine greeting + colors
        import datetime
        current_hour = datetime.datetime.now().hour
        
        if 5 <= current_hour < 12:
            greeting = "Good Morning! ☀️"
            greeting_color = "#FFB74D"
            progress_color = "#FFB74D"
        elif 12 <= current_hour < 17:
            greeting = "Good Afternoon! ⛅"
            greeting_color = "#42A5F5"
            progress_color = "#42A5F5"
        elif 17 <= current_hour < 21:
            greeting = "Good Evening! 🌅"
            greeting_color = "#FF7043"
            progress_color = "#FF7043"
        else:
            greeting = "Good Night! 🌙"
            greeting_color = "#9C27B0"
            progress_color = "#9C27B0"
        
        # Progress bar for auto-close timer
        progress_frame = tk.Frame(root, bg="#1A1A1A", height=3)
        progress_frame.pack(side="top", fill="x")
        progress_frame.pack_propagate(False)
        
        progress_bar = tk.Frame(progress_frame, bg=progress_color, height=3)
        progress_bar.pack(side="left", fill="y")
        
        # Border effect
        border_frame = tk.Frame(root, bg="#2D2D2D", highlightthickness=0)
        border_frame.pack(fill="both", expand=True, padx=1, pady=1)
        
        # Main content frame
        main_frame = tk.Frame(border_frame, bg="#1A1A1A", highlightthickness=0)
        main_frame.pack(fill="both", expand=True, padx=1, pady=1)

        # Header section
        header_frame = tk.Frame(main_frame, bg="#1A1A1A", height=40)
        header_frame.pack(fill="x", padx=20, pady=(15, 0))
        header_frame.pack_propagate(False)
        
        greeting_label = tk.Label(
            header_frame,
            text=greeting,
            font=("Segoe UI", 11, "bold"),
            fg=greeting_color,
            bg="#1A1A1A"
        )
        greeting_label.pack(side="left", anchor="w")

        # Message content
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

        # Button section
        action_frame = tk.Frame(main_frame, bg="#1A1A1A", height=50)
        action_frame.pack(side="bottom", fill="x", padx=20, pady=(10, 15))
        action_frame.pack_propagate(False)

        # Button styling function
        def style_button(button, bg_color, hover_color, text_color="#FFFFFF"):
            def on_enter(e):
                if not window_destroyed.is_set():
                    try:
                        button.config(bg=hover_color)
                    except tk.TclError:
                        pass
            def on_leave(e):
                if not window_destroyed.is_set():
                    try:
                        button.config(bg=bg_color)
                    except tk.TclError:
                        pass
            
            button.bind("<Enter>", on_enter)
            button.bind("<Leave>", on_leave)

        # Safe destroy function that prevents TclError
        def safe_destroy():
            if not window_destroyed.is_set():
                window_destroyed.set()
                animation_running.clear()
                try:
                    # First withdraw to hide the window
                    root.withdraw()
                    # Force update to process withdraw
                    root.update_idletasks()
                    # Small delay to ensure smooth cleanup
                    root.after_idle(lambda: root.quit())
                    # Destroy after quit
                    root.after(10, root.destroy)
                except tk.TclError:
                    # If TclError still occurs, force destroy in a more aggressive way
                    try:
                        root.quit()
                        root.destroy()
                    except:
                        pass

        # Like button
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
            command=lambda: [on_like(), safe_destroy()]
        )
        like_btn.pack(side="left", padx=(0, 10))
        
        # Dislike button
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
            command=lambda: [on_dislike(), safe_destroy()]
        )
        dislike_btn.pack(side="left")
        
        style_button(like_btn, "#00C851", "#00A844", "#FFFFFF")
        style_button(dislike_btn, "#FF4444", "#E53E3E", "#FFFFFF")
        
        # Thread-safe progress bar animation
        def animate_progress(step=0):
            if window_destroyed.is_set() or not animation_running.is_set():
                return
                
            try:
                if step < duration * 10 and not window_destroyed.is_set():
                    progress_width = int((width * (duration * 10 - step)) / (duration * 10))
                    if progress_width > 0:
                        progress_bar.config(width=progress_width)
                    root.after(100, lambda: animate_progress(step + 1))
                else:
                    # Animation completed, trigger auto-close
                    if not window_destroyed.is_set():
                        safe_destroy()
            except tk.TclError:
                # Window was destroyed during animation
                window_destroyed.set()
                animation_running.clear()
        
        # Slide-in animation
        def slide_in():
            if window_destroyed.is_set():
                return
                
            start_x = screen.width
            end_x = screen.width - width - 20
            steps = 20
            
            try:
                for i in range(steps + 1):
                    if window_destroyed.is_set():
                        break
                    current_x = start_x - (start_x - end_x) * (i / steps)
                    root.geometry(f"{width}x{height}+{int(current_x)}+{y}")
                    root.update()
                    time.sleep(0.02)
            except tk.TclError:
                window_destroyed.set()
        
        # Cleanup on window close
        def on_closing():
            safe_destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Start animations
        animation_running.set()
        root.after(10, slide_in)
        root.after(50, animate_progress)
        
        # Set initial alpha
        try:
            root.attributes("-alpha", 0.95)
        except:
            pass
        
        # Start the main loop
        try:
            root.mainloop()
        except tk.TclError:
            pass
        finally:
            # Ensure cleanup happens
            if not window_destroyed.is_set():
                window_destroyed.set()
            animation_running.clear()

    # Create and start thread
    t = threading.Thread(target=run, daemon=True)
    t.start()
    # Don't join here - let it run independently
    return t  # Return thread reference if needed