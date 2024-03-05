from src.models.user import User
from src.models.user_type import UserType
from graphene.types import ObjectType
from datetime import datetime
from typing import Union

class UserMapperService(ObjectType):
    @staticmethod
    def map_user_to_user_type(user: User) -> UserType:
        return UserType(
            id=user.id,
            name=user.name,
            email=user.email,
            password=user.password,
            create_date=datetime.strptime(user.create_date, "%Y-%m-%d %H:%M:%S.%f"),
            update_date=datetime.strptime(user.update_date, "%Y-%m-%d %H:%M:%S.%f"),
            is_verified=user.is_verified,
            verify_code=user.verify_code
        )

    @staticmethod
    def map_user_type_to_user(user_type: UserType) -> User:
        return User(
            id=user_type.id,
            name=user_type.name,
            email=user_type.email,
            password=user_type.password,
            create_date=user_type.create_date.strftime("%Y-%m-%d %H:%M:%S.%f"),
            update_date=user_type.update_date.strftime("%Y-%m-%d %H:%M:%S.%f"),
            is_verified=user_type.is_verified,
            verify_code=user_type.verify_code
        )