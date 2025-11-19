"""ATON Decoder - Convert ATON format back to Python objects."""

from typing import Dict, List, Any
import re


class ATONDecoder:
    """
    Convert ATON format back to Python dictionaries.
    
    Example:
        >>> decoder = ATONDecoder()
        >>> aton = '''
        ... @schema[id:int, name:str]
        ... users(1):
        ...   1, "John"
        ... '''
        >>> data = decoder.decode(aton)
        >>> print(data)
        {'users': [{'id': 1, 'name': 'John'}]}
    """
    
    def decode(self, aton_str: str) -> Dict[str, Any]:
        """
        Parse ATON string to dictionary.
        
        Args:
            aton_str: ATON formatted string
            
        Returns:
            Parsed dictionary
        """
        lines = aton_str.strip().split('\n')
        result = {}
        current_entity = None
        current_schema = None
        current_defaults = {}
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if not line:
                i += 1
                continue
            
            # Parse schema
            if line.startswith('@schema['):
                current_schema = self._parse_schema(line)
                i += 1
                continue
            
            # Parse defaults
            if line.startswith('@defaults['):
                current_defaults = self._parse_defaults(line)
                i += 1
                continue
            
            # Parse entity header
            if '(' in line and line.endswith(':'):
                match = re.match(r'(\w+)\((\d+)\):', line)
                if match:
                    entity_name = match.group(1)
                    count = int(match.group(2))
                    result[entity_name] = []
                    current_entity = entity_name
                    i += 1
                    continue
            
            # Parse data rows
            if current_entity and current_schema:
                row_data = self._parse_row(line, current_schema, current_defaults)
                if row_data:
                    result[current_entity].append(row_data)
            
            i += 1
        
        return result
    
    def _parse_schema(self, line: str) -> List[Dict]:
        """Parse @schema[...] line."""
        content = line[8:-1]  # Remove @schema[ and ]
        fields = []
        
        for field in content.split(','):
            field = field.strip()
            if ':' in field:
                name, type_name = field.split(':', 1)
                fields.append({'name': name.strip(), 'type': type_name.strip()})
        
        return fields
    
    def _parse_defaults(self, line: str) -> Dict:
        """Parse @defaults[...] line."""
        content = line[10:-1]  # Remove @defaults[ and ]
        defaults = {}
        
        for item in content.split(','):
            item = item.strip()
            if ':' in item:
                key, value = item.split(':', 1)
                defaults[key.strip()] = self._parse_value(value.strip())
        
        return defaults
    
    def _parse_row(self, line: str, schema: List[Dict], defaults: Dict) -> Dict:
        """Parse data row."""
        # Remove leading whitespace
        line = line.strip()
        if not line:
            return None
        
        values = self._split_values(line)
        row = {}
        
        for i, field in enumerate(schema):
            if i < len(values):
                value = values[i].strip()
                
                # Use default if empty
                if not value and field['name'] in defaults:
                    row[field['name']] = defaults[field['name']]
                else:
                    row[field['name']] = self._parse_typed_value(value, field['type'])
        
        return row
    
    def _split_values(self, line: str) -> List[str]:
        """Split line by commas, respecting quotes and brackets."""
        values = []
        current = []
        in_quotes = False
        in_brackets = 0
        
        for char in line:
            if char == '"' and (not current or current[-1] != '\\'):
                in_quotes = not in_quotes
                current.append(char)
            elif char in '[{' and not in_quotes:
                in_brackets += 1
                current.append(char)
            elif char in ']}' and not in_quotes:
                in_brackets -= 1
                current.append(char)
            elif char == ',' and not in_quotes and in_brackets == 0:
                values.append(''.join(current))
                current = []
            else:
                current.append(char)
        
        if current:
            values.append(''.join(current))
        
        return values
    
    def _parse_value(self, value: str) -> Any:
        """Parse generic value."""
        value = value.strip()
        
        if not value:
            return None
        elif value == 'true':
            return True
        elif value == 'false':
            return False
        elif value.startswith('"') and value.endswith('"'):
            return value[1:-1]
        elif value.startswith('['):
            return self._parse_array(value)
        elif value.startswith('{'):
            return self._parse_object(value)
        else:
            try:
                if '.' in value:
                    return float(value)
                return int(value)
            except ValueError:
                return value
    
    def _parse_typed_value(self, value: str, type_name: str) -> Any:
        """Parse value with type information."""
        if not value:
            return None
        
        if type_name == 'int':
            return int(value)
        elif type_name == 'float':
            return float(value)
        elif type_name == 'bool':
            return value.lower() == 'true'
        elif type_name == 'str':
            return value.strip('"')
        elif type_name == 'arr':
            return self._parse_array(value)
        elif type_name == 'obj':
            return self._parse_object(value)
        else:
            return self._parse_value(value)
    
    def _parse_array(self, value: str) -> List:
        """Parse array [...]."""
        content = value[1:-1]  # Remove [ and ]
        if not content:
            return []
        
        items = self._split_values(content)
        return [self._parse_value(item.strip()) for item in items]
    
    def _parse_object(self, value: str) -> Dict:
        """Parse object {...}."""
        content = value[1:-1]  # Remove { and }
        if not content:
            return {}
        
        obj = {}
        items = self._split_values(content)
        
        for item in items:
            if ':' in item:
                key, val = item.split(':', 1)
                obj[key.strip()] = self._parse_value(val.strip())
        
        return obj
