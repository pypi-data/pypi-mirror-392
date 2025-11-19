"""
textstyle - Simple cross-platform terminal text styling library

Example:
    >>> import textstyle as ts
    >>> print(ts.style("Error", color="red", bg="white", look="bold"))
    >>> print(ts.style("Custom", color="#FF5733"))
    >>> ts.create("error", color="red", look="bold")
    >>> print(ts.format("An <error>error</error> occurred"))
"""

__version__ = "1.0.1"

import sys
import os
import re
from contextlib import contextmanager

# ANSI color codes (foreground)
COLORS = {
    "black": 30, "red": 31, "green": 32, "yellow": 33,
    "blue": 34, "magenta": 35, "cyan": 36, "white": 37,
    "bright_black": 90, "bright_red": 91, "bright_green": 92,
    "bright_yellow": 93, "bright_blue": 94, "bright_magenta": 95,
    "bright_cyan": 96, "bright_white": 97,
}

# ANSI background color codes
BG_COLORS = {
    "bg_black": 40, "bg_red": 41, "bg_green": 42, "bg_yellow": 43,
    "bg_blue": 44, "bg_magenta": 45, "bg_cyan": 46, "bg_white": 47,
    "bg_bright_black": 100, "bg_bright_red": 101, "bg_bright_green": 102,
    "bg_bright_yellow": 103, "bg_bright_blue": 104, "bg_bright_magenta": 105,
    "bg_bright_cyan": 106, "bg_bright_white": 107,
}

LOOKS = {
    "bold": 1, "dim": 2, "italic": 3, "underline": 4,
    "blink": 5, "reverse": 7, "hidden": 8, "strikethrough": 9,
}


class _Config:
    """Runtime configuration for styling"""
    enabled = True


# Custom styles registry (user-defined)
_custom_styles = {}

# Predefined styles (built-in tags)
_predefined_styles = {}

# Active theme
_current_theme = {}


def _init_predefined_styles():
    """Initialize predefined color and look tags"""
    # Add all foreground colors as predefined tags
    for color_name in COLORS.keys():
        _predefined_styles[color_name] = {"color": color_name, "bg": None, "look": None}
    
    # Add all background colors as predefined tags
    for bg_name in BG_COLORS.keys():
        _predefined_styles[bg_name] = {"color": None, "bg": bg_name, "look": None}
    
    # Add all looks as predefined tags
    for look_name in LOOKS.keys():
        _predefined_styles[look_name] = {"color": None, "bg": None, "look": look_name}


def _init_windows():
    """Enable ANSI support on Windows"""
    if sys.platform == "win32":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
            mode = ctypes.c_ulong()
            kernel32.GetConsoleMode(handle, ctypes.byref(mode))
            mode.value |= 0x0004  # ENABLE_VIRTUAL_TERMINAL_PROCESSING
            kernel32.SetConsoleMode(handle, mode)
        except Exception:
            pass


def _init_config():
    """Initialize cross-platform support and configuration"""
    if os.getenv("NO_COLOR"):
        _Config.enabled = False
        return
    
    if os.getenv("FORCE_COLOR"):
        _Config.enabled = True
        _init_windows()
        return
    
    if hasattr(sys.stdout, "isatty") and not sys.stdout.isatty():
        _Config.enabled = False
        return
    
    _init_windows()
    _Config.enabled = True


# Initialize on import
_init_config()
_init_predefined_styles()


def _hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join([c*2 for c in hex_color])
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def _rgb_to_ansi(r, g, b, background=False):
    """Convert RGB to ANSI 24-bit true color code"""
    prefix = 48 if background else 38
    return f"{prefix};2;{r};{g};{b}"


