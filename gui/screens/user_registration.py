import customtkinter as ctk
from PIL import Image
import os
import calendar
import datetime # Re-import datetime for current year (for dynamic year list)

# --- UserRegistrationScreen Class ---
class UserRegistrationScreen(ctk.CTkFrame):
    def __init__(self, root):
        super().__init__(root, fg_color="transparent")
        self.root = root
        root.title("WellMind - User Registration")
        self.pack(fill=ctk.BOTH, expand=True)

        # Store references to entries and their corresponding error labels
        self.first_name_entry = None
        self.first_name_error_label = None
        self.last_name_entry = None
        self.last_name_error_label = None

        # Birthday dropdowns and their error labels
        self.birth_year_combobox = None
        self.birth_month_combobox = None
        self.birth_day_combobox = None
        self.birthday_error_label = None # Combined error label for all date components

        self.gender_combobox = None
        self.gender_error_label = None

        self.build_ui()

    def build_ui(self):
        image_path = os.path.join("assets", "logo", "logo.png")
        image = Image.open(image_path)
        self.logo_image = ctk.CTkImage(light_image=image, dark_image=image, size=(100, 100))
        ctk.CTkLabel(self, image=self.logo_image, text="").pack(pady=(40, 10))

        # Step Indicator Top-Right
        ctk.CTkLabel(self, text="Step 1 of 2", font=ctk.CTkFont("Poppins", 12)).place(relx=0.95, rely=0.05, anchor="ne")

        ctk.CTkLabel(self, text="Welcome to WellMind!", font=ctk.CTkFont("Poppins", 26, "bold")).pack(pady=(20, 5))
        ctk.CTkLabel(self, text="Create Your Profile Here", font=ctk.CTkFont("Poppins", 14)).pack(pady=(0, 20))

        form_frame = ctk.CTkFrame(self, fg_color="transparent")
        form_frame.pack(pady=10)

        # First Name field with onChange (KeyRelease) binding
        self.first_name_entry, self.first_name_error_label = self.add_entry_field(form_frame, "First Name", 0, 0)
        self.first_name_entry.bind("<KeyRelease>", lambda event: self.hide_error_on_input(self.first_name_entry, self.first_name_error_label))

        # Last Name field with onChange (KeyRelease) binding
        self.last_name_entry, self.last_name_error_label = self.add_entry_field(form_frame, "Last Name", 0, 1)
        self.last_name_entry.bind("<KeyRelease>", lambda event: self.hide_error_on_input(self.last_name_entry, self.last_name_error_label))

        # Birthday Selection (Year, Month, Day)
        birthday_outer_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        birthday_outer_frame.grid(row=1, column=0, padx=30, pady=10, sticky="ew")

        ctk.CTkLabel(birthday_outer_frame, text="Birthday", font=ctk.CTkFont("Poppins", 12)).pack(anchor="w", pady=(0, 2))

        birthday_dropdown_frame = ctk.CTkFrame(birthday_outer_frame, fg_color="transparent")
        birthday_dropdown_frame.pack(fill="x", expand=True)

        # Year Dropdown
        current_year = datetime.datetime.now().year # Get current year dynamically
        years = [str(y) for y in range(current_year, 1900, -1)] # From current year down to 1900
        years.insert(0, "Year") # Placeholder
        self.birth_year_combobox = ctk.CTkComboBox(birthday_dropdown_frame, values=years, width=80, height=35,
                                                   font=ctk.CTkFont("Poppins", 12),
                                                   command=lambda val: self.on_date_dropdown_change())
        self.birth_year_combobox.set("Year")
        self.birth_year_combobox.pack(side=ctk.LEFT, padx=(0, 5))

        # Month Dropdown (by name)
        month_names = ["Month"] + [calendar.month_name[i] for i in range(1, 13)]
        self.birth_month_combobox = ctk.CTkComboBox(birthday_dropdown_frame, values=month_names, width=120, height=35,
                                                    font=ctk.CTkFont("Poppins", 12),
                                                    command=lambda val: self.on_date_dropdown_change())
        self.birth_month_combobox.set("Month")
        self.birth_month_combobox.pack(side=ctk.LEFT, padx=(0, 5))

        # Day Dropdown (dynamically populated)
        days = ["Day"] + [str(i) for i in range(1, 32)] # Initial population (will be updated)
        self.birth_day_combobox = ctk.CTkComboBox(birthday_dropdown_frame, values=days, width=70, height=35,
                                                  font=ctk.CTkFont("Poppins", 12),
                                                  command=lambda val: self.on_date_dropdown_change())
        self.birth_day_combobox.set("Day")
        self.birth_day_combobox.pack(side=ctk.LEFT, padx=(0, 0))

        # Error label for birthday selection
        self.birthday_error_label = ctk.CTkLabel(birthday_outer_frame, text="This field is required",
                                                 font=ctk.CTkFont("Poppins", 10), text_color="red")
        self.birthday_error_label.pack(anchor="w", padx=0, pady=(0, 5))
        self.birthday_error_label.pack_forget() # Hide initially

        # Initialize day options on startup (important for initial valid state)
        self.update_day_options()

        # Gender Dropdown (Combobox)
        gender_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        gender_frame.grid(row=1, column=1, padx=30, pady=10, sticky="ew")
        ctk.CTkLabel(gender_frame, text="Gender", font=ctk.CTkFont("Poppins", 12)).pack(anchor="w", pady=(0, 2))
        gender_options = ["Select Gender", "Male", "Female", "Prefer not to say"]
        self.gender_combobox = ctk.CTkComboBox(gender_frame, values=gender_options,
                                                width=250, height=35, font=ctk.CTkFont("Poppins", 12),
                                                command=lambda val: self.hide_error_on_input(self.gender_combobox, self.gender_error_label))
        self.gender_combobox.set("Select Gender") # Default placeholder text
        self.gender_combobox.pack(anchor="w")
        # Error label for gender combobox
        self.gender_error_label = ctk.CTkLabel(gender_frame, text="This field is required",
                                              font=ctk.CTkFont("Poppins", 10), text_color="red")
        self.gender_error_label.pack(anchor="w", padx=0, pady=(0,5))
        self.gender_error_label.pack_forget() # Hide initially


        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=40)

        cancel_btn = ctk.CTkButton(button_frame, text="Cancel", fg_color="#a10000", hover_color="#800000",
                                   font=ctk.CTkFont("Poppins", 14), width=120, height=40,
                                   command=self.root.destroy)

        next_btn = ctk.CTkButton(button_frame, text="Next", fg_color="#0047AB", hover_color="#003380",
                                 font=ctk.CTkFont("Poppins", 14), width=120, height=40,
                                 command=self.goto_preferences)

        cancel_btn.grid(row=0, column=0, padx=30)
        next_btn.grid(row=0, column=1, padx=30)

    def add_entry_field(self, parent, label_text, row, col):
        field_frame = ctk.CTkFrame(parent, fg_color="transparent")
        field_frame.grid(row=row, column=col, padx=30, pady=10, sticky="ew")
        ctk.CTkLabel(field_frame, text=label_text, font=ctk.CTkFont("Poppins", 12)).pack(anchor="w", pady=(0, 2))
        entry = ctk.CTkEntry(field_frame, width=250, height=35, font=ctk.CTkFont("Poppins", 12))
        entry.pack(anchor="w")
        # Create and return the error label for this field
        error_label = ctk.CTkLabel(field_frame, text="This field is required",
                                   font=ctk.CTkFont("Poppins", 10), text_color="red")
        error_label.pack(anchor="w", padx=0, pady=(0,5))
        error_label.pack_forget() # Hide initially
        return entry, error_label

    def hide_error_on_input(self, widget, error_label):
        """Hides the error label if the widget is no longer empty or at its placeholder."""
        if isinstance(widget, ctk.CTkEntry):
            if widget.get(): # If there's any text
                error_label.pack_forget()
        elif isinstance(widget, ctk.CTkComboBox):
            # Check if it's no longer the "Select Gender", "Year", "Month", or "Day" placeholder
            if widget.get() not in ["Select Gender", "Year", "Month", "Day"]:
                error_label.pack_forget()

    def on_date_dropdown_change(self, *args):
        """Handles changes in year/month/day dropdowns and updates day options, hides error."""
        self.update_day_options()
        # Also check if all date components are selected to hide the error
        if (self.birth_year_combobox.get() != "Year" and
            self.birth_month_combobox.get() != "Month" and
            self.birth_day_combobox.get() != "Day"):
            self.birthday_error_label.pack_forget()


    def update_day_options(self, *args):
        """Updates the day dropdown based on the selected year and month."""
        try:
            year_str = self.birth_year_combobox.get()
            month_name = self.birth_month_combobox.get()

            # Ensure we have valid selections before calculating days
            if year_str == "Year" or month_name == "Month":
                # If placeholder, populate with all possible days
                days_in_month = 31
                month_num = 1 # Dummy value for calendar.monthrange if not valid
                current_day_value = "Day"
            else:
                year = int(year_str)
                month_num = list(calendar.month_name).index(month_name)
                days_in_month = calendar.monthrange(year, month_num)[1]

                current_day_value = self.birth_day_combobox.get()

            day_options = ["Day"] + [str(d) for d in range(1, days_in_month + 1)]
            self.birth_day_combobox.configure(values=day_options)

            # Re-set the day value to ensure it's valid for the new month/year
            if current_day_value in day_options:
                 self.birth_day_combobox.set(current_day_value)
            else:
                 self.birth_day_combobox.set("Day") # Reset if previous day is invalid

        except (ValueError, IndexError):
            # Fallback if parsing fails (e.g., initial state)
            self.birth_day_combobox.configure(values=["Day"] + [str(d) for d in range(1, 32)])
            self.birth_day_combobox.set("Day")


    def validate_field(self, widget, error_label):
        """Validates a single entry field or combobox and shows/hides its error label."""
        if isinstance(widget, ctk.CTkEntry):
            if not widget.get():
                error_label.pack(anchor="w", padx=0, pady=(0,5))
                return False
            else:
                error_label.pack_forget()
                return True
        elif isinstance(widget, ctk.CTkComboBox):
            # For combobox, check if it's the default placeholder or empty
            if widget.get() in ["Select Gender", "Year", "Month", "Day"] or not widget.get():
                error_label.pack(anchor="w", padx=0, pady=(0,5))
                return False
            else:
                error_label.pack_forget()
                return True
        return False # Should not reach here for supported widgets

    def goto_preferences(self):
        # Hide all error messages first before re-validating
        self.first_name_error_label.pack_forget()
        self.last_name_error_label.pack_forget()
        self.birthday_error_label.pack_forget()
        self.gender_error_label.pack_forget()

        all_valid = True

        # Validate each field sequentially
        if not self.validate_field(self.first_name_entry, self.first_name_error_label):
            all_valid = False
        if not self.validate_field(self.last_name_entry, self.last_name_error_label):
            all_valid = False

        # Validate birthday dropdowns as a group
        if (self.birth_year_combobox.get() == "Year" or
            self.birth_month_combobox.get() == "Month" or
            self.birth_day_combobox.get() == "Day"):
            self.birthday_error_label.pack(anchor="w", padx=0, pady=(0,5))
            all_valid = False
        else:
            # If all parts of the birthday are selected, ensure error is hidden
            self.birthday_error_label.pack_forget()


        if not self.validate_field(self.gender_combobox, self.gender_error_label):
            all_valid = False

        if not all_valid:
            ctk.CTkMessagebox.show_warning("Missing Information", "Please fill in all required fields.")
            return

        # If all fields are valid, proceed
        first_name = self.first_name_entry.get()
        last_name = self.last_name_entry.get()

        # Combine birthday components for the user_data
        year = self.birth_year_combobox.get()
        # Convert month name to 2-digit number (e.g., 'January' -> '01')
        month = str(list(calendar.month_name).index(self.birth_month_combobox.get())).zfill(2)
        day = self.birth_day_combobox.get().zfill(2) # Ensure 2 digits (e.g., '1' -> '01')
        birthday = f"{year}-{month}-{day}"

        gender = self.gender_combobox.get()

        print(f"User Data: {first_name}, {last_name}, {birthday}, {gender}")

        self.pack_forget()
        from screens.select_preferences import SelectPreferencesScreen
        SelectPreferencesScreen(self.root, self.root, first_name, last_name, birthday, gender)