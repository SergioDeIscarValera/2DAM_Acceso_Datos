from graphene import ObjectType, String, ID, DateTime, Boolean
class TaskType(ObjectType):
    id = ID()
    title = String()
    description = String()
    done = Boolean()
    is_important = Boolean()
    end_date = DateTime()
    create_date = DateTime()
    update_date = DateTime()
