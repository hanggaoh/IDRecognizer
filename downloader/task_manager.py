import threading
import time
import json

class TaskManager:
    def __init__(self, db_manager, registry):
        self.db_manager = db_manager
        self.registry = registry
        self.running = False

    def add_task(self, name, *args, **kwargs):
        self.db_manager.add_task(name, json.dumps(args), json.dumps(kwargs))

    def run(self, poll_interval=2):
        self.running = True
        while self.running:
            task = self.db_manager.get_next_task()
            if task:
                task_id, name, args, kwargs = task
                func = self.registry.get(name)
                if func:
                    try:
                        func(*json.loads(args), **json.loads(kwargs))
                        self.db_manager.update_task_status(task_id, 'done')
                    except Exception as e:
                        self.db_manager.update_task_status(task_id, 'failed')
                else:
                    self.db_manager.update_task_status(task_id, 'unknown')
            else:
                time.sleep(poll_interval)

    def start(self):
        t = threading.Thread(target=self.run, daemon=True)
        t.start()