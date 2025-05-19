# Choose downloader
from downloader.qbittorrent_downloader import QbittorrentDownloader
from downloader.deluge_downloader import DelugeDownloader

qbit = QbittorrentDownloader("http://localhost:8080", "admin", "adminadmin")
qbit.add_torrent("magnet:?xt=urn:btih:0080a6732a0b07dbeff44aae0d0a13486c5dbe3b&dn=%5BThz.la%5Dokax-333&tr=udp://tracker.openbittorrent.com:80&tr=udp://tracker.opentrackr.org:1337/announce")
qbit.get_file_list("0080a6732a0b07dbeff44aae0d0a13486c5dbe3b")
qbit.set_file_priorities("0080a6732a0b07dbeff44aae0d0a13486c5dbe3b", [0, 1, 2], [1, 2, 3])


# deluge = DelugeDownloader("http://localhost:8112", "deluge")