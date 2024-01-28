# from datetime import datetime

from mongoengine import Document
from mongoengine.fields import ListField, StringField, ReferenceField 


class Author(Document):
    fullname = StringField()
    born_date = StringField()
    born_location = StringField()
    description = StringField()


class Quotes(Document):
    tags = ListField()
    author = ReferenceField('Author')
    quote = StringField()


