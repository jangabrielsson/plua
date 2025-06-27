"""
HTML Extensions for PLua
Provides functions to convert HTML content to console-friendly text with ANSI color codes
"""

import re
from .registry import registry


# ANSI color codes for 256-color support
ANSI_COLORS = {
    # Basic colors
    'black': 0, 'red': 9, 'green': 2, 'yellow': 11, 'blue': 12,
    'magenta': 201, 'cyan': 6, 'white': 15, 'gray': 8, 'grey': 8,

    # Bright colors
    'bright_black': 8, 'bright_red': 9, 'bright_green': 10, 'bright_yellow': 11,
    'bright_blue': 12, 'bright_magenta': 13, 'bright_cyan': 14, 'bright_white': 15,

    # Extended colors (16-231 are RGB colors)
    'orange': 214, 'purple': 99, 'pink': 218, 'brown': 130,
    'light_blue': 39, 'light_green': 46, 'light_red': 203, 'light_yellow': 227,

    # Grays
    'dark_gray': 236, 'light_gray': 248,

    # Common web colors
    'navy': 4, 'teal': 6, 'olive': 3, 'lime': 10, 'fuchsia': 13,
    'aqua': 14, 'maroon': 1, 'silver': 7, 'gold': 220, 'indigo': 55,

    # Additional comprehensive color set
    'aquamarine1': 122, 'aquamarine3': 79, 'blue1': 21, 'blue3': 20, 'blueviolet': 57,
    'cadetblue': 73, 'chartreuse1': 118, 'chartreuse2': 112, 'chartreuse3': 76,
    'chartreuse4': 64, 'cornflowerblue': 69, 'cornsilk1': 230, 'cyan1': 51,
    'cyan2': 50, 'cyan3': 43, 'darkblue': 18, 'darkcyan': 36, 'darkgoldenrod': 136,
    'darkgreen': 22, 'darkkhaki': 143, 'darkmagenta': 91, 'darkolivegreen1': 192,
    'darkolivegreen2': 155, 'darkolivegreen3': 149, 'darkorange': 208, 'darkorange3': 166,
    'darkred': 88, 'darkseagreen': 108, 'darkseagreen1': 193, 'darkseagreen2': 157,
    'darkseagreen3': 150, 'darkseagreen4': 71, 'darkslategray1': 123, 'darkslategray2': 87,
    'darkslategray3': 116, 'darkturquoise': 44, 'darkviolet': 128, 'deeppink1': 199,
    'deeppink2': 197, 'deeppink3': 162, 'deeppink4': 125, 'deepskyblue1': 39,
    'deepskyblue2': 38, 'deepskyblue3': 32, 'deepskyblue4': 25, 'dodgerblue1': 33,
    'dodgerblue2': 27, 'dodgerblue3': 26, 'gold1': 220, 'gold3': 178,
    'green1': 46, 'green3': 40, 'green4': 28, 'greenyellow': 154,
    'grey0': 16, 'grey100': 231, 'grey11': 234, 'grey15': 235,
    'grey19': 236, 'grey23': 237, 'grey27': 238, 'grey3': 232, 'grey30': 239,
    'grey35': 240, 'grey37': 59, 'grey39': 241, 'grey42': 242, 'grey46': 243,
    'grey50': 244, 'grey53': 102, 'grey54': 245, 'grey58': 246, 'grey62': 247,
    'grey63': 139, 'grey66': 248, 'grey69': 145, 'grey7': 233, 'grey70': 249,
    'grey74': 250, 'grey78': 251, 'grey82': 252, 'grey84': 188, 'grey85': 253,
    'grey89': 254, 'grey93': 255, 'honeydew2': 194, 'hotpink': 206, 'hotpink2': 169,
    'hotpink3': 168, 'indianred': 167, 'indianred1': 204, 'khaki1': 228, 'khaki3': 185,
    'coral': 210, 'lightcoral': 210, 'lightcyan1': 195, 'lightcyan3': 152,
    'lightgoldenrod1': 227, 'lightgoldenrod2': 222, 'lightgoldenrod3': 179,
    'lightgreen': 120, 'lightpink1': 217, 'lightpink3': 174, 'lightpink4': 95,
    'lightsalmon1': 216, 'lightsalmon3': 173, 'lightseagreen': 37, 'lightskyblue1': 153,
    'lightskyblue3': 110, 'lightslateblue': 105, 'lightslategrey': 103, 'lightsteelblue': 147,
    'lightsteelblue1': 189, 'lightsteelblue3': 146, 'lightyellow3': 187,
    'magenta2': 200, 'magenta3': 164, 'mediumorchid': 134,
    'mediumorchid1': 207, 'mediumorchid3': 133, 'mediumpurple': 104, 'mediumpurple1': 141,
    'mediumpurple2': 140, 'mediumpurple3': 98, 'mediumpurple4': 60, 'mediumspringgreen': 49,
    'mediumturquoise': 80, 'mediumvioletred': 126, 'mistyrose1': 224, 'mistyrose3': 181,
    'navajowhite1': 223, 'navajowhite3': 144, 'navyblue': 17,
    'orange3': 172, 'orange4': 94, 'orangered1': 202, 'orchid': 170,
    'orchid1': 213, 'orchid2': 212, 'palegreen1': 156, 'palegreen3': 114, 'paleturquoise1': 159,
    'paleturquoise4': 66, 'palevioletred1': 211, 'pink3': 175, 'plum1': 219,
    'plum2': 183, 'plum3': 176, 'plum4': 96, 'purple0': 93, 'purple3': 56, 'purple4': 55,
    'purple5': 129, 'purples': 5, 'red1': 196, 'red3': 160, 'rosybrown': 138,
    'royalblue1': 63, 'salmon1': 209, 'sandybrown': 215, 'seagreen1': 85, 'seagreen2': 83,
    'seagreen3': 78, 'skyblue': 117, 'skyblue2': 111, 'skyblue3': 74,
    'slateblue1': 99, 'slateblue3': 62, 'springgreen1': 48, 'springgreen2': 47,
    'springgreen3': 41, 'springgreen4': 29, 'steelblue': 67, 'steelblue1': 81,
    'steelblue3': 68, 'tan': 180, 'thistle1': 225, 'thistle3': 182,
    'turquoise2': 45, 'turquoise4': 30, 'violet': 177, 'wheat1': 229, 'wheat4': 101,
    'yellow1': 226, 'yellow2': 190, 'yellow3': 184, 'yellow4': 106, 'floralwhite': 230,
    'darkslateblue': 60, 'gainsboro': 188, 'slategray': 102, 'darkslategray': 58,
    'lemonchiffon': 187, 'khaki': 143, 'lightgoldenrodyellow': 186, 'lavenderblush': 225,
    'lavender': 189, 'slateblue': 62, 'deepskyblue': 39
}


