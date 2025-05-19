import requests
from .base_downloader import BaseDownloader

class DelugeDownloader(BaseDownloader):
    def __init__(self, host, password):
        self.host = host
        self.session = requests.Session()
        self.session_id = None
        self._login(password)

    def _login(self, password):
        r = self.session.post(f"{self.host}/json", json={"method": "auth.login", "params": [password], "id": 1})
        r.raise_for_status()
        self.session_id = r.cookies.get("session_id")

    def add_torrent(self, torrent_url):
        self.session.post(f"{self.host}/json", json={"method": "core.add_torrent_url", "params": [torrent_url, {}], "id": 2})

    def get_file_list(self, torrent_id):
        r = self.session.post(f"{self.host}/json", json={"method": "core.get_torrent_files", "params": [torrent_id], "id": 3})
        r.raise_for_status()
        return r.json()["result"]

    def set_file_priorities(self, torrent_id, file_priorities):
        self.session.post(f"{self.host}/json", json={"method": "core.set_torrent_file_priorities", "params": [torrent_id, file_priorities], "id": 4})