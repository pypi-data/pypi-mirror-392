"""
StyleManager - Verwaltet die visuellen Eigenschaften und das Styling von Tabellen.
"""

try:
    from rich.console import Console
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class StyleManager:
    """Verwaltet Styling-Optionen für Tabellen."""
    
    # Border-Stile Definitionen
    BORDER_STYLES = {
        "single": {
            "horizontal": "─",
            "vertical": "│",
            "top_left": "┌",
            "top_right": "┐",
            "bottom_left": "└",
            "bottom_right": "┘",
            "top_tee": "┬",
            "bottom_tee": "┴",
            "left_tee": "├",
            "right_tee": "┤",
            "cross": "┼"
        },
        "double": {
            "horizontal": "═",
            "vertical": "║",
            "top_left": "╔",
            "top_right": "╗",
            "bottom_left": "╚",
            "bottom_right": "╝",
            "top_tee": "╦",
            "bottom_tee": "╩",
            "left_tee": "╠",
            "right_tee": "╣",
            "cross": "╬"
        },
        "rounded": {
            "horizontal": "─",
            "vertical": "│",
            "top_left": "╭",
            "top_right": "╮",
            "bottom_left": "╰",
            "bottom_right": "╯",
            "top_tee": "┬",
            "bottom_tee": "┴",
            "left_tee": "├",
            "right_tee": "┤",
            "cross": "┼"
        },
        "minimal": {
            "horizontal": " ",
            "vertical": "│",
            "top_left": " ",
            "top_right": " ",
            "bottom_left": " ",
            "bottom_right": " ",
            "top_tee": " ",
            "bottom_tee": " ",
            "left_tee": "│",
            "right_tee": "│",
            "cross": " "
        },
        "none": {
            "horizontal": " ",
            "vertical": " ",
            "top_left": " ",
            "top_right": " ",
            "bottom_left": " ",
            "bottom_right": " ",
            "top_tee": " ",
            "bottom_tee": " ",
            "left_tee": " ",
            "right_tee": " ",
            "cross": " "
        }
    }
    
    def __init__(self):
        self._border_style = "single"
        self._alignment = "left"
        self._padding = 1
        self._use_colors = RICH_AVAILABLE
        self._header_color = "bold cyan"
        self._footer_color = "bold yellow"
        self._row_colors = None  # Dict: row_index -> color
        self._cell_colors = {}  # Dict: (row, col) -> color
        self._cell_bg_colors = {}  # Dict: (row, col) -> background color
        self._row_bg_colors = {}  # Dict: row_index -> background color
        self._cell_formats = {}  # Dict: (row, col) -> format dict
        self._row_formats = {}  # Dict: row_index -> format dict
        self._custom_themes = {}  # Dict: theme_name -> theme_config
        self._theme = "default"
        self._console = Console() if RICH_AVAILABLE else None
    
    def set_border_style(self, style):
        """
        Setzt den Border-Stil.
        
        Args:
            style: Einer der verfügbaren Stile ("single", "double", "rounded", "minimal", "none")
        """
        if style not in self.BORDER_STYLES:
            raise ValueError(f"Ungültiger Border-Stil: {style}. Verfügbar: {list(self.BORDER_STYLES.keys())}")
        self._border_style = style
    
    def set_alignment(self, alignment):
        """
        Setzt die Textausrichtung.
        
        Args:
            alignment: "left", "center", oder "right"
        """
        if alignment not in ["left", "center", "right"]:
            raise ValueError(f"Ungültige Ausrichtung: {alignment}. Verfügbar: left, center, right")
        self._alignment = alignment
    
    def set_padding(self, padding):
        """
        Setzt den Padding-Wert.
        
        Args:
            padding: Anzahl der Leerzeichen auf jeder Seite
        """
        self._padding = max(0, int(padding))
    
    def get_border_chars(self):
        """Gibt die Border-Zeichen für den aktuellen Stil zurück."""
        return self.BORDER_STYLES[self._border_style]
    
    def get_alignment(self):
        """Gibt die aktuelle Textausrichtung zurück."""
        return self._alignment
    
    def get_padding(self):
        """Gibt den aktuellen Padding-Wert zurück."""
        return self._padding
    
    def align_text(self, text, width):
        """
        Richtet Text entsprechend der eingestellten Ausrichtung aus.
        
        Args:
            text: Der zu formatierende Text
            width: Die Zielbreite
        
        Returns:
            Formatierter Text
        """
        text = str(text)
        padding = self._padding
        available_width = width - (2 * padding)
        
        if len(text) > available_width:
            text = text[:available_width-3] + "..."
        
        if self._alignment == "left":
            return text.ljust(available_width)
        elif self._alignment == "right":
            return text.rjust(available_width)
        elif self._alignment == "center":
            return text.center(available_width)
        else:
            return text.ljust(available_width)
    
    def set_colors(self, enabled=True):
        """
        Aktiviert/deaktiviert Farben.
        
        Args:
            enabled: True um Farben zu aktivieren
        """
        self._use_colors = enabled and RICH_AVAILABLE
    
    def set_header_color(self, color):
        """
        Setzt die Farbe für Header.
        
        Args:
            color: Rich-Farbstring (z.B. "bold cyan", "red", "green")
        """
        self._header_color = color
    
    def set_footer_color(self, color):
        """
        Setzt die Farbe für Footer.
        
        Args:
            color: Rich-Farbstring
        """
        self._footer_color = color
    
    def set_row_color(self, row_index, color):
        """
        Setzt die Farbe für eine bestimmte Zeile.
        
        Args:
            row_index: Index der Zeile
            color: Rich-Farbstring
        """
        if self._row_colors is None:
            self._row_colors = {}
        self._row_colors[row_index] = color
    
    def set_cell_color(self, row_index, col_index, color):
        """
        Setzt die Vordergrundfarbe für eine bestimmte Zelle.
        
        Args:
            row_index: Index der Zeile
            col_index: Index der Spalte
            color: Rich-Farbstring (z.B. "red", "bold green", "rgb(255,0,0)")
        """
        self._cell_colors[(row_index, col_index)] = color
    
    def set_cell_bg_color(self, row_index, col_index, bg_color):
        """
        Setzt die Hintergrundfarbe für eine bestimmte Zelle.
        
        Args:
            row_index: Index der Zeile
            col_index: Index der Spalte
            bg_color: Hintergrundfarbe (z.B. "on red", "on rgb(255,0,0)")
        """
        self._cell_bg_colors[(row_index, col_index)] = bg_color
    
    def set_row_bg_color(self, row_index, bg_color):
        """
        Setzt die Hintergrundfarbe für eine bestimmte Zeile.
        
        Args:
            row_index: Index der Zeile
            bg_color: Hintergrundfarbe (z.B. "on red", "on rgb(255,0,0)")
        """
        self._row_bg_colors[row_index] = bg_color
    
    def set_cell_format(self, row_index, col_index, bold=False, italic=False, underline=False):
        """
        Setzt Text-Formatierung für eine bestimmte Zelle.
        
        Args:
            row_index: Index der Zeile
            col_index: Index der Spalte
            bold: Fettdruck
            italic: Kursiv
            underline: Unterstrichen
        """
        self._cell_formats[(row_index, col_index)] = {
            "bold": bold,
            "italic": italic,
            "underline": underline
        }
    
    def set_row_format(self, row_index, bold=False, italic=False, underline=False):
        """
        Setzt Text-Formatierung für eine bestimmte Zeile.
        
        Args:
            row_index: Index der Zeile
            bold: Fettdruck
            italic: Kursiv
            underline: Unterstrichen
        """
        self._row_formats[row_index] = {
            "bold": bold,
            "italic": italic,
            "underline": underline
        }
    
    def rgb_color(self, r, g, b):
        """
        Erstellt einen RGB-Farbstring.
        
        Args:
            r: Rot-Wert (0-255)
            g: Grün-Wert (0-255)
            b: Blau-Wert (0-255)
        
        Returns:
            RGB-Farbstring für Rich
        """
        return f"rgb({r},{g},{b})"
    
    def rgb_bg_color(self, r, g, b):
        """
        Erstellt einen RGB-Hintergrundfarbstring.
        
        Args:
            r: Rot-Wert (0-255)
            g: Grün-Wert (0-255)
            b: Blau-Wert (0-255)
        
        Returns:
            RGB-Hintergrundfarbstring für Rich
        """
        return f"on rgb({r},{g},{b})"
    
    def set_theme(self, theme_name):
        """
        Setzt ein vordefiniertes oder benutzerdefiniertes Theme.
        
        Args:
            theme_name: "default", "dark", "light", "colorful" oder Name eines Custom-Themes
        """
        self._theme = theme_name
        
        # Vordefinierte Themes
        builtin_themes = {
            "default": {
                "header": "bold cyan",
                "footer": "bold yellow",
                "header_bg": None,
                "footer_bg": None
            },
            "dark": {
                "header": "bold white",
                "footer": "bold white",
                "header_bg": None,
                "footer_bg": None
            },
            "light": {
                "header": "bold blue",
                "footer": "bold magenta",
                "header_bg": None,
                "footer_bg": None
            },
            "colorful": {
                "header": "bold bright_cyan",
                "footer": "bold bright_yellow",
                "header_bg": None,
                "footer_bg": None
            }
        }
        
        # Prüfe ob es ein Custom-Theme ist
        if theme_name in self._custom_themes:
            theme_config = self._custom_themes[theme_name]
            self._header_color = theme_config.get("header", "bold cyan")
            self._footer_color = theme_config.get("footer", "bold yellow")
        elif theme_name in builtin_themes:
            theme_config = builtin_themes[theme_name]
            self._header_color = theme_config["header"]
            self._footer_color = theme_config["footer"]
    
    def register_theme(self, theme_name, header_color=None, footer_color=None, 
                       header_bg=None, footer_bg=None):
        """
        Registriert ein benutzerdefiniertes Theme.
        
        Args:
            theme_name: Name des Themes
            header_color: Farbe für Header (z.B. "bold cyan", "rgb(255,0,0)")
            footer_color: Farbe für Footer
            header_bg: Hintergrundfarbe für Header
            footer_bg: Hintergrundfarbe für Footer
        """
        self._custom_themes[theme_name] = {
            "header": header_color or "bold cyan",
            "footer": footer_color or "bold yellow",
            "header_bg": header_bg,
            "footer_bg": footer_bg
        }
    
    def format_text(self, text, color=None, bg_color=None, bold=False, italic=False, 
                   underline=False, is_header=False, is_footer=False, 
                   row_index=None, col_index=None):
        """
        Formatiert Text mit Farben und Formatierung (falls aktiviert).
        
        Args:
            text: Der zu formatierende Text
            color: Optionale Vordergrundfarbe
            bg_color: Optionale Hintergrundfarbe
            bold: Fettdruck
            italic: Kursiv
            underline: Unterstrichen
            is_header: Ob es ein Header ist
            is_footer: Ob es ein Footer ist
            row_index: Zeilenindex (für Zellfarben)
            col_index: Spaltenindex (für Zellfarben)
        
        Returns:
            Formatierter Text (String oder Rich Text)
        """
        if not self._use_colors:
            return str(text)
        
        # Baue Style-String zusammen
        style_parts = []
        
        # Header/Footer Farben
        if is_header:
            if self._header_color:
                style_parts.append(self._header_color)
        elif is_footer:
            if self._footer_color:
                style_parts.append(self._footer_color)
        elif row_index is not None and col_index is not None:
            # Zell-spezifische Farben und Formatierung
            cell_color = self._cell_colors.get((row_index, col_index))
            cell_bg = self._cell_bg_colors.get((row_index, col_index))
            cell_format = self._cell_formats.get((row_index, col_index), {})
            
            if cell_color:
                style_parts.append(cell_color)
            if cell_bg:
                style_parts.append(cell_bg)
            if cell_format.get("bold"):
                style_parts.append("bold")
            if cell_format.get("italic"):
                style_parts.append("italic")
            if cell_format.get("underline"):
                style_parts.append("underline")
        elif row_index is not None:
            # Zeilen-spezifische Farben und Formatierung
            row_color = self._row_colors.get(row_index) if self._row_colors else None
            row_bg = self._row_bg_colors.get(row_index)
            row_format = self._row_formats.get(row_index, {})
            
            if row_color:
                style_parts.append(row_color)
            if row_bg:
                style_parts.append(row_bg)
            if row_format.get("bold"):
                style_parts.append("bold")
            if row_format.get("italic"):
                style_parts.append("italic")
            if row_format.get("underline"):
                style_parts.append("underline")
        
        # Explizite Parameter (überschreiben Zell/Zeilen-Styles)
        if color:
            style_parts.append(color)
        if bg_color:
            style_parts.append(bg_color)
        if bold:
            style_parts.append("bold")
        if italic:
            style_parts.append("italic")
        if underline:
            style_parts.append("underline")
        
        # Erstelle Rich-Formatierung
        if style_parts:
            style_str = " ".join(style_parts)
            return f"[{style_str}]{text}[/{style_str}]"
        
        return str(text)
    
    def get_row_color(self, row_index):
        """Gibt die Farbe für eine Zeile zurück."""
        if self._row_colors:
            return self._row_colors.get(row_index)
        return None

