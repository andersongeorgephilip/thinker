# gui.py
import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog, ttk
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
        self.categories = []  # All categories fetched from WordPress
        self.category_vars = {}  # Checkbutton variables for selected categories
        self.status_var = tk.StringVar()  # Status bar variable
        ensure_folders_exist()
        self.initialize_components()
        self.load_categories()

    def update_status(self, message):
        """Update the status bar text"""
        self.status_var.set(message)
        self.root.update_idletasks()  # Ensure UI updates immediately

    def initialize_components(self):
        """Initialize all UI components in proper order"""
        self.create_menu()  # Ensure this is called
        self.setup_gui()
        self.create_status_bar()
        self.add_publish_date_controls()

    # --- Core GUI Components ---
    def setup_gui(self):
        """Set up the main GUI components"""
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
        
        # Category Section (Add below Output Section)
        category_frame = tk.LabelFrame(main_frame, text="Select Categories")
        category_frame.pack(fill=tk.BOTH, padx=10, pady=5)
        
        self.category_canvas = tk.Canvas(category_frame)
        self.category_scrollbar = ttk.Scrollbar(
            category_frame, orient=tk.VERTICAL, command=self.category_canvas.yview
        )
        self.category_inner_frame = tk.Frame(self.category_canvas)
        
        self.category_inner_frame.bind(
            "<Configure>",
            lambda e: self.category_canvas.configure(scrollregion=self.category_canvas.bbox("all")),
        )
        
        self.category_canvas.create_window((0, 0), window=self.category_inner_frame, anchor="nw")
        self.category_canvas.configure(yscrollcommand=self.category_scrollbar.set)
        
        self.category_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.category_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bottom Buttons
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        tk.Button(button_frame, text="Generate", command=self.generate).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Post to WordPress", command=self.post_to_wordpress).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Clear", command=self.clear).pack(side=tk.LEFT, padx=5)

    def create_status_bar(self):
        """Create status bar at bottom of window"""
        status_bar = tk.Label(self.root, 
                              textvariable=self.status_var,
                              bd=1, 
                              relief=tk.SUNKEN, 
                              anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_var.set("Ready")

    # --- Date/Time Picker ---
    def add_publish_date_controls(self):
        """Add datetime picker to GUI"""
        date_frame = tk.Frame(self.root)
        date_frame.pack(pady=5)
        
        tk.Label(date_frame, text="Publish Date:").pack(side=tk.LEFT)
        self.publish_date = DateEntry(date_frame)
        self.publish_date.pack(side=tk.LEFT, padx=5)
        
        tk.Label(date_frame, text="Time:").pack(side=tk.LEFT)
        self.publish_time = tk.Spinbox(
            date_frame, 
            values=[f"{h:02d}:{m:02d}" for h in range(24) for m in [0, 15, 30, 45]]
        )
        self.publish_time.pack(side=tk.LEFT)
        
        tk.Label(date_frame, text="(Server Timezone)").pack(side=tk.LEFT, padx=5)

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

    # --- Core Functionality ---
    def load_categories(self):
        """Load categories from WordPress"""
        try:
            self.update_status("Loading categories...")
            self.categories = self.wp_client.get_categories()
            
            # Clear existing checkboxes
            for widget in self.category_inner_frame.winfo_children():
                widget.destroy()
            
            # Create new checkboxes
            self.category_vars = {}
            for category in self.categories:
                var = tk.BooleanVar()
                cb = tk.Checkbutton(
                    self.category_inner_frame, 
                    text=category['name'], 
                    variable=var
                )
                cb.pack(anchor="w")
                self.category_vars[category['id']] = var
                
            self.update_status("Categories loaded")
        except Exception as e:
            messagebox.showerror("Category Error", f"Failed to load categories: {str(e)}")
            self.update_status("Category load failed")

    def generate(self):
        """Generate article and image using AI"""
        prompt = self.prompt_entry.get()
        if not prompt:
            messagebox.showwarning("Warning", "Please enter a prompt")
            return

        try:
            # Load rules from the rules.txt file
            with open("rules.txt", "r") as file:
                rules = file.read().strip()

            self.update_status("Generating article...")
            combined_input = f"Rules:\n{rules}\n\nPrompt:\n{prompt}"
            article = self.ai.generate_article(combined_input)
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, article)

            self.update_status("Generating image...")
            self.current_image = self.ai.generate_image(prompt)
            self.display_image()

            self.update_status("Ready")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.update_status("Error occurred")

    def post_to_wordpress(self):
        """Post the generated content to WordPress"""
        article_content = self.output_text.get(1.0, tk.END).strip()
        if not article_content:
            messagebox.showwarning("Warning", "No content to post. Please generate an article first.")
            return

        try:
            # Extract the title from the first line of the content
            lines = article_content.split("\n", 1)
            title = lines[0].strip() if len(lines) > 0 else "Generated Article"
            content_body = lines[1].strip() if len(lines) > 1 else article_content

            # Get selected categories
            selected_categories = [
                cat_id for cat_id, var in self.category_vars.items() if var.get()
            ]

            self.update_status("Posting to WordPress...")
            publish_date = self.publish_date.get_date()
            publish_time = self.publish_time.get()
            full_datetime = datetime.datetime.strptime(f"{publish_date} {publish_time}", "%Y-%m-%d %H:%M").isoformat()

            # Use the create_post method of WordPressClient
            response = self.wp_client.create_post(
                title=title,
                content=content_body,
                categories=selected_categories,
                schedule_time=full_datetime
            )
            messagebox.showinfo("Success", f"Article posted to WordPress! Post ID: {response['id']}")
            self.update_status("Ready")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to post to WordPress: {e}")
            self.update_status("Error occurred")

    def clear(self):
        """Clear all input and output fields"""
        self.prompt_entry.delete(0, tk.END)
        self.output_text.delete(1.0, tk.END)
        self.publish_date.set_date(datetime.datetime.now())
        self.publish_time.delete(0, tk.END)
        self.publish_time.insert(0, "00:00")
        self.current_image = None
        for var in self.category_vars.values():
            var.set(False)
        self.update_status("Ready")

    def set_api_key(self):
        """Set or update the OpenAI API key"""
        key_file = "openai_api_key.txt"
        
        if os.path.exists(key_file):
            with open(key_file, "r") as file:
                current_key = file.read().strip()
        else:
            current_key = ""
        
        new_key = simpledialog.askstring("Set API Key", "Enter your OpenAI API Key:", initialvalue=current_key)
        
        if new_key:
            with open(key_file, "w") as file:
                file.write(new_key)
            messagebox.showinfo("Success", "API Key updated successfully!")
        else:
            messagebox.showwarning("Warning", "API Key update canceled.")

    def configure_wordpress(self):
        """Placeholder for WordPress configuration"""
        messagebox.showinfo("WordPress Config", "WordPress configuration not yet implemented.")