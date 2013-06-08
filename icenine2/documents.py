from mongoengine import *

from metaclass import enum


class FileTypes:
    __metaclass__ = enum
    TV = 'tv'
    MOVIE = 'movie'


class EntityTypes:
    __metaclass__ = enum
    FILE = 'file'
    DIRECTORY = 'directory'


class Directory(Document):
    type = StringField(required=True, choices=FileTypes.values)
    name = StringField(required=True)
    parent_id = ObjectIdField()
    found = BooleanField(required=True, default=False)
    relative_path = StringField(required=True)
    info_link = URLField()

    meta = {
        'indexes': [
            {
                'fields': ('type', 'relative_path'),
                'unique': True
            },
            {
                'fields': ('type', 'parent_id', 'name'),
                'unique': True
            }
        ]
    }


class File(Document):
    type = StringField(required=True, choices=FileTypes.values)
    name = StringField(required=True)
    filesystem_path = StringField(required=True, unique=True)
    size = LongField(min_value=0)
    addition_date = DateTimeField()
    parent_id = ObjectIdField()
    found = BooleanField(required=True, default=False)
    relative_path = StringField(required=True)
    info_link = URLField()
    keywords = ListField(StringField)
    rating = DecimalField(min_value=0, max_value=10, precision=2)

    meta = {
        'indexes': [
            {
                'fields': ('type', 'parent_id', 'name'),
                'unique': True
            },
            '-addition_date'
        ]
    }



