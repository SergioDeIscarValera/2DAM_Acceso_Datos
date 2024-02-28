import uuid
import datetime

class Task:
    def __init__(self, title: str, description: str, done: bool, is_important: bool, end_date: str, update_date: str = None, create_date: str = None, id: str = str(uuid.uuid4()), ):
        now = datetime.datetime.now()
        if update_date is None:
            update_date = now.strftime("%Y-%m-%d %H:%M:%S.%f")
        if create_date is None:
            create_date = now.strftime("%Y-%m-%d %H:%M:%S.%f")
        
        self.id = id
        self.title = title
        self.description = description
        self.done = done
        self.end_date = end_date
        self.create_date = create_date
        self.update_date = update_date
        self.is_important = is_important
