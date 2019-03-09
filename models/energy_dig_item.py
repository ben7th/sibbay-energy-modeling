from mongoengine import *
from datetime import datetime

from models.fake.drugging import FakeDrugging
from models.fake.treating import FakeTreating
from models.user import User
from models.uplevel_relation import UplevelRelation
from models.white_deer_relation import WhiteDeerRelation

# 挖矿类型与来源对照表
DIG_TABLE = {
    'FakeDrugging': { 'type': 'DRUGGING', 'energy': 1500, 'desc': '用药记录' },
    'FakeTreating': { 'type': 'TREATING', 'energy': 2500, 'desc': '治疗记录' },
}

TYPE_CODES = list(map(lambda x: x['type'], DIG_TABLE.values()))

# 挖矿记录项状态
STATE_CODES = {
    'DEALING': '正在处理',
    'SETTLED': '处理结束'
}

# 记录挖矿记录项
class EnergyDigItem(Document):
    # 挖矿的记录来源
    source_id = ObjectIdField(required=True)    # 来源模型 id
    source_model = StringField(required=True)   # 来源模型

    # 挖矿类型，参考类型对应表
    dig_type = StringField(required=True, choices=TYPE_CODES)

    # 挖矿产生的待分配生命力
    # 所有分配记录生命力 + 进入系统池生命力 = 待分配生命力
    # 此处取值毫牛顿，为对用户显示的值 * 1000
    dig_energy = IntField(required=True)

    # 挖矿的用户
    dig_user = ReferenceField(User, required=True)

    # 挖矿时间（生命力产生时间）
    dig_time = DateTimeField(required=True, default=datetime.now)

    # 处理状态
    # DEALING - 记录挖矿记录项已经产生，正等待各分配对象领取
    # SETTLED - 所有分配对象已领取/到时未领取生命力
    state = StringField(required=True, choices=STATE_CODES.keys(), default='DEALING')


    settled_time = DateTimeField()          # 生命力结清（分配完成）时间

    # 分配结束时，归纳到系统池的生命力，毫牛顿
    sys_pool_energy_value = IntField(required=True, default=0)

    # 从记录模型产生挖矿
    # 自动根据模型类型判断挖矿类型
    @classmethod
    def dig_from(cls, source):
        source_id = source.id
        source_model = source.__class__.__name__
        d = DIG_TABLE[source_model]
        dig_type = d['type']
        dig_energy = d['energy']
        dig_user = source.user

        edi = EnergyDigItem.objects.create(
            source_id=source_id,
            source_model=source_model,
            dig_type=dig_type,
            dig_energy=dig_energy,
            dig_user=dig_user
        )

        return edi

    # 建立分配项
    def do_split(self):
        # 先找到所有分配位对应的 user
        userC = self.dig_user
        userU1 = UplevelRelation.get_uplevel_of(userC)
        userU2 = UplevelRelation.get_uplevel_of(userU1)
        userU3 = UplevelRelation.get_uplevel_of(userU2)
        userWHITE = WhiteDeerRelation.get_white_user_of(userC)
        return [userC, userU1, userU2, userU3, userWHITE]
      
    # 获取来源对象
    def source(self):
        klass = globals()[self.source_model]
        return klass.objects(id=self.source_id).first()

    # 获取指定用户的挖矿记录项
    @classmethod
    def get_items_by_user(cls, user):
        return cls.objects(dig_user=user)

    # 获取指定用户总共的挖矿能量值
    @classmethod
    def get_total_dig_energy_by_user(cls, user):
        items = cls.get_items_by_user(user)
        _m = map(lambda x: x.dig_energy, items)
        return sum(list(_m))

    # 获取指定模型的挖矿记录项
    @classmethod
    def get_items_by_source_model(cls, model_klass):
        source_model = model_klass.__name__
        return cls.objects(source_model=source_model)

    # 获取指定类型的挖矿记录项
    @classmethod
    def get_items_by_dig_type(cls, dig_type):
        return cls.objects(dig_type=dig_type)