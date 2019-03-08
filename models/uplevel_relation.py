from mongoengine import *

from models.user import User

class UplevelRelation(Document):
    # 当前用户
    # 不能为同一个用户创建不同的上级
    base_user = ReferenceField(User, required=True, unique=True)

    # 该用户的上级用户
    uplevel_user = ReferenceField(User)

    def clean(self):
        # 如果两个用户之间已经有上下级关系，不能重复创建
        ur = UplevelRelation.objects(
            base_user=self.base_user, 
            uplevel_user=self.uplevel_user
        ).first()
        if ur:
            raise ValidationError('不能重复建立上下级关系')

        # 如果两个用户之间已经有上下级关系，不能反过来创建
        ur = UplevelRelation.objects(
            base_user=self.uplevel_user, 
            uplevel_user=self.base_user
        ).first()
        if ur:
            raise ValidationError('不能颠倒创立上下级关系')

        # 不能建立循环关系
        ancestors = UplevelRelation.get_ancestors_of(self.uplevel_user)
        if self.base_user in ancestors:
            raise ValidationError('不能建立循环关系')


    # 设置两个用户之间的上下级关系
    @classmethod
    def set_relation(cls, base, uplevel):
        return cls.objects.create(base_user=base, uplevel_user=uplevel)

    # 获取指定用户的上级用户
    @classmethod
    def get_uplevel_of(cls, user):
        x = cls.objects(base_user=user).first()
        if x:
            return x.uplevel_user
        else:
            return None

    # 获取指定用户的祖先用户
    @classmethod
    def get_ancestors_of(cls, user):
        result = []
        u = user
        while True:
            uplevel_user = cls.get_uplevel_of(u)
            if uplevel_user:
                result.append(uplevel_user)
                u = uplevel_user
            else:
                break
        return result

    # 获取指定用户的下级用户
    @classmethod
    def get_downlevels_of(cls, user):
        items = cls.objects(uplevel_user=user)
        _map = map(lambda x: x.base_user, items)
        return list(_map)