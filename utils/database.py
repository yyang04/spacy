from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Mapped
import json
from typing import List


class Base(DeclarativeBase):
    pass


class Word(Base):
    __tablename__ = 'word'
    id: Mapped[int] = mapped_column(primary_key=True)
    word: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    definitions: Mapped[List['Definition']] = relationship(back_populates='word')  # ClassName,ColumnName


class Definition(Base):
    __tablename__ = 'definition'
    id: Mapped[int] = mapped_column(primary_key=True)
    word: Mapped['Word'] = relationship(back_populates='definitions')
    definition: Mapped[str] = mapped_column(String(200), nullable=True)
    pos: Mapped[str] = mapped_column(String(50), nullable=True)

    word_id: Mapped[int] = mapped_column(ForeignKey('word.id'))  # tableName.columnName
    sentences: Mapped[List['Sentence']] = relationship(back_populates='definition')


class Sentence(Base):
    __tablename__ = 'sentence'
    id: Mapped[int] = mapped_column(primary_key=True)
    definition: Mapped['Definition'] = relationship(back_populates='sentences')
    sentence: Mapped[str] = mapped_column(String(200), nullable=True)

    definition_id: Mapped[int] = mapped_column(ForeignKey('definition.id'))


class DataBase:
    def __init__(self):
        self.engine = create_engine('sqlite:///database.db', echo=True)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def createTable(self):
        Base.metadata.create_all(self.engine)

    def insert(self, instance):
        self.session.add(instance)
        self.session.commit()





# user = User(name='Alice', age=25)
# session.add(user)
# session.commit()
#
#
# users = session.query(User).all()
# for user in users:
#     print(user.name, user.age)


if __name__ == '__main__':
    database = DataBase()





