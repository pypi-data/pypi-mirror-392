#!/usr/bin/env python3
"""
Tinybeans authentication module
"""
import requests
import yaml

class TinybeansAuth:
    def __init__(self, config_path='config.yaml'):
        self.config = self._load_config(config_path)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.authenticated = False
        self.user_info = None

    def _load_config(self, config_path):
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            raise Exception(f"Error loading config file: {e}")

    def authenticate(self):
        """Authenticate with Tinybeans API"""
        if self.authenticated:
            return True

        auth_config = self.config.get('auth', {})
        email = auth_config.get('email')
        password = auth_config.get('password')

        if not email or not password:
            raise ValueError("Email and password required in config.yaml")

        # API authentication
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        login_data = {
            'doNotCreateUser': True,
            'clientId': 'd324d503-0127-4a85-a547-d9f2439ffeae',  # Found in main.js
            'captchaToken': '',
            'username': email,
            'password': password
        }

        try:
            response = self.session.post(
                'https://tinybeans.com/api/1/authenticate',
                json=login_data,
                headers=headers
            )

            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'ok':
                    self.authenticated = True
                    self.user_info = data.get('user', {})

                    # Set auth header if we get a token
                    access_token = data.get('accessToken')
                    if access_token:
                        self.session.headers['Authorization'] = f'Bearer {access_token}'

                    return True
                else:
                    raise Exception(f"Authentication failed: {data.get('detailedMessage', 'Unknown error')}")

        except Exception as e:
            raise Exception(f"Authentication error: {e}")

        return False

    def get_session(self):
        """Get authenticated session"""
        if not self.authenticated and not self.authenticate():
            raise Exception("Authentication failed")
        return self.session

    def get_tinybeans_id(self):
        """Get tinybeans ID from config"""
        return self.config.get('tinybeans_id')