def _parse_color(color, background=False):
    """Parse color input (name, hex, or RGB tuple) to ANSI code"""
    if not color:
        return None
    
    # Named color
    color_dict = BG_COLORS if background else COLORS
    color_key = f"bg_{color}" if background and not color.startswith("bg_") else color
    
    if color_key in color_dict:
        return str(color_dict[color_key])
    if color in color_dict:
        return str(color_dict[color])
    
    # Hex color
    if isinstance(color, str) and color.startswith('#'):
        r, g, b = _hex_to_rgb(color)
        return _rgb_to_ansi(r, g, b, background)
    
    # RGB tuple
    if isinstance(color, (tuple, list)) and len(color) == 3:
        return _rgb_to_ansi(*color, background)
    
    return None


def enable():
    """Enable styling globally."""
    _Config.enabled = True


def disable():
    """Disable styling globally."""
    _Config.enabled = False


def style(text, color=None, bg=None, look=None):
    """Apply color, background, and/or look to text.
    
    Args:
        text: Text to style
        color: Foreground color (name, hex like '#FF5733', or RGB tuple like (255, 87, 51))
        bg: Background color (name, hex, or RGB tuple)
        look: Style name (e.g., 'bold', 'underline')
    
    Returns:
        Styled text with ANSI codes (or plain text if disabled)
        
    Example:
        >>> import textstyle as ts
        >>> print(ts.style("Error", color="red", bg="white", look="bold"))
        >>> print(ts.style("Custom", color="#FF5733"))
        >>> print(ts.style("RGB", color=(255, 87, 51)))
    """
    if not _Config.enabled:
        return text
    
    codes = []
    
    # Parse foreground color
    fg_code = _parse_color(color, background=False)
    if fg_code:
        codes.append(fg_code)
    
    # Parse background color
    bg_code = _parse_color(bg, background=True)
    if bg_code:
        codes.append(bg_code)
    
    # Parse look
    if look:
        if isinstance(look, str) and look in LOOKS:
            codes.append(str(LOOKS[look]))
        elif isinstance(look, (list, tuple)):
            for l in look:
                if l in LOOKS:
                    codes.append(str(LOOKS[l]))
    
    if not codes:
        return text
    
    return f"\033[{';'.join(codes)}m{text}\033[0m"


def create(name, color=None, bg=None, look=None):
    """Create a custom style tag for use in format().
    
    Args:
        name: Name for the custom style tag
        color: Foreground color (name, hex, or RGB tuple)
        bg: Background color (name, hex, or RGB tuple)
        look: Style name or list of style names
        
    Example:
        >>> import textstyle as ts
        >>> ts.create("error", color="red", bg="white", look="bold")
        >>> ts.create("highlight", color="#FFFF00", bg="#000000")
        >>> print(ts.format("An <error>error</error> occurred"))
    """
    if not name:
        raise ValueError("Style name cannot be empty")
    
    if not color and not bg and not look:
        raise ValueError("Must specify at least color, bg, or look")
    
    _custom_styles[name] = {"color": color, "bg": bg, "look": look}


def delete(name):
    """Delete a custom style tag.
    
    Args:
        name: Name of the custom style to delete
        
    Returns:
        True if deleted, False if style didn't exist
    """
    if name in _custom_styles:
        del _custom_styles[name]
        return True
    return False


def strip(text):
    """Remove all markup tags from text.
    
    Args:
        text: Text containing markup tags
        
    Returns:
        Plain text without any tags
        
    Example:
        >>> import textstyle as ts
        >>> ts.strip("<red>Hello</red> <bold>World</bold>")
        'Hello World'
    """
    return re.sub(r'</?[\w_#-]+>', '', text)


def clean(text):
    """Remove all ANSI escape codes from text.
    
    Args:
        text: Text containing ANSI codes
        
    Returns:
        Plain text without ANSI codes
        
    Example:
        >>> import textstyle as ts
        >>> styled = ts.style("Hello", color="red")
        >>> ts.clean(styled)
        'Hello'
    """
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)


def length(text):
    """Calculate the visible length of text (ignoring ANSI codes).
    
    Args:
        text: Text that may contain ANSI codes
        
    Returns:
        Integer length of visible characters
        
    Example:
        >>> import textstyle as ts
        >>> styled = ts.style("Hello", color="red")
        >>> ts.length(styled)  # Returns 5, not 15
        5
    """
    return len(clean(text))


