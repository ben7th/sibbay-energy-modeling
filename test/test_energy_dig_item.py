import test.config

import unittest
from bson import ObjectId
from models.energy_dig_item import EnergyDigItem
from models.user import User
from models.fake.drugging import FakeDrugging
from models.fake.treating import FakeTreating
from test.config import output

class TestEnergyDigItem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 创建用户
        cls.user = User.objects.create(
            name='宋亮',
            email='ben7th@gmail.com'
        )

    # 从用药记录挖矿
    def step1(self):
        # 创建用药记录
        drugging = FakeDrugging.objects.create(
            name='板蓝根冲剂',
            user=self.user
        )
        edi = EnergyDigItem.dig_from(drugging)
        output(edi.to_json())
        self.assertEqual(edi.dig_energy, 1500)
        self.assertEqual(edi.dig_type, 'DRUGGING')
        self.assertEqual(edi.source(), drugging)
        self.assertEqual(edi.source().user, self.user)
        self.assertEqual(edi.dig_user, self.user)

    # 从治疗记录挖矿
    def step2(self):
        # 创建治疗记录
        treating = FakeTreating.objects.create(
            name='针灸',
            user=self.user
        )
        edi = EnergyDigItem.dig_from(treating)
        output(edi.to_json())
        self.assertEqual(edi.dig_energy, 2500)
        self.assertEqual(edi.dig_type, 'TREATING')
        self.assertEqual(edi.source(), treating)
        self.assertEqual(edi.source().user, self.user) 
        self.assertEqual(edi.dig_user, self.user)
        self.assertEqual(edi.state, 'DEALING')

    # 查询用户挖矿记录
    def step3(self):
        items = EnergyDigItem.get_items_by_user(self.user)
        self.assertEqual(len(items), 2)
        total = EnergyDigItem.get_total_dig_energy_by_user(self.user)
        self.assertEqual(total, 4000)

    # 查询指定模型挖矿记录
    def step4(self):
        items1 = EnergyDigItem.get_items_by_source_model(FakeDrugging)
        self.assertEqual(len(items1), 1)
        items2 = EnergyDigItem.get_items_by_source_model(FakeTreating)
        self.assertEqual(len(items2), 1)
        items3 = EnergyDigItem.get_items_by_dig_type('DRUGGING')
        items4 = EnergyDigItem.get_items_by_dig_type('TREATING')
        self.assertEqual(len(items3), 1)
        self.assertEqual(len(items4), 1)

    # 建立分配项
    def step_split(self):
        a = EnergyDigItem.objects.first()
        print(a.do_split())

    def test_steps(self):
        self.step1()
        self.step2()
        self.step3()
        self.step4()
        self.step_split()