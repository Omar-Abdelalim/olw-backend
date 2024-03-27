from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Date,Float,JSON
from sqlalchemy.orm import relationship
from db.base_class import Base


class Customer(Base):
    id = Column(Integer, primary_key=True, index=True)
    firstName=Column(String,nullable=False)
    lastName=Column(String,nullable=False)
    fullAddress=Column(String,nullable=False)
    customerStatus=Column(String,nullable=False)
    comment=Column(String,nullable=True)


    def __str__(self):
        return self.id