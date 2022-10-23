from datetime import datetime

import config

from sqlalchemy import (
    create_engine,
    Column,
    Integer, String, Date, ForeignKey, DateTime, Boolean,
)

from sqlalchemy.orm import (
    declarative_base,
    sessionmaker,
    scoped_session,
    declared_attr, relationship
)


class Base:
    @declared_attr
    def __tablename__(cls):
        return f'{cls.__name__.lower()}s'

    id = Column(Integer, primary_key=True)

    def __repr__(self):
        return str(self)


engine = create_engine(url=config.DB_URL, echo=config.DB_ECHO)
Base = declarative_base(bind=engine, cls=Base)
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)


class TimestampMixin:
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class Event(TimestampMixin, Base):
    event_name = Column(String(200), unique=False, nullable=False)
    event_city = Column(String(200), unique=False, nullable=False)
    event_country = Column(String(200), unique=False, nullable=False)
    event_date_start = Column(Date, unique=False, nullable=False)
    event_date_end = Column(Date, unique=False, nullable=False)
    event_desc = Column(String(1024), unique=False, nullable=False)
    event_photo = Column(String(1024), unique=False, nullable=False)
    deleted = Column(Boolean, unique=False, nullable=False, default=False)

    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship('User', back_populates='events', uselist=True)

    def __str__(self):
        return f'{self.__class__.__name__}(' \
               f'id={self.id} ' \
               f'title={self.event_name} )'


class User(TimestampMixin, Base):
    first_name = Column(String(200), unique=False, nullable=False)
    second_name = Column(String(200), unique=False, nullable=False)
    nickname = Column(String(200), unique=False, nullable=False)
    access_level = Column(Integer, unique=False, nullable=False, default=1)
    deleted = Column(Boolean, unique=False, nullable=False, default=False)

    events = relationship('Event', back_populates='user', uselist=False)

    def __str__(self):
        return f'{self.__class__.__name__}(' \
               f'id={self.id} ' \
               f'title={self.nickname} )'