"""
vargula - Simple cross-platform terminal text styling library with advanced color palette generation

Example:
    >>> import vargula as vg
    >>> print(vg.style("Error", color="red", bg="white", look="bold"))
    >>> print(vg.style("Custom", color="#FF5733"))
    >>> vg.create("error", color="red", look="bold")
    >>> print(vg.format("An <error>error</error> occurred"))
    
    # Generate color palettes
    >>> palette = vg.generate_palette("#3498db", "complementary", 5)
    >>> theme = vg.generate_theme_palette("analogous", "#e74c3c")
    >>> vg.apply_palette_theme(theme)
"""

__version__ = "1.2.0"

import sys
import os
import re
import random
import colorsys
import json
from contextlib import contextmanager
from typing import List, Tuple, Dict, Literal, Optional
from pathlib import Path

# Type definitions
PaletteScheme = Literal[
    "monochromatic", "analogous", "complementary", 
    "triadic", "tetradic", "split_complementary", "square", "random"
]
ColorBlindType = Literal["protanopia", "deuteranopia", "tritanopia", "protanomaly", "deuteranomaly", "tritanomaly"]

# Color theory constants
ANALOGOUS_SPREAD = 60
TRIADIC_SPREAD = 120
TETRADIC_OFFSEts = [0, 60, 180, 240]
SQUARE_OFFSEts = [0, 90, 180, 270]
SPLIT_COMPLEMENTARY_OFFSEts = [0, 150, 210]

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


# ============================================
# Core vargula functions
# ============================================

def _init_predefined_styles():
    """Initialize predefined color and look tags"""
    for color_name in COLORS.keys():
        _predefined_styles[color_name] = {"color": color_name, "bg": None, "look": None}
    
    for bg_name in BG_COLORS.keys():
        _predefined_styles[bg_name] = {"color": None, "bg": bg_name, "look": None}
    
    for look_name in LOOKS.keys():
        _predefined_styles[look_name] = {"color": None, "bg": None, "look": look_name}


def _init_windows():
    """Enable ANSI support on Windows"""
    if sys.platform == "win32":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            handle = kernel32.GetstdHandle(-11)
            mode = ctypes.c_ulong()
            kernel32.GetConsoleMode(handle, ctypes.byref(mode))
            mode.value |= 0x0004
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


def _hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join([c*2 for c in hex_color])
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def _rgb_to_hex(r, g, b):
    """Convert RGB tuple to hex color"""
    return f"#{int(r):02x}{int(g):02x}{int(b):02x}"


def _rgb_to_ansi(r, g, b, background=False):
    """Convert RGB to ANSI 24-bit true color code"""
    prefix = 48 if background else 38
    return f"{prefix};2;{r};{g};{b}"


def _parse_color(color, background=False):
    """Parse color input (name, hex, or RGB tuple) to ANSI code"""
    if not color:
        return None
    
    color_dict = BG_COLORS if background else COLORS
    color_key = f"bg_{color}" if background and not color.startswith("bg_") else color
    
    if color_key in color_dict:
        return str(color_dict[color_key])
    if color in color_dict:
        return str(color_dict[color])
    
    if isinstance(color, str) and color.startswith('#'):
        r, g, b = _hex_to_rgb(color)
        return _rgb_to_ansi(r, g, b, background)
    
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
    """Apply color, background, and/or look to text."""
    if not _Config.enabled:
        return text
    
    codes = []
    
    fg_code = _parse_color(color, background=False)
    if fg_code:
        codes.append(fg_code)
    
    bg_code = _parse_color(bg, background=True)
    if bg_code:
        codes.append(bg_code)
    
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
    """Create a custom style tag for use in format()."""
    if not name:
        raise ValueError("Style name cannot be empty")
    
    if not color and not bg and not look:
        raise ValueError("Must specify at least color, bg, or look")
    
    _custom_styles[name] = {"color": color, "bg": bg, "look": look}


