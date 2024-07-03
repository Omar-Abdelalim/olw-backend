from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Date,Float,JSON
from sqlalchemy.orm import relationship
from db.base_class import Base


class TransactionRequestIncoming(Base):
    id = Column(Integer, primary_key=True, index=True)
    dateTime=Column(String,nullable=False)

    inIBan=Column(String,nullable=False)
    accountNo=Column(String,nullable=False)
    currency=Column(String,nullable=False)
    country=Column(String,nullable=False)
    sendingCurrency=Column(String,nullable=False)
    sendingCountry=Column(String,nullable=False)

    direction=Column(String,nullable=False)
    
    
    transactionStatus=Column(String,nullable=False)
    description=Column(String,nullable=True)
    amount=Column(Integer,nullable=False)
    feesCode=Column(String,nullable=False)
    

    def __str__(self):
        return self.id