# ============================================
# File: textstyle/__init__.py
# ============================================
"""
textstyle - Simple cross-platform terminal text styling library

Example:
    >>> import textstyle as ts
    >>> print(ts.style("Error", color="red", bg="white", look="bold"))
    >>> print(ts.style("Custom", color="#FF5733"))
    >>> ts.create("error", color="red", look="bold")
    >>> print(ts.format("An <error>error</error> occurred"))
"""

# Import everything from the main module
from .textstyle import (
    # Main functions
    style,
    format,
    create,
    delete,
    strip,
    clean,
    length,
    enable,
    disable,
    set_theme,
    temporary,
    
    # Constants
    COLORS,
    BG_COLORS,
    LOOKS,
    
    # Metadata
    __version__,
)

# Package metadata
__author__ = "Sivaprasad Murali"
__email__ = "sivaprasad.off@example.com"
__license__ = "MIT"
__description__ = "Simple cross-platform terminal text styling library"
__url__ = "https://github.com/crystallinecore/textstyle"
__all__ = [
    "style",
    "format",
    "create",
    "delete",
    "strip",
    "clean",
    "length",
    "enable",
    "disable",
    "set_theme",
    "temporary",
    "COLORS",
    "BG_COLORS",
    "LOOKS",
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    "__description__",
    "__url__",
]
