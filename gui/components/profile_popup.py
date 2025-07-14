import customtkinter as ctk
from PIL import Image
import os
from services.database import delete_user

class ProfilePopup(ctk.CTkToplevel):
    def __init__(self, parent_root, first_name, last_name, birthday, gender, user_id):
        super().__init__(parent_root)
        self.parent_root = parent_root
        self.first_name = first_name
        self.last_name = last_name
        self.birthday = birthday
        self.gender = gender
        self.user_id = user_id
        self.title("Profile")
        self.geometry("380x450")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.transient(parent_root)

        self.update_idletasks()
        parent_x = parent_root.winfo_x()
        parent_y = parent_root.winfo_y()
        parent_width = parent_root.winfo_width()
        parent_height = parent_root.winfo_height()

        popup_width = self.winfo_width()
        popup_height = self.winfo_height()

        x = parent_x + (parent_width // 2) - (popup_width // 2)
        y = parent_y + (parent_height // 2) - (popup_height // 2)

        self.geometry(f"+{x}+{y}")

        self.load_icons()
        self.build_ui()

    def _load_png_icon(self, icon_name, icon_size=(24, 24)):
        """Helper to load a PNG icon from assets/icons and return CTkImage."""
        script_dir = os.path.dirname(__file__)
        assets_dir = os.path.join(script_dir, "..", "assets", "icons")
        icon_path = os.path.join(assets_dir, icon_name)

        try:
            img_pil = Image.open(icon_path)
            return ctk.CTkImage(light_image=img_pil, dark_image=img_pil, size=icon_size)
        except FileNotFoundError:
            print(f"Warning: Icon '{icon_name}' not found at {icon_path}. Using placeholder.")
            return ctk.CTkImage(Image.new('RGBA', icon_size, (24, 24), (255, 255, 255, 0)), size=icon_size)
        except Exception as e:
            print(f"Error loading icon '{icon_name}': {e}. Using placeholder.")
            return ctk.CTkImage(Image.new('RGBA', icon_size, (24, 24), (255, 255, 255, 0)), size=icon_size)

    def load_icons(self):
        # Load avatar background image
        self.avatar_background_image = self._load_png_icon("circle.png", icon_size=(80, 80)) # Size for the avatar background

        # Birthday icon
        self.calendar_icon = self._load_png_icon("calendar_month.png")

        # Gender icon based on value
        gender_icon_filename = "agender.png"
        if self.gender == "Male":
            gender_icon_filename = "male.png"
        elif self.gender == "Female":
            gender_icon_filename = "female.png"

        self.gender_icon = self._load_png_icon(gender_icon_filename)

    def build_ui(self):
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # --- Avatar (Image Background with Initials Text) ---
        # Calculate initials
        initials = ""
        if self.first_name:
            initials += self.first_name[0].upper()
        if self.last_name:
            initials += self.last_name[0].upper()

        # Frame to hold the image and text, acting as the avatar container
        avatar_container = ctk.CTkFrame(content_frame, fg_color="transparent")
        avatar_container.pack(pady=(0, 20))

        # Background image label
        ctk.CTkLabel(avatar_container, image=self.avatar_background_image, text=initials, font=ctk.CTkFont("Poppins", 30, "bold"),text_color="black").pack()

        # Full Name
        ctk.CTkLabel(content_frame, text=f"{self.first_name} {self.last_name}",font=ctk.CTkFont("Poppins", 22, "bold")).pack(pady=(0, 20))

        # --- Cards for Birthday and Gender ---
        cards_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        cards_frame.pack(fill="x", pady=10)

        # Birthday Card
        birthday_card = ctk.CTkFrame(cards_frame, fg_color="#F0F0F0", corner_radius=10)
        birthday_card.pack(fill="x", pady=(5, 5), padx=5)

        birthday_content_frame = ctk.CTkFrame(birthday_card, fg_color="transparent")
        birthday_content_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(birthday_content_frame, image=self.calendar_icon, text="").pack(side=ctk.LEFT, padx=(0, 10))
        ctk.CTkLabel(birthday_content_frame, text=f"Birthday: {self.birthday}",
                     font=ctk.CTkFont("Poppins", 14), text_color="#333").pack(side=ctk.LEFT, anchor="w")

        # Gender Card
        gender_card = ctk.CTkFrame(cards_frame, fg_color="#F0F0F0", corner_radius=10)
        gender_card.pack(fill="x", pady=(5, 5), padx=5)

        gender_content_frame = ctk.CTkFrame(gender_card, fg_color="transparent")
        gender_content_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(gender_content_frame, image=self.gender_icon, text="").pack(side=ctk.LEFT, padx=(0, 10))
        ctk.CTkLabel(gender_content_frame, text=f"Gender: {self.gender}",
                     font=ctk.CTkFont("Poppins", 14), text_color="#333").pack(side=ctk.LEFT, anchor="w")

        # Delete Account button
        ctk.CTkButton(self, text="Delete Account", command=self.delete_account_and_redirect,
                      fg_color="#a10000", hover_color="#800000",
                      font=ctk.CTkFont("Poppins", 14), width=140, height=35).pack(pady=(10, 20))

    def delete_account_and_redirect(self):
        try:
            delete_user(self.user_id)
            self.destroy()

            # Clear all widgets in the root and load splash screen
            for widget in self.parent_root.winfo_children():
                widget.destroy()

            from screens.splash import SplashScreen  # ✅ Import here to avoid circular import
            SplashScreen(self.parent_root)

        except Exception as e:
            print(f"Error deleting account: {e}")


