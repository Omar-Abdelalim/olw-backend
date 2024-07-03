from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Date,Float,JSON
from sqlalchemy.orm import relationship
from db.base_class import Base


class Password(Base):
    id = Column(Integer, primary_key=True, index=True)
    customerID=Column(Integer,nullable=False)
    dateTime=Column(String,nullable=False)
    passwordStatus=Column(String,nullable=False)
    passwordHash=Column(String,nullable=False)
    

    def __str__(self):
        return self.id