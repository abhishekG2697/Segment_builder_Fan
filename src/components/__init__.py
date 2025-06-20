"""
UI Components for Segment Builder with Nested Container Support
"""
from .sidebar import render_sidebar
from .segment_builder import render_segment_builder
from .preview import render_preview
from .library import render_library

# Enhanced React component with nested container support
try:
    from .react_segment_builder import render_react_segment_builder
except ImportError:
    render_react_segment_builder = None

# Optional components
try:
    from .drag_drop import render_drag_drop_builder
except ImportError:
    render_drag_drop_builder = None

try:
    from .integrated_builder import render_integrated_builder
except ImportError:
    render_integrated_builder = None

__all__ = [
    'render_sidebar', 
    'render_segment_builder', 
    'render_preview', 
    'render_library',
    'render_react_segment_builder',
    'render_drag_drop_builder',
    'render_integrated_builder'
]