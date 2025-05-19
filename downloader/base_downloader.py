from abc import ABC, abstractmethod

class BaseDownloader(ABC):
    @abstractmethod
    def add_torrent(self, torrent_url):
        pass

    @abstractmethod
    def get_file_list(self, torrent_hash):
        pass

    @abstractmethod
    def set_file_priorities(self, torrent_hash, file_ids, priorities):
        pass