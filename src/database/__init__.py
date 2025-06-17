"""
Database operations and queries
"""
from .init_db import initialize_database
from .queries import (
    get_db_connection,
    execute_segment_query,
    get_available_values,
    get_field_statistics,
    validate_segment_sql,
    get_segment_statistics,
    save_segment,
    load_saved_segments
)

__all__ = [
    'initialize_database',
    'get_db_connection',
    'execute_segment_query',
    'get_available_values',
    'get_field_statistics',
    'validate_segment_sql',
    'get_segment_statistics',
    'save_segment',
    'load_saved_segments'
]