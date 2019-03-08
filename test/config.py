from mongoengine import connect
connect('energy-test')

from models.energy_dig_item import EnergyDigItem
from models.user import User
from models.fake.drugging import FakeDrugging
from models.fake.treating import FakeTreating
from models.uplevel_relation import UplevelRelation

# 清空测试数据库
EnergyDigItem.objects.delete()
User.objects.delete()
FakeDrugging.objects.delete()
FakeTreating.objects.delete()
UplevelRelation.objects.delete()

def output(str):
    print(str.encode('latin-1').decode('unicode-escape'))