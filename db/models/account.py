from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Date,Float,JSON
from sqlalchemy.orm import relationship
from db.base_class import Base


class Account(Base):
    id = Column(Integer, primary_key=True, index=True)
    customerID=Column(Integer,nullable=False)
    dateTime=Column(String,nullable=False)
    accountStatus=Column(String,nullable=False)
    accountNumber=Column(String,nullable=False)
    accountType=Column(String,nullable=False)
    primaryAccount=Column(Boolean,nullable=False)
    balance=Column(Integer,nullable=False)
    country=Column(String,nullable=False)
    currency=Column(String,nullable=False)
    friendlyName=Column(String,nullable=False)
    iBan=Column(String,nullable=False)

    
    

    def __str__(self):
        return self.id