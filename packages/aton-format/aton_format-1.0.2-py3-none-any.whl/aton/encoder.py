"""ATON Encoder - Convert Python objects to ATON format."""

from typing import Dict, List, Any, Optional
from datetime import datetime


class ATONEncoder:
    """
    Convert Python dictionaries to ATON (Adaptive Token-Oriented Notation) format.
    
    ATON is optimized for LLM applications with 50-60% token reduction vs JSON.
    
    Args:
        optimize: Enable optimizations (defaults, schema)
        include_schema: Generate @schema[...] headers
        include_defaults: Generate @defaults[...] and omit repeated values
        min_items: Minimum array size to apply optimizations
    
    Example:
        >>> encoder = ATONEncoder(optimize=True)
        >>> data = {"users": [{"id": 1, "name": "John"}]}
        >>> aton = encoder.encode(data)
        >>> print(aton)
        @schema[id:int, name:str]
        
        users(1):
          1, "John"
    """
    
    def __init__(
        self,
        optimize: bool = True,
        include_schema: bool = True,
        include_defaults: bool = True,
        min_items: int = 1
    ):
        self.optimize = optimize
        self.include_schema = include_schema
        self.include_defaults = include_defaults
        self.min_items = min_items
    
    def encode(self, data: Dict[str, Any]) -> str:
        """
        Convert dictionary to ATON format.
        
        Args:
            data: Dictionary with arrays of homogeneous objects
            
        Returns:
            ATON formatted string
        """
        result = []
        
        for key, value in data.items():
            if isinstance(value, list) and len(value) > 0:
                if isinstance(value[0], dict):
                    result.append(self._encode_entity_array(key, value))
        
        return '\n\n'.join(result)
    
    def _encode_entity_array(self, name: str, items: List[Dict]) -> str:
        """Encode array of objects."""
        if len(items) == 0:
            return f"{name}(0):"
        
        schema = self._infer_schema(items)
        defaults = self._find_defaults(items) if self.optimize and self.include_defaults else {}
        
        lines = []
        
        # Add schema if enabled
        if self.include_schema and len(items) >= self.min_items:
            lines.append(self._format_schema(schema))
            
            if self.include_defaults and defaults:
                lines.append(self._format_defaults(defaults))
            
            lines.append('')
        
        # Add entity header
        lines.append(f"{name}({len(items)}):")
        
        # Add data rows
        for item in items:
            row = self._encode_row(item, schema, defaults)
            lines.append(f"  {row}")
        
        return '\n'.join(lines)
    
    def _infer_schema(self, items: List[Dict]) -> Dict:
        """Infer schema from items."""
        if not items:
            return {'fields': []}
        
        first = items[0]
        fields = []
        
        for key, value in first.items():
            type_name = self._get_type_name(value)
            fields.append({'name': key, 'type': type_name})
        
        return {'fields': fields}
    
    def _get_type_name(self, value: Any) -> str:
        """Get ATON type name for value."""
        if isinstance(value, bool):
            return 'bool'
        elif isinstance(value, int):
            return 'int'
        elif isinstance(value, float):
            return 'float'
        elif isinstance(value, str):
            return 'str'
        elif isinstance(value, list):
            return 'arr'
        elif isinstance(value, dict):
            return 'obj'
        elif isinstance(value, datetime):
            return 'datetime'
        else:
            return 'str'
    
    def _find_defaults(self, items: List[Dict]) -> Dict:
        """Find common default values."""
        if len(items) < 2:
            return {}
        
        defaults = {}
        first = items[0]
        
        for key, value in first.items():
            # Check if this value appears in >50% of items
            count = sum(1 for item in items if item.get(key) == value)
            if count > len(items) * 0.5:
                defaults[key] = value
        
        return defaults
    
    def _format_schema(self, schema: Dict) -> str:
        """Format schema header."""
        fields = [f"{f['name']}:{f['type']}" for f in schema['fields']]
        return f"@schema[{', '.join(fields)}]"
    
    def _format_defaults(self, defaults: Dict) -> str:
        """Format defaults header."""
        items = []
        for key, value in defaults.items():
            if isinstance(value, str):
                items.append(f'{key}:"{value}"')
            elif isinstance(value, bool):
                items.append(f'{key}:{str(value).lower()}')
            else:
                items.append(f'{key}:{value}')
        return f"@defaults[{', '.join(items)}]"
    
    def _encode_row(self, item: Dict, schema: Dict, defaults: Dict) -> str:
        """Encode single data row."""
        values = []
        
        for field in schema['fields']:
            key = field['name']
            value = item.get(key)
            
            # Omit if matches default
            if self.optimize and self.include_defaults and key in defaults and value == defaults[key]:
                values.append('')
            else:
                values.append(self._format_value(value))
        
        # Join with commas, preserve empty values
        return ', '.join(values)
    
    def _format_value(self, value: Any) -> str:
        """Format single value."""
        if value is None or value == '':
            return ''
        elif isinstance(value, str):
            return f'"{value}"'
        elif isinstance(value, bool):
            return str(value).lower()
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, list):
            formatted = [self._format_value(v) for v in value]
            return f"[{','.join(formatted)}]"
        elif isinstance(value, dict):
            items = [f"{k}:{self._format_value(v)}" for k, v in value.items()]
            return f"{{{','.join(items)}}}"
        elif isinstance(value, datetime):
            return value.isoformat()
        else:
            return str(value)
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count (rough approximation).
        
        Args:
            text: Text to estimate
            
        Returns:
            Estimated token count (~4 chars per token)
        """
        return len(text) // 4