def delete(name):
    """Delete a custom style tag."""
    if name in _custom_styles:
        del _custom_styles[name]
        return True
    return False


def strip(text):
    """Remove all markup tags from text."""
    return re.sub(r'</?[\w_#-]+>', '', text)


def clean(text):
    """Remove all ANSI escape codes from text."""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)


def length(text):
    """Calculate the visible length of text (ignoring ANSI codes)."""
    return len(clean(text))


def set_theme(theme):
    """Set a theme with predefined styles."""
    global _current_theme
    
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
    
    for name, style_def in theme.items():
        create(name, **style_def)


@contextmanager
def temporary(name, color=None, bg=None, look=None):
    """Context manager for temporary custom styles."""
    create(name, color=color, bg=bg, look=look)
    try:
        yield
    finally:
        delete(name)


def format(text):
    """Format text with markup-style tags."""
    if not _Config.enabled:
        return strip(text)
    
    all_styles = {**_predefined_styles, **_current_theme, **_custom_styles}
    
    tag_pattern = r'<([\w_#-]+)>(.*?)</\1>'
    
    def replace_tag(match):
        tag_name = match.group(1)
        content = match.group(2)
        
        if tag_name.startswith('#'):
            return style(content, color=tag_name)
        
        if tag_name in all_styles:
            style_def = all_styles[tag_name]
            return style(content, 
                        color=style_def.get("color"),
                        bg=style_def.get("bg"),
                        look=style_def.get("look"))
        
        return match.group(0)
    
    prev_text = None
    while prev_text != text:
        prev_text = text
        text = re.sub(tag_pattern, replace_tag, text)
    
    return text


# ============================================
# Color Space Conversions
# ============================================

def _hex_to_hsv(hex_color: str) -> Tuple[float, float, float]:
    """Convert hex color to HSV tuple (0-1 range)"""
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    return colorsys.rgb_to_hsv(r, g, b)


def _hsv_to_hex(h: float, s: float, v: float) -> str:
    """Convert HSV (0-1 range) to hex color"""
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"


