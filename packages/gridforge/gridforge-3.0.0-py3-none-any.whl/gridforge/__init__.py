"""
GridForge - Eine extrem schnelle und moderne Python-Bibliothek zur Erstellung von Tabellen in der Konsole.
"""

from .table_generator import TableGenerator
from .style_manager import StyleManager
from .export_manager import ExportManager
from .data_validator import DataValidator
from .input_handler import InputHandler
from .builder import GridBuilder, grid

__version__ = "3.0.0"
__all__ = ["create", "Table", "GridBuilder", "grid"]


class Table:
    """Hauptklasse für die einfache Tabellenerstellung."""
    
    def __init__(self):
        self._generator = TableGenerator()
        self._style_manager = StyleManager()
        self._export_manager = ExportManager()
        self._validator = DataValidator()
        self._input_handler = InputHandler()
        self._headers = None
        self._rows = []
        self._footer = None
        self._created = False
    
    def create(self, headers=None):
        """
        Erstellt eine neue Tabelle.
        
        Args:
            headers: Liste von Header-Strings (optional)
        
        Returns:
            self für Method-Chaining
        """
        self._headers = headers if headers else []
        self._rows = []
        self._created = True
        return self
    
    def add_row(self, *args):
        """
        Fügt eine Zeile zur Tabelle hinzu.
        
        Args:
            *args: Werte für die Zeile
        
        Returns:
            self für Method-Chaining
        """
        if not self._created:
            raise ValueError("Tabelle muss zuerst mit create() erstellt werden")
        
        row = list(args)
        self._rows.append(row)
        return self
    
    def set_footer(self, *args):
        """
        Setzt einen Footer für die Tabelle.
        
        Args:
            *args: Footer-Werte
        
        Returns:
            self für Method-Chaining
        """
        self._footer = list(args)
        return self
    
    def display(self):
        """
        Zeigt die Tabelle in der Konsole an.
        """
        if not self._created:
            raise ValueError("Tabelle muss zuerst mit create() erstellt werden")
        
        # Setze Daten nur wenn noch nicht gesetzt oder wenn sich Daten geändert haben
        if (self._generator._headers != self._headers or 
            self._generator._rows != self._rows or 
            self._generator._footer != self._footer):
            self._generator.set_data(self._headers, self._rows, self._footer)
        
        self._generator.set_style_manager(self._style_manager)
        output = self._generator.generate()
        
        # Rich-Formatierung ausgeben (falls verfügbar)
        if self._style_manager._use_colors and self._style_manager._console:
            self._style_manager._console.print(output)
        else:
            print(output)
        
        return self
    
    def set_border_style(self, style="single"):
        """
        Setzt den Border-Stil.
        
        Args:
            style: "single", "double", "rounded", "minimal", "none"
        """
        self._style_manager.set_border_style(style)
        return self
    
    def set_alignment(self, alignment="left"):
        """
        Setzt die Textausrichtung.
        
        Args:
            alignment: "left", "center", "right"
        """
        self._style_manager.set_alignment(alignment)
        return self
    
    # Styling-Methoden
    def set_colors(self, enabled=True):
        """Aktiviert/deaktiviert Farben."""
        self._style_manager.set_colors(enabled)
        return self
    
    def set_theme(self, theme_name):
        """Setzt ein Theme ("default", "dark", "light", "colorful")."""
        self._style_manager.set_theme(theme_name)
        return self
    
    def color_row(self, row_index, color):
        """Färbt eine Zeile ein."""
        self._style_manager.set_row_color(row_index, color)
        return self
    
    def color_cell(self, row_index, col_index, color):
        """Färbt eine Zelle ein."""
        self._style_manager.set_cell_color(row_index, col_index, color)
        return self
    
    def color_cell_bg(self, row_index, col_index, bg_color):
        """Setzt Hintergrundfarbe für eine Zelle."""
        self._style_manager.set_cell_bg_color(row_index, col_index, bg_color)
        return self
    
    def color_row_bg(self, row_index, bg_color):
        """Setzt Hintergrundfarbe für eine Zeile."""
        self._style_manager.set_row_bg_color(row_index, bg_color)
        return self
    
    def format_cell(self, row_index, col_index, bold=False, italic=False, underline=False):
        """Formatiert eine Zelle (fett, kursiv, unterstrichen)."""
        self._style_manager.set_cell_format(row_index, col_index, bold, italic, underline)
        return self
    
    def format_row(self, row_index, bold=False, italic=False, underline=False):
        """Formatiert eine Zeile (fett, kursiv, unterstrichen)."""
        self._style_manager.set_row_format(row_index, bold, italic, underline)
        return self
    
    def rgb_color(self, r, g, b):
        """Erstellt RGB-Farbe (0-255)."""
        return self._style_manager.rgb_color(r, g, b)
    
    def rgb_bg_color(self, r, g, b):
        """Erstellt RGB-Hintergrundfarbe (0-255)."""
        return self._style_manager.rgb_bg_color(r, g, b)
    
    def register_theme(self, theme_name, header_color=None, footer_color=None, 
                       header_bg=None, footer_bg=None):
        """Registriert ein benutzerdefiniertes Theme."""
        self._style_manager.register_theme(theme_name, header_color, footer_color, header_bg, footer_bg)
        return self
    
    # Datenmanipulation
    def sort(self, column_index, reverse=False):
        """Sortiert nach einer Spalte."""
        if not self._created:
            raise ValueError("Tabelle muss zuerst mit create() erstellt werden")
        # Stelle sicher, dass Daten aktuell sind
        if (self._generator._headers != self._headers or 
            self._generator._rows != self._rows or 
            self._generator._footer != self._footer):
            self._generator.set_data(self._headers, self._rows, self._footer)
        self._generator.sort(column_index, reverse)
        return self
    
    def filter(self, filter_func):
        """Filtert Zeilen basierend auf einer Funktion."""
        if not self._created:
            raise ValueError("Tabelle muss zuerst mit create() erstellt werden")
        # Stelle sicher, dass Daten aktuell sind
        if (self._generator._headers != self._headers or 
            self._generator._rows != self._rows or 
            self._generator._footer != self._footer):
            self._generator.set_data(self._headers, self._rows, self._footer)
        self._generator.filter(filter_func)
        return self
    
    def clear_filter(self):
        """Entfernt Filter."""
        self._generator.clear_filter()
        return self
    
    def page(self, page_size):
        """Aktiviert Pagination."""
        if not self._created:
            raise ValueError("Tabelle muss zuerst mit create() erstellt werden")
        # Stelle sicher, dass Daten aktuell sind
        if (self._generator._headers != self._headers or 
            self._generator._rows != self._rows or 
            self._generator._footer != self._footer):
            self._generator.set_data(self._headers, self._rows, self._footer)
        self._generator.set_page_size(page_size)
        return self
    
    def next_page(self):
        """Nächste Seite."""
        self._generator.next_page()
        return self
    
    def prev_page(self):
        """Vorherige Seite."""
        self._generator.previous_page()
        return self
    
    # Datenquellen-Integration
    def from_csv(self, filepath, has_header=True):
        """Lädt Daten aus CSV."""
        headers, rows = self._export_manager.from_csv(filepath, has_header=has_header)
        self._headers = headers if has_header else None
        self._rows = rows
        self._created = True
        return self
    
    def from_json(self, filepath):
        """Lädt Daten aus JSON."""
        headers, rows = self._export_manager.from_json(filepath)
        self._headers = headers
        self._rows = rows
        self._created = True
        return self
    
    def to_csv(self, filepath):
        """Exportiert nach CSV."""
        if not self._created:
            raise ValueError("Tabelle muss zuerst mit create() erstellt werden")
        self._export_manager.to_csv(self._headers, self._rows, filepath)
        return self
    
    def to_json(self, filepath):
        """Exportiert nach JSON."""
        if not self._created:
            raise ValueError("Tabelle muss zuerst mit create() erstellt werden")
        self._export_manager.to_json(self._headers, self._rows, filepath)
        return self
    
    # Typ-Formatierung
    def format_int(self, enabled=True, thousands_sep=False):
        """Konfiguriert Integer-Formatierung."""
        self._generator.get_type_formatter().set_int_formatting(enabled, thousands_sep)
        return self
    
    def format_float(self, enabled=True, precision=2):
        """Konfiguriert Float-Formatierung."""
        self._generator.get_type_formatter().set_float_formatting(enabled, precision)
        return self
    
    def format_bool(self, enabled=True, style="True/False"):
        """Konfiguriert Boolean-Formatierung (True/False, Yes/No, Ja/Nein, ✓/✗, 1/0)."""
        self._generator.get_type_formatter().set_bool_formatting(enabled, style)
        return self
    
    def format_datetime(self, enabled=True, format_string="%Y-%m-%d %H:%M:%S"):
        """Konfiguriert Datetime-Formatierung."""
        self._generator.get_type_formatter().set_datetime_formatting(enabled, format_string)
        return self
    
    def format_none(self, enabled=True, display="-"):
        """Konfiguriert None-Formatierung."""
        self._generator.get_type_formatter().set_none_formatting(enabled, display)
        return self


def create(headers=None):
    """
    Factory-Funktion zum Erstellen einer neuen Tabelle.
    
    Args:
        headers: Liste von Header-Strings (optional)
    
    Returns:
        Table-Instanz
    """
    return Table().create(headers)

