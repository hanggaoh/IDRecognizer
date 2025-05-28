import sqlite3

class DatabaseManager:
    def __init__(self, db_path="tasks.db"):
        self.db_path = db_path
        self._setup_db()

    def _setup_db(self):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    args TEXT,
                    kwargs TEXT,
                    status TEXT DEFAULT 'pending'
                )
            ''')
            conn.commit()

    def add_task(self, name, args, kwargs):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('INSERT INTO tasks (name, args, kwargs, status) VALUES (?, ?, ?, ?)',
                      (name, args, kwargs, 'pending'))
            conn.commit()

    def get_next_task(self):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT id, name, args, kwargs FROM tasks WHERE status='pending' ORDER BY id LIMIT 1")
            row = c.fetchone()
            if row:
                c.execute("UPDATE tasks SET status='running' WHERE id=?", (row[0],))
                conn.commit()
            return row

    def update_task_status(self, task_id, status):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("UPDATE tasks SET status=? WHERE id=?", (status, task_id))
            conn.commit()