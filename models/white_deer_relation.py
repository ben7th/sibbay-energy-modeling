from mongoengine import *

from models.user import User

class WhiteDeerRelation(Document):
    # 大白用户
    white_user = ReferenceField(User, required=True)

    # 小鹿用户
    deer_user = ReferenceField(User, required=True)

    # 设置两个用户之间的大白小鹿关系
    @classmethod
    def set_relation(cls, white, deer):
        return cls.objects.create(white_user=white, deer_user=deer)

    # 获取指定用户的大白
    @classmethod
    def get_white_user_of(cls, user):
        x = cls.objects(deer_user=user).first()
        if x:
            return x.white_user
        else:
            return None