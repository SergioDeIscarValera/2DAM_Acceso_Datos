import uuid
import datetime

class User:
    def __init__(self, 
    name: str, email: str, 
    password: str, 
    id: str = None, 
    update_date: str = None, 
    create_date: str = None, 
    is_verified: bool = False,
    verify_code: str = None):
        now = datetime.datetime.now()
        if update_date is None:
            update_date = now.strftime("%Y-%m-%d %H:%M:%S.%f")
        if create_date is None:
            create_date = now.strftime("%Y-%m-%d %H:%M:%S.%f")
        if id is None:
            self.id = str(uuid.uuid4())
        else:
            self.id = id
        if verify_code is None:
            self.verify_code = str(uuid.uuid4())
        else:
            self.verify_code = verify_code
        self.name = name
        self.email = email
        self.password = password
        self.create_date = create_date
        self.update_date = update_date
        self.is_verified = is_verified