# ai_services.py
import openai
import base64
from io import BytesIO
from PIL import Image
from config import RULES_FILE, IMAGE_RULES_FILE, IMAGE_FOLDER, API_KEY_FILE
import os

class AIServices:
    def __init__(self):
        self.api_key = self.load_api_key()
        if self.api_key:
            openai.api_key = self.api_key
    
    def load_api_key(self):
        if os.path.exists(API_KEY_FILE):
            with open(API_KEY_FILE, 'r') as f:
                return f.read().strip()
        return None
    
    def check_api_key(self):
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Please set your API key first.")
    
    def generate_article(self, prompt):
        self.check_api_key()
        rules = ""
        if os.path.exists(RULES_FILE):
            with open(RULES_FILE, 'r') as f:
                rules = f.read()
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"Follow these rules: {rules}"},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    
    def generate_image(self, prompt):
        self.check_api_key()
        image_rules = ""
        if os.path.exists(IMAGE_RULES_FILE):
            with open(IMAGE_RULES_FILE, 'r') as f:
                image_rules = f.read()
        
        full_prompt = f"{prompt}. {image_rules}" if image_rules else prompt
        
        response = openai.Image.create(
            prompt=full_prompt,
            n=1,
            size="512x512",
            response_format="b64_json"
        )
        
        image_data = base64.b64decode(response['data'][0]['b64_json'])
        return Image.open(BytesIO(image_data))