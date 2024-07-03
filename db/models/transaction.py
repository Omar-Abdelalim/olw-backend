from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Date,Float,JSON
from sqlalchemy.orm import relationship
from db.base_class import Base


class Transaction(Base):
    id = Column(Integer, primary_key=True, index=True)
    dateTime=Column(String,nullable=False)

    accountNo=Column(String,nullable=False)
    outAccountNo=Column(String,nullable=False)
    
    
    transactionStatus=Column(String,nullable=False)
    description=Column(String,nullable=True)
    amount=Column(Integer,nullable=False)

    sendID=Column(Integer,nullable=False)
    recID = Column(Integer,nullable=False)
    
    

    def __str__(self):
        return self.id