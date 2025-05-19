import requests
from .base_downloader import BaseDownloader

class QbittorrentDownloader(BaseDownloader):
    def __init__(self, host, username, password):
        self.host = host
        self.session = requests.Session()
        self.session.post(f"{host}/api/v2/auth/login", data={"username": username, "password": password})

    def add_torrent(self, torrent_url):
        r = self.session.post(f"{self.host}/api/v2/torrents/add", data={"urls": torrent_url})
        r.raise_for_status()

    def get_file_list(self, torrent_hash):
        r = self.session.get(f"{self.host}/api/v2/torrents/files", params={"hash": torrent_hash})
        r.raise_for_status()
        return r.json()

    def set_file_priorities(self, torrent_hash, file_ids, priorities):
        for file_id, priority in zip(file_ids, priorities):
            self.session.post(f"{self.host}/api/v2/torrents/filePrio", data={"hash": torrent_hash, "id": file_id, "priority": priority})