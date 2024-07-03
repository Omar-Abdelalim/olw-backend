from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Date,Float,JSON
from sqlalchemy.orm import relationship
from db.base_class import Base


class Options(Base):
    id = Column(Integer, primary_key=True, index=True)
    name=Column(String,nullable=False)
    table=Column(String,nullable=False)
    start=Column(Integer,nullable=False)
    end=Column(Integer,nullable=False)
    
    

    def __str__(self):
        return self.id