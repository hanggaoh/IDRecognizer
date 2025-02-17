# Crawler with cronjob and parser and database and magnet support

## High-Level Workflow

Crawler Initialization: The Crawler starts with an initial list of URLs. Each URL is fetched, and the content is passed to the Parser.
Parsing: The Parser processes the content, extracts data, and sends it to the relevant DatabaseHandler. If additional URLs are discovered, they are passed back to the Crawler to be added to the queue.
Database Handling: The DatabaseHandler stores parsed data, creating new entries in the respective tables.
MagnetService Operations: If a page contains a magnet link, the Parser can call the MagnetService to add it to the torrent client, with the DatabaseHandler updating the status based on the result.