from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Date,Float,JSON
from sqlalchemy.orm import relationship
from db.base_class import Base


class QRTer(Base):
    id = Column(Integer, primary_key=True, index=True)
    dateTime=Column(String,nullable=False)
    terminalID=Column(String,nullable=False)

    displayName=Column(String,nullable=False)
    merchantName=Column(String,nullable=False)
    currency=Column(String,nullable=False)
    qrStatus=Column(String,nullable=False)
    amount=Column(Float,nullable=False)
    transactionID = Column(Integer,nullable=True)
    

    def __str__(self):
        return self.id