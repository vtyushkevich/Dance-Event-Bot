# from sqlalchemy import Column, String
# from sqlalchemy.orm import relationship
#
# from core.mixins import TimestampMixin
# from core.models import Base
#
#
# class User(TimestampMixin, Base):
#     first_name = Column(String(200), unique=False, nullable=False)
#     second_name = Column(String(200), unique=False, nullable=False)
#     nickname = Column(String(200), unique=False, nullable=False)
#
#     author = relationship('User', back_populates='users', uselist=False)
#
#     def __str__(self):
#         return f'{self.__class__.__name__}(' \
#                f'id={self.id} ' \
#                f'title={self.nickname} )'