from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Date, Float, JSON
from sqlalchemy.orm import relationship
from db.base_class import Base


class VCard(Base):
    id = Column(Integer, primary_key=True, index=True)
    AccountId = Column(Integer, nullable=False)
    customerName = Column(String, nullable=False)
    CardNumber = Column(String, nullable=False)
    issueDate = Column(String, nullable=False)
    expiryDate = Column(String, nullable=False)
    cardName = Column(String, nullable=False)
    cardBrand = Column(Boolean, nullable=False)
    cardType = Column(String, nullable=False)
    status = Column(String, nullable=False)
    cardProfile=Column(JSON,nullable=False)
    isPhysical = Column(Boolean,nullable = False)
    lastTransaction = Column(String, nullable=True)
    def __str__(self):
        return self.CardNumber