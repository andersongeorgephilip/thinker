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
        self.root = root
        self.ai = AIServices()
        self.wp_client = WordPressClient()
        self.current_image = None
        ensure_folders_exist()
        self.initialize_components()

    def initialize_components(self):
        """Initialize all UI components in proper order"""
        self.create_menu()
        self.setup_gui()
        self.create_status_bar()
        self.add_publish_date_controls()

    # --- Core GUI Components ---
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

    # --- Date/Time Picker ---
    def add_publish_date_controls(self):
        """Add datetime picker to GUI"""
        date_frame = tk.Frame(self.root)
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

    # --- Core Functionality ---
    def generate(self):
        """Generate article and image using AI"""
        prompt = self.prompt_entry.get()
        if not prompt:
            messagebox.showwarning("Warning", "Please enter a prompt")
            return
        
        try:
            self.update_status("Generating article...")
            article = self.ai.generate_article(prompt)
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, article)
            
            self.update_status("Generating image...")
            self.current_image = self.ai.generate_image(prompt)
            self.display_image()
            
            self.update_status("Ready")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.update_status("Error occurred")

    def display_image(self):
        """Display generated image in new window"""
        if self.current_image:
            img = self.current_image.copy()
            img.thumbnail((300, 300))
            photo = ImageTk.PhotoImage(img)
            
            img_window = tk.Toplevel(self.root)
            img_window.title("Generated Image")
            label = tk.Label(img_window, image=photo)
            label.image = photo
            label.pack()

    # --- Additional Methods ---
    def create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        
        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Settings Menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label="API Key", command=self.set_api_key)
        settings_menu.add_command(label="WordPress Config", command=self.configure_wordpress)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        
        self.root.config(menu=menubar)

    def create_status_bar(self):
        """Create status bar at bottom"""
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = tk.Label(self.root, textvariable=self.status_var, 
                            bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def update_status(self, message):
        """Update status bar message"""
        self.status_var.set(message)
        self.root.update()

    # ... (rest of the methods remain the same)