from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Date,Float,JSON
from sqlalchemy.orm import relationship
from db.base_class import Base


class Pin(Base):
    id = Column(Integer, primary_key=True, index=True)
    customerID=Column(String,nullable=False)
    pin=Column(String,nullable=False)
    password=Column(String,nullable=True)
    status = Column(String,nullable=False)
    
    

    def __str__(self):
        return self.id