"""
TOON Renderer for Django REST Framework.
"""

from decimal import Decimal
from rest_framework.renderers import BaseRenderer
from json_toon import json_to_toon


def convert_decimals(obj):
    """
    Recursively convert Decimal objects to float for JSON serialization.
    
    Args:
        obj: Python object that may contain Decimal values
        
    Returns:
        Object with Decimal values converted to float
    """
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {key: convert_decimals(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimals(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_decimals(item) for item in obj)
    else:
        return obj


class TOONRenderer(BaseRenderer):
    """
    Renderer that converts Python data to TOON format (Token-Oriented Object Notation).
    
    The client must send the 'Accept: application/toon' header to receive
    the response in TOON format.
    """
    
    media_type = 'application/toon'
    format = 'toon'
    charset = 'utf-8'
    
    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Renders data in TOON format.
        
        Args:
            data: The data to render (dict, list, or Python primitives)
            accepted_media_type: The accepted media type (ignored)
            renderer_context: Additional renderer context (ignored)
            
        Returns:
            bytes: The data converted to TOON format as bytes
        """
        if data is None:
            return b''
        
        try:
            # Convert Decimal objects to float for JSON serialization
            data = convert_decimals(data)
            
            # Convert Python data to TOON format
            toon_string = json_to_toon(data)
            
            # Return as bytes with the specified charset
            return toon_string.encode(self.charset)
            
        except Exception as e:
            # In case of error, we could raise an exception or return an error
            # For now, we raise the exception so DRF can handle it
            raise ValueError(f"Error converting data to TOON: {str(e)}")
