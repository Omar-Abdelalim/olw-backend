from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Date,Float,JSON
from sqlalchemy.orm import relationship
from db.base_class import Base


class Notification(Base):
    id = Column(Integer, primary_key=True, index=True)
    customerID=Column(Integer,nullable=False)
    dateTime=Column(String,nullable=False)
    notificationStatus=Column(String,nullable=False)
    notificationText = Column(String,nullable=False)
    notificationType = Column(String,nullable=False)
    action = Column(String,nullable=True)
    
    

    def __str__(self):
        return self.id