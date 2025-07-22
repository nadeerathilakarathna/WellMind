import customtkinter as ctk
from PIL import Image
import os
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from components.profile_popup import ProfilePopup
from datetime import datetime
from services.database import fetch_latest_user
from services.database import fetch_recent_recommendations
from services.database import get_feedback_counts
from services.database import get_stress_metrics
from services.database import fetch_user_dashboard

class DashboardScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.controller.title("WellMind - Dashboard")
        self.pack(fill=ctk.BOTH, expand=True)

        # Load user from DB
        user_data = fetch_latest_user()
        if not user_data:
            ctk.CTkLabel(self, text="No user data found!", font=ctk.CTkFont("Poppins", 16)).pack(pady=20)
            return

        self.first_name = user_data["first_name"]
        self.last_name = user_data["last_name"]
        self.birthday = user_data["birthday"]
        self.gender = user_data["gender"]
        self.user_id = user_data["user_id"]

        # Continue as normal
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill=ctk.BOTH, expand=True)

        self.canvas = ctk.CTkCanvas(self.main_frame, highlightthickness=0)
        self.canvas.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)

        self.scrollbar = ctk.CTkScrollbar(self.main_frame, orientation="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side=ctk.RIGHT, fill=ctk.Y)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.scrollable_frame = ctk.CTkFrame(self.canvas)
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=self.winfo_width())

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.bind("<Configure>", self.on_frame_configure)

        # Mouse wheel scroll binding
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)  # Windows/macOS
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)  # Linux scroll up
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)  # Linux scroll down

        self.build_ui()

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.itemconfig(1, width=event.width)

    def _on_mousewheel(self, event):
        if os.name == 'nt':  # Windows
            self.canvas.yview_scroll(-1 * (event.delta // 120), "units")
        elif event.num == 4:  # Linux scroll up
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:  # Linux scroll down
            self.canvas.yview_scroll(1, "units")
        else:
            # macOS uses delta differently
            self.canvas.yview_scroll(-1 * int(event.delta), "units")

    def on_time_period_change(self, selected_period):
        """Handle time period dropdown change"""
        print(f"Time period changed to: {selected_period}")
        # Here you can add logic to update the graph based on the selected period
        # For now, we'll just print the selection
        self.update_stress_graph(selected_period)

    def update_stress_graph(self, selected_period):
        """Update the stress graph based on selected time period"""
        self.selected_period = selected_period

        if self.selected_period == "Today":
            self.data = fetch_user_dashboard('daily')
        elif self.selected_period == "This week":
            self.data = fetch_user_dashboard('weekly')
        elif self.selected_period == "This month":
            self.data = fetch_user_dashboard('monthly')

        # Clear the existing graph and create new one
        if hasattr(self, 'chart'):
            self.chart.get_tk_widget().destroy()

        fig, ax = plt.subplots(figsize=(6, 2.5))
        
        if self.data['rows']:
            rows = self.data['rows']
            
            # Extract data from rows (assuming row structure: [id, timestamp, facial_expression_stress, keystroke_stress, stress_level, overall])
            timestamps = []
            facial_expression_stresses = []
            keystroke_stresses = []
            overall_stresses = []
            
            for row in rows:
                timestamps.append(row[1])  # timestamp
                facial_expression_stresses.append(row[2] if row[2] is not None else None)  # facial expression stress
                keystroke_stresses.append(row[3] if row[3] is not None else None)  # keystroke stress
                overall_stresses.append(row[5] if row[5] is not None else None)  # overall stress
            
            if timestamps:
                # Convert timestamps to datetime objects for plotting
                from datetime import datetime
                datetime_objects = [datetime.strptime(ts, "%Y-%m-%d %H:%M:%S") for ts in timestamps]
                
                # Sort all data by timestamp to ensure proper line plotting
                # Handle None values by replacing them with a placeholder for sorting, then restore
                data_tuples = list(zip(datetime_objects, facial_expression_stresses, keystroke_stresses, overall_stresses))
                sorted_data = sorted(data_tuples, key=lambda x: x[0])  # Sort only by datetime (first element)
                datetime_objects, facial_expression_stresses, keystroke_stresses, overall_stresses = zip(*sorted_data)
                
                # Plot facial expression stress data
                facial_valid_data = [(dt, stress) for dt, stress in zip(datetime_objects, facial_expression_stresses) if stress is not None]
                if facial_valid_data:
                    facial_times, facial_values = zip(*facial_valid_data)
                    ax.plot(facial_times, facial_values, marker="o", color="#FF5722", 
                        linewidth=1, markersize=3, label="Facial Expression Stress", alpha=0.5, 
                        linestyle='-', drawstyle='default')
                
                # Plot keystroke stress data
                keystroke_valid_data = [(dt, stress) for dt, stress in zip(datetime_objects, keystroke_stresses) if stress is not None]
                if keystroke_valid_data:
                    keystroke_times, keystroke_values = zip(*keystroke_valid_data)
                    ax.plot(keystroke_times, keystroke_values, marker="o", color="#4CAF50", 
                        linewidth=1, markersize=3, label="Keystroke Stress", alpha=0.5, 
                        linestyle='-', drawstyle='default')
                
                # Plot overall stress data
                overall_valid_data = [(dt, stress) for dt, stress in zip(datetime_objects, overall_stresses) if stress is not None]
                if overall_valid_data:
                    overall_times, overall_values = zip(*overall_valid_data)
                    ax.plot(overall_times, overall_values, marker="o", color="#3F51B5", 
                        linewidth=3, markersize=6, label="Overall Stress", 
                        linestyle='-', drawstyle='default')
                
                # Get date range from data info
                point_date_str = self.data['info']['point_date']
                before_date_str = self.data['info']['before_date']
                point_date_dt = datetime.strptime(point_date_str, "%Y-%m-%d %H:%M:%S")
                before_date_dt = datetime.strptime(before_date_str, "%Y-%m-%d %H:%M:%S")
                
                # Set x-axis limits to the actual date range
                ax.set_xlim(before_date_dt, point_date_dt)
                
                # Format x-axis based on the selected period
                if self.selected_period == "Today":
                    ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter("%H:%M"))
                    ax.xaxis.set_major_locator(plt.matplotlib.dates.HourLocator(interval=2))
                elif self.selected_period == "This week":
                    ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter("%a %d"))
                    ax.xaxis.set_major_locator(plt.matplotlib.dates.DayLocator())
                elif self.selected_period == "This month":
                    ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter("%m/%d"))
                    ax.xaxis.set_major_locator(plt.matplotlib.dates.WeekdayLocator())
                
                # Rotate x-axis labels for better readability
                plt.xticks(rotation=45)
                
                # Add legend to distinguish between different stress types
                ax.legend(loc='upper right', fontsize=8)
                

            else:
                # No data available - show empty graph with message
                ax.text(0.5, 0.5, 'No data available for this period', 
                    horizontalalignment='center', verticalalignment='center', 
                    transform=ax.transAxes, fontsize=12, color='gray')
        else:
            # No data available - show empty graph with message
            ax.text(0.5, 0.5, 'No data available for this period', 
                horizontalalignment='center', verticalalignment='center', 
                transform=ax.transAxes, fontsize=12, color='gray')
        
        ax.set_ylabel("Stress Level")
        ax.set_ylim(0, 100)
        ax.grid(True)
        ax.set_title(f"Stress Level - {selected_period}")
        
        # Adjust layout to prevent label cutoff
        plt.tight_layout()
        
        self.chart = FigureCanvasTkAgg(fig, master=self.graph_frame)
        self.chart.draw()
        self.chart.get_tk_widget().pack(fill=ctk.BOTH, expand=True)









    def build_ui(self):
        top_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        top_frame.pack(fill=ctk.X, padx=10, pady=(10, 0))

        logo_path = os.path.join("assets", "logo", "logo.png")
        logo_img = Image.open(logo_path) if os.path.exists(logo_path) else Image.new('RGBA', (40, 40),
                                                                                     (255, 255, 255, 0))
        self.logo = ctk.CTkImage(light_image=logo_img, dark_image=logo_img, size=(40, 40))
        ctk.CTkLabel(top_frame, image=self.logo, text="").pack(side=ctk.LEFT, padx=10)

        avatar_size = 50
        initials = (self.first_name[0] + self.last_name[0]).upper()
        avatar_frame = ctk.CTkFrame(top_frame, fg_color="transparent", width=50, height=50)
        avatar_frame.pack(side=ctk.RIGHT, padx=10)
        avatar_frame.pack_propagate(False)

        circle_path = os.path.join("assets", "icons", "circle.png")
        circle_img = Image.open(circle_path).resize((avatar_size, avatar_size)) if os.path.exists(
            circle_path) else Image.new("RGBA", (avatar_size, avatar_size), (200, 200, 200, 255))
        circle_ctk = ctk.CTkImage(light_image=circle_img, dark_image=circle_img, size=(avatar_size, avatar_size))

        avatar_label = ctk.CTkLabel(avatar_frame, image=circle_ctk, text=initials,
                                    font=ctk.CTkFont("Poppins", 18, "bold"), text_color="black")
        avatar_label.place(relx=0.5, rely=0.5, anchor="center")
        avatar_label.bind("<Button-1>", lambda event: self.open_profile_popup())

        # Page header
        ctk.CTkLabel(self.scrollable_frame, text="Dashboard", font=ctk.CTkFont("Poppins", 22, "bold")).pack(anchor="w",padx=25,pady=(10, 0))

        # Greeting
        greeting = self.get_greeting()
        ctk.CTkLabel(self.scrollable_frame, text=f"{greeting}, {self.first_name}!", font=ctk.CTkFont("Poppins", 16),
                     text_color="#CCC").pack(anchor="w", padx=25, pady=(0, 20))

        # Data Cards
        thumb_up_path = os.path.join("assets", "icons", "thumb_up.png")
        thumb_down_path = os.path.join("assets", "icons", "thumb_down.png")

        thumb_up_img = Image.open(thumb_up_path).resize((16, 16)) if os.path.exists(thumb_up_path) else Image.new(
            "RGBA", (16, 16), (0, 0, 0, 0))
        thumb_down_img = Image.open(thumb_down_path).resize((16, 16)) if os.path.exists(thumb_down_path) else Image.new(
            "RGBA", (16, 16), (0, 0, 0, 0))

        thumb_up_ctk = ctk.CTkImage(light_image=thumb_up_img, dark_image=thumb_up_img, size=(16, 16))
        thumb_down_ctk = ctk.CTkImage(light_image=thumb_down_img, dark_image=thumb_down_img, size=(16, 16))

        card_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="#333333", corner_radius=12)
        card_frame.pack(fill=ctk.X, padx=25, pady=(0, 10))

        metrics = get_stress_metrics()

        if metrics:
            for title, value in metrics.items():
                card = ctk.CTkFrame(card_frame, corner_radius=12, width=140, height=100, fg_color="#E3F2FD")
                card.pack(side="left", padx=10, pady=10, fill="both", expand=True)
                ctk.CTkLabel(card, text=title, font=ctk.CTkFont("Poppins", 12, "bold"), text_color="#000").pack(
                    pady=(10, 0))
                ctk.CTkLabel(card, text=value, font=ctk.CTkFont("Poppins", 14), text_color="#254D70").pack(pady=(0, 10))
        else:
            # Optional fallback if metrics not found
            ctk.CTkLabel(card_frame, text="No stress metrics available", font=ctk.CTkFont("Poppins", 14)).pack(pady=20)

        # Feedback Card with icons
        feedback_card = ctk.CTkFrame(card_frame, corner_radius=12, width=140, height=100, fg_color="#E3F2FD")
        feedback_card.pack(side="left", padx=10, pady=10, fill="both", expand=True)

        ctk.CTkLabel(feedback_card, text="Feedback", font=ctk.CTkFont("Poppins", 12, "bold"), text_color="#000").pack(
            pady=(10, 0))
        feedback_icon_frame = ctk.CTkFrame(feedback_card, fg_color="transparent")
        feedback_icon_frame.pack(pady=(0, 10))

        # Fetch feedback counts from DB
        feedback_counts = get_feedback_counts()
        likes = feedback_counts["likes"]
        unlikes = feedback_counts["unlikes"]

        # Like count
        like_frame = ctk.CTkFrame(feedback_icon_frame, fg_color="transparent")
        like_frame.pack(side="left", padx=(0, 15))
        ctk.CTkLabel(like_frame, image=thumb_up_ctk, text="", width=16, height=16).pack(side="left")
        ctk.CTkLabel(like_frame, text=str(likes), font=ctk.CTkFont("Poppins", 12), text_color="#254D70", padx=6).pack(
            side="left")

        # Unlike count
        unlike_frame = ctk.CTkFrame(feedback_icon_frame, fg_color="transparent")
        unlike_frame.pack(side="left")
        ctk.CTkLabel(unlike_frame, image=thumb_down_ctk, text="", width=16, height=16).pack(side="left")
        ctk.CTkLabel(unlike_frame, text=str(unlikes), font=ctk.CTkFont("Poppins", 12), text_color="#254D70",
                     padx=6).pack(side="left")

        # Stress Summary Graph
        graph_card = ctk.CTkFrame(self.scrollable_frame, fg_color="#333333", corner_radius=12)
        graph_card.pack(fill=ctk.X, padx=25, pady=(10, 20))

        stress_icon_path = os.path.join("assets", "icons", "monitoring.png")
        stress_icon_img = Image.open(stress_icon_path).resize((20, 20)) if os.path.exists(
            stress_icon_path) else Image.new("RGBA", (20, 20), (255, 255, 255, 0))
        stress_icon_ctk = ctk.CTkImage(light_image=stress_icon_img, dark_image=stress_icon_img, size=(20, 20))

        stress_title_frame = ctk.CTkFrame(graph_card, fg_color="transparent")
        stress_title_frame.pack(fill="x", padx=20, pady=(10, 5))

        # Left side - title with icon
        title_left_frame = ctk.CTkFrame(stress_title_frame, fg_color="transparent")
        title_left_frame.pack(side="left")

        ctk.CTkLabel(title_left_frame, image=stress_icon_ctk, text="", width=20, height=20).pack(side="left")
        ctk.CTkLabel(title_left_frame, text="Stress Summary",
                     font=ctk.CTkFont("Poppins", 14, "bold"), text_color="#FFF", padx=8).pack(side="left")

        # Right side - dropdown
        dropdown_frame = ctk.CTkFrame(stress_title_frame, fg_color="transparent")
        dropdown_frame.pack(side="right")

        self.time_period_dropdown = ctk.CTkComboBox(
            dropdown_frame,
            values=["Today", "This week", "This month"],
            command=self.on_time_period_change,
            width=120,
            height=30,
            font=ctk.CTkFont("Poppins", 12),
            dropdown_font=ctk.CTkFont("Poppins", 12)
        )
        self.time_period_dropdown.set("This week")  # Default value
        self.time_period_dropdown.pack()

        self.graph_frame = ctk.CTkFrame(graph_card, fg_color="white", corner_radius=10)
        self.graph_frame.pack(fill=ctk.BOTH, expand=True, padx=20, pady=10)

        # Initialize with default graph
        self.update_stress_graph("This week")

        # Recommendations section
        rec_section = ctk.CTkFrame(self.scrollable_frame, fg_color="#333333", corner_radius=12)
        rec_section.pack(fill=ctk.X, padx=25, pady=(0, 20))

        rec_icon_path = os.path.join("assets", "icons", "lightbulb.png")
        rec_icon_img = Image.open(rec_icon_path).resize((20, 20)) if os.path.exists(rec_icon_path) else Image.new(
            "RGBA", (20, 20), (255, 255, 255, 0))
        rec_icon_ctk = ctk.CTkImage(light_image=rec_icon_img, dark_image=rec_icon_img, size=(20, 20))

        rec_title_frame = ctk.CTkFrame(rec_section, fg_color="transparent")
        rec_title_frame.pack(anchor="w", padx=10, pady=(10, 5))

        ctk.CTkLabel(rec_title_frame, image=rec_icon_ctk, text="", width=20, height=20).pack(side="left")
        ctk.CTkLabel(rec_title_frame, text="Recommendations",
                     font=ctk.CTkFont("Poppins", 14, "bold"), text_color="#FFF", padx=8).pack(side="left")

        recommendations = fetch_recent_recommendations()

        now = datetime.now()

        if not recommendations:
            # Show message if no recommendations
            ctk.CTkLabel(
                rec_section,
                text="No recommendations available.",
                font=ctk.CTkFont("Poppins", 12),
                text_color="#DDD",
                padx=10,
                pady=10
            ).pack(padx=10, pady=10)
        else:
            # Sort and display recommendations
            recommendations.sort(
                key=lambda rec: datetime.strptime(rec["timestamp"], "%Y-%m-%d %H:%M:%S"),
                reverse=True
            )

            for rec_data in recommendations:
                recommendation = rec_data["recommendation"]
                timestamp = rec_data["timestamp"]
                reaction = rec_data["reaction"]

                feedback_datetime = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                time_diff = (now - feedback_datetime).total_seconds()

                if time_diff < 60:
                    time_display = "Just now"
                elif time_diff < 3600:
                    minutes = int(time_diff // 60)
                    time_display = f"{minutes} minute{'s' if minutes != 1 else ''} ago"
                elif time_diff < 86400:
                    hours = int(time_diff // 3600)
                    time_display = f"{hours} hour{'s' if hours != 1 else ''} ago"
                else:
                    time_display = feedback_datetime.strftime("%b %d, %Y | %I:%M %p")

                if reaction == "liked":
                    feedback_icon = thumb_up_ctk
                    feedback_text = "Like"
                    feedback_color = "#1B5E20"
                elif reaction == "unliked":
                    feedback_icon = thumb_down_ctk
                    feedback_text = "Unlike"
                    feedback_color = "#B71C1C"
                else:
                    feedback_icon = None
                    feedback_text = "--"
                    feedback_color = "#888888"

                card = ctk.CTkFrame(rec_section, fg_color="#FFFFFF", corner_radius=10)
                card.pack(padx=10, pady=5, fill="x")
                card.grid_columnconfigure(0, weight=1)
                card.grid_columnconfigure(1, weight=0)

                # Create a frame to hold the two colored labels side by side
                text_frame = ctk.CTkFrame(card, fg_color="transparent")
                text_frame.grid(row=0, column=0, sticky="w", padx=10, pady=10)

                # Label for recommendation (black)
                rec_label = ctk.CTkLabel(
                    text_frame,
                    text=recommendation,
                    font=ctk.CTkFont("Poppins", 12),
                    text_color="#000000"
                )
                rec_label.pack(side="left")

                # Label for dot and time_display (grey)
                time_label = ctk.CTkLabel(
                    text_frame,
                    text=f" • {time_display}",
                    font=ctk.CTkFont("Poppins", 12),
                    text_color="#CCCCCC"
                )
                time_label.pack(side="left")

                feedback_frame = ctk.CTkFrame(card, fg_color="transparent")
                feedback_frame.grid(row=0, column=1, sticky="e", padx=10)

                ctk.CTkLabel(feedback_frame, image=feedback_icon, text="", width=16, height=16).pack(side="left")
                ctk.CTkLabel(feedback_frame, text=feedback_text,
                             font=ctk.CTkFont("Poppins", 12), text_color=feedback_color, padx=6).pack(side="left")

        # Footer
        ctk.CTkLabel(self.scrollable_frame, text="WellMind V.1.0.0.1\nAll Rights Reserved © 2025",
                     font=ctk.CTkFont("Poppins", 12), text_color="#AAA").pack(pady=(0, 10))

    def get_greeting(self):
        hour = datetime.now().hour
        if 5 <= hour < 12:
            return "Good Morning"
        elif 12 <= hour < 17:
            return "Good Afternoon"
        elif 17 <= hour < 21:
            return "Good Evening"
        else:
            return "Good Night"

    def open_profile_popup(self):
        if not hasattr(self, '_profile_popup') or not self._profile_popup.winfo_exists():
            self._profile_popup = ProfilePopup(self.controller, self.first_name, self.last_name, self.birthday,
                                               self.gender, self.user_id)
            self._profile_popup.grab_set()
            self._profile_popup.wait_window()
            self._profile_popup.grab_release()