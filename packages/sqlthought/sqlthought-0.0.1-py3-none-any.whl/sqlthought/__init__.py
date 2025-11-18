"""
sqlthought: A modular multi-agent SQL-of-Thought library.

Public API:
    - sqlthought.to_sql()
    - sqlthought.build_llm()
"""

from .llm import build_llm
from .nlq.conversion import to_sql

__all__ = [
    "build_llm",
    "to_sql",
]

__version__ = "0.0.1"

