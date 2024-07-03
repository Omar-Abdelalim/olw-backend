from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Date,Float,JSON
from sqlalchemy.orm import relationship
from db.base_class import Base


class Bank(Base):
    id = Column(Integer, primary_key=True, index=True)
    accountNumber=Column(String,nullable=False)
    bankName=Column(String,nullable=False)
    friendlyName=Column(String,nullable=False)
    country=Column(String,nullable=False)
    currency=Column(String,nullable=False)
    otherNames=Column(String,nullable=False)
    surName=Column(String,nullable=False)
    bankType=Column(String,nullable=False)
    iBan=Column(String,nullable=False)
    bic=Column(String,nullable=True)
    beneficiary=Column(String,nullable=False)
    beneficiaryAddress=Column(String,nullable=False)
    shortDescription=Column(String,nullable=False)
    

    def __str__(self):
        return self.id