def _rgb_to_relative_luminance(r: int, g: int, b: int) -> float:
    """Calculate relative luminance for WCAG contrast ratio"""
    def adjust(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    
    return 0.2126 * adjust(r) + 0.7152 * adjust(g) + 0.0722 * adjust(b)


# ============================================
# Accessibility Functions
# ============================================

def calculate_contrast_ratio(color1: str, color2: str) -> float:
    """Calculate WCAG 2.1 contrast ratio between two colors.
    
    Args:
        color1: First hex color
        color2: Second hex color
        
    Returns:
        Contrast ratio (1-21, where 21 is maximum contrast)
        
    Example:
        >>> calculate_contrast_ratio("#FFFFFF", "#000000")
        21.0
        >>> calculate_contrast_ratio("#3498db", "#1a1a1a")
        5.2
    """
    r1, g1, b1 = _hex_to_rgb(color1)
    r2, g2, b2 = _hex_to_rgb(color2)
    
    l1 = _rgb_to_relative_luminance(r1, g1, b1)
    l2 = _rgb_to_relative_luminance(r2, g2, b2)
    
    lighter = max(l1, l2)
    darker = min(l1, l2)
    
    return (lighter + 0.05) / (darker + 0.05)


def meets_wcag(color1: str, color2: str, level: str = "AA", large_text: bool = False) -> bool:
    """Check if color pair meets WCAG contrast requiremenvg.
    
    Args:
        color1: First hex color (e.g., text color)
        color2: Second hex color (e.g., background color)
        level: WCAG level - "AA" or "AAA"
        large_text: True if text is 18pt+ or 14pt+ bold
        
    Returns:
        True if colors meet the specified WCAG level
        
    Example:
        >>> meets_wcag("#FFFFFF", "#000000", "AAA")
        True
        >>> meets_wcag("#777777", "#888888", "AA")
        False
    """
    ratio = calculate_contrast_ratio(color1, color2)
    
    if level == "AAA":
        required = 4.5 if large_text else 7.0
    else:  # AA
        required = 3.0 if large_text else 4.5
    
    return ratio >= required


def ensure_contrast(foreground: str, background: str, min_ratio: float = 4.5, 
                   max_iterations: int = 20) -> str:
    """Adjust foreground color to meet minimum contrast ratio.
    
    Args:
        foreground: Foreground hex color to adjust
        background: Background hex color
        min_ratio: Minimum contrast ratio to achieve
        max_iterations: Maximum adjustment attempts
        
    Returns:
        Adjusted foreground color that meets contrast requirement
        
    Example:
        >>> ensure_contrast("#888888", "#999999", min_ratio=4.5)
        '#3d3d3d'  # Darkened to meet contrast
    """
    current_ratio = calculate_contrast_ratio(foreground, background)
    
    if current_ratio >= min_ratio:
        return foreground
    
    h, s, v = _hex_to_hsv(foreground)
    bg_h, bg_s, bg_v = _hex_to_hsv(background)
    
    # Determine if we should lighten or darken
    should_lighten = bg_v < 0.5
    
    for _ in range(max_iterations):
        if should_lighten:
            v = min(1.0, v + 0.05)
        else:
            v = max(0.0, v - 0.05)
        
        adjusted = _hsv_to_hex(h, s, v)
        current_ratio = calculate_contrast_ratio(adjusted, background)
        
        if current_ratio >= min_ratio:
            return adjusted
    
    # If we can't meet the ratio by adjusting value, try full white/black
    return "#ffffff" if should_lighten else "#000000"


# ============================================
# Color Blindness Simulation
# ============================================

def simulate_colorblindness(hex_color: str, cb_type: ColorBlindType) -> str:
    """Simulate how a color appears to colorblind individuals.
    
    Uses Brettel, Viénot and Mollon (1997) algorithm.
    
    Args:
        hex_color: Input hex color
        cb_type: Type of color blindness
        
    Returns:
        Hex color as it would appear to someone with specified color blindness
        
    Example:
        >>> simulate_colorblindness("#FF0000", "deuteranopia")
        '#b89000'  # Red appears brownish-yellow
    """
    r, g, b = _hex_to_rgb(hex_color)
    
    # Transformation matrices for different types (simplified)
    matrices = {
        "protanopia": [  # Red-blind
            [0.567, 0.433, 0.000],
            [0.558, 0.442, 0.000],
            [0.000, 0.242, 0.758]
        ],
        "deuteranopia": [  # Green-blind
            [0.625, 0.375, 0.000],
            [0.700, 0.300, 0.000],
            [0.000, 0.300, 0.700]
        ],
        "tritanopia": [  # Blue-blind
            [0.950, 0.050, 0.000],
            [0.000, 0.433, 0.567],
            [0.000, 0.475, 0.525]
        ],
        "protanomaly": [  # Red-weak
            [0.817, 0.183, 0.000],
            [0.333, 0.667, 0.000],
            [0.000, 0.125, 0.875]
        ],
        "deuteranomaly": [  # Green-weak
            [0.800, 0.200, 0.000],
            [0.258, 0.742, 0.000],
            [0.000, 0.142, 0.858]
        ],
        "tritanomaly": [  # Blue-weak
            [0.967, 0.033, 0.000],
            [0.000, 0.733, 0.267],
            [0.000, 0.183, 0.817]
        ]
    }
    
    if cb_type not in matrices:
        return hex_color
    
    matrix = matrices[cb_type]
    
    # Apply transformation
    new_r = matrix[0][0] * r + matrix[0][1] * g + matrix[0][2] * b
    new_g = matrix[1][0] * r + matrix[1][1] * g + matrix[1][2] * b
    new_b = matrix[2][0] * r + matrix[2][1] * g + matrix[2][2] * b
    
    # Clamp values
    new_r = max(0, min(255, int(new_r)))
    new_g = max(0, min(255, int(new_g)))
    new_b = max(0, min(255, int(new_b)))
    
    return _rgb_to_hex(new_r, new_g, new_b)


def validate_colorblind_safety(colors: List[str], cb_type: ColorBlindType = "deuteranopia",
                               min_difference: float = 30) -> Tuple[bool, List[Tuple[int, int]]]:
    """Check if palette colors are distinguishable for colorblind users.
    
    Args:
        colors: List of hex colors to validate
        cb_type: Type of color blindness to test
        min_difference: Minimum perceptual difference required
        
    Returns:
        Tuple of (is_safe, list of problematic color pair indices)
        
    Example:
        >>> colors = ["#FF0000", "#00FF00", "#0000FF"]
        >>> is_safe, problems = validate_colorblind_safety(colors)
        >>> if not is_safe:
        ...     print(f"Colors {problems[0]} are too similar")
    """
    simulated = [simulate_colorblindness(c, cb_type) for c in colors]
    problems = []
    
    for i in range(len(simulated)):
        for j in range(i + 1, len(simulated)):
            r1, g1, b1 = _hex_to_rgb(simulated[i])
            r2, g2, b2 = _hex_to_rgb(simulated[j])
            
            # Calculate Euclidean distance in RGB space
            distance = ((r2 - r1)**2 + (g2 - g1)**2 + (b2 - b1)**2) ** 0.5
            
            if distance < min_difference:
                problems.append((i, j))
    
    return len(problems) == 0, problems


# ============================================
# Color Manipulation Functions
# ============================================

def lighten(color: str, amount: float = 0.1) -> str:
    """Increase brightness (value) of a color.
    
    Args:
        color: Hex color to lighten
        amount: Amount to increase value (0-1)
        
    Returns:
        Lightened hex color
        
    Example:
        >>> lighten("#3498db", 0.2)
        '#5dbbff'
    """
    h, s, v = _hex_to_hsv(color)
    v = min(1.0, v + amount)
    return _hsv_to_hex(h, s, v)


def darken(color: str, amount: float = 0.1) -> str:
    """Decrease brightness (value) of a color.
    
    Args:
        color: Hex color to darken
        amount: Amount to decrease value (0-1)
        
    Returns:
        Darkened hex color
        
    Example:
        >>> darken("#3498db", 0.2)
        '#1a5a87'
    """
    h, s, v = _hex_to_hsv(color)
    v = max(0.0, v - amount)
    return _hsv_to_hex(h, s, v)


def saturate(color: str, amount: float = 0.1) -> str:
    """Increase saturation of a color.
    
    Args:
        color: Hex color to saturate
        amount: Amount to increase saturation (0-1)
        
    Returns:
        More saturated hex color
        
    Example:
        >>> saturate("#80a0c0", 0.3)
        '#5a9ad8'
    """
    h, s, v = _hex_to_hsv(color)
    s = min(1.0, s + amount)
    return _hsv_to_hex(h, s, v)


def desaturate(color: str, amount: float = 0.1) -> str:
    """Decrease saturation of a color.
    
    Args:
        color: Hex color to desaturate
        amount: Amount to decrease saturation (0-1)
        
    Returns:
        Less saturated hex color
        
    Example:
        >>> desaturate("#3498db", 0.3)
        '#5a8aad'
    """
    h, s, v = _hex_to_hsv(color)
    s = max(0.0, s - amount)
    return _hsv_to_hex(h, s, v)


def shift_hue(color: str, degrees: float) -> str:
    """Rotate hue by specified degrees.
    
    Args:
        color: Hex color to shift
        degrees: Degrees to rotate hue (-360 to 360)
        
    Returns:
        Hue-shifted hex color
        
    Example:
        >>> shift_hue("#FF0000", 120)  # Red -> Green
        '#00ff00'
    """
    h, s, v = _hex_to_hsv(color)
    h = (h + degrees / 360) % 1.0
    return _hsv_to_hex(h, s, v)


def invert(color: str) -> str:
    """Invert a color.
    
    Args:
        color: Hex color to invert
        
    Returns:
        Inverted hex color
        
    Example:
        >>> invert("#FF0000")
        '#00ffff'
    """
    r, g, b = _hex_to_rgb(color)
    return _rgb_to_hex(255 - r, 255 - g, 255 - b)


def mix(color1: str, color2: str, weight: float = 0.5) -> str:
    """Mix two colors together.
    
    Args:
        color1: First hex color
        color2: Second hex color
        weight: Weight of first color (0-1, default 0.5 for equal mix)
        
    Returns:
        Mixed hex color
        
    Example:
        >>> mix("#FF0000", "#0000FF", 0.5)  # Red + Blue = Purple
        '#7f007f'
    """
    r1, g1, b1 = _hex_to_rgb(color1)
    r2, g2, b2 = _hex_to_rgb(color2)
    
    r = int(r1 * weight + r2 * (1 - weight))
    g = int(g1 * weight + g2 * (1 - weight))
    b = int(b1 * weight + b2 * (1 - weight))
    
    return _rgb_to_hex(r, g, b)


# ============================================
# Palette Generation
# ============================================

def generate_palette(
    base_color: str = None,
    scheme: PaletteScheme = "random",
    count: int = 5,
    saturation_range: Tuple[float, float] = (0.4, 0.9),
    value_range: Tuple[float, float] = (0.5, 0.95),
    randomize: bool = True
) -> List[str]:
    """Generate a color palette based on color theory.
    
    Args:
        base_color: Starting hex color (e.g., '#FF5733'). If None, random.
        scheme: Color harmony scheme to use
        count: Number of colors to generate
        saturation_range: (min, max) saturation values (0-1)
        value_range: (min, max) brightness values (0-1)
        randomize: Add slight random variations for more natural palettes
        
    Returns:
        List of hex color strings
        
    Examples:
        >>> generate_palette("#3498db", "complementary", 5)
        ['#3498db', '#db7834', '#34a4db', '#db3449', '#4ddb34']
        
        >>> generate_palette(scheme="random", count=8)
        ['#e74c3c', '#3498db', '#2ecc71', ...]
    """
    if base_color is None:
        h = random.random()
        s = random.uniform(*saturation_range)
        v = random.uniform(*value_range)
    else:
        h, s, v = _hex_to_hsv(base_color)
    
    colors = []
    
    if scheme == "monochromatic":
        colors.append(_hsv_to_hex(h, s, v))
        for i in range(1, count):
            new_s = s * (0.6 + 0.8 * i / count)
            new_v = v * (0.7 + 0.6 * i / count)
            if randomize:
                new_s += random.uniform(-0.1, 0.1)
                new_v += random.uniform(-0.1, 0.1)
            new_s = max(0.2, min(1.0, new_s))
            new_v = max(0.3, min(1.0, new_v))
            colors.append(_hsv_to_hex(h, new_s, new_v))
    
    elif scheme == "analogous":
        step = ANALOGOUS_SPREAD / max(count - 1, 1)
        for i in range(count):
            offset = -30 + i * step
            if randomize:
                offset += random.uniform(-5, 5)
            new_h = (h + offset / 360) % 1.0
            new_s = s + random.uniform(-0.1, 0.1) if randomize else s
            new_v = v + random.uniform(-0.1, 0.1) if randomize else v
            new_s = max(0.3, min(1.0, new_s))
            new_v = max(0.4, min(1.0, new_v))
            colors.append(_hsv_to_hex(new_h, new_s, new_v))
    
    elif scheme == "complementary":
        colors.append(_hsv_to_hex(h, s, v))
        complement_h = (h + 0.5) % 1.0
        colors.append(_hsv_to_hex(complement_h, s, v))
        
        for i in range(2, count):
            use_base = i % 2 == 0
            base_h = h if use_base else complement_h
            offset = random.uniform(-0.1, 0.1) if randomize else 0
            new_h = (base_h + offset) % 1.0
            new_s = s + random.uniform(-0.15, 0.15) if randomize else s
            new_v = v + random.uniform(-0.15, 0.15) if randomize else v
            new_s = max(0.3, min(1.0, new_s))
            new_v = max(0.4, min(1.0, new_v))
            colors.append(_hsv_to_hex(new_h, new_s, new_v))
    
    elif scheme == "split_complementary":
        for i, offset in enumerate(SPLIT_COMPLEMENTARY_OFFSEts * ((count // 3) + 1)):
            if len(colors) >= count:
                break
            if randomize:
                offset += random.uniform(-10, 10)
            new_h = (h + offset / 360) % 1.0
            variation = (i // 3) * 0.1
            new_s = s - variation + random.uniform(-0.1, 0.1) if randomize else s - variation
            new_v = v - variation * 0.5 + random.uniform(-0.1, 0.1) if randomize else v - variation * 0.5
            new_s = max(0.3, min(1.0, new_s))
            new_v = max(0.4, min(1.0, new_v))
            colors.append(_hsv_to_hex(new_h, new_s, new_v))
    
    elif scheme == "triadic":
        for i in range(count):
            offset = (i % 3) * TRIADIC_SPREAD
            if randomize:
                offset += random.uniform(-10, 10)
            new_h = (h + offset / 360) % 1.0
            variation = i // 3 * 0.15
            new_s = s - variation + random.uniform(-0.1, 0.1) if randomize else s - variation
            new_v = v - variation * 0.5 + random.uniform(-0.1, 0.1) if randomize else v - variation * 0.5
            new_s = max(0.3, min(1.0, new_s))
            new_v = max(0.4, min(1.0, new_v))
            colors.append(_hsv_to_hex(new_h, new_s, new_v))
    
    elif scheme == "tetradic":
        for i in range(count):
            offset = TETRADIC_OFFSEts[i % 4]
            if randomize:
                offset += random.uniform(-10, 10)
            new_h = (h + offset / 360) % 1.0
            variation = i // 4 * 0.1
            new_s = s - variation + random.uniform(-0.08, 0.08) if randomize else s - variation
            new_v = v - variation * 0.5 + random.uniform(-0.08, 0.08) if randomize else v - variation * 0.5
            new_s = max(0.3, min(1.0, new_s))
            new_v = max(0.4, min(1.0, new_v))
            colors.append(_hsv_to_hex(new_h, new_s, new_v))
    
    elif scheme == "square":
        for i in range(count):
            offset = SQUARE_OFFSEts[i % 4]
            if randomize:
                offset += random.uniform(-8, 8)
            new_h = (h + offset / 360) % 1.0
            variation = i // 4 * 0.1
            new_s = s - variation + random.uniform(-0.08, 0.08) if randomize else s - variation
            new_v = v - variation * 0.5 + random.uniform(-0.08, 0.08) if randomize else v - variation * 0.5
            new_s = max(0.3, min(1.0, new_s))
            new_v = max(0.4, min(1.0, new_v))
            colors.append(_hsv_to_hex(new_h, new_s, new_v))
    
    else:  # random
        for _ in range(count):
            rand_h = random.random()
            rand_s = random.uniform(*saturation_range)
            rand_v = random.uniform(*value_range)
            colors.append(_hsv_to_hex(rand_h, rand_s, rand_v))
    
    return colors[:count]


def generate_theme_palette(
    scheme: PaletteScheme = "random",
    base_color: str = None,
    include_neutrals: bool = True,
    force_semantic_colors: bool = False
) -> Dict[str, str]:
    """Generate a complete theme palette with semantic colors.
    
    Args:
        scheme: Color harmony scheme
        base_color: Optional base color to build from
        include_neutrals: Add grayscale colors for backgrounds/text
        force_semantic_colors: Use standard green/yellow/red for success/warning/error
        
    Returns:
        Dictionary mapping theme names to hex colors
        
    Example:
        >>> palette = generate_theme_palette("complementary", "#3498db")
        >>> palette
        {
            'primary': '#3498db',
            'secondary': '#db7834',
            'accent': '#34dbb4',
            'success': '#2ecc71',
            'warning': '#f39c12',
            'error': '#e74c3c',
            'info': '#3498db',
            'background': '#1a1a1a',
            'foreground': '#e0e0e0'
        }
    """
    colors = generate_palette(base_color, scheme, count=7)
    
    theme = {
        'primary': colors[0],
        'secondary': colors[1] if len(colors) > 1 else colors[0],
        'accent': colors[2] if len(colors) > 2 else colors[0],
    }
    
    if force_semantic_colors:
        # Always use recognizable colors for semantic meanings
        theme['success'] = _hsv_to_hex(0.33, 0.7, 0.8)  # Green
        theme['warning'] = _hsv_to_hex(0.15, 0.8, 0.9)  # Yellow
        theme['error'] = _hsv_to_hex(0.0, 0.8, 0.85)  # Red
        theme['info'] = colors[0]
    else:
        if len(colors) > 3:
            theme['success'] = colors[3]
            theme['warning'] = colors[4] if len(colors) > 4 else _hsv_to_hex(0.15, 0.8, 0.9)
            theme['error'] = colors[5] if len(colors) > 5 else _hsv_to_hex(0.0, 0.8, 0.85)
            theme['info'] = colors[6] if len(colors) > 6 else colors[0]
        else:
            theme['success'] = _hsv_to_hex(0.33, 0.7, 0.8)
            theme['warning'] = _hsv_to_hex(0.15, 0.8, 0.9)
            theme['error'] = _hsv_to_hex(0.0, 0.8, 0.85)
            theme['info'] = colors[0]
    
    if include_neutrals:
        theme['background'] = '#1a1a1a'
        theme['foreground'] = '#e0e0e0'
        theme['muted'] = '#666666'
        theme['border'] = '#333333'
    
    return theme


def generate_accessible_theme(
    base_color: str,
    scheme: PaletteScheme = "complementary",
    background: str = "#1a1a1a",
    min_contrast: float = 4.5,
    wcag_level: str = "AA"
) -> Dict[str, str]:
    """Generate theme palette with WCAG contrast validation.
    
    Automatically adjusts colors to meet minimum contrast ratios
    against the specified background.
    
    Args:
        base_color: Base color to build theme from
        scheme: Color harmony scheme
        background: Background color to test contrast against
        min_contrast: Minimum contrast ratio (4.5 for AA, 7.0 for AAA)
        wcag_level: WCAG level "AA" or "AAA"
        
    Returns:
        Dictionary with accessible color theme
        
    Example:
        >>> theme = generate_accessible_theme("#3498db", "complementary", "#ffffff")
        >>> # All colors will have sufficient contrast on white background
    """
    theme = generate_theme_palette(scheme, base_color, force_semantic_colors=True)
    
    # Adjust foreground colors for accessibility
    for key in ['primary', 'secondary', 'accent', 'error', 'warning', 'success', 'info']:
        if key in theme:
            original = theme[key]
            adjusted = ensure_contrast(original, background, min_contrast)
            theme[key] = adjusted
    
    theme['background'] = background
    theme['foreground'] = ensure_contrast('#e0e0e0', background, min_contrast)
    
    return theme


def preview_palette(colors: List[str], width: int = 40, show_info: bool = True) -> str:
    """Generate a text preview of a color palette.
    
    Args:
        colors: List of hex colors
        width: Width of each color block in characters
        show_info: Show additional color information
        
    Returns:
        Formatted string showing colored blocks
    """
    output = []
    for i, color in enumerate(colors):
        block = "█" * width
        styled_block = style(block, color=color)
        line = f"{i+1}. {color:8s} {styled_block}"
        
        if show_info:
            h, s, v = _hex_to_hsv(color)
            line += f"  H:{h*360:3.0f}° S:{s*100:3.0f}% V:{v*100:3.0f}%"
        
        output.append(line)
    return "\n".join(output)


def apply_palette_theme(palette: Dict[str, str], register_styles: bool = True):
    """Apply a generated palette as the active theme.
    
    Args:
        palette: Dictionary from generate_theme_palette()
        register_styles: If True, register each color as a custom style
        
    Example:
        >>> theme = generate_theme_palette("analogous", "#e74c3c")
        >>> apply_palette_theme(theme)
        >>> print(format("<primary>Primary text</primary>"))
        >>> print(format("<error>Error message</error>"))
    """
    global _current_theme
    
    theme_styles = {}
    for name, color in palette.items():
        theme_styles[name] = {"color": color, "bg": None, "look": None}
    
    _current_theme = theme_styles
    
    if register_styles:
        for name, style_def in theme_styles.items():
            create(name, **style_def)


# ============================================
# Palette Persistence
# ============================================

def save_palette(colors: List[str], filename: str, metadata: Optional[Dict] = None):
    """Save color palette to JSON file.
    
    Args:
        colors: List of hex colors to save
        filename: Output file path
        metadata: Optional metadata (name, description, scheme, etc.)
        
    Example:
        >>> palette = generate_palette("#3498db", "complementary", 5)
        >>> save_palette(palette, "my_theme.json", 
        ...              metadata={"name": "Ocean Blue", "scheme": "complementary"})
    """
    data = {
        "colors": colors,
        "metadata": metadata or {}
    }
    
    filepath = Path(filename)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)


def load_palette(filename: str) -> Tuple[List[str], Dict]:
    """Load color palette from JSON file.
    
    Args:
        filename: Input file path
        
    Returns:
        Tuple of (colors list, metadata dict)
        
    Example:
        >>> colors, metadata = load_palette("my_theme.json")
        >>> print(f"Loaded: {metadata['name']}")
        >>> preview_palette(colors)
    """
    with open(filename, 'r') as f:
        data = json.load(f)
    
    return data.get("colors", []), data.get("metadata", {})


def save_theme(theme: Dict[str, str], filename: str, metadata: Optional[Dict] = None):
    """Save theme palette to JSON file.
    
    Args:
        theme: Theme dictionary from generate_theme_palette()
        filename: Output file path
        metadata: Optional metadata
        
    Example:
        >>> theme = generate_theme_palette("triadic", "#9b59b6")
        >>> save_theme(theme, "purple_theme.json", 
        ...            metadata={"name": "Purple Rain", "author": "Me"})
    """
    data = {
        "theme": theme,
        "metadata": metadata or {}
    }
    
    filepath = Path(filename)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)


def load_theme(filename: str) -> Tuple[Dict[str, str], Dict]:
    """Load theme palette from JSON file.
    
    Args:
        filename: Input file path
        
    Returns:
        Tuple of (theme dict, metadata dict)
        
    Example:
        >>> theme, metadata = load_theme("purple_theme.json")
        >>> apply_palette_theme(theme)
        >>> print(format("<primary>Using loaded theme!</primary>"))
    """
    with open(filename, 'r') as f:
        data = json.load(f)
    
    return data.get("theme", {}), data.get("metadata", {})


# ============================================
# Initialization
# ============================================

_init_config()
_init_predefined_styles()


__all__ = [
    # Core styling
    "style", "format", "create", "delete", "strip", "clean", "length",
    "enable", "disable", "set_theme", "temporary",
    
    # Palette generation
    "generate_palette", "generate_theme_palette", "generate_accessible_theme",
    "preview_palette", "apply_palette_theme",
    
    # Color manipulation
    "lighten", "darken", "saturate", "desaturate", "shift_hue", "invert", "mix",
    
    # Accessibility
    "calculate_contrast_ratio", "meets_wcag", "ensure_contrast",
    
    # Color blindness
    "simulate_colorblindness", "validate_colorblind_safety",
    
    # Persistence
    "save_palette", "load_palette", "save_theme", "load_theme",
    
    # Constants
    "COLORS", "BG_COLORS", "LOOKS", "PaletteScheme", "ColorBlindType"
]