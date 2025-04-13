# config.py
import os

# Default paths for configuration files and folders
RULES_FILE = "rules.txt"
IMAGE_RULES_FILE = "image_rules.txt"
API_KEY_FILE = "openai_api_key.txt"
WP_CONFIG_FILE = "wordpress_config.txt"
IMAGE_FOLDER = "generated_images"
ARTICLES_FOLDER = "generated_articles"

def ensure_folders_exist():
    """Ensure all required folders exist"""
    os.makedirs(IMAGE_FOLDER, exist_ok=True)
    os.makedirs(ARTICLES_FOLDER, exist_ok=True)

def load_api_key():
    """Load the OpenAI API key from file"""
    if os.path.exists(API_KEY_FILE):
        with open(API_KEY_FILE, 'r') as f:
            return f.read().strip()
    return None