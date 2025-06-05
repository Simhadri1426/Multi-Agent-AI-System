from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON
from sqlalchemy.sql import func
from app.core.database import Base

class FileMetadata(Base):
    __tablename__ = "file_metadata"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    file_type = Column(String)  # PDF, JSON, Email
    business_intent = Column(String)  # RFQ, Complaint, Invoice, Regulation, Fraud Risk
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)

class EmailProcessing(Base):
    __tablename__ = "email_processing"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, index=True)
    sender_email = Column(String)
    tone = Column(String)  # angry, polite, threatening
    urgency = Column(String)  # low, medium, high
    is_escalated = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class JsonProcessing(Base):
    __tablename__ = "json_processing"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, index=True)
    schema_valid = Column(Boolean)
    anomalies = Column(JSON)  # List of anomalies found
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class PdfProcessing(Base):
    __tablename__ = "pdf_processing"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, index=True)
    total_amount = Column(Float, nullable=True)
    is_high_value = Column(Boolean, default=False)
    has_gdpr = Column(Boolean, default=False)
    has_fda = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ActionLog(Base):
    __tablename__ = "action_log"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, index=True)
    action_type = Column(String)  # crm_escalation, risk_alert
    status = Column(String)  # success, failed
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True) 