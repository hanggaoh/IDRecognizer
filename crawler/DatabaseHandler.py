class DatabaseHandler:
    def __init__(self, db_name):
        # Initialize DB connection
        pass

    def execute_query(self, query, params):
        # Execute generic query
        pass

class PageDataHandler(DatabaseHandler):
    def insert_page_data(self, data):
        # Insert page-specific data into the database
        pass

class TorrentDataHandler(DatabaseHandler):
    def insert_torrent_data(self, data):
        # Insert torrent-specific data into the database
        pass
