# gui.py
import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog
from tkcalendar import DateEntry
from PIL import ImageTk
import os
import datetime
from config import ensure_folders_exist, WP_CONFIG_FILE, IMAGE_FOLDER
from ai_services import AIServices
from wordpress import WordPressClient

class ArticleApp:
    def __init__(self, root):
        self.root = root  # This must be FIRST
        self.ai = AIServices()
        self.wp_client = WordPressClient()
        self.current_image = None
        ensure_folders_exist()
        self.initialize_components()

    def initialize_components(self):
        """Initialize all UI components in proper order"""
        self.setup_gui()
        self.create_menu()
        self.create_status_bar()
        self.add_publish_date_controls()  # Now called AFTER root exists

    def setup_gui(self):
        self.root.title("Article Generator")
        self.root.geometry("800x600")
        
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Input Section
        input_frame = tk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(input_frame, text="Enter Prompt:").pack(side=tk.LEFT)
        self.prompt_entry = tk.Entry(input_frame, width=50)
        self.prompt_entry.pack(side=tk.LEFT, padx=5)
        
        # Output Section
        self.output_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        # Bottom Buttons
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        tk.Button(button_frame, text="Generate", command=self.generate).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Post to WordPress", command=self.post_to_wordpress).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Clear", command=self.clear).pack(side=tk.LEFT, padx=5)

    def add_publish_date_controls(self):
        """Add datetime picker to GUI"""
        date_frame = tk.Frame(self.root)  # Now using self.root that exists
        date_frame.pack(pady=5)
        
        tk.Label(date_frame, text="Publish Date:").pack(side=tk.LEFT)
        self.publish_date = DateEntry(date_frame)
        self.publish_date.pack(side=tk.LEFT, padx=5)
        
        tk.Label(date_frame, text="Time:").pack(side=tk.LEFT)
        self.publish_time = tk.Spinbox(date_frame, 
                                     values=[f"{h:02d}:{m:02d}" 
                                             for h in range(24) 
                                             for m in [0, 15, 30, 45]])
        self.publish_time.pack(side=tk.LEFT)
        
        tk.Label(date_frame, text="(Server Timezone)").pack(side=tk.LEFT, padx=5)

    # KEEP ALL OTHER METHODS AS ORIGINALLY DEFINED
    # (create_menu, create_status_bar, generate, etc.)
    # REMOVE DUPLICATE CLASS DEFINITION AT BOTTOM