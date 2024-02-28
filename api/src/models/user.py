import uuid
import datetime

class User:
    def __init__(self, name: str, email: str, password: str, id: str = str(uuid.uuid4()), update_date: str = None, create_date: str = None, is_active: bool = True):
        now = datetime.datetime.now()
        if update_date is None:
            update_date = now.strftime("%Y-%m-%d %H:%M:%S.%f")
        if create_date is None:
            create_date = now.strftime("%Y-%m-%d %H:%M:%S.%f")
        self.id = id
        self.name = name
        self.email = email
        self.password = password
        self.create_date = create_date
        self.update_date = update_date
        self.is_active = is_active