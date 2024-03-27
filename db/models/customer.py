from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Date,Float,JSON
from sqlalchemy.orm import relationship
from db.base_class import Base


class Customer(Base):
    id = Column(Integer, primary_key=True, index=True)
    firstName=Column(String,nullable=False)
    lastName=Column(String,nullable=False)
    email=Column(String,nullable=True)
    dateTime=Column(String,nullable=False)

    birthDate = Column(String,nullable=False)
    status=Column(String,nullable=False)
    phoneNumber=Column(String,nullable=True)
    countryCode=Column(String,nullable=True)
    nationalInterID=Column(String,nullable=True)
    

    def __str__(self):
        return self.id