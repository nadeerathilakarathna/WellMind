import customtkinter as ctk
from PIL import Image, ImageTk
import os
from services.database import fetch_latest_user
from screens.dashboard import DashboardScreen
from screens.user_registration import UserRegistrationScreen

class SplashScreen(ctk.CTkFrame):
    def __init__(self, root):
        super().__init__(root, fg_color="transparent") # Use transparent for frame to let root's color show
        self.root = root
        self.pack(fill=ctk.BOTH, expand=True)

        self.display_content()
        self.after(2000, self.navigate_next_screen)  # Navigate after 2 sec

    def display_content(self):
        image_path = os.path.join("assets", "logo", "logo.png")
        image = Image.open(image_path)
        # CustomTkinter automatically handles image rendering with PIL, no need for ImageTk directly
        self.logo_image = ctk.CTkImage(light_image=image, dark_image=image, size=(200, 200))

        ctk.CTkLabel(self, image=self.logo_image, text="").pack(pady=(120, 10))

        ctk.CTkLabel(self, text="WellMind", font=ctk.CTkFont("Poppins", 32, "bold")).pack()
        # Corrected line: changed "italic" from weight to slant
        ctk.CTkLabel(self, text="Optimize Your Mind, Maximize Your Performance", font=ctk.CTkFont("Poppins", 16)).pack(pady=5)
        ctk.CTkLabel(self, text="V.1.0.0.1", font=ctk.CTkFont("Poppins", 14)).pack(pady=(20, 0))

    def navigate_next_screen(self):
        self.pack_forget()
        try:
            user = fetch_latest_user()
            if user:
                DashboardScreen(self.root, self.root)  # Or pass controller if needed
            else:
                UserRegistrationScreen(self.root)
        except Exception as e:
            print(f"Error fetching user data: {e}")
            UserRegistrationScreen(self.root)
