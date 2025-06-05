import json
from typing import Tuple, Dict, Any
from fastapi import UploadFile, HTTPException
import PyPDF2
from app.models.models import FileMetadata
from sqlalchemy.orm import Session
from app.models import models
import io

class ClassifierAgent:
    def __init__(self):
        self.file_types = ["Email", "JSON", "PDF"]
        self.business_intents = [
            "Invoice Processing",
            "Contract Analysis",
            "Report Generation",
            "Data Extraction"
        ]

    async def detect_file_type(self, filename: str, content: bytes) -> str:
        """Detect the type of file based on content and extension."""
        # Simple extension-based classification
        if filename.lower().endswith('.pdf'):
            return "PDF"
        elif filename.lower().endswith('.json'):
            return "JSON"
        elif filename.lower().endswith(('.eml', '.msg')):
            return "Email"
        
        # Content-based classification
        try:
            # Try to parse as JSON
            json.loads(content.decode('utf-8'))
            return "JSON"
        except:
            pass
        
        # Check for email headers
        if b"From:" in content or b"To:" in content:
            return "Email"
        
        # Default to PDF if no other type is detected
        return "PDF"

    def classify_business_intent(self, content: str) -> str:
        """Classify the business intent based on content analysis."""
        content_lower = content.lower()
        max_matches = 0
        best_intent = "Unknown"

        for intent, keywords in self.business_intents.items():
            matches = sum(1 for keyword in keywords if keyword in content_lower)
            if matches > max_matches:
                max_matches = matches
                best_intent = intent

        return best_intent

    async def process_file(self, filename: str, content: bytes, db: Session) -> models.FileMetadata:
        """Classify the uploaded file and determine its business intent."""
        try:
            # Determine file type based on content and extension
            file_type = await self.detect_file_type(filename, content)
            
            # Determine business intent
            business_intent = self._determine_business_intent(content)
            
            # Create metadata record
            metadata = models.FileMetadata(
                filename=filename,
                file_type=file_type,
                business_intent=business_intent
            )
            db.add(metadata)
            db.commit()
            db.refresh(metadata)
            
            return metadata
            
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
    
    def _determine_business_intent(self, content: bytes) -> str:
        """Determine the business intent of the file."""
        content_str = content.decode('utf-8', errors='ignore').lower()
        
        # Check for invoice-related keywords
        if any(word in content_str for word in ['invoice', 'payment', 'amount', 'total']):
            return "Invoice Processing"
        
        # Check for contract-related keywords
        if any(word in content_str for word in ['contract', 'agreement', 'terms', 'conditions']):
            return "Contract Analysis"
        
        # Check for report-related keywords
        if any(word in content_str for word in ['report', 'summary', 'analysis', 'findings']):
            return "Report Generation"
        
        # Default to data extraction
        return "Data Extraction"

    def _read_pdf_content(self, content: bytes) -> str:
        """Extract text content from PDF bytes."""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error reading PDF content: {str(e)}")

    def _read_json_content(self, content: bytes) -> str:
        """Extract content from JSON bytes."""
        try:
            json_data = json.loads(content)
            return json.dumps(json_data)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error reading JSON content: {str(e)}")

    def _read_email_content(self, content: bytes) -> str:
        """Extract content from email bytes."""
        try:
            return content.decode('utf-8')
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error decoding email content: {str(e)}") 