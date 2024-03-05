from graphene import ObjectType, String, ID, DateTime, Boolean
class UserType(ObjectType):
    id = ID()
    name = String()
    email = String()
    password = String()
    create_date = DateTime()
    update_date = DateTime()
    is_verified = Boolean()
    verify_code = String()