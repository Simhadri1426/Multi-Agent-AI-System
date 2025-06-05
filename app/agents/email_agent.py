import re
from typing import Tuple, Dict, Any
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.models import EmailProcessing, ActionLog
from datetime import datetime

class EmailAgent:
    def __init__(self):
        self.tone_keywords = {
            "angry": ["angry", "furious", "outraged", "unacceptable", "terrible", "charged twice", "refund"],
            "polite": ["please", "thank", "appreciate", "kindly", "regards"],
            "threatening": ["sue", "legal", "lawyer", "court", "action"]
        }
        
        self.urgency_keywords = {
            "high": ["urgent", "immediately", "asap", "critical", "emergency", "high"],
            "medium": ["soon", "shortly", "prompt", "quick", "timely"],
            "low": ["whenever", "convenient", "sometime", "eventually"]
        }

    def analyze_email(self, content: str) -> Tuple[str, str]:
        """Analyze email content to determine tone and urgency."""
        content_lower = content.lower()
        
        # Analyze tone
        tone_scores = {
            tone: sum(1 for keyword in keywords if keyword in content_lower)
            for tone, keywords in self.tone_keywords.items()
        }
        tone = max(tone_scores.items(), key=lambda x: x[1])[0]
        
        # Analyze urgency
        urgency_scores = {
            urgency: sum(1 for keyword in keywords if keyword in content_lower)
            for urgency, keywords in self.urgency_keywords.items()
        }
        urgency = max(urgency_scores.items(), key=lambda x: x[1])[0]
        
        return tone, urgency

    def extract_sender_email(self, content: str) -> str:
        """Extract sender email from email content."""
        # Look for From: field first
        from_match = re.search(r'From:\s*([\w\.-]+@[\w\.-]+\.\w+)', content, re.IGNORECASE)
        if from_match:
            return from_match.group(1)
        
        # Fallback to any email in the content
        email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
        matches = re.findall(email_pattern, content)
        
        if not matches:
            raise HTTPException(status_code=400, detail="No sender email found in content")
        
        return matches[0]

    def extract_request(self, content: str) -> str:
        """Extract the main request from the email content."""
        # Look for Request: field
        request_match = re.search(r'Request:\s*(.*?)(?:\n|$)', content, re.IGNORECASE)
        if request_match:
            return request_match.group(1).strip()
        
        # If no Request: field, return the whole content
        return content.strip()

    async def process_email(self, content: str, file_id: int, db: Session) -> EmailProcessing:
        """Process email content and store results in database."""
        try:
            # Extract sender email
            sender_email = self.extract_sender_email(content)
            
            # Extract request
            request = self.extract_request(content)
            
            # Analyze tone and urgency
            tone, urgency = self.analyze_email(content)
            
            # Create email processing record
            email_processing = EmailProcessing(
                file_id=file_id,
                sender_email=sender_email,
                tone=tone,
                urgency=urgency,
                is_escalated=False
            )
            
            # Check if escalation is needed
            if tone == "angry" and urgency == "high":
                email_processing.is_escalated = True
                # Create action log for escalation
                action_log = ActionLog(
                    file_id=file_id,
                    action_type="crm_escalation",
                    status="pending",
                    retry_count=0
                )
                db.add(action_log)
            
            db.add(email_processing)
            db.commit()
            db.refresh(email_processing)
            
            return email_processing
            
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error processing email: {str(e)}")

    async def handle_escalation(self, email_processing: EmailProcessing, db: Session) -> None:
        """Handle email escalation by creating appropriate action logs."""
        if email_processing.is_escalated:
            action_log = ActionLog(
                file_id=email_processing.file_id,
                action_type="crm_escalation",
                status="pending",
                retry_count=0
            )
            db.add(action_log)
            db.commit() 