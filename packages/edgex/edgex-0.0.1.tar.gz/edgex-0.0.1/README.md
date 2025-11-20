# Vargula


[![Python Version](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Cross Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey.svg)](https://github.com/crystallinecore/vargula)

> Lightweight terminal styling with advanced color theory



**A modern, designer-friendly terminal styling library for Python with color theory superpowers.**

Vargula brings HTML-like markup, automatic reset handling, color palette generation, and accessibility features to terminal styling. Unlike traditional libraries that require manual ANSI code management, vargula lets you write clean, semantic markup that's easy to read and maintain.

**Zero dependencies. Beautiful output.**

```python
import vargula as vg

# Simple and intuitive
vg.write("<bold><green>✓</green></bold> Build completed successfully!")

# Create custom styles
vg.create("error", color="red", look="bold")
vg.write("An <error>error</error> occurred in <code>module.py</code>")

# Generate beautiful color palettes
palette = vg.generate_palette("#3498db", "complementary", 5)
theme = vg.generate_theme_palette("analogous", "#e74c3c")
vg.apply_palette_theme(theme)
```

---

##  Why Vargula?

### **Problem with Traditional Libraries (like colorama)**
```python
from colorama import Fore, Style
# Manual reset codes everywhere 😰
print(Fore.RED + "Error: " + Style.RESET_ALL + "File " + Fore.CYAN + "data.json" + Style.RESET_ALL + " not found")
# Nesting? Good luck!
print(Fore.RED + "Outer " + Fore.BLUE + "inner" + Fore.RED + " outer" + Style.RESET_ALL)
```

### **The Vargula Way**
```python
import vargula as vg
# Clean, semantic, automatic resets 😊
vg.write("<red>Error:</red> File <cyan>data.json</cyan> not found")
# Nesting just works
vg.write("<red>Outer <blue>inner</blue> outer</red>")
```

---

##  Installation

```bash
pip install vargula
```

**Requirements:** Python 3.7+, Windows 10+/macOS/Linux

---

##  Core Styling Functions

### `style(text, color=None, bg=None, look=None)`

Apply colors and text effects to a string programmatically.

**What makes it unique:** Supports named colors, hex colors (#FF5733), RGB tuples (255, 87, 51), and multiple text effects simultaneously. Handles all color conversions internally.

```python
# Named colors
print(vg.style("Error", color="red", look="bold"))

# Hex colors (24-bit true color)
print(vg.style("Brand", color="#FF5733", bg="#1a1a1a"))

# RGB tuples
print(vg.style("Custom", color=(255, 87, 51)))

# Multiple effects
print(vg.style("Important", color="yellow", bg="black", look=["bold", "underline"]))
```

**Parameters:**
- `text` (str): Text to style
- `color` (str|tuple): Foreground color (name, hex, or RGB tuple)
- `bg` (str|tuple): Background color (name, hex, or RGB tuple)
- `look` (str|list): Text effect(s) - bold, dim, italic, underline, blink, reverse, hidden, strikethrough

**Returns:** Styled string with ANSI codes

---

### `format(text)`

Parse and render HTML-like markup tags in text. This is vargula's killer feature.

**What makes it unique:** Automatic nested tag handling, no manual resets needed, supports inline hex colors, and combines predefined + custom + theme styles seamlessly.

```python
# Basic tags
print(vg.format("<red>Error</red> in <blue>module.py</blue>"))

# Nested tags (automatic handling!)
print(vg.format("<bold>Important: <red>Critical</red> issue</bold>"))

# Inline hex colors
print(vg.format("Brand color: <#FF5733>orange text</orange>"))

# Mix predefined + custom styles
vg.create("code", color="cyan", bg="black")
print(vg.format("Run <code>pip install</code> to fix <error>dependency</error>"))
```

**How it works:** Recursively processes tags from innermost to outermost, applying styles from predefined, theme, and custom registries. Automatically strips tags when styling is disabled.

**Parameters:**
- `text` (str): Text with markup tags

**Returns:** Styled string with ANSI codes

---

### `write(text)`

Convenience function that formats and prints in one call.

**What makes it unique:** Simple shorthand for `print(vg.format(text))`. Saves typing when you just want to output styled text.

```python
# Instead of: print(vg.format("<red>Error</red>"))
vg.write("<red>Error</red>")

# Works with all markup
vg.write("<bold><green>✓</green></bold> Tests passed")
```

---

### `create(name, color=None, bg=None, look=None)`

Register custom reusable style tags.

**What makes it unique:** Define semantic styles once, use them everywhere. Promotes consistent styling across your application and makes refactoring colors trivial.

```python
# Define semantic styles
vg.create("error", color="red", look="bold")
vg.create("success", color="green", look="bold")
vg.create("code", color="cyan", bg="black", look="italic")
vg.create("highlight", color="yellow", bg="black")

# Use throughout your app
vg.write("<error>Failed to connect</error>")
vg.write("<success>Connected successfully</success>")
vg.write("Run <code>npm start</code> to begin")
vg.write("Found <highlight>3 matches</highlight>")

# Change colors in one place - updates everywhere!
vg.create("error", color="#ff3333", look="bold")  # Now all errors use this
```

**Parameters:**
- `name` (str): Tag name (used as `<name>text</name>`)
- `color` (str|tuple): Foreground color
- `bg` (str|tuple): Background color
- `look` (str|list): Text effect(s)

**Raises:** ValueError if name is empty or no styling specified

---

### `delete(name)`

Remove a custom style tag.

**What makes it unique:** Clean up temporary styles or override existing definitions.

```python
vg.create("temp", color="yellow")
vg.write("<temp>Temporary style</temp>")
vg.delete("temp")  # Returns True

vg.delete("nonexistent")  # Returns False
```

**Parameters:**
- `name` (str): Tag name to delete

**Returns:** True if deleted, False if not found

---

### `set_theme(theme)`

Apply a complete theme with predefined semantic styles.

**What makes it unique:** Switch your entire app's color scheme with one function call. Supports built-in themes ("dark", "light") or custom theme dictionaries.

```python
# Built-in dark theme
vg.set_theme("dark")
vg.write("<error>Error</error> <warning>Warning</warning> <success>Success</success>")

# Built-in light theme
vg.set_theme("light")

# Custom theme
vg.set_theme({
    "error": {"color": "#ff3333", "look": "bold"},
    "success": {"color": "#00ff00", "look": "bold"},
    "info": {"color": "#3498db"},
    "code": {"color": "cyan", "bg": "black", "look": "italic"}
})

# Now all semantic tags use theme colors
vg.write("<error>Error</error> <info>Info</info> <code>code</code>")
```

**Built-in themes include:** error, success, warning, info, debug, critical

**Parameters:**
- `theme` (str|dict): "dark", "light", or custom theme dictionary

---

### `temporary(name, color=None, bg=None, look=None)`

Context manager for temporary styles.

**What makes it unique:** Create scoped styles that automatically clean up. Perfect for one-off styling without polluting the global registry.

```python
# Style exists only within the context
with vg.temporary("special", color="magenta", look="bold"):
    vg.write("<special>This is special</special>")
    vg.write("<special>Still special</special>")

# Style automatically deleted after context
vg.write("<special>This won't be styled</special>")
```

**Parameters:**
- `name` (str): Temporary tag name
- `color`, `bg`, `look`: Style properties

---

### `strip(text)`

Remove all markup tags from text, leaving only content.

**What makes it unique:** Clean way to get plaintext version of styled content for length calculations, logging to files, or display in non-terminal contexts.

```python
text = "<red>Error: <bold>Critical</bold> failure</red>"
print(vg.strip(text))  # Output: "Error: Critical failure"

# Useful for logging to files
with open("log.txt", "w") as f:
    f.write(vg.strip(styled_text))
```

**Parameters:**
- `text` (str): Text with markup tags

**Returns:** Text without tags

---

### `clean(text)`

Remove ANSI escape codes from text.

**What makes it unique:** Strips the actual rendered ANSI sequences (not tags). Useful for processing already-styled text or output from other tools.

```python
styled = vg.format("<red>Error</red>")  # Contains ANSI codes
print(vg.clean(styled))  # Output: "Error" (no codes)

# Clean output from external commands
import subprocess
output = subprocess.check_output(["some-command"]).decode()
clean_output = vg.clean(output)  # Remove any ANSI codes
```

**Parameters:**
- `text` (str): Text with ANSI codes

**Returns:** Text without ANSI codes

---

### `length(text)`

Calculate visible text length, ignoring ANSI codes.

**What makes it unique:** Accurate length for styled text. Critical for alignment, padding, and text layout when using terminal styling.

```python
text = vg.format("<red><bold>Error</bold></red>")
print(len(text))        # 24 (includes ANSI codes)
print(vg.length(text))  # 5 (visible characters only)

# Perfect for padding
message = vg.format("<green>Success</green>")
padded = message + " " * (20 - vg.length(message))  # Right-pad to 20 chars
```

**Parameters:**
- `text` (str): Styled text

**Returns:** Visible character count (int)

---

### `enable()` / `disable()`

Globally enable or disable styling.

**What makes it unique:** Easy toggle for production vs development, CI/CD environments, or user preferences. When disabled, `format()` automatically strips tags.

```python
import os

# Disable in CI environments
if os.getenv("CI"):
    vg.disable()

# Styled in terminal, plain in CI
vg.write("<green>Success</green>")  # Green in terminal, "Success" in CI

# Re-enable
vg.enable()
```

---

##  Color Palette Generation

### `generate_palette(base_color=None, scheme="random", count=5, saturation_range=(0.4, 0.9), value_range=(0.5, 0.95), randomize=True)`

Generate harmonious color palettes based on color theory.

**What makes it unique:** Implements 8 professional color harmony schemes with optional randomization for natural-looking palettes. Unlike manual color picking, this uses proven color theory to create aesthetically pleasing combinations.

```python
# Complementary colors (opposite on color wheel)
palette = vg.generate_palette("#3498db", "complementary", 5)
# ['#3498db', '#db7834', '#34a4db', '#db3449', '#4ddb34']

# Analogous colors (adjacent on color wheel)
palette = vg.generate_palette("#e74c3c", "analogous", 6)

# Triadic harmony (evenly spaced)
palette = vg.generate_palette("#9b59b6", "triadic", 9)

# Random beautiful colors
palette = vg.generate_palette(scheme="random", count=8)

# Precise control
palette = vg.generate_palette(
    base_color="#FF5733",
    scheme="monochromatic",
    count=7,
    saturation_range=(0.6, 1.0),  # High saturation
    value_range=(0.7, 1.0),       # Bright colors
    randomize=False                # No variation
)
```

**Color Schemes:**
- `monochromatic` - Same hue, varying saturation/brightness
- `analogous` - Adjacent hues (60° spread)
- `complementary` - Opposite hues (180° apart)
- `split_complementary` - Base + two colors adjacent to complement
- `triadic` - Three evenly spaced hues (120° apart)
- `tetradic` - Two complementary pairs
- `square` - Four evenly spaced hues (90° apart)
- `random` - Random beautiful colors

**Parameters:**
- `base_color` (str): Starting hex color (None = random)
- `scheme` (str): Color harmony scheme
- `count` (int): Number of colors to generate
- `saturation_range` (tuple): Min/max saturation (0-1)
- `value_range` (tuple): Min/max brightness (0-1)
- `randomize` (bool): Add natural variation

**Returns:** List of hex color strings

---

### `generate_theme_palette(scheme="random", base_color=None, include_neutrals=True, force_semantic_colors=False)`

Generate a complete semantic theme with primary, secondary, accent, success, warning, error, info colors.

**What makes it unique:** Creates production-ready themes with meaningful color roles. Automatically includes neutral colors for backgrounds and borders. Option to force recognizable colors (green=success, red=error) for intuitive UIs.

```python
# Generate complete theme
theme = vg.generate_theme_palette("complementary", "#3498db")
# {
#     'primary': '#3498db',
#     'secondary': '#db7834', 
#     'accent': '#34dbb4',
#     'success': '#2ecc71',
#     'warning': '#f39c12',
#     'error': '#e74c3c',
#     'info': '#3498db',
#     'background': '#1a1a1a',
#     'foreground': '#e0e0e0',
#     'muted': '#666666',
#     'border': '#333333'
# }

# Use semantic colors
vg.apply_palette_theme(theme)
vg.write("<primary>Primary action</primary>")
vg.write("<success>Operation successful</success>")
vg.write("<error>An error occurred</error>")

# Force standard semantic colors (UX best practice)
theme = vg.generate_theme_palette(
    "analogous", 
    "#9b59b6",
    force_semantic_colors=True  # Green=success, yellow=warning, red=error
)
```

**Parameters:**
- `scheme` (str): Color harmony scheme
- `base_color` (str): Starting color (None = random)
- `include_neutrals` (bool): Add grayscale colors
- `force_semantic_colors` (bool): Use standard colors for success/warning/error

**Returns:** Dictionary with semantic color names

---

### `generate_accessible_theme(base_color, scheme="complementary", background="#1a1a1a", min_contrast=4.5, wcag_level="AA")`

Generate WCAG-compliant themes with automatic contrast adjustment.

**What makes it unique:** Automatically ensures all colors meet accessibility standards. Adjusts colors to meet contrast ratios without manual tweaking. Critical for inclusive design and legal compliance (ADA, Section 508).

```python
# Generate accessible theme on dark background
theme = vg.generate_accessible_theme(
    base_color="#3498db",
    scheme="triadic",
    background="#1a1a1a",
    wcag_level="AA"  # 4.5:1 contrast for normal text
)

# All colors automatically adjusted for readability
vg.apply_palette_theme(theme)
vg.write("<primary>Readable on dark</primary>")
vg.write("<success>Meets WCAG AA</success>")

# Stricter AAA compliance
theme = vg.generate_accessible_theme(
    "#e74c3c",
    "complementary",
    "#ffffff",  # Light background
    wcag_level="AAA"  # 7:1 contrast
)

# Every color guaranteed to be readable!
```

**WCAG Levels:**
- `AA` - 4.5:1 contrast (industry standard)
- `AAA` - 7:1 contrast (enhanced accessibility)

**Parameters:**
- `base_color` (str): Starting hex color
- `scheme` (str): Color harmony scheme
- `background` (str): Background color to test against
- `min_contrast` (float): Minimum contrast ratio
- `wcag_level` (str): "AA" or "AAA"

**Returns:** Accessible theme dictionary

---

### `preview_palette(colors, width=40, show_info=True)`

Generate visual terminal preview of a color palette.

**What makes it unique:** Instant visual feedback for palette generation. Shows colors with optional HSV values for designers.

```python
palette = vg.generate_palette("#3498db", "triadic", 6)

# Visual preview in terminal
print(vg.preview_palette(palette))
# 1. #3498db ████████████████████████████████████████  H:204° S: 71% V: 86%
# 2. #db3498 ████████████████████████████████████████  H:324° S: 71% V: 86%
# 3. #98db34 ████████████████████████████████████████  H: 84° S: 71% V: 86%
# ...

# Minimal preview
print(vg.preview_palette(palette, width=20, show_info=False))
```

**Parameters:**
- `colors` (list): List of hex colors
- `width` (int): Width of color blocks
- `show_info` (bool): Show HSV values

**Returns:** Formatted string with colored blocks

---

### `apply_palette_theme(palette, register_styles=True)`

Apply generated palette as active theme.

**What makes it unique:** Bridges palette generation and markup system. Automatically registers palette colors as usable tags.

```python
# Generate and apply in one workflow
theme = vg.generate_theme_palette("analogous", "#e74c3c")
vg.apply_palette_theme(theme)

# Now use semantic tags from theme
vg.write("<primary>Primary button</primary>")
vg.write("<error>Error message</error>")
vg.write("<success>Success notification</success>")

# Don't register as tags (manual usage)
vg.apply_palette_theme(theme, register_styles=False)
color = theme['primary']  # Access colors directly
```

**Parameters:**
- `palette` (dict): Theme dictionary
- `register_styles` (bool): Register as custom tags

---

## Color Manipulation

### `lighten(color, amount=0.1)` / `darken(color, amount=0.1)`

Adjust color brightness.

**What makes it unique:** Intuitive brightness control without RGB math. Works in HSV space for perceptually accurate lightening/darkening.

```python
base = "#3498db"
lighter = vg.lighten(base, 0.2)    # '#5dbbff' (20% brighter)
darker = vg.darken(base, 0.3)      # '#1a5a87' (30% darker)

# Create color scales
light = vg.lighten(base, 0.3)
medium = base
dark = vg.darken(base, 0.2)
```

---

### `saturate(color, amount=0.1)` / `desaturate(color, amount=0.1)`

Adjust color saturation (intensity).

**What makes it unique:** Control color vibrancy independently of brightness. Make colors more vivid or more muted.

```python
base = "#80a0c0"
vivid = vg.saturate(base, 0.3)     # '#5a9ad8' (more intense)
muted = vg.desaturate(base, 0.4)   # '#8c99a6' (more gray)

# Create hover effects
normal = "#3498db"
hover = vg.saturate(normal, 0.2)  # Brighter on hover
```

---

### `shift_hue(color, degrees)`

Rotate hue around color wheel.

**What makes it unique:** Precise hue manipulation. Shift colors to analogous, complementary, or any position on the color wheel.

```python
red = "#FF0000"
green = vg.shift_hue(red, 120)   # '#00ff00' (shift to green)
blue = vg.shift_hue(red, 240)    # '#0000ff' (shift to blue)

# Create analogous colors
base = "#3498db"
similar1 = vg.shift_hue(base, 30)
similar2 = vg.shift_hue(base, -30)
```

**Parameters:**
- `color` (str): Hex color
- `degrees` (float): Rotation angle (-360 to 360)

---

### `invert(color)`

Invert a color (opposite on RGB cube).

**What makes it unique:** Perfect for creating contrasting colors or dark mode inversions.

```python
light = "#FFFFFF"
dark = vg.invert(light)   # '#000000'

blue = "#3498db"
orange = vg.invert(blue)  # '#cb6724'
```

---

### `mix(color1, color2, weight=0.5)`

Blend two colors together.

**What makes it unique:** Smooth color transitions and gradients. Control blend ratio for custom mixes.

```python
red = "#FF0000"
blue = "#0000FF"
purple = vg.mix(red, blue, 0.5)      # '#7f007f' (equal mix)
reddish = vg.mix(red, blue, 0.7)     # '#b2004c' (more red)
blueish = vg.mix(red, blue, 0.3)     # '#4c00b2' (more blue)

# Create smooth gradients
colors = [
    vg.mix("#FF0000", "#0000FF", i/10)
    for i in range(11)
]
```

**Parameters:**
- `color1`, `color2` (str): Hex colors to mix
- `weight` (float): Weight of first color (0-1)

---

##  Accessibility Functions

### `calculate_contrast_ratio(color1, color2)`

Calculate WCAG 2.1 contrast ratio between two colors.

**What makes it unique:** Precise contrast calculation using WCAG standards. Essential for accessible design and legal compliance.

```python
ratio = vg.calculate_contrast_ratio("#FFFFFF", "#000000")
print(ratio)  # 21.0 (maximum contrast)

ratio = vg.calculate_contrast_ratio("#3498db", "#1a1a1a")
print(ratio)  # ~5.2

# Test text on background
text_color = "#3498db"
bg_color = "#ffffff"
ratio = vg.calculate_contrast_ratio(text_color, bg_color)
if ratio >= 4.5:
    print("Readable for normal text")
```

**Returns:** Float from 1 (no contrast) to 21 (maximum contrast)

---

### `meets_wcag(color1, color2, level="AA", large_text=False)`

Check if color pair meets WCAG standards.

**What makes it unique:** Simple boolean check for compliance. No need to remember contrast ratios.

```python
# Test for AA compliance (4.5:1 for normal text)
if vg.meets_wcag("#FFFFFF", "#3498db", "AA"):
    print("✓ Accessible")

# Test for AAA compliance (7:1)
if vg.meets_wcag("#FFFFFF", "#333333", "AAA"):
    print("✓ Highly accessible")

# Large text has lower requirements (18pt+ or 14pt+ bold)
if vg.meets_wcag("#888888", "#FFFFFF", "AA", large_text=True):
    print("✓ Accessible for headings")
```

**WCAG Standards:**
- AA normal: 4.5:1
- AA large: 3:1
- AAA normal: 7:1
- AAA large: 4.5:1

**Parameters:**
- `color1`, `color2` (str): Hex colors to test
- `level` (str): "AA" or "AAA"
- `large_text` (bool): True for 18pt+ or 14pt+ bold

**Returns:** Boolean

---

### `ensure_contrast(foreground, background, min_ratio=4.5, max_iterations=20)`

Automatically adjust foreground color to meet contrast requirements.

**What makes it unique:** Fixes contrast issues automatically. No trial and error. Intelligently lightens or darkens to maintain hue.

```python
# Adjust color to meet contrast
fg = "#888888"
bg = "#999999"
adjusted = vg.ensure_contrast(fg, bg, min_ratio=4.5)
print(adjusted)  # '#3d3d3d' (darkened to meet 4.5:1)

# Ensure all UI colors are readable
theme_colors = ['#3498db', '#e74c3c', '#2ecc71']
background = '#ffffff'

accessible = {
    name: vg.ensure_contrast(color, background, 4.5)
    for name, color in zip(['primary', 'error', 'success'], theme_colors)
}
```

**Parameters:**
- `foreground` (str): Color to adjust
- `background` (str): Background color
- `min_ratio` (float): Target contrast ratio
- `max_iterations` (int): Adjustment attempts

**Returns:** Adjusted hex color

---

## Color Blindness

### `simulate_colorblindness(hex_color, cb_type)`

Simulate how colors appear to colorblind individuals.

**What makes it unique:** Test your designs for ~8% of males who have color vision deficiency. Uses scientifically accurate transformation matrices.

```python
red = "#FF0000"

# Protanopia (red-blind, ~1% of males)
print(vg.simulate_colorblindness(red, "protanopia"))
# '#908400' (appears brownish-yellow)

# Deuteranopia (green-blind, ~1% of males)
print(vg.simulate_colorblindness(red, "deuteranopia"))
# '#b89000' (appears olive)

# Tritanopia (blue-blind, ~0.01% of people)
print(vg.simulate_colorblindness("#0000FF", "tritanopia"))
# '#00e1ff' (appears cyan)

# Test entire palette
palette = ['#FF0000', '#00FF00', '#0000FF']
for color in palette:
    simulated = vg.simulate_colorblindness(color, "deuteranopia")
    print(f"{color} → {simulated}")
```

**Color Blindness Types:**
- `protanopia` - Red-blind (no red cones)
- `deuteranopia` - Green-blind (no green cones)
- `tritanopia` - Blue-blind (no blue cones)
- `protanomaly` - Red-weak (defective red cones)
- `deuteranomaly` - Green-weak (defective green cones)
- `tritanomaly` - Blue-weak (defective blue cones)

**Parameters:**
- `hex_color` (str): Color to simulate
- `cb_type` (str): Type of color blindness

**Returns:** Simulated hex color

---

### `validate_colorblind_safety(colors, cb_type="deuteranopia", min_difference=30)`

Check if palette colors are distinguishable for colorblind users.

**What makes it unique:** Validates entire palettes at once. Identifies which color pairs are problematic.

```python
# Test palette safety
colors = ["#FF0000", "#00FF00", "#0000FF"]
is_safe, problems = vg.validate_colorblind_safety(colors, "deuteranopia")

if not is_safe:
    print(f"Warning: Colors at indices {problems[0]} are too similar")
    # e.g., "Warning: Colors at indices (0, 1) are too similar"

# Test all types
for cb_type in ["protanopia", "deuteranopia", "tritanopia"]:
    is_safe, problems = vg.validate_colorblind_safety(palette, cb_type)
    print(f"{cb_type}: {'✓ Safe' if is_safe else '✗ Unsafe'}")
```

**Parameters:**
- `colors` (list): List of hex colors
- `cb_type` (str): Color blindness type
- `min_difference` (float): Minimum perceptual distance

**Returns:** Tuple of (is_safe: bool, problems: list of index pairs)

---

##  Palette Persistence

### `save_palette(colors, filename, metadata=None)` / `load_palette(filename)`

Save and load color palettes to/from JSON.

**What makes it unique:** Version control your color schemes. Share palettes across projects. Include metadata like name, author, description.

```python
# Generate and save palette
palette = vg.generate_palette("#3498db", "triadic", 6)
vg.save_palette(
    palette, 
    "ocean_theme.json",
    metadata={
        "name": "Ocean Blues",
        "author": "Designer Name",
        "scheme": "triadic",
        "description": "Professional blue palette for corporate sites"
    }
)

# Load and use
colors, metadata = vg.load_palette("ocean_theme.json")
print(f"Loaded: {metadata['name']}")
print(vg.preview_palette(colors))
```

---

### `save_theme(theme, filename, metadata=None)` / `load_theme(filename)`

Save and load complete semantic themes.

**What makes it unique:** Persist entire application color schemes. Switch themes by loading different files.

```python
# Create and save theme
theme = vg.generate_theme_palette("complementary", "#3498db")
vg.save_theme(
    theme,
    "corporate_theme.json",
    metadata={
        "name": "Corporate Blue",
        "for": "enterprise dashboard",
        "created": "2025-01-01"
    }
)

# Load and apply
theme, metadata = vg.load_theme("corporate_theme.json")
vg.apply_palette_theme(theme)
print(f"Applied: {metadata['name']}")

# Now all semantic tags use loaded theme
vg.write("<primary>Primary</primary> <error>Error</error>")
```

---

##  Real-World Examples

### Beautiful CLI Logger

```python
import vargula as vg
import time

vg.set_theme({
    "timestamp": {"color": "bright_black"},
    "info": {"color": "cyan"},
    "success": {"color": "green", "look": "bold"},
    "error": {"color": "red", "look": "bold"},
    "warning": {"color": "yellow", "look": "bold"},
})

def log(level, message):
    timestamp = time.strftime("%H:%M:%S")
    vg.write(f"<timestamp>[{timestamp}]</timestamp> <{level}>{level.upper():<7}</{level}> {message}")

log("info", "Application started")
log("success", "Database connected")
log("warning", "High memory usage")
log("error", "Failed to load config")
```

### Accessible Theme Generator

```python
import vargula as vg

# Generate theme that meets WCAG AA on dark background
theme = vg.generate_accessible_theme(
    base_color="#e74c3c",
    scheme="complementary",
    background="#1a1a1a",
    wcag_level="AA"
)

# Verify all colors are accessible
for name, color in theme.items():
    if name in ['primary', 'error', 'success']:
        ratio = vg.calculate_contrast_ratio(color, theme['background'])
        print(f"{name}: {color} - Contrast: {ratio:.2f}")

# Apply and use
vg.apply_palette_theme(theme)
vg.write("<primary>Primary text</primary> <error>Error text</error>")
```

### Colorblind-Safe Palette

```python
import vargula as vg

# Generate palette
palette = vg.generate_palette("#3498db", "triadic", 5)

# Validate for different types of colorblindness
for cb_type in ["deuteranopia", "protanopia", "tritanopia"]:
    is_safe, problems = vg.validate_colorblind_safety(palette, cb_type)
    
    if is_safe:
        print(f"✓ Palette is safe for {cb_type}")
    else:
        print(f"✗ Palette has issues for {cb_type}")
        print(f"  Problem pairs: {problems}")

# Preview how it looks to colorblind users
print("\nDeuteranopia simulation:")
for color in palette:
    simulated = vg.simulate_colorblindness(color, "deuteranopia")
    print(vg.style("████", color=color), "→", vg.style("████", color=simulated))
```

### Status Dashboard

```python
import vargula as vg

vg.set_theme({
    "header": {"color": "cyan", "look": "bold"},
    "good": {"color": "green"},
    "warn": {"color": "yellow"},
    "error": {"color": "red"},
    "dim": {"color": "bright_black"},
})

vg.write("""
<header>╔══════════════════════════════════╗</header>
<header>║        SYSTEM STATUS             ║</header>
<header>╚══════════════════════════════════╝</header>

<dim>Server Status</dim>
  web-01     <good>● ONLINE</good>   CPU: 23%  Mem: 45%
  web-02     <warn>◐ WARNING</warn>  CPU: 78%  Mem: 82%
  db-01      <error>○ OFFLINE</error>  CPU: --   Mem: --

<dim>Services</dim>
  nginx      <good>✓ Running</good>
  postgres   <good>✓ Running</good>
  redis      <error>✗ Stopped</error>
""")
```

### Progress with Dynamic Colors

```python
import vargula as vg
import time

def progress_bar(current, total):
    percent = int((current / total) * 100)
    filled = int((current / total) * 40)
    
    # Dynamic color based on progress
    if percent < 50:
        color = "#e74c3c"  # Red
    elif percent < 80:
        color = "#f39c12"  # Yellow
    else:
        color = "#2ecc71"  # Green
    
    bar = vg.style("█" * filled, color=color)
    empty = vg.style("░" * (40 - filled), color="bright_black")
    
    print(f"\r{bar}{empty} {percent}%", end="", flush=True)

for i in range(101):
    progress_bar(i, 100)
    time.sleep(0.02)
print()
```

---

##  Utility Functions

```python
import vargula as vg

# Remove markup tags
markup = "<red>Hello</red> <bold>World</bold>"
plain = vg.strip(markup)  # "Hello World"

# Remove ANSI codes
styled = vg.style("Hello", color="red")
clean = vg.clean(styled)  # "Hello"

# Get visible length (ignoring ANSI)
styled = vg.style("Hello", color="red", look="bold")
length = vg.length(styled)  # 5 (not 19)

# Temporarily disable/enable
vg.disable()  # All styling returns plain text
vg.enable()   # Re-enable styling

# Temporary styles (context manager)
with vg.temporary("temp", color="magenta"):
    vg.write("<temp>Temporary style</temp>")
# Style auto-deleted after context
```

---

##  Environment Variables

```bash
# Disable all colors (standard)
export NO_COLOR=1

# Force colors even in pipes/redirects
export FORCE_COLOR=1

# Disable in production
if os.getenv("PRODUCTION"):
    vg.disable()
```

---

##  Palette Persistence

```python
import vargula as vg

# Generate and save palette
palette = vg.generate_palette("#3498db", "complementary", 5)
vg.save_palette(palette, "my_palette.json", 
                metadata={"name": "Ocean", "scheme": "complementary"})

# Load and use
colors, metadata = vg.load_palette("my_palette.json")
print(f"Loaded: {metadata['name']}")

# Save/load complete themes
theme = vg.generate_theme_palette("triadic", "#9b59b6")
vg.save_theme(theme, "purple_theme.json")

theme, metadata = vg.load_theme("purple_theme.json")
vg.apply_palette_theme(theme)
```

---

##  Comparison

| Feature | vargula | colorama | rich |
|---------|---------|----------|------|
| **Size** | 50KB | 25KB | 500KB+ |
| **Dependencies** | 0 | 0 | Multiple |
| **Markup syntax** | ✔ | ✗ | ✔ |
| **Hex/RGB colors** | ✔ | ✗ | ✔ |
| **Palette generation** | ✔ | ✗ | ✗ |
| **WCAG checking** | ✔ | ✗ | ✗ |
| **Colorblind simulation** | ✔ | ✗ | ✗ |
| **Color manipulation** | ✔ | ✗ | ✗ |
| **Tables/layouts** | ✗ | ✗ | ✔ |
| **Import speed** | Fast | Fast | Slower |

**Use vargula if you need:**
- Simple, clean styling without complexity
- Color theory and palette generation
- Accessibility features (WCAG, colorblind support)
- Lightweight package with fast imports
- Just styling, not full TUI framework

**Use rich if you need:**
- Tables, progress bars, panels, layouts
- Syntax highlighting for code
- Full-featured TUI framework
- Don't mind larger dependency

---

##  Requirements

- Python 3.6+
- No external dependencies

### Platform Support

| Platform | Status |
|----------|--------|
| Linux    | ✔ Full support |
| macOS    | ✔ Full support |
| Windows  | ✔ Full support (ANSI auto-enabled) |

---

## Contributing

Contributions welcome! To contribute:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

### Development Setup

```bash
git clone https://github.com/crystallinecore/vargula.git
cd vargula
pip install -e .

# Run tests
python -m vargula
```

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

##  Links

- **GitHub:** [github.com/crystallinecore/vargula](https://github.com/crystallinecore/vargula)
- **PyPI:** [pypi.org/project/vargula](https://pypi.org/project/vargula)
- **Issues:** [Report bugs or request features](https://github.com/crystallinecore/vargula/issues)

---

<div align="center">

**Made with ❤️ by Sivaprasad Murali**

If vargula helps your project, consider giving it a ⭐ on GitHub!

</div>

---