def set_theme(theme):
    """Set a theme with predefined styles.
    
    Args:
        theme: Dictionary mapping style names to style definitions,
               or string name of a built-in theme ('dark', 'light')
        
    Example:
        >>> import textstyle as ts
        >>> ts.set_theme({
        ...     "error": {"color": "red", "look": "bold"},
        ...     "success": {"color": "green", "look": "bold"},
        ...     "warning": {"color": "yellow"},
        ...     "info": {"color": "cyan"}
        ... })
        >>> print(ts.format("<error>Failed</error>"))
    """
    global _current_theme
    
    # Built-in themes
    if isinstance(theme, str):
        if theme == "dark":
            theme = {
                "error": {"color": "bright_red", "look": "bold"},
                "success": {"color": "bright_green", "look": "bold"},
                "warning": {"color": "bright_yellow", "look": "bold"},
                "info": {"color": "bright_cyan"},
                "debug": {"color": "bright_black"},
                "critical": {"color": "white", "bg": "red", "look": "bold"},
            }
        elif theme == "light":
            theme = {
                "error": {"color": "red", "look": "bold"},
                "success": {"color": "green", "look": "bold"},
                "warning": {"color": "yellow", "look": "bold"},
                "info": {"color": "blue"},
                "debug": {"color": "magenta"},
                "critical": {"color": "white", "bg": "red", "look": "bold"},
            }
        else:
            raise ValueError(f"Unknown theme: {theme}")
    
    _current_theme = theme
    
    # Register all theme styles
    for name, style_def in theme.items():
        create(name, **style_def)


@contextmanager
def temporary(name, color=None, bg=None, look=None):
    """Context manager for temporary custom styles.
    
    Args:
        name: Name for the temporary style
        color: Foreground color
        bg: Background color
        look: Style name
        
    Example:
        >>> import textstyle as ts
        >>> with ts.temporary("temp", color="cyan", look="bold"):
        ...     print(ts.format("<temp>Temporary style</temp>"))
        # 'temp' style is automatically deleted after context
    """
    create(name, color=color, bg=bg, look=look)
    try:
        yield
    finally:
        delete(name)


def format(text):
    """Format text with markup-style tags.
    
    Supports predefined tags, custom tags, hex colors, and nested tags.
    
    Args:
        text: Text containing markup tags
        
    Returns:
        Formatted text with ANSI codes applied
        
    Example:
        >>> import textstyle as ts
        >>> print(ts.format("This is <red>red</red> text"))
        >>> print(ts.format("This is <#FF5733>hex color</#FF5733>"))
        >>> print(ts.format("<red><bold>Nested</bold></red>"))
    """
    if not _Config.enabled:
        return strip(text)
    
    # Combine predefined, theme, and custom styles
    all_styles = {**_predefined_styles, **_current_theme, **_custom_styles}
    
    # Pattern matches opening and closing tags (including hex colors)
    tag_pattern = r'<([\w_#-]+)>(.*?)</\1>'
    
    def replace_tag(match):
        tag_name = match.group(1)
        content = match.group(2)
        
        # Check if it's a hex color tag
        if tag_name.startswith('#'):
            return style(content, color=tag_name)
        
        if tag_name in all_styles:
            style_def = all_styles[tag_name]
            return style(content, 
                        color=style_def.get("color"),
                        bg=style_def.get("bg"),
                        look=style_def.get("look"))
        
        # Unknown tag, return as-is
        return match.group(0)
    
    # Keep replacing until no more tags (handles nested tags)
    prev_text = None
    while prev_text != text:
        prev_text = text
        text = re.sub(tag_pattern, replace_tag, text)
    
    return text


def __getattr__(name):
    """Dynamic attribute access for custom styles."""
    if name in _custom_styles:
        s = _custom_styles[name]
        return lambda text: style(text, color=s.get("color"), bg=s.get("bg"), look=s.get("look"))
    
    raise AttributeError(f"module 'textstyle' has no attribute '{name}'")


