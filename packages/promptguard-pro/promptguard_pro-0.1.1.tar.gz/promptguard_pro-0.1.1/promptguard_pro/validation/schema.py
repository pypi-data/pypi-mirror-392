"""Pydantic schema validation for PromptGuard."""
from typing import Optional, Type, Any, Dict
import json
import re

try:
    from pydantic import BaseModel, ValidationError
except ImportError:
    raise ImportError("pydantic is required")


class SchemaValidator:
    """Validator for Pydantic schemas."""
    
    def __init__(self, schema: Type[BaseModel]):
        """Initialize schema validator.
        
        Args:
            schema: Pydantic BaseModel class
        """
        self.schema = schema
    
    def validate(self, data: Any) -> tuple[bool, Optional[BaseModel], Optional[str]]:
        """Validate data against schema.
        
        Args:
            data: Data to validate (string or dict)
            
        Returns:
            Tuple of (success, validated_object, error_message)
        """
        try:
            # If data is string, try to parse as JSON
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except json.JSONDecodeError:
                    # Try to extract JSON from markdown code blocks
                    json_match = re.search(r'```(?:json)?\s*(.*?)\s*```', data, re.DOTALL)
                    if json_match:
                        data = json.loads(json_match.group(1))
                    else:
                        return False, None, "Could not parse response as JSON"
            
            # Validate against schema
            validated_obj = self.schema(**data) if isinstance(data, dict) else self.schema(**data)
            return True, validated_obj, None
        except ValidationError as e:
            error_msg = f"Validation failed: {e.error_count()} error(s)"
            errors = []
            for error in e.errors():
                errors.append(f"{'.'.join(str(loc) for loc in error['loc'])}: {error['msg']}")
            error_msg += "\n" + "\n".join(errors)
            return False, None, error_msg
        except Exception as e:
            return False, None, f"Unexpected error during validation: {str(e)}"
    
    def extract_from_response(self, response: str) -> tuple[bool, Optional[BaseModel], Optional[str]]:
        """Extract and validate data from response text.
        
        Args:
            response: Response text potentially containing JSON
            
        Returns:
            Tuple of (success, validated_object, error_message)
        """
        # Try multiple extraction strategies
        strategies = [
            lambda r: json.loads(r),  # Raw JSON
            lambda r: json.loads(re.search(r'```(?:json)?\s*(.*?)\s*```', r, re.DOTALL).group(1)),  # JSON in code block
            lambda r: json.loads(re.search(r'{.*}', r, re.DOTALL).group(0)),  # First JSON object
        ]
        
        extracted_data = None
        for strategy in strategies:
            try:
                extracted_data = strategy(response)
                break
            except Exception:
                continue
        
        if extracted_data is None:
            return False, None, "Could not extract JSON from response"
        
        return self.validate(extracted_data)
    
    def get_schema_description(self) -> str:
        """Get description of schema for prompting."""
        if hasattr(self.schema, 'model_json_schema'):
            schema_dict = self.schema.model_json_schema()
            return json.dumps(schema_dict, indent=2)
        return str(self.schema)
