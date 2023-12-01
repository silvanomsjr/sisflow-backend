"""
Reused from flask-api-starter-kit: Define an Abstract Base Class (ABC) for models
Allows model operations: Conversion to json, Print, Conversion to dict, saving and deleting
"""
from datetime import datetime
from weakref import WeakValueDictionary

from sqlalchemy import inspect
from sqlalchemy.orm import aliased
from sqlalchemy.orm.collections import InstrumentedList

from . import db

class MetaBaseModel(db.Model.__class__):
    """ Define a metaclass for the BaseModel
        Implement `__getitem__` for managing aliases """

    def __init__(cls, *args):
        super().__init__(*args)
        cls.aliases = WeakValueDictionary()

    def __getitem__(cls, key):
        try:
            alias = cls.aliases[key]
        except KeyError:
            alias = aliased(cls)
            cls.aliases[key] = alias
        return alias

class BaseModel:
    """ Generalize __init__, __repr__ and to_json
        Based on the models columns """

    print_filter = []
    to_json_filter = []

    def __repr__(self):
        """ Define a custom __repr__ to format the models printing
            Columns inside `print_filter` var in the model are excluded """
        return "%s(%s)" % (
            self.__class__.__name__,
            {
                column: value
                for column, value in self._to_dict().items()
                if column not in self.print_filter
            },
        )

    @property
    def json(self):
        """ Define a base way to jsonify models
            Columns inside `to_json_filter` var in the model are excluded 
            Avoid returning InstrumentedList or BaseModel relationships """
        
        return {
            column: value
            if not isinstance(value, datetime)
            else value.strftime("%Y-%m-%d")
            for column, value in self._to_dict().items()
            if column not in self.to_json_filter and not isinstance(value, (InstrumentedList, BaseModel))
        }

    def _to_dict(self):
        """ Allows to_json to be overriden without impacting __repr__ 
            Because this method is used in __repr__ """
        return {
            column.key: getattr(self, column.key)
            for column in inspect(self.__class__).attrs
        }

    def save(self):
        """ Saves the object to db """
        db.session.add(self)
        db.session.commit()
        return self

    def delete(self):
        """ Deletes the object from db """
        db.session.delete(self)
        db.session.commit()