__all__ = [
    "style", "format", "create", "delete", "strip", "clean", "length",
    "enable", "disable", "set_theme", "temporary",
    "COLORS", "BG_COLORS", "LOOKS"
]


# ============================================
# Example usage / tests
# ============================================
if __name__ == "__main__":
    print("=== Basic Style Function ===")
    print(style("Error", color="red", look="bold"))
    print(style("Success", color="green", bg="black", look="bold"))
    print(style("Warning", color="yellow", bg="blue"))
    
    print("\n=== Hex Colors ===")
    print(style("Hex Red", color="#FF0000"))
    print(style("Hex Green", color="#00FF00"))
    print(style("Custom Orange", color="#FF5733", look="bold"))
    
    print("\n=== RGB Colors ===")
    print(style("RGB Red", color=(255, 0, 0)))
    print(style("RGB Purple", color=(128, 0, 128), look="italic"))
    
    print("\n=== Background Colors ===")
    print(style("Alert", color="white", bg="red", look="bold"))
    print(style("Success", color="black", bg="green", look="bold"))
    print(style("Hex BG", color="white", bg="#FF5733"))
    
    print("\n=== Predefined Tags with Backgrounds ===")
    print(format("Normal <bg_red><white>Alert!</white></bg_red> text"))
    print(format("<bg_green><black>Success</black></bg_green>"))
    
    print("\n=== Hex Color Tags ===")
    print(format("This is <#FF5733>hex color</#FF5733> text"))
    print(format("<#00FF00>Green</#00FF00> and <#FF0000>Red</#FF0000>"))
    
    print("\n=== Custom Styles with Backgrounds ===")
    create("alert", color="white", bg="red", look="bold")
    create("ok", color="black", bg="green", look="bold")
    create("highlight", color="#FFFF00", bg="#000000", look="bold")
    
    print(format("<alert>ALERT!</alert> System critical"))
    print(format("<ok>OK</ok> All systems operational"))
    print(format("Please <highlight>note this</highlight> carefully"))
    
    print("\n=== Strip and Clean Functions ===")
    markup_text = "<red>Hello</red> <bold>World</bold>"
    print(f"Original: {markup_text}")
    print(f"Stripped: {strip(markup_text)}")
    
    styled_text = style("Hello World", color="red", look="bold")
    print(f"Styled length (with ANSI): {len(styled_text)}")
    print(f"Visible length: {length(styled_text)}")
    print(f"Cleaned: '{clean(styled_text)}'")
    
    print("\n=== Theme System (Dark) ===")
    set_theme("dark")
    print(format("<error>Error:</error> Connection failed"))
    print(format("<success>Success:</success> Connected to server"))
    print(format("<warning>Warning:</warning> Low disk space"))
    print(format("<info>Info:</info> Processing data"))
    print(format("<critical>CRITICAL</critical> System failure"))
    
    print("\n=== Theme System (Light) ===")
    set_theme("light")
    print(format("<error>Error:</error> Connection failed"))
    print(format("<success>Success:</success> Connected"))
    
    print("\n=== Custom Theme ===")
    set_theme({
        "primary": {"color": "#007AFF", "look": "bold"},
        "danger": {"color": "white", "bg": "#FF3B30", "look": "bold"},
        "muted": {"color": "bright_black"}
    })
    print(format("<primary>Primary action</primary>"))
    print(format("<danger>Danger zone</danger>"))
    print(format("<muted>Less important info</muted>"))
    
    print("\n=== Temporary Styles ===")
    with temporary("temp", color="magenta", look="italic"):
        print(format("<temp>This is temporary</temp>"))
    # 'temp' is now deleted
    print(format("<temp>This will be plain text</temp>"))
    
    print("\n=== Complex Example ===")
    set_theme("dark")
    print(format("""
<critical>SYSTEM ERROR</critical>
<error>Failed to connect to database</error>
  <info>Host:</info> <#00FFFF>db.example.com</#00FFFF>
  <info>Port:</info> 5432
  <warning>Retrying in 5 seconds...</warning>
<success>Connection restored</success>
"""))