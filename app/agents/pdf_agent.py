import re
from typing import Tuple, Optional
from fastapi import HTTPException
import PyPDF2
from sqlalchemy.orm import Session
from app.models.models import PdfProcessing, ActionLog

class PdfAgent:
    def __init__(self):
        self.high_value_threshold = 10000
        self.regulation_keywords = {
            "GDPR": ["gdpr", "general data protection regulation", "data protection"],
            "FDA": ["fda", "food and drug administration", "medical device"]
        }

    async def process_pdf(self, content: bytes, file_id: int, db: Session) -> PdfProcessing:
        """Process PDF content and store results in database."""
        try:
            # Extract text from PDF
            text = self._extract_text_from_pdf(content)
            
            # Extract total amount
            total_amount = self._extract_total_amount(text)
            
            # Check for regulations
            has_gdpr = self._check_regulation(text, "GDPR")
            has_fda = self._check_regulation(text, "FDA")
            
            # Create PDF processing record
            pdf_processing = PdfProcessing(
                file_id=file_id,
                total_amount=total_amount,
                is_high_value=total_amount is not None and total_amount > self.high_value_threshold,
                has_gdpr=has_gdpr,
                has_fda=has_fda
            )
            
            # Create risk alert if high value or regulations found
            if (pdf_processing.is_high_value or pdf_processing.has_gdpr or 
                pdf_processing.has_fda):
                action_log = ActionLog(
                    file_id=file_id,
                    action_type="risk_alert",
                    status="pending",
                    retry_count=0
                )
                db.add(action_log)
            
            db.add(pdf_processing)
            db.commit()
            db.refresh(pdf_processing)
            
            return pdf_processing
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def _extract_text_from_pdf(self, content: bytes) -> str:
        """Extract text content from PDF bytes."""
        try:
            pdf_reader = PyPDF2.PdfReader(content)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error reading PDF: {str(e)}")

    def _extract_total_amount(self, text: str) -> Optional[float]:
        """Extract total amount from PDF text."""
        # Common patterns for total amount
        patterns = [
            r'total[\s:]+[$]?(\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'amount[\s:]+[$]?(\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'[$]?(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:total|amount)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Convert string amount to float
                amount_str = matches[0].replace(',', '')
                try:
                    return float(amount_str)
                except ValueError:
                    continue
        
        return None

    def _check_regulation(self, text: str, regulation: str) -> bool:
        """Check if text contains specific regulation keywords."""
        if regulation not in self.regulation_keywords:
            return False
            
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.regulation_keywords[regulation])

    def _is_invoice(self, text: str) -> bool:
        """Check if PDF is an invoice based on common keywords."""
        invoice_keywords = [
            "invoice", "bill", "payment", "amount", "total",
            "due date", "payment terms", "tax", "subtotal"
        ]
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in invoice_keywords)

    def _is_policy_document(self, text: str) -> bool:
        """Check if PDF is a policy document based on common keywords."""
        policy_keywords = [
            "policy", "regulation", "compliance", "guidelines",
            "terms", "conditions", "agreement", "requirements"
        ]
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in policy_keywords) 