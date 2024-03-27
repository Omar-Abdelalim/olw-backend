from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Date,Float,JSON
from sqlalchemy.orm import relationship
from db.base_class import Base


class OTP(Base):
    id = Column(Integer, primary_key=True, index=True)
    dateTime=Column(String,nullable=False)
    phoneNumber=Column(String,nullable=False)
    countryCode=Column(String,nullable=False)
    otp=Column(String,nullable=False)
    status=Column(String,nullable=False)
    remainingTrials=Column(Integer,nullable=False)
    timeoutTime=Column(String,nullable=False)
    

    def __str__(self):
        return self.id