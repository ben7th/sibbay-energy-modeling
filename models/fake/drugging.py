from mongoengine import *
from datetime import datetime

class FakeDrugging(Document):
    name = StringField()
    user = ReferenceField('User')
    time = DateTimeField(required=True, default=datetime.now)