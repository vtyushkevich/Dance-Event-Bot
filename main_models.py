from datetime import datetime

import config

from sqlalchemy import (
    create_engine,
    Column,
    Integer, String, Date, ForeignKey, DateTime, Boolean, BigInteger,
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
    unique_id = Column(BigInteger, unique=True, nullable=False)
    first_name = Column(String(200), unique=False, nullable=True)
    second_name = Column(String(200), unique=False, nullable=True)
    nickname = Column(String(200), unique=False, nullable=True)
    access_level = Column(Integer, unique=False, nullable=False, default=1)
    deleted = Column(Boolean, unique=False, nullable=False, default=False)

    events = relationship('Event', back_populates='user', uselist=False)
    parties = relationship('Party', back_populates='user', uselist=True)

    def __str__(self):
        return f'{self.__class__.__name__}(' \
               f'id={self.id} ' \
               f'title={self.nickname} )'


class Party(TimestampMixin, Base):
    event_id = Column(Integer, ForeignKey('events.id'), unique=False, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), unique=False, nullable=False)
    status = Column(Integer, unique=False, nullable=False)

    user = relationship('User', back_populates='parties', uselist=False)

    def __str__(self):
        return f'{self.__class__.__name__}(' \
               f'id={self.id} ' \
               f'user_id={self.user_id} ' \
               f'user_nick={self.user.nickname} ' \
               f'event_id={self.event_id} )'