def _get_ansi_color_code(color_name):
    """Get ANSI color code for a color name"""
    color_name = color_name.lower().strip()

    # Direct color name lookup
    if color_name in ANSI_COLORS:
        return ANSI_COLORS[color_name]

    # Handle hex colors (convert to closest 256 color)
    if color_name.startswith('#') and len(color_name) == 7:
        try:
            # Convert hex to RGB
            r = int(color_name[1:3], 16)
            g = int(color_name[3:5], 16)
            b = int(color_name[5:7], 16)

            # Convert RGB to 256 color code
            # This is a simplified conversion - for more accuracy, you'd need a full color mapping
            if r == g == b:
                # Grayscale
                gray = int(r * 5 / 255)
                return 232 + gray
            else:
                # RGB color (6x6x6 cube)
                r_idx = int(r * 5 / 255)
                g_idx = int(g * 5 / 255)
                b_idx = int(b * 5 / 255)
                return 16 + (r_idx * 36) + (g_idx * 6) + b_idx
        except ValueError:
            pass

    # Handle rgb() format
    rgb_match = re.match(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)', color_name)
    if rgb_match:
        try:
            r = int(rgb_match.group(1))
            g = int(rgb_match.group(2))
            b = int(rgb_match.group(3))

            if r == g == b:
                gray = int(r * 5 / 255)
                return 232 + gray
            else:
                r_idx = int(r * 5 / 255)
                g_idx = int(g * 5 / 255)
                b_idx = int(b * 5 / 255)
                return 16 + (r_idx * 36) + (g_idx * 6) + b_idx
        except ValueError:
            pass

    # Default to white if color not found
    return 7


def _apply_ansi_color(text, color_code):
    """Apply ANSI color code to text"""
    return f"\033[38;5;{color_code}m{text}\033[0m"


