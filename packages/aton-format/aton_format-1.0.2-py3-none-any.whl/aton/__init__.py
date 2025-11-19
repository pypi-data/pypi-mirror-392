"""
ATON - Adaptive Token-Oriented Notation

A data serialization format optimized for Large Language Models (LLMs).
Achieves 50-60% token reduction compared to JSON while maintaining
full data integrity and human readability.

Example:
    >>> from aton import ATONEncoder
    >>> 
    >>> encoder = ATONEncoder(optimize=True)
    >>> data = {
    ...     "users": [
    ...         {"id": 1, "name": "John", "active": True},
    ...         {"id": 2, "name": "Jane", "active": True}
    ...     ]
    ... }
    >>> 
    >>> aton_string = encoder.encode(data)
    >>> print(aton_string)
    @schema[id:int, name:str, active:bool]
    @defaults[active:true]
    
    users(2):
      1, "John"
      2, "Jane"

"""

from .encoder import ATONEncoder
from .decoder import ATONDecoder
from .version import __version__, __author__, __email__, __license__

__all__ = [
    'ATONEncoder',
    'ATONDecoder',
    '__version__',
]
