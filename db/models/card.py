from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Date,Float,JSON
from sqlalchemy.orm import relationship
from db.base_class import Base


class Card(Base):
    id = Column(Integer, primary_key=True, index=True)
    dateTime=Column(String,nullable=False)
    customerID=Column(String,nullable=False)
    token=Column(String,nullable=False)

    cardNumber=Column(String,nullable=False)
    expMonth=Column(String,nullable=False)
    expYear=Column(String,nullable=False)
    holderName=Column(String,nullable=False)
    secretNumber=Column(String,nullable=False)
    
    cardStatus = Column(String,nullable=False)
    cardDescription = Column(String,nullable=False)
    
    def __str__(self):
        return self.id