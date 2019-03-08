import test.config

import unittest
from models.user import User
from models.fake.drugging import FakeDrugging
from models.uplevel_relation import UplevelRelation
from mongoengine.errors import NotUniqueError
from mongoengine import ValidationError

output = test.config.output
def list_equal(list1, list2):
    l = list(set(list1).difference(set(list2)))
    return len(l) == 0

class TestOthers(unittest.TestCase):
    def test_create(self):
        count = len(User.objects)
        user = User.objects.create(
            email='ben7th@sina.com', 
            name='ben7th'
        )
        self.assertEqual(len(User.objects), count + 1)
        user.delete()

    def test_create_drugging(self):
        user = User.objects.create(
            email='ben7th@126.com', 
            name='宋亮'
        )

        count = len(FakeDrugging.objects)
        fd = FakeDrugging.objects.create(
            name='白加黑',
            user=user
        )
        self.assertEqual(len(FakeDrugging.objects), count + 1)
        self.assertEqual(fd.user.name, '宋亮')
        output(fd.to_json())
        user.delete()
        fd.delete()

    def _prepare_users(self):
        self.userA = User.objects.create(
            email='duckA@duck.ai', 
            name='小鸭A'
        )
        self.userB = User.objects.create(
            email='duckB@duck.ai', 
            name='小鸭B'
        )
        self.userC = User.objects.create(
            email='duckC@duck.ai', 
            name='小鸭C'
        )
        self.userD = User.objects.create(
            email='duckD@duck.ai', 
            name='小鸭D'
        )
        self.userE = User.objects.create(
            email='duckE@duck.ai', 
            name='小鸭E'
        )
        self.userF = User.objects.create(
            email='duckF@duck.ai', 
            name='小鸭F'
        )

    def _build_relation(self):
        UplevelRelation.set_relation(base=self.userA, uplevel=self.userB)
        UplevelRelation.set_relation(base=self.userC, uplevel=self.userB)

        self.assertEqual(len(UplevelRelation.objects), 2)
        self.assertEqual(UplevelRelation.get_uplevel_of(self.userA), self.userB)
        self.assertEqual(list_equal(UplevelRelation.get_downlevels_of(self.userB), 
            [self.userC, self.userA]), True)

        UplevelRelation.set_relation(base=self.userB, uplevel=self.userE)
        UplevelRelation.set_relation(base=self.userE, uplevel=self.userF)

        ancestors = UplevelRelation.get_ancestors_of(self.userA)
        self.assertEqual(list_equal(ancestors, [self.userB, self.userE, self.userF]), True)
        self.assertEqual(UplevelRelation.get_uplevel_of(self.userF), None)

    def _create_dup_base_user_relation(self):
        UplevelRelation.set_relation(base=self.userA, uplevel=self.userD)

    def _create_dup_relation(self):
        UplevelRelation.set_relation(base=self.userA, uplevel=self.userB)

    def _create_reverse_relation(self):
        UplevelRelation.set_relation(base=self.userB, uplevel=self.userA)

    def _create_circle_relation(self):
        UplevelRelation.set_relation(base=self.userF, uplevel=self.userA)

    def test_uplevel_relation(self):
        self._prepare_users()
        self._build_relation()

        # 不能为同一个用户创建不同的上级
        self.assertRaises(NotUniqueError, self._create_dup_base_user_relation)

        # 不能重复建立上下级关系
        self.assertRaises(ValidationError, self._create_dup_relation)

        # 不能颠倒建立上下级关系
        self.assertRaises(ValidationError, self._create_reverse_relation)

        # 不能建立循环关系
        self.assertRaises(ValidationError, self._create_circle_relation)