from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Date,Float,JSON
from sqlalchemy.orm import relationship
from db.base_class import Base


class KYC(Base):
    id = Column(Integer, primary_key=True, index=True)
    customerID=Column(Integer,nullable=False)
    firstName=Column(String,nullable=False)
    familyName=Column(String,nullable=False)
    birthDate=Column(String,nullable=False)
    fullAddress=Column(String,nullable=False)
    birthCountry=Column(String,nullable=False)
    residenceCountry=Column(String,nullable=False)
    kycStatus=Column(String,nullable=False)
    images=Column(String,nullable=True)
    
    

    def __str__(self):
        return self.id