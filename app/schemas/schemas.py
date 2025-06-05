from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class FileMetadataBase(BaseModel):
    filename: str
    file_type: str
    business_intent: str

class FileMetadataCreate(FileMetadataBase):
    pass

class FileMetadata(FileMetadataBase):
    id: int
    created_at: datetime
    processed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class EmailContent(BaseModel):
    content: str
    sender_email: EmailStr

class EmailProcessingBase(BaseModel):
    sender_email: EmailStr
    tone: str
    urgency: str
    is_escalated: bool = False

class EmailProcessingCreate(EmailProcessingBase):
    file_id: int

class EmailProcessing(EmailProcessingBase):
    id: int
    file_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class JsonWebhook(BaseModel):
    data: Dict[str, Any]

class JsonProcessingBase(BaseModel):
    schema_valid: bool
    anomalies: List[str]

class JsonProcessingCreate(JsonProcessingBase):
    file_id: int

class JsonProcessing(JsonProcessingBase):
    id: int
    file_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class PdfProcessingBase(BaseModel):
    total_amount: Optional[float] = None
    is_high_value: bool = False
    has_gdpr: bool = False
    has_fda: bool = False

class PdfProcessingCreate(PdfProcessingBase):
    file_id: int

class PdfProcessing(PdfProcessingBase):
    id: int
    file_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ActionLogBase(BaseModel):
    file_id: int
    action_type: str
    status: str
    retry_count: int = 0

class ActionLogCreate(ActionLogBase):
    pass

class ActionLog(ActionLogBase):
    id: int
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True 