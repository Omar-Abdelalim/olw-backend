from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Date,Float,JSON
from sqlalchemy.orm import relationship
from db.base_class import Base


class Fee(Base):
    id = Column(Integer, primary_key=True, index=True)
    groupCode = Column(String,nullable=False)
    feeCode=Column(String,nullable=False)
    feeDesc=Column(String,nullable=False)
    feeRate=Column(Float,nullable=False)
    feeAmount=Column(Float,nullable=False)
    feeStatus=Column(String,nullable=False)

    feeMax=Column(Float,nullable=False)
    feeMin=Column(Float,nullable=False)
    
    

    def __str__(self):
        return self.id