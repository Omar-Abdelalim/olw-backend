from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Date, Float, JSON
from sqlalchemy.orm import relationship
from db.base_class import Base


class VCardLogs(Base):
    id = Column(Integer, primary_key=True, index=True)
    Card = Column(Integer, nullable=False)
    Status = Column(String, nullable=False)
    date_time = Column(String, nullable=False)
    def __str__(self):
        return self.CardNumber