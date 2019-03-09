from mongoengine import *

POSITION_CODES = {
    'C': '挖矿人',
    'U1': '上一级',
    'U2': '上二级',
    'U3': '上三级',
    'WHITE': '大白'
}

# 记录挖矿分配项（流水项）
class EnergySplitItem(Document):
    # 隶属的记录挖矿记录项
    # CASCADE (2) - Deletes the documents associated with the reference.
    dig_item = ReferenceField('EnergyDigItem', reverse_delete_rule=CASCADE, required=True)

    # 分配位
    position = StringField(required=True, choices=POSITION_CODES.keys())

    # 被分配的能量值，毫牛顿
    energy_value = IntField(required=True)

    create_time = DateTimeField(required=True)      # 分配项创建时间
    deadline_time = DateTimeField(required=True)    # 分配项领取截止时间
    collected_time = DateTimeField()                # 实际领取时间
