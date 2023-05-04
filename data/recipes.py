import sqlalchemy
from .db_session import SqlAlchemyBase


class Recipe(SqlAlchemyBase):
    __tablename__ = 'recipes'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    ingridients = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    cooking_method = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    nutrition_facts = sqlalchemy.Column(sqlalchemy.String, nullable=True)

