import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import os
from screens.dashboard import DashboardScreen
from services.database import (
    create_user_table,
    insert_user,
    get_all_categories,
    get_preferences_by_category,
    create_user_preferences_mapping_table,
)

class SelectPreferencesScreen(ctk.CTkFrame):
    def __init__(self, root, controller, first_name, last_name, birthday, gender):
        super().__init__(root, fg_color="transparent")
        self.root = root
        root.title("WellMind - Select Preferences")
        self.controller = controller
        self.first_name = first_name
        self.last_name = last_name
        self.birthday = birthday
        self.gender = gender
        self.pack(fill=ctk.BOTH, expand=True)

        self.preference_vars = {}  # Holds {preference_name: StringVar}

        self.build_ui()

    def build_ui(self):
        # Logo (Top-Left)
        image_path = os.path.join("assets", "logo", "logo.png")
        image = Image.open(image_path)
        self.logo_image = ctk.CTkImage(light_image=image, dark_image=image, size=(40, 40))
        ctk.CTkLabel(self, image=self.logo_image, text="").place(x=20, y=20)

        # Step Indicator Top-Right
        ctk.CTkLabel(self, text="Step 2 of 2", font=ctk.CTkFont("Poppins", 12)).place(relx=0.95, rely=0.05, anchor="ne")

        # Heading
        ctk.CTkLabel(self, text="What Interests You?", font=ctk.CTkFont("Poppins", 24, "bold")).pack(pady=(70, 5))
        ctk.CTkLabel(self, text="Select your preferences and subcategories to personalize your experience.",
                     font=ctk.CTkFont("Poppins", 12)).pack(pady=(0, 20))

        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(pady=10)

        # Load categories and preferences
        for category_id, category_name in get_all_categories():
            preferences = get_preferences_by_category(category_id)
            pref_names = [pref[1] for pref in preferences]
            self.create_section(content_frame, category_name, pref_names)

        # Navigation Buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=40)

        ctk.CTkButton(button_frame, text="Back", fg_color="#a10000", hover_color="#800000",
                      font=ctk.CTkFont("Poppins", 14), width=120, height=40,
                      command=self.go_back).grid(row=0, column=0, padx=30)

        ctk.CTkButton(button_frame, text="Complete", fg_color="#0047AB", hover_color="#003380",
                      font=ctk.CTkFont("Poppins", 14), width=120, height=40,
                      command=self.complete_registration).grid(row=0, column=1, padx=30)

    def create_section(self, parent_frame, title, options):
        frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        frame.pack(pady=10, fill="x", padx=50)

        ctk.CTkLabel(frame, text=title, font=ctk.CTkFont("Poppins", 15, "bold")).pack(anchor="w", pady=(0, 5))

        option_frame = ctk.CTkFrame(frame, fg_color="transparent")
        option_frame.pack(anchor="w")

        for i, option in enumerate(options):
            var = ctk.StringVar(value="off")
            self.preference_vars[option] = var
            checkbox = ctk.CTkCheckBox(option_frame, text=option, variable=var, onvalue=option, offvalue="off",
                                       font=ctk.CTkFont("Poppins", 11))
            checkbox.grid(row=i // 4, column=i % 4, padx=8, pady=5, sticky="w")

    def go_back(self):
        self.pack_forget()
        from screens.user_registration import UserRegistrationScreen
        UserRegistrationScreen(self.root)

    def complete_registration(self):
        selected_preferences = [
            name for name, var in self.preference_vars.items() if var.get() != "off"
        ]

        if not selected_preferences:
            messagebox.showwarning("No Preferences Selected", "Please select at least one preference.")
            return

        # Step 1: Create necessary tables
        create_user_table()
        create_user_preferences_mapping_table()

        # Step 2: Insert user into the 'user' table
        insert_user(
            self.first_name,
            self.last_name,
            self.gender,
            self.birthday
        )

        # Step 3: Fetch the latest user (just created)
        from services.database import fetch_latest_user, get_preference_id_by_name, insert_user_preference_mapping
        latest_user = fetch_latest_user()
        if not latest_user:
            messagebox.showerror("Error", "Failed to retrieve user after saving.")
            return

        user_id = latest_user["user_id"]

        # Step 4: Save selected preferences for this user
        for preference_name in selected_preferences:
            preference_id = get_preference_id_by_name(preference_name)
            if preference_id:
                insert_user_preference_mapping(user_id, preference_id)

        # Step 5: Proceed to dashboard
        self.pack_forget()
        DashboardScreen(self.root, self.controller)

