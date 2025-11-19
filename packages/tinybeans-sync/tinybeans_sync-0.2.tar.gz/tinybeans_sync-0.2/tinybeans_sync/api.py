#!/usr/bin/env python3
"""
Tinybeans API client
"""
from .auth import TinybeansAuth

class TinybeansAPI:
    def __init__(self, config_path='config.yaml'):
        self.auth = TinybeansAuth(config_path)

    def get_entries(self, year, month):
        """Get all entries for a specific year/month"""
        session = self.auth.get_session()
        tinybeans_id = self.auth.get_tinybeans_id()

        if not tinybeans_id:
            raise ValueError("tinybeans_id required in config.yaml")

        endpoint = f"https://tinybeans.com/api/1/journals/{tinybeans_id}/entries"
        params = {'year': year, 'month': month}

        response = session.get(endpoint, params=params)
        response.raise_for_status()

        data = response.json()
        return data.get('entries', [])

    def get_user_info(self):
        """Get authenticated user info"""
        if not self.auth.authenticated:
            self.auth.authenticate()
        return self.auth.user_info
