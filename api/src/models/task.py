import uuid


class Task:
    def __init__(self, title: str, description: str, done: bool, end_date: str, id: str = None, ):
        if id is None:
            self.id = str(uuid.uuid4())
        else:
            self.id = id
        self.title = title
        self.description = description
        self.done = done
        self.end_date = end_date
