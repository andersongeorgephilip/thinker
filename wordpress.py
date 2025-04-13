# wordpress.py
import requests
import os
from requests.auth import HTTPBasicAuth
from config import WP_CONFIG_FILE, IMAGE_FOLDER

class WordPressClient:
    def __init__(self):
        self.wp_url = None
        self.auth = None
        self._load_and_validate_config()

    def _load_and_validate_config(self):
        config = {}
        if os.path.exists(WP_CONFIG_FILE):
            with open(WP_CONFIG_FILE, 'r') as f:
                for line in f:
                    if line.strip() and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        config[key.strip()] = value.strip()

        required = ['WORDPRESS_URL', 'WORDPRESS_USERNAME', 'WORDPRESS_PASSWORD']
        missing = [field for field in required if not config.get(field)]
        
        if missing:
            raise ValueError(f"Missing WordPress config: {', '.join(missing)}")

        self.wp_url = config['WORDPRESS_URL'].rstrip('/')
        self.auth = HTTPBasicAuth(
            config['WORDPRESS_USERNAME'],
            config['WORDPRESS_PASSWORD']
        )

    def upload_media(self, image_path):
        url = f"{self.wp_url}/wp-json/wp/v2/media"
        
        with open(image_path, 'rb') as image_file:
            response = requests.post(
                url,
                files={'file': (os.path.basename(image_path), image_file, 'image/png')},
                auth=self.auth
            )
        
        response.raise_for_status()
        return response.json()['id']

    def create_post(self, title, content, image_path=None, categories=None, schedule_time=None):
        """Create or schedule post"""
        media_id = None
        if image_path and os.path.exists(image_path):
            media_id = self.upload_media(image_path)
        
        post_data = {
            'title': title,
            'content': content,
            'status': 'publish' if not schedule_time else 'future',
            'categories': categories or []
        }
        
        if schedule_time:
            post_data['date'] = schedule_time  # ISO 8601 format
            
        if media_id:
            post_data['featured_media'] = media_id
            
        response = requests.post(
            f"{self.wp_url}/wp-json/wp/v2/posts",
            json=post_data,
            auth=self.auth
        )
        
        response.raise_for_status()
        return response.json()
