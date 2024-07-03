from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Date,Float,JSON
from sqlalchemy.orm import relationship
from db.base_class import Base


class Currency(Base):
    id = Column(Integer, primary_key=True, index=True)
    country=Column(String,nullable=False)
    currencyName=Column(String,nullable=False)
    code=Column(String,nullable=False)
    status=Column(String,nullable=False)
    
    

    def __str__(self):
        return self.id