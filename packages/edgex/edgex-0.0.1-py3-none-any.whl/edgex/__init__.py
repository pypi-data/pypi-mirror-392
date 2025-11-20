# ============================================
# File: edgex/__init__.py
# ============================================
"""
edgex - Simple cross-platform terminal text styling library

Example:
    >>> import edgex as vg
    >>> print(vg.style("Error", color="red", bg="white", look="bold"))
    >>> print(vg.style("Custom", color="#FF5733"))
    >>> vg.create("error", color="red", look="bold")
    >>> print(vg.format("An <error>error</error> occurred"))
"""

# Import everything from the main module
from .edgex import (
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
    write,
    
    # Constanvg
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
__url__ = "https://github.com/crystallinecore/edgex"
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
    "write",
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