def _parse_html_tags(html_text):
    """Parse HTML text and convert to console-friendly text with ANSI colors"""
    if not html_text:
        return ""

    # Replace HTML entities
    html_text = html_text.replace('&nbsp;', ' ')
    html_text = html_text.replace('&amp;', '&')
    html_text = html_text.replace('&lt;', '<')
    html_text = html_text.replace('&gt;', '>')
    html_text = html_text.replace('&quot;', '"')
    html_text = html_text.replace('&#39;', "'")

    # Handle <br> and </br> tags
    html_text = re.sub(r'</?br\s*/?>', '\n', html_text, flags=re.IGNORECASE)

    # Process the text with color stack
    color_stack = []
    result = ""
    i = 0
    
    while i < len(html_text):
        if html_text[i] == '<':
            # Check if this is a font tag
            if html_text[i:i+5].lower() == '<font':
                # Find the end of the opening font tag
                tag_end = html_text.find('>', i)
                if tag_end == -1:
                    # Malformed tag, treat as text
                    result += html_text[i:]
                    break
                
                # Extract the font tag
                font_tag = html_text[i:tag_end+1]
                
                # Extract color attribute
                color_match = re.search(r'color\s*=\s*[\'"]([^\'"]+)[\'"]', font_tag, re.IGNORECASE)
                if color_match:
                    color_name = color_match.group(1)
                    color_code = _get_ansi_color_code(color_name)
                    color_stack.append(color_code)
                
                i = tag_end + 1
                
            elif html_text[i:i+7].lower() == '</font>':
                # Closing font tag
                if color_stack:
                    color_stack.pop()
                i += 7
                
            else:
                # Not a font tag, treat as text, apply color if active
                char = html_text[i]
                if color_stack:
                    result += _apply_ansi_color(char, color_stack[-1])
                else:
                    result += char
                i += 1
        else:
            # Regular text character
            char = html_text[i]
            if color_stack:
                result += _apply_ansi_color(char, color_stack[-1])
            else:
                result += char
            i += 1

    return result


def _find_matching_closing_tag(html_text, start_pos):
    """Find the matching closing </font> tag, handling nested tags correctly"""
    depth = 1  # We're already inside one font tag
    i = start_pos

    while i < len(html_text):
        # Look for opening font tags
        if html_text[i:i+5].lower() == '<font':
            depth += 1
            # Skip to end of this tag
            tag_end = html_text.find('>', i)
            if tag_end == -1:
                return -1  # Malformed HTML
            i = tag_end + 1
        # Look for closing font tags
        elif html_text[i:i+7].lower() == '</font>':
            depth -= 1
            if depth == 0:
                return i  # Found the matching closing tag
            i += 7
        else:
            i += 1

    return -1  # No matching closing tag found


@registry.register(description="Convert HTML tags to console-friendly text with ANSI colors", category="html")
def html2console(html_text):
    """
    Convert HTML text to console-friendly text with ANSI color codes.

    Supports:
    - <br> and </br> tags -> newlines
    - &nbsp; -> space
    - <font color='name'>...</font> -> ANSI color codes
    - Nested font tags
    - Common HTML entities

    Args:
        html_text (str): HTML text to convert

    Returns:
        str: Console-friendly text with ANSI color codes
    """
    if not isinstance(html_text, str):
        return str(html_text)

    return _parse_html_tags(html_text)


@registry.register(description="Get available color names for HTML conversion", category="html", inject_runtime=True)
def get_available_colors(lua_runtime):
    """
    Get a list of available color names that can be used in font tags.

    Returns:
        table: Lua table with available color names
    """
    return lua_runtime.table(*ANSI_COLORS.keys())


@registry.register(description="Test HTML to console conversion with examples", category="html")
def test_html_conversion():
    """
    Test the HTML to console conversion with various examples.

    Returns:
        str: Test output showing different conversions
    """
    test_cases = [
        "Hello <font color='red'>World</font>!",
        "Line 1<br>Line 2<br/>Line 3",
        "Space&nbsp;here",
        "<font color='blue'>Blue <font color='red'>Red</font> Blue</font>",
        "<font color='#FF0000'>Red hex</font>",
        "<font color='rgb(0,255,0)'>Green RGB</font>"
    ]

    result = "HTML to Console Conversion Test:\n"
    result += "=" * 40 + "\n\n"

    for i, test in enumerate(test_cases, 1):
        result += f"Test {i}: {test}\n"
        result += f"Result: {html2console(test)}\n\n"

    return result
