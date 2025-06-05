import json
from typing import List, Dict, Any, Tuple
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.models import JsonProcessing, ActionLog

class JsonAgent:
    def __init__(self):
        # Define expected schema for webhook data
        self.expected_schema = {
            "type": "object",
            "required": ["event_type", "timestamp", "data"],
            "properties": {
                "event_type": {"type": "string"},
                "timestamp": {"type": "string", "format": "date-time"},
                "data": {
                    "type": "object",
                    "required": ["user_id", "action"],
                    "properties": {
                        "user_id": {"type": "string"},
                        "action": {"type": "string"},
                        "metadata": {"type": "object"}
                    }
                }
            }
        }

    def validate_schema(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate JSON data against expected schema."""
        anomalies = []
        
        # Check required top-level fields
        for field in self.expected_schema["required"]:
            if field not in data:
                anomalies.append(f"Missing required field: {field}")
                continue
            
            # Validate field types
            expected_type = self.expected_schema["properties"][field]["type"]
            if not isinstance(data[field], self._get_python_type(expected_type)):
                anomalies.append(f"Invalid type for {field}: expected {expected_type}")

        # Validate nested data object if present
        if "data" in data:
            data_schema = self.expected_schema["properties"]["data"]
            for field in data_schema["required"]:
                if field not in data["data"]:
                    anomalies.append(f"Missing required field in data: {field}")
                else:
                    expected_type = data_schema["properties"][field]["type"]
                    if not isinstance(data["data"][field], self._get_python_type(expected_type)):
                        anomalies.append(f"Invalid type for data.{field}: expected {expected_type}")

        return len(anomalies) == 0, anomalies

    def _get_python_type(self, json_type: str) -> type:
        """Convert JSON type to Python type."""
        type_map = {
            "string": str,
            "number": (int, float),
            "integer": int,
            "boolean": bool,
            "object": dict,
            "array": list
        }
        return type_map.get(json_type, object)

    async def process_json(self, content: str, file_id: int, db: Session) -> JsonProcessing:
        """Process JSON content and store results in database."""
        try:
            # Parse JSON content
            data = json.loads(content)
            
            # Validate schema
            is_valid, anomalies = self.validate_schema(data)
            
            # Create JSON processing record
            json_processing = JsonProcessing(
                file_id=file_id,
                schema_valid=is_valid,
                anomalies=anomalies
            )
            
            # If anomalies found, create risk alert
            if not is_valid:
                action_log = ActionLog(
                    file_id=file_id,
                    action_type="risk_alert",
                    status="pending",
                    retry_count=0
                )
                db.add(action_log)
            
            db.add(json_processing)
            db.commit()
            db.refresh(json_processing)
            
            return json_processing
            
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON format")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def detect_anomalies(self, data: Dict[str, Any]) -> List[str]:
        """Detect anomalies in JSON data beyond schema validation."""
        anomalies = []
        
        # Check for suspicious patterns
        if "data" in data and "action" in data["data"]:
            action = data["data"]["action"].lower()
            if "delete" in action or "remove" in action:
                anomalies.append("Suspicious action detected: deletion operation")
            
            if "metadata" in data["data"]:
                metadata = data["data"]["metadata"]
                if isinstance(metadata, dict):
                    # Check for unusual timestamps
                    if "timestamp" in metadata:
                        try:
                            import datetime
                            timestamp = datetime.datetime.fromisoformat(metadata["timestamp"])
                            if timestamp > datetime.datetime.now():
                                anomalies.append("Future timestamp detected")
                        except ValueError:
                            anomalies.append("Invalid timestamp format")
        
        return anomalies 