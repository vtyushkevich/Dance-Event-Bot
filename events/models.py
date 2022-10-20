# from sqlalchemy import Column, String, Integer, ForeignKey, Date
# from sqlalchemy.orm import relationship
#
# from core.mixins import TimestampMixin
# from core.models import Base
#
#
# class Event(TimestampMixin, Base):
#     event_name = Column(String(200), unique=False, nullable=False)
#     event_city = Column(String(200), unique=False, nullable=False)
#     event_country = Column(String(200), unique=False, nullable=False)
#     event_date_start = Column(Date, unique=False, nullable=False)
#     event_date_end = Column(Date, unique=False, nullable=False)
#     event_desc = Column(String(1024), unique=False, nullable=False)
#
#     created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
#     user = relationship('User', back_populates='events', uselist=True)
#
#     def __str__(self):
#         return f'{self.__class__.__name__}(' \
#                f'id={self.id} ' \
#                f'title={self.event_name} )'