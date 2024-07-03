from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Date,Float,JSON
from sqlalchemy.orm import relationship
from db.base_class import Base


class Charge(Base):
    id = Column(Integer, primary_key=True, index=True)
    dateTime=Column(String,nullable=False)
    customerID=Column(String,nullable=False)
    accountNo=Column(String,nullable=False)

    currency=Column(String,nullable=False)
    amount=Column(Float,nullable=False)
    feesService=Column(Float,nullable=False)
    feesCurrency=Column(Float,nullable=False)

    email=Column(String,nullable=False)
    firstName=Column(String,nullable=False)
    lastName=Column(String,nullable=False)
    address=Column(String,nullable=False)
    zipcode=Column(String,nullable=False)
    city=Column(String,nullable=False)
    country=Column(String,nullable=False)
    countryCode=Column(String,nullable=False)
    mobilenumber=Column(String,nullable=False)
    birthDate=Column(String,nullable=False)

    chargeStatus = Column(String,nullable=False)
    method = Column(String,nullable=False)
    transactionID = Column(String,nullable=True)
    webhookID = Column(String,nullable=True)
    

    def __str__(self):
        return self.id