from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Date,Float,JSON
from sqlalchemy.orm import relationship
from db.base_class import Base


class QR(Base):
    id = Column(Integer, primary_key=True, index=True)
    dateTime=Column(String,nullable=False)
    customerID=Column(String,nullable=False)
    accountNo=Column(String,nullable=False)

    currency=Column(String,nullable=False)
    qrStatus=Column(String,nullable=False)
    amount=Column(Integer,nullable=False)
    transactionID = Column(Integer,nullable=True)
    

    def __str__(self):
        return self.id