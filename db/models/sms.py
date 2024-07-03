from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Date,Float,JSON
from sqlalchemy.orm import relationship
from db.base_class import Base


class Sms(Base):
    id = Column(Integer, primary_key=True, index=True)
    customerID=Column(Integer,nullable=False)
    dateTime=Column(String,nullable=False)
    message=Column(String,nullable=False)
    mobileNumber=Column(String,nullable=False)
    countryCode=Column(String,nullable=False)
    priority=Column(String,nullable=True)
    result=Column(String,nullable=True)
    
    

    def __str__(self):
        return self.id