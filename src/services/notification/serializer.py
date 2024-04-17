from pydantic import BaseModel, constr
from datetime import datetime

class ResponseNotificationSerializer(BaseModel):
    message: constr()
    read: bool
    created_at: datetime
