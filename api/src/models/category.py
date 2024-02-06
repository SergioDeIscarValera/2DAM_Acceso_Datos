import uuid

class Category:
    def __init__(self, title: str, description: str, priority: int, tasks: map, id: str = None):
        if id is None:
            self.id = uuid.uuid4().int
        else:
            self.id = id
        self.title = title
        self.description = description
        self.priority = priority
        self.tasks = tasks