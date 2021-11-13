from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from models.database import Base


class UserInfo(Base):
    __tablename__ = 'users_info'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    surname = Column(String)
    name = Column(String)
    patronymic = Column(String)
    role = Column(String)
    type_organization = Column(String)
    name_organization = Column(String)
    ITN = Column(String)
    CRR = Column(String)

    user = relationship('User', backref="users_info")

    def __init__(self, full_name: list[str], role: str, type_organization: str, name_organization: str, itn: str, crr: str):
        self.surname = full_name[0]
        self.name = full_name[1]
        self.patronymic = full_name[2]
        self.role = role
        self.type_organization = type_organization
        self.name_organization = name_organization
        self.ITN = itn
        self.CRR = crr

    def __repr__(self):
        return f'{self.user_id}, {self.surname}, {self.name}, {self.patronymic}, {self.role}, {self.type_organization}, {self.name_organization}, {self.ITN}, {self.CRR